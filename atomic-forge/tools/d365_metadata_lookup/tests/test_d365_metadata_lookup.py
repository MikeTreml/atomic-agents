import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from tool.d365_metadata_lookup import (  # noqa: E402
    D365MetadataLookupTool,
    D365MetadataLookupToolConfig,
    D365MetadataLookupToolInputSchema,
    MetadataEntry,
    _BUNDLED,
)


def test_known_table_returns_data():
    tool = D365MetadataLookupTool()
    out = tool.run(D365MetadataLookupToolInputSchema(object_name="CustTable"))
    assert out.found is True
    assert out.canonical_name == "CustTable"
    assert out.category == "table"
    assert "AccountNum" in out.key_members
    assert out.references


def test_case_insensitive_match_preserves_canonical_name():
    tool = D365MetadataLookupTool()
    out = tool.run(D365MetadataLookupToolInputSchema(object_name="RUNBASEBATCH"))
    assert out.found is True
    assert out.canonical_name == "RunBaseBatch"  # preserved original casing
    assert out.category == "class"


def test_unknown_object_returns_search_url():
    tool = D365MetadataLookupTool()
    out = tool.run(D365MetadataLookupToolInputSchema(object_name="ZzNotARealObject"))
    assert out.found is False
    assert out.category == "unknown"
    assert out.references[0].startswith("https://learn.microsoft.com/")
    assert out.key_members == []


def test_extra_lookup_extends_and_overrides():
    extra = {
        "CustTable": MetadataEntry(
            category="table",
            description="overridden description",
            members=["custom"],
            references=["https://example.com/cust"],
        ),
        "AcmeCustomTable": MetadataEntry(
            category="table",
            description="ISV custom table",
            members=["AcmeId"],
            references=[],
        ),
    }
    tool = D365MetadataLookupTool(config=D365MetadataLookupToolConfig(extra_lookup=extra))
    overridden = tool.run(D365MetadataLookupToolInputSchema(object_name="CustTable"))
    assert overridden.description == "overridden description"
    assert overridden.key_members == ["custom"]

    custom = tool.run(D365MetadataLookupToolInputSchema(object_name="AcmeCustomTable"))
    assert custom.found is True
    assert "AcmeId" in custom.key_members


def test_bundled_reference_data_is_well_formed():
    valid_categories = {"table", "class", "edt", "base_enum", "framework", "form"}
    for name, entry in _BUNDLED.items():
        assert name.strip() == name
        assert entry.category in valid_categories, (name, entry.category)
        assert entry.description.strip()
        assert isinstance(entry.members, list)
        assert isinstance(entry.references, list)
        assert all(ref.startswith("http") for ref in entry.references), name


def test_bundled_table_has_minimum_coverage():
    # Sanity: confirm we ship at least one entry in each of the major categories.
    cats = {e.category for e in _BUNDLED.values()}
    assert {"table", "class", "edt", "base_enum", "framework"}.issubset(cats)
    assert len(_BUNDLED) >= 40, f"bundled table only has {len(_BUNDLED)} entries"


if __name__ == "__main__":
    test_known_table_returns_data()
    test_case_insensitive_match_preserves_canonical_name()
    test_unknown_object_returns_search_url()
    test_extra_lookup_extends_and_overrides()
    test_bundled_reference_data_is_well_formed()
    test_bundled_table_has_minimum_coverage()
    print("ok")
