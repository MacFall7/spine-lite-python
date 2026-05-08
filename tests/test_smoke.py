"""Smoke tests covering package import and version constant."""

from __future__ import annotations


def test_package_imports() -> None:
    import spine_lite

    assert hasattr(spine_lite, "__version__")


def test_version_is_phase_one_alpha() -> None:
    import spine_lite

    assert spine_lite.__version__ == "0.1.0a0"


def test_public_surface_excludes_private_names() -> None:
    import spine_lite

    for name in spine_lite.__all__:
        assert not name.startswith("_") or name == "__version__"
