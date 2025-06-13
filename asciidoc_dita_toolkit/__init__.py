"""
AsciiDoc DITA Toolkit Package

Top-level package for the AsciiDoc DITA Toolkit.
"""

# Import version from pyproject.toml via setuptools metadata
try:
    from importlib.metadata import version
    __version__ = version("asciidoc-dita-toolkit")
except ImportError:
    # Fallback for Python < 3.8
    try:
        from importlib_metadata import version
        __version__ = version("asciidoc-dita-toolkit")
    except ImportError:
        # Final fallback
        __version__ = "1.0.1"
