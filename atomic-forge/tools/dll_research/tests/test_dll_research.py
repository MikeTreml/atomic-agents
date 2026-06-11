import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from tool.dll_research import (  # noqa: E402
    DllEntry,
    DllResearchTool,
    DllResearchToolConfig,
    DllResearchToolInputSchema,
    _BUNDLED,
    _canonical,
)


def test_canonicalization():
    assert _canonical("kernel32") == "kernel32.dll"
    assert _canonical("KERNEL32.DLL") == "kernel32.dll"
    assert _canonical("  User32  ") == "user32.dll"


def test_known_dll_returns_data():
    tool = DllResearchTool()
    out = tool.run(DllResearchToolInputSchema(dll_name="kernel32"))
    assert out.found is True
    assert out.canonical_name == "kernel32.dll"
    assert out.category == "windows-core"
    assert "CreateFileW" in out.common_functions
    assert out.references


def test_unknown_dll_returns_search_url():
    tool = DllResearchTool()
    out = tool.run(DllResearchToolInputSchema(dll_name="not-a-real-dll-xyz"))
    assert out.found is False
    assert out.category == "unknown"
    assert out.references[0].startswith("https://learn.microsoft.com/")
    assert out.common_functions == []


def test_case_insensitive_match():
    tool = DllResearchTool()
    out = tool.run(DllResearchToolInputSchema(dll_name="WS2_32.DLL"))
    assert out.found is True
    assert out.canonical_name == "ws2_32.dll"


def test_extra_lookup_overrides_and_extends():
    extra = {
        "kernel32.dll": DllEntry(
            category="windows-core",
            description="overridden description",
            functions=["custom"],
            references=["https://example.com/kernel32"],
        ),
        "MyApp.dll": DllEntry(
            category="unknown",
            description="my app's private DLL",
            functions=["DoThing"],
            references=[],
        ),
    }
    tool = DllResearchTool(config=DllResearchToolConfig(extra_lookup=extra))
    overridden = tool.run(DllResearchToolInputSchema(dll_name="kernel32"))
    assert overridden.description == "overridden description"
    assert overridden.common_functions == ["custom"]

    custom = tool.run(DllResearchToolInputSchema(dll_name="myapp"))
    assert custom.found is True
    assert "DoThing" in custom.common_functions


def test_bundled_reference_data_is_well_formed():
    # Smoke check: every bundled entry must populate the required fields and use
    # one of the documented categories.
    valid_categories = {"windows-core", "windows-gui", "windows-net", "crt", "dotnet"}
    for name, entry in _BUNDLED.items():
        assert name.endswith(".dll")
        assert entry.category in valid_categories, (name, entry.category)
        assert entry.description.strip()
        assert isinstance(entry.functions, list)
        assert isinstance(entry.references, list)
        assert all(ref.startswith("http") for ref in entry.references), name


if __name__ == "__main__":
    test_canonicalization()
    test_known_dll_returns_data()
    test_unknown_dll_returns_search_url()
    test_case_insensitive_match()
    test_extra_lookup_overrides_and_extends()
    test_bundled_reference_data_is_well_formed()
    print("ok")
