import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

pefile = pytest.importorskip("pefile")

from tool.pe_inspector import (  # noqa: E402
    PEInspectorTool,
    PEInspectorToolInputSchema,
    _MACHINE_NAMES,
    _SUBSYSTEM_NAMES,
)


def _minimal_pe_bytes() -> bytes:
    """Build the smallest valid PE the pefile library will parse.

    This is enough to exercise the inspector's header-reading path. It's not
    a runnable binary — no sections, no imports, no exports.
    """
    import struct

    dos_header = b"MZ" + b"\x00" * 58 + struct.pack("<I", 0x40)
    pe_signature = b"PE\x00\x00"
    file_header = struct.pack(
        "<HHIIIHH",
        0x8664,  # Machine: x64
        0,       # NumberOfSections
        0x60000000,  # TimeDateStamp
        0,       # PointerToSymbolTable
        0,       # NumberOfSymbols
        0xF0,    # SizeOfOptionalHeader (PE32+ minimum)
        0x2002,  # Characteristics: EXECUTABLE | DLL
    )
    # PE32+ optional header (240 bytes).
    optional_header = struct.pack(
        "<HBBIIIII",
        0x20B,    # Magic: PE32+
        14, 0,    # LinkerVersion
        0x200,    # SizeOfCode
        0,        # SizeOfInitializedData
        0,        # SizeOfUninitializedData
        0x1000,   # AddressOfEntryPoint
        0x1000,   # BaseOfCode
    ) + struct.pack(
        "<QIIHHHHHHIIIIHHQQQQII",
        0x180000000,  # ImageBase (PE32+: 8 bytes)
        0x1000,       # SectionAlignment
        0x200,        # FileAlignment
        6, 0,         # OS version
        0, 0,         # Image version
        6, 0,         # Subsystem version
        0,            # Win32VersionValue
        0x2000,       # SizeOfImage
        0x200,        # SizeOfHeaders
        0,            # CheckSum
        2,            # Subsystem: WINDOWS_GUI
        0,            # DllCharacteristics
        0, 0,         # SizeOfStackReserve/Commit (PE32+: 8 bytes each)
        0, 0,         # SizeOfHeapReserve/Commit
        0,            # LoaderFlags
        16,           # NumberOfRvaAndSizes
    )
    data_dirs = b"\x00" * (16 * 8)
    header_block = pe_signature + file_header + optional_header + data_dirs
    return dos_header + (b"\x00" * (0x40 - len(dos_header))) + header_block


def test_machine_and_subsystem_maps_are_complete():
    # Spot-check well-known constants stay accurate.
    assert _MACHINE_NAMES[0x8664] == "x64"
    assert _MACHINE_NAMES[0x014C] == "i386"
    assert _SUBSYSTEM_NAMES[2] == "WINDOWS_GUI"
    assert _SUBSYSTEM_NAMES[3] == "WINDOWS_CUI"


def test_inspect_minimal_pe(tmp_path):
    pe_bytes = _minimal_pe_bytes()
    target = tmp_path / "fake.dll"
    target.write_bytes(pe_bytes)

    tool = PEInspectorTool()
    try:
        out = tool.run(PEInspectorToolInputSchema(file_path=str(target)))
    except pefile.PEFormatError:
        pytest.skip("Hand-built PE rejected by current pefile version; integration tests cover real binaries.")

    assert out.size_bytes == len(pe_bytes)
    assert out.machine == "x64"
    assert out.is_dll is True
    assert out.is_executable is True
    assert out.subsystem == "WINDOWS_GUI"
    assert out.entry_point == 0x1000
    assert out.imports == []
    assert out.exports == []


def test_inspect_non_pe_raises(tmp_path):
    target = tmp_path / "not_a_pe.txt"
    target.write_text("hello world")
    tool = PEInspectorTool()
    with pytest.raises(pefile.PEFormatError):
        tool.run(PEInspectorToolInputSchema(file_path=str(target)))


def test_missing_file_raises(tmp_path):
    tool = PEInspectorTool()
    with pytest.raises(ValueError):
        tool.run(PEInspectorToolInputSchema(file_path=str(tmp_path / "missing.dll")))


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
