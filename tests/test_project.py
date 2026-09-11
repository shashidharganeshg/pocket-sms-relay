import ast
import configparser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_python_sources_parse():
    for path in [ROOT / "main.py", *sorted((ROOT / "gateway").glob("*.py"))]:
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


def test_single_native_library_input():
    spec = (ROOT / "buildozer.spec").read_text(encoding="utf-8")
    assert spec.count("android.add_libs_arm64_v8a") == 1
    assert "src/main/jniLibs" not in spec


def test_required_assets_exist():
    assert (ROOT / "templates" / "index.html").is_file()
    assert (ROOT / "static" / "app.css").is_file()
    assert (ROOT / "static" / "app.js").is_file()
    assert (ROOT / "assets" / "icon.png").is_file()


def test_dropbear_build_inputs_exist():
    assert (ROOT / "tools" / "build_dropbear.py").is_file()
    assert (ROOT / "patches" / "dropbear-zero-port-errno.patch").is_file()
    patch = (ROOT / "patches" / "dropbear-zero-port-errno.patch").read_text(
        encoding="utf-8"
    )
    assert "errno = 0;" in patch



def test_refresh_restarts_tunnel_session():
    tunnel_source = (ROOT / "gateway" / "tunnel.py").read_text(
        encoding="utf-8"
    )
    refresh_start = tunnel_source.index("    def refresh(self):")
    next_method = tunnel_source.index("    def _environment(self):", refresh_start)
    refresh_source = tunnel_source[refresh_start:next_method]

    assert "self.stop()" in refresh_source
    assert "self.start()" in refresh_source
    assert 'url=""' in refresh_source
    assert "time.sleep(1)" in refresh_source
