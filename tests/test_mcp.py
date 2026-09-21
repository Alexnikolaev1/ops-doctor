import tempfile
from pathlib import Path

from ops_doctor.presentation.composition_root import (
    build_application,
    default_store_path,
)
from ops_doctor.presentation.mcp_server import host_preflight, host_status


def test_default_store_path_respects_env(monkeypatch, tmp_path: Path):
    monkeypatch.setenv("OPS_DOCTOR_STORE", str(tmp_path / "x.jsonl"))
    assert default_store_path() == tmp_path / "x.jsonl"


def test_build_application_wires_use_case(tmp_path: Path):
    app = build_application(store_path=tmp_path / "s.jsonl")
    assert app.preflight is not None


def test_host_preflight_tool_returns_verdict(tmp_path: Path):
    import ops_doctor.presentation.mcp_server as server

    server.app = build_application(store_path=tmp_path / "live.jsonl")
    text = host_preflight(heavy=False)
    assert text.startswith("VERDICT:")
    assert "History points:" in text


def test_host_status_delegates(tmp_path: Path):
    import ops_doctor.presentation.mcp_server as server

    path = Path(tempfile.mkdtemp()) / "s.jsonl"
    server.app = build_application(store_path=path)
    assert host_status().startswith("VERDICT:")
