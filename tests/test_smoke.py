"""Smoke tests covering package import and version constant."""

from __future__ import annotations


def test_package_imports() -> None:
    import spine_lite

    assert hasattr(spine_lite, "__version__")


def test_version_is_phase_three_alpha() -> None:
    import spine_lite

    assert spine_lite.__version__ == "0.3.0a0"


def test_public_surface_excludes_private_names() -> None:
    import spine_lite

    for name in spine_lite.__all__:
        assert not name.startswith("_") or name == "__version__"


def test_phase_two_three_modules_import_cleanly() -> None:
    """Every scaffolded module must at least parse and import."""
    import importlib

    for module_name in (
        "spine_lite.classifier",
        "spine_lite.manifest",
        "spine_lite.posture",
        "spine_lite.receipt",
        "spine_lite.hook",
    ):
        importlib.import_module(module_name)
