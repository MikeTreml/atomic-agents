import hashlib
from pathlib import Path
from typing import Dict, List, Optional

from pydantic import Field

from atomic_agents import BaseIOSchema, BaseTool, BaseToolConfig

import pefile


################
# INPUT SCHEMA #
################
class PEInspectorToolInputSchema(BaseIOSchema):
    """
    Tool for inspecting a Portable Executable (PE) file — Windows .exe, .dll,
    .sys, or .ocx. Reads headers, imports, exports, sections, and metadata
    without executing the binary. Useful as a first pass for reverse
    engineering, malware triage, or just figuring out what a DLL provides.
    """

    file_path: str = Field(..., description="Absolute or relative path to a PE-format file.")
    include_imports: bool = Field(default=True, description="Include imported DLLs and their functions.")
    include_exports: bool = Field(default=True, description="Include exported function names (typical for DLLs).")
    include_sections: bool = Field(default=True, description="Include section table (name, size, virtual address).")
    max_imports_per_dll: int = Field(
        default=50, ge=1, description="Cap on imported function names listed per DLL, to keep output manageable."
    )


#################
# OUTPUT SCHEMA #
#################
class PESection(BaseIOSchema):
    """A section in the PE section table."""

    name: str = Field(..., description="Section name (e.g. .text, .data, .rsrc).")
    virtual_size: int = Field(..., description="Virtual size of the section in bytes.")
    virtual_address: int = Field(..., description="RVA of the section.")
    raw_size: int = Field(..., description="Size of raw data on disk.")
    characteristics: int = Field(..., description="Section characteristics bitmask.")


class PEImport(BaseIOSchema):
    """One imported DLL and the function names imported from it."""

    dll: str = Field(..., description="Name of the imported DLL.")
    functions: List[str] = Field(..., description="Imported function names (truncated to max_imports_per_dll).")
    truncated: bool = Field(default=False, description="True if the function list was truncated.")


class PEInspectorToolOutputSchema(BaseIOSchema):
    """Schema for the output of the PEInspectorTool."""

    file_path: str = Field(..., description="Absolute path that was inspected.")
    size_bytes: int = Field(..., description="File size in bytes.")
    sha256: str = Field(..., description="SHA-256 hash of the file contents.")
    machine: str = Field(..., description="Target machine architecture (e.g. 'x64', 'i386', 'arm64').")
    is_dll: bool = Field(..., description="True when the PE characteristics flag IMAGE_FILE_DLL is set.")
    is_executable: bool = Field(..., description="True when IMAGE_FILE_EXECUTABLE_IMAGE is set.")
    entry_point: int = Field(..., description="Address of entry point (RVA).")
    image_base: int = Field(..., description="Preferred load address.")
    timestamp: Optional[int] = Field(default=None, description="Unix timestamp from the PE header (often the build time).")
    subsystem: str = Field(..., description="Subsystem (e.g. 'WINDOWS_GUI', 'WINDOWS_CUI', 'NATIVE').")
    sections: List[PESection] = Field(default_factory=list, description="Section table entries.")
    imports: List[PEImport] = Field(default_factory=list, description="Imported DLLs and their functions.")
    exports: List[str] = Field(default_factory=list, description="Exported function names (DLLs only).")


#################
# CONFIGURATION #
#################
class PEInspectorToolConfig(BaseToolConfig):
    """
    Configuration for the PEInspectorTool.

    Attributes:
        fast_load: When True, only the PE headers are parsed (no full directory walk).
            Faster, but some fields (like rich imports) may be empty.
    """

    fast_load: bool = False


# Mapping for human-readable machine names. From IMAGE_FILE_MACHINE_* constants.
_MACHINE_NAMES: Dict[int, str] = {
    0x014C: "i386",
    0x0200: "ia64",
    0x8664: "x64",
    0xAA64: "arm64",
    0x01C0: "arm",
    0x01C4: "armnt",
}

