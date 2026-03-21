import os
import json
import tempfile
from app.services.detection_service import detect_framework


def _make_dir(files: dict[str, str]) -> str:
    d = tempfile.mkdtemp()
    for name, content in files.items():
        path = os.path.join(d, name)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write(content)
    return d


def test_detect_react():
    pkg = json.dumps({"dependencies": {"react": "^18.0.0", "react-dom": "^18.0.0"}})
    d   = _make_dir({"package.json": pkg, "src/App.tsx": ""})
    assert detect_framework(d) == "react"


def test_detect_nextjs():
    d = _make_dir({"next.config.js": "module.exports = {}", "package.json": "{}"})
    assert detect_framework(d) == "nextjs"


def test_detect_fastapi():
    d = _make_dir({"main.py": "from fastapi import FastAPI\napp = FastAPI()"})
    assert detect_framework(d) == "fastapi"


def test_detect_flask():
    d = _make_dir({"app.py": "from flask import Flask\napp = Flask(__name__)"})
    assert detect_framework(d) == "flask"


def test_detect_static():
    d = _make_dir({"index.html": "<html><body>Hello</body></html>"})
    assert detect_framework(d) == "static"


def test_detect_unknown():
    d = _make_dir({"README.md": "# My project"})
    assert detect_framework(d) == "unknown"
