import os


FRAMEWORK_SIGNALS: list[tuple[str, list[str]]] = [
    # Check most specific first
    ("nextjs",   ["next.config.js", "next.config.ts", "next.config.mjs"]),
    ("react",    ["package.json"]),   # refined below
    ("vue",      ["vue.config.js", "vite.config.js"]),
    ("flask",    ["app.py", "wsgi.py", "run.py"]),
    ("fastapi",  ["main.py", "app/main.py"]),
    ("static",   ["index.html"]),
]


def detect_framework(directory: str) -> str:
    """
    Walk the top two levels of `directory` and return the most likely framework.
    Falls back to 'unknown' if nothing matches.
    """
    present: set[str] = set()
    for root, _dirs, files in os.walk(directory):
        # Only look two levels deep
        depth = root.replace(directory, "").count(os.sep)
        if depth > 2:
            continue
        for f in files:
            present.add(f)
            # also track relative paths like "app/main.py"
            rel = os.path.relpath(os.path.join(root, f), directory)
            present.add(rel.replace("\\", "/"))

    # Next.js check
    if any(s in present for s in ["next.config.js", "next.config.ts", "next.config.mjs"]):
        return "nextjs"

    # React / Vite check via package.json dependencies
    pkg_path = os.path.join(directory, "package.json")
    if os.path.exists(pkg_path):
        try:
            import json
            with open(pkg_path) as f:
                pkg = json.load(f)
            deps = {
                **pkg.get("dependencies", {}),
                **pkg.get("devDependencies", {}),
            }
            if "react" in deps:
                return "react"
            if "vue" in deps:
                return "vue"
        except Exception:
            pass

    # Python frameworks
    if "main.py" in present or "app/main.py" in present:
        # Check for FastAPI import
        for candidate in ["main.py", "app/main.py"]:
            full = os.path.join(directory, candidate)
            if os.path.exists(full):
                try:
                    content = open(full).read()
                    if "fastapi" in content.lower():
                        return "fastapi"
                    if "flask" in content.lower():
                        return "flask"
                except Exception:
                    pass

    if "app.py" in present or "wsgi.py" in present:
        return "flask"

    if "index.html" in present:
        return "static"

    return "unknown"
