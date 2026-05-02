"""Export the OpenAPI spec from FastAPI without starting a server."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.main import app  # noqa: E402

spec = app.openapi()
output = Path(__file__).resolve().parent.parent / "openapi.json"
output.write_text(json.dumps(spec, indent=2) + "\n")
