import os
import subprocess
import sys
from pathlib import Path

import pytest
import overfunc


def test_dispatcher_exports_are_loaded_lazily() -> None:
    env = os.environ.copy()
    src_path = str(Path(__file__).parents[1] / "src")
    current_path = env.get("PYTHONPATH")
    env["PYTHONPATH"] = os.pathsep.join(
        [src_path, current_path] if current_path else [src_path]
    )
    script = """
import sys
import overfunc

assert not any(
    name in sys.modules
    for name in (
        "overfunc.multifunc",
        "overfunc.typedfunc",
        "overfunc.comparefunc",
        "overfunc.versionfunc",
    )
)

from overfunc import MultiFunc
assert "overfunc.multifunc" in sys.modules
assert "overfunc.typedfunc" not in sys.modules
assert "overfunc.comparefunc" not in sys.modules
assert "overfunc.versionfunc" not in sys.modules

from overfunc import TypedFunc, CompareDecorator, CompareFunc, VersionedDecorator, VersionedFunc
assert issubclass(TypedFunc, MultiFunc)
assert issubclass(CompareFunc, MultiFunc)
assert issubclass(VersionedFunc, CompareFunc)
assert issubclass(VersionedDecorator, CompareDecorator)
"""
    subprocess.run([sys.executable, "-c", script], check=True, env=env)


def test_lazy_exports_resolve_and_unknown_names_raise() -> None:
    multifunc = overfunc.MultiFunc

    assert overfunc.MultiFunc is multifunc
    assert "MultiFunc" in dir(overfunc)
    with pytest.raises(AttributeError):
        getattr(overfunc, "Unknown")
