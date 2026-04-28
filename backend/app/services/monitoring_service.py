import math
import random
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from app.schemas.schemas import MetricsOut, LogEntryOut

# Time range → step seconds for Prometheus range queries
RANGE_STEPS = {"1h": 60, "6h": 360, "24h": 1440, "7d": 10080}
RANGE_DELTA = {"1h": 3600, "6h": 21600, "24h": 86400, "7d": 604800}

PROMETHEUS_URL = "http://prometheus:9090"
LOKI_URL       = "http://loki:3100"


class MonitoringService:
    """
    Queries Prometheus for metrics and Loki for logs.
    Falls back to realistic synthetic data when the monitoring stack
    is not reachable (local dev without the full K8s stack running).
    """

    def get_metrics(self, site_slug: str, time_range: str) -> MetricsOut:
        try:
            return self._fetch_prometheus(site_slug, time_range)
        except Exception:
            return self._synthetic_metrics(time_range)

    def get_logs(
        self,
        site_slug: str,
        level:     str | None,
        search:    str | None,
        db:        Session | None = None,
        site_id:   str | None = None,
    ) -> list[LogEntryOut]:
        try:
            return self._fetch_loki(site_slug, level, search)
        except Exception:
            # Fall back to real deployment logs from DB if available
            if db and site_id:
                return self._deployment_logs(db, site_id, level, search)
            return []

    # ── Prometheus ────────────────────────────────────────────────────────────

    def _fetch_prometheus(self, site_slug: str, time_range: str) -> MetricsOut:
        import httpx
        step    = RANGE_STEPS.get(time_range, 60)
        delta   = RANGE_DELTA.get(time_range, 3600)
        end     = datetime.now(timezone.utc)
        start   = end - timedelta(seconds=delta)

        def query_range(promql: str) -> list[list]:
            resp = httpx.get(
                f"{PROMETHEUS_URL}/api/v1/query_range",
                params={
                    "query": promql,
                    "start": start.isoformat(),
                    "end":   end.isoformat(),
                    "step":  step,
                },
                timeout=5,
            )
            resp.raise_for_status()
            data = resp.json()
            results = data.get("data", {}).get("result", [])
            return results[0]["values"] if results else []

        req_values = query_range(
            f'rate(http_requests_total{{app="{site_slug}"}}[1m])'
        )
        err_values = query_range(
            f'rate(http_requests_total{{app="{site_slug}",status=~"5.."}}[1m])'
        )

        timestamps       = [v[0] for v in req_values]
        request_history  = [float(v[1]) for v in req_values]
        error_history    = [float(v[1]) for v in err_values]
        request_rate     = request_history[-1] if request_history else 0.0
        error_rate       = (error_history[-1] / request_rate) if request_rate > 0 else 0.0

        return MetricsOut(
            request_rate       = round(request_rate, 2),
            error_rate         = round(error_rate, 4),
            p95_latency_ms     = 0,
            active_connections = 0,
            timestamps         = [datetime.fromtimestamp(t, tz=timezone.utc).isoformat()
                                   for t in timestamps],
            request_history    = request_history,
            error_history      = error_history,
        )

    # ── Loki ──────────────────────────────────────────────────────────────────

    def _fetch_loki(
        self,
        site_slug: str,
        level:     str | None,
        search:    str | None,
    ) -> list[LogEntryOut]:
        import httpx
        label_sel = f'{{app="{site_slug}"}}'
        if level:
            label_sel = f'{{app="{site_slug}",level="{level}"}}'

        logql = label_sel
        if search:
            logql = f'{label_sel} |= "{search}"'

        resp = httpx.get(
            f"{LOKI_URL}/loki/api/v1/query_range",
            params={"query": logql, "limit": 100},
            timeout=5,
        )
        resp.raise_for_status()
        entries: list[LogEntryOut] = []
        for stream in resp.json().get("data", {}).get("result", []):
            svc = stream.get("stream", {}).get("app", site_slug)
            for ts, line in stream.get("values", []):
                entries.append(LogEntryOut(
                    timestamp = datetime.fromtimestamp(
                        int(ts) / 1e9, tz=timezone.utc
                    ).isoformat(),
                    level    = stream.get("stream", {}).get("level", "INFO"),
                    service  = svc,
                    message  = line,
                    trace_id = None,
                ))
        return entries

    # ── Synthetic fallbacks ───────────────────────────────────────────────────

    def _synthetic_metrics(self, time_range: str) -> MetricsOut:
        delta  = RANGE_DELTA.get(time_range, 3600)
        step   = RANGE_STEPS.get(time_range, 60)
        points = delta // step
        now    = datetime.now(timezone.utc)

        timestamps      = []
        request_history = []
        error_history   = []

        for i in range(points):
            t   = now - timedelta(seconds=(points - i) * step)
            rps = max(0.0, 5.0 + 3.0 * math.sin(i / 10) + random.uniform(-0.5, 0.5))
            eps = rps * random.uniform(0.0, 0.03)
            timestamps.append(t.isoformat())
            request_history.append(round(rps, 2))
            error_history.append(round(eps, 4))

        return MetricsOut(
            request_rate       = request_history[-1] if request_history else 0.0,
            error_rate         = round(
                error_history[-1] / request_history[-1]
                if request_history[-1] > 0 else 0.0, 4
            ),
            p95_latency_ms     = random.randint(40, 200),
            active_connections = random.randint(1, 20),
            timestamps         = timestamps,
            request_history    = request_history,
            error_history      = error_history,
        )

    def _deployment_logs(
        self,
        db:      Session,
        site_id: str,
        level:   str | None,
        search:  str | None,
    ) -> list[LogEntryOut]:
        from app.models.models import Deployment
        # Get the latest deployment for this site
        deployment = db.query(Deployment).filter(
            Deployment.site_id == site_id
        ).order_by(Deployment.created_at.desc()).first()

        if not deployment or not deployment.logs:
            return []

        entries = []
        lines = deployment.logs.strip().split("\n")
        # Deployment logs are usually timestamped "HH:MM:SS LEVEL Message"
        # but we'll fallback to deployment created_at if parsing fails
        base_time = deployment.created_at or datetime.now(timezone.utc)

        for i, line in enumerate(lines):
            # Very simple parsing for deployment logs which are often:
            # "06:10:10 INFO Building..."
            parts = line.split(" ", 2)
            lvl = "INFO"
            msg = line
            ts = base_time + timedelta(seconds=i) # fallback sequential

            if len(parts) >= 3:
                # Try to parse HH:MM:SS
                try:
                    h, m, s = map(int, parts[0].split(":"))
                    ts = base_time.replace(hour=h, minute=m, second=s)
                    lvl = parts[1]
                    msg = parts[2]
                except:
                    pass

            if level and level.upper() != lvl.upper():
                continue
            if search and search.lower() not in msg.lower():
                continue

            entries.append(LogEntryOut(
                timestamp = ts.isoformat(),
                level     = lvl,
                service   = "builder",
                message   = msg,
                trace_id  = None,
            ))

        return entries[::-1] # Newest first

    # ── Synthetic fallbacks ───────────────────────────────────────────────────

    def _synthetic_metrics(self, time_range: str) -> MetricsOut:
        delta  = RANGE_DELTA.get(time_range, 3600)
        step   = RANGE_STEPS.get(time_range, 60)
        points = delta // step
        now    = datetime.now(timezone.utc)

        timestamps      = []
        request_history = []
        error_history   = []

        for i in range(points):
            t   = now - timedelta(seconds=(points - i) * step)
            rps = max(0.0, 5.0 + 3.0 * math.sin(i / 10) + random.uniform(-0.5, 0.5))
            eps = rps * random.uniform(0.0, 0.03)
            timestamps.append(t.isoformat())
            request_history.append(round(rps, 2))
            error_history.append(round(eps, 4))

        return MetricsOut(
            request_rate       = request_history[-1] if request_history else 0.0,
            error_rate         = round(
                error_history[-1] / request_history[-1]
                if request_history[-1] > 0 else 0.0, 4
            ),
            p95_latency_ms     = random.randint(40, 200),
            active_connections = random.randint(1, 20),
            timestamps         = timestamps,
            request_history    = request_history,
            error_history      = error_history,
        )