_SUBSYSTEM_NAMES: Dict[int, str] = {
    1: "NATIVE",
    2: "WINDOWS_GUI",
    3: "WINDOWS_CUI",
    7: "POSIX_CUI",
    9: "WINDOWS_CE_GUI",
    10: "EFI_APPLICATION",
    11: "EFI_BOOT_SERVICE_DRIVER",
    12: "EFI_RUNTIME_DRIVER",
    13: "EFI_ROM",
    14: "XBOX",
    16: "WINDOWS_BOOT_APPLICATION",
}


#####################
# MAIN TOOL & LOGIC #
#####################
class PEInspectorTool(BaseTool[PEInspectorToolInputSchema, PEInspectorToolOutputSchema]):
    """Static analysis of a Portable Executable file via the `pefile` library."""

    def __init__(self, config: PEInspectorToolConfig = PEInspectorToolConfig()):
        super().__init__(config)
        self.fast_load = config.fast_load

    def run(self, params: PEInspectorToolInputSchema) -> PEInspectorToolOutputSchema:
        path = Path(params.file_path).expanduser().resolve()
        if not path.is_file():
            raise ValueError(f"file_path is not a file: {path}")

        size = path.stat().st_size
        sha = _sha256_file(path)

        pe = pefile.PE(str(path), fast_load=self.fast_load)
        try:
            if not self.fast_load:
                pe.parse_data_directories()

            machine_val = pe.FILE_HEADER.Machine
            characteristics = pe.FILE_HEADER.Characteristics
            optional = pe.OPTIONAL_HEADER

            output_imports: List[PEImport] = []
            if params.include_imports and hasattr(pe, "DIRECTORY_ENTRY_IMPORT"):
                for entry in pe.DIRECTORY_ENTRY_IMPORT:
                    dll_name = (entry.dll or b"").decode(errors="replace")
                    fn_names: List[str] = []
                    for imp in entry.imports:
                        if imp.name:
                            fn_names.append(imp.name.decode(errors="replace"))
                        elif imp.ordinal:
                            fn_names.append(f"#ord{imp.ordinal}")
                        if len(fn_names) >= params.max_imports_per_dll:
                            break
                    output_imports.append(
                        PEImport(
                            dll=dll_name,
                            functions=fn_names,
                            truncated=len(entry.imports) > len(fn_names),
                        )
                    )

            output_exports: List[str] = []
            if params.include_exports and hasattr(pe, "DIRECTORY_ENTRY_EXPORT"):
                for exp in pe.DIRECTORY_ENTRY_EXPORT.symbols:
                    if exp.name:
                        output_exports.append(exp.name.decode(errors="replace"))
                    elif exp.ordinal:
                        output_exports.append(f"#ord{exp.ordinal}")

            output_sections: List[PESection] = []
            if params.include_sections:
                for sect in pe.sections:
                    output_sections.append(
                        PESection(
                            name=sect.Name.rstrip(b"\x00").decode(errors="replace"),
                            virtual_size=int(sect.Misc_VirtualSize),
                            virtual_address=int(sect.VirtualAddress),
                            raw_size=int(sect.SizeOfRawData),
                            characteristics=int(sect.Characteristics),
                        )
                    )

            return PEInspectorToolOutputSchema(
                file_path=str(path),
                size_bytes=size,
                sha256=sha,
                machine=_MACHINE_NAMES.get(machine_val, f"unknown(0x{machine_val:04x})"),
                is_dll=bool(characteristics & 0x2000),
                is_executable=bool(characteristics & 0x0002),
                entry_point=int(optional.AddressOfEntryPoint),
                image_base=int(optional.ImageBase),
                timestamp=int(pe.FILE_HEADER.TimeDateStamp) or None,
                subsystem=_SUBSYSTEM_NAMES.get(int(optional.Subsystem), f"unknown({optional.Subsystem})"),
                sections=output_sections,
                imports=output_imports,
                exports=output_exports,
            )
        finally:
            pe.close()


def _sha256_file(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 64), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


#################
# EXAMPLE USAGE #
#################
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("usage: pe_inspector.py <path-to-pe-file>")
        sys.exit(2)

    tool = PEInspectorTool()
    out = tool.run(PEInspectorToolInputSchema(file_path=sys.argv[1]))
    print(out)
