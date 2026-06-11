from typing import Dict, List, Optional

from pydantic import Field

from atomic_agents import BaseIOSchema, BaseTool, BaseToolConfig


################
# INPUT SCHEMA #
################
class DllResearchToolInputSchema(BaseIOSchema):
    """
    Tool for looking up what a Windows DLL does — its purpose, the common
    functions it exposes, and where to read more. Useful after running
    PEInspectorTool and wanting to know what each imported DLL provides
    without having to round-trip to a search engine.

    The tool uses a bundled reference table of ~50 well-known Windows
    system DLLs plus a few common runtime DLLs. For unknown DLLs it returns
    a `category` of "unknown" and a Microsoft Learn search URL the agent
    can hand off to a web-search tool for follow-up.
    """

    dll_name: str = Field(
        ..., description="Name of the DLL to look up. Case-insensitive; the '.dll' suffix is optional."
    )


#################
# OUTPUT SCHEMA #
#################
class DllResearchToolOutputSchema(BaseIOSchema):
    """Schema for the output of the DllResearchTool."""

    canonical_name: str = Field(..., description="The canonical filename (e.g. 'kernel32.dll').")
    category: str = Field(
        ..., description="One of: 'windows-core', 'windows-gui', 'windows-net', 'crt', 'dotnet', 'unknown'."
    )
    description: str = Field(..., description="One-paragraph explanation of what the DLL provides.")
    common_functions: List[str] = Field(
        default_factory=list, description="Notable functions exported by this DLL (illustrative, not exhaustive)."
    )
    references: List[str] = Field(
        default_factory=list, description="URLs for deeper reading (Microsoft Learn, MSDN archives)."
    )
    found: bool = Field(..., description="True if the DLL was in the bundled reference table.")


#################
# CONFIGURATION #
#################
class DllResearchToolConfig(BaseToolConfig):
    """
    Configuration for the DllResearchTool.

    Attributes:
        extra_lookup: Optional caller-supplied table of additional DLL names to
            descriptions, merged on top of the bundled reference data. Useful
            for project-specific or third-party DLLs.
    """

    extra_lookup: Optional[Dict[str, "DllEntry"]] = None


#####################
# REFERENCE DATA    #
#####################
class DllEntry:
    """Internal record shape for bundled DLL knowledge."""

    __slots__ = ("category", "description", "functions", "references")

    def __init__(
        self,
        category: str,
        description: str,
        functions: List[str],
        references: List[str],
    ) -> None:
        self.category = category
        self.description = description
        self.functions = functions
        self.references = references


# Curated knowledge for the most-imported Windows system DLLs. Function lists
# are illustrative — every DLL exports far more than what's shown here.
_BUNDLED: Dict[str, DllEntry] = {
    "kernel32.dll": DllEntry(
        category="windows-core",
        description=(
            "Core Win32 user-mode services: process, thread, file, memory, and synchronization "
            "primitives. Almost every Windows binary imports from kernel32."
        ),
        functions=["CreateFileW", "ReadFile", "WriteFile", "VirtualAlloc", "LoadLibraryW", "GetProcAddress",
                   "CreateProcessW", "CreateThread", "WaitForSingleObject", "ExitProcess"],
        references=["https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/",
                    "https://learn.microsoft.com/en-us/windows/win32/api/fileapi/"],
    ),
    "user32.dll": DllEntry(
        category="windows-gui",
        description="Windowing and input: window creation, message pump, mouse and keyboard input, menus, clipboard.",
        functions=["CreateWindowExW", "DefWindowProcW", "GetMessageW", "DispatchMessageW", "MessageBoxW",
                   "ShowWindow", "SetWindowTextW", "GetWindowTextW", "RegisterClassExW"],
        references=["https://learn.microsoft.com/en-us/windows/win32/api/winuser/"],
    ),
    "gdi32.dll": DllEntry(
        category="windows-gui",
        description="Graphics Device Interface: device contexts, drawing primitives, fonts, bitmaps, printing.",
        functions=["CreateCompatibleDC", "BitBlt", "TextOutW", "CreateFontW", "SelectObject", "DeleteDC"],
        references=["https://learn.microsoft.com/en-us/windows/win32/api/wingdi/"],
    ),
    "advapi32.dll": DllEntry(
        category="windows-core",
        description="Advanced services: registry, services control manager, security descriptors, cryptography (legacy).",
        functions=["RegOpenKeyExW", "RegQueryValueExW", "RegSetValueExW", "OpenServiceW", "ControlService",
                   "CryptAcquireContextW", "OpenProcessToken", "AdjustTokenPrivileges"],
        references=["https://learn.microsoft.com/en-us/windows/win32/api/winreg/",
                    "https://learn.microsoft.com/en-us/windows/win32/api/winsvc/"],
    ),
    "ntdll.dll": DllEntry(
        category="windows-core",
        description=(
            "User-mode NT API: low-level system calls under the Win32 surface. Most imports here are "
            "kernel32 implementations or undocumented Nt*/Zw* APIs."
        ),
        functions=["NtCreateFile", "NtQueryInformationProcess", "RtlGetVersion", "RtlInitUnicodeString",
                   "NtAllocateVirtualMemory"],
        references=["https://learn.microsoft.com/en-us/windows/win32/api/winternl/"],
    ),
    "ole32.dll": DllEntry(
        category="windows-core",
        description="Object Linking and Embedding / COM: COM initialization, marshaling, IUnknown plumbing.",
        functions=["CoInitializeEx", "CoCreateInstance", "CoTaskMemAlloc", "CoTaskMemFree", "OleInitialize"],
        references=["https://learn.microsoft.com/en-us/windows/win32/api/combaseapi/"],
    ),
    "oleaut32.dll": DllEntry(
        category="windows-core",
        description="OLE Automation: VARIANT/BSTR types, IDispatch, type library loading. Required for COM Automation clients.",
        functions=["SysAllocString", "SysFreeString", "VariantInit", "VariantClear", "LoadTypeLib"],
        references=["https://learn.microsoft.com/en-us/windows/win32/api/oleauto/"],
    ),
    "shell32.dll": DllEntry(
        category="windows-gui",
        description="Windows Shell: file dialogs, shell namespace, icons, tray notifications, special folders.",
        functions=["ShellExecuteW", "SHGetKnownFolderPath", "SHGetFileInfoW", "Shell_NotifyIconW"],
        references=["https://learn.microsoft.com/en-us/windows/win32/api/shellapi/"],
    ),
    "comctl32.dll": DllEntry(
        category="windows-gui",
        description="Common Controls v6: listview, treeview, toolbar, status bar, tab control, property sheets.",
        functions=["InitCommonControlsEx", "ImageList_Create", "PropertySheetW"],
        references=["https://learn.microsoft.com/en-us/windows/win32/api/commctrl/"],
    ),
    "comdlg32.dll": DllEntry(
        category="windows-gui",
        description="Common Dialogs: Open/Save File, Color, Font, Print dialogs.",
        functions=["GetOpenFileNameW", "GetSaveFileNameW", "ChooseColorW", "ChooseFontW", "PrintDlgExW"],
        references=["https://learn.microsoft.com/en-us/windows/win32/api/commdlg/"],
    ),
    "ws2_32.dll": DllEntry(
        category="windows-net",
        description="Winsock 2: TCP/UDP sockets, address resolution, async IO. The standard sockets API on Windows.",
        functions=["WSAStartup", "socket", "connect", "send", "recv", "select", "getaddrinfo", "closesocket"],
        references=["https://learn.microsoft.com/en-us/windows/win32/api/winsock2/"],
    ),
    "wininet.dll": DllEntry(
        category="windows-net",
        description="High-level HTTP/FTP/Gopher client API. Largely superseded by WinHTTP for service code.",
        functions=["InternetOpenW", "InternetConnectW", "HttpOpenRequestW", "HttpSendRequestW", "InternetReadFile"],
        references=["https://learn.microsoft.com/en-us/windows/win32/api/wininet/"],
    ),
    "winhttp.dll": DllEntry(
        category="windows-net",
        description="Service-friendly HTTP client API. Preferred over WinInet for non-interactive code.",
        functions=["WinHttpOpen", "WinHttpConnect", "WinHttpOpenRequest", "WinHttpSendRequest", "WinHttpReadData"],
        references=["https://learn.microsoft.com/en-us/windows/win32/api/winhttp/"],
    ),
    "crypt32.dll": DllEntry(
        category="windows-core",
        description="CryptoAPI: certificates, message encoding, CMS/PKCS#7. The certificate-store half of Windows crypto.",
        functions=["CertOpenStore", "CertFindCertificateInStore", "CryptProtectData", "CryptUnprotectData"],
        references=["https://learn.microsoft.com/en-us/windows/win32/api/wincrypt/"],
    ),
    "bcrypt.dll": DllEntry(
        category="windows-core",
        description="Cryptography Next Generation (CNG): modern primitive crypto API. Successor to CryptoAPI for ciphers/hashes.",
        functions=["BCryptOpenAlgorithmProvider", "BCryptGenerateSymmetricKey", "BCryptEncrypt", "BCryptHash"],
        references=["https://learn.microsoft.com/en-us/windows/win32/api/bcrypt/"],
    ),
    "msvcrt.dll": DllEntry(
        category="crt",
        description="Legacy C runtime DLL shipped with Windows. New code should statically link or use the Universal CRT.",
        functions=["printf", "malloc", "free", "strcpy", "memcpy", "fopen"],
        references=["https://learn.microsoft.com/en-us/cpp/c-runtime-library/"],
    ),
    "ucrtbase.dll": DllEntry(
        category="crt",
        description="Universal C Runtime (UCRT). Hosts most stdio/string/memory functions for binaries built with VS 2015+.",
        functions=["printf", "malloc", "free", "memcpy", "_snprintf"],
        references=["https://learn.microsoft.com/en-us/cpp/c-runtime-library/crt-library-features"],
    ),
    "vcruntime140.dll": DllEntry(
        category="crt",
        description="Visual C++ runtime support: exception handling, stack unwinding, EH personality routines.",
        functions=["__CxxFrameHandler4", "_CxxThrowException", "memcpy"],
        references=["https://learn.microsoft.com/en-us/cpp/windows/redistributing-visual-cpp-files"],
    ),
    "mscoree.dll": DllEntry(
        category="dotnet",
        description="CLR shim. Loads the .NET runtime and starts managed code. Imported by any .NET executable.",
        functions=["_CorExeMain", "_CorDllMain"],
        references=["https://learn.microsoft.com/en-us/dotnet/framework/unmanaged-api/hosting/"],
    ),
    "clr.dll": DllEntry(
        category="dotnet",
        description=".NET Framework Common Language Runtime: JIT, GC, type system, assembly loader.",
        functions=["GetCLRRuntimeHost"],
        references=["https://learn.microsoft.com/en-us/dotnet/framework/unmanaged-api/"],
    ),
    "coreclr.dll": DllEntry(
        category="dotnet",
        description="The CoreCLR runtime used by .NET (Core) 5+. Equivalent role to clr.dll for the modern .NET stack.",
        functions=["coreclr_initialize", "coreclr_execute_assembly"],
        references=["https://github.com/dotnet/runtime"],
    ),
    "psapi.dll": DllEntry(
        category="windows-core",
        description="Process Status API: enumerate processes, modules, working sets. Largely re-exported from kernel32.",
        functions=["EnumProcesses", "GetModuleFileNameExW", "GetProcessMemoryInfo"],
        references=["https://learn.microsoft.com/en-us/windows/win32/api/psapi/"],
    ),
    "version.dll": DllEntry(
        category="windows-core",
        description="File version-info resource APIs. Read the VS_VERSION_INFO block embedded in PE resources.",
        functions=["GetFileVersionInfoW", "VerQueryValueW", "GetFileVersionInfoSizeW"],
        references=["https://learn.microsoft.com/en-us/windows/win32/api/winver/"],
    ),
    "rpcrt4.dll": DllEntry(
        category="windows-core",
        description="Microsoft RPC runtime: client/server stubs for MSRPC over LRPC, named pipes, TCP.",
        functions=["RpcStringBindingComposeW", "RpcBindingFromStringBindingW", "NdrClientCall2"],
        references=["https://learn.microsoft.com/en-us/windows/win32/api/rpcdce/"],
    ),
    "secur32.dll": DllEntry(
        category="windows-core",
        description="Security Support Provider Interface (SSPI) — used by SChannel/Kerberos/NTLM for authentication.",
        functions=["AcquireCredentialsHandleW", "InitializeSecurityContextW", "AcceptSecurityContext"],
        references=["https://learn.microsoft.com/en-us/windows/win32/api/sspi/"],
    ),
    "iphlpapi.dll": DllEntry(
        category="windows-net",
        description="IP Helper API: network adapter info, routing table, ARP cache, ICMP echo.",
        functions=["GetAdaptersAddresses", "GetIpForwardTable", "IcmpSendEcho"],
        references=["https://learn.microsoft.com/en-us/windows/win32/api/iphlpapi/"],
    ),
    "dnsapi.dll": DllEntry(
        category="windows-net",
        description="DNS client API: resolve names, read DNS records, manage the local cache.",
        functions=["DnsQuery_W", "DnsRecordListFree", "DnsFlushResolverCache"],
        references=["https://learn.microsoft.com/en-us/windows/win32/api/windns/"],
    ),
    "wintrust.dll": DllEntry(
        category="windows-core",
        description="Signature verification: Authenticode trust providers, catalog files, certificate chain trust.",
        functions=["WinVerifyTrust", "CryptCATAdminCalcHashFromFileHandle"],
        references=["https://learn.microsoft.com/en-us/windows/win32/api/wintrust/"],
    ),
    "userenv.dll": DllEntry(
        category="windows-core",
        description="User environment: profile loading, group policy, environment block creation for new processes.",
        functions=["LoadUserProfileW", "CreateEnvironmentBlock", "DestroyEnvironmentBlock"],
        references=["https://learn.microsoft.com/en-us/windows/win32/api/userenv/"],
    ),
    "setupapi.dll": DllEntry(
        category="windows-core",
        description="Device and driver installation: PnP enumeration, INF parsing, device installation.",
        functions=["SetupDiGetClassDevsW", "SetupDiEnumDeviceInfo", "SetupDiGetDeviceRegistryPropertyW"],
        references=["https://learn.microsoft.com/en-us/windows/win32/api/setupapi/"],
    ),
    "imagehlp.dll": DllEntry(
        category="windows-core",
        description="Image helper: walk PE headers, manipulate checksums, work with debug info. Used by debuggers.",
        functions=["MapAndLoad", "ImageDirectoryEntryToData", "CheckSumMappedFile"],
        references=["https://learn.microsoft.com/en-us/windows/win32/api/imagehlp/"],
    ),
    "dbghelp.dll": DllEntry(
        category="windows-core",
        description="Debug helper: symbol resolution (PDB), stack walking, minidump read/write.",
        functions=["SymInitialize", "SymFromAddr", "StackWalk64", "MiniDumpWriteDump"],
        references=["https://learn.microsoft.com/en-us/windows/win32/debug/dbghelp-functions"],
    ),
    "msi.dll": DllEntry(
        category="windows-core",
        description="Windows Installer client API: query / install / repair MSI packages programmatically.",
        functions=["MsiInstallProductW", "MsiOpenDatabaseW", "MsiGetProductInfoW"],
        references=["https://learn.microsoft.com/en-us/windows/win32/api/msi/"],
    ),
    "wtsapi32.dll": DllEntry(
        category="windows-core",
        description="Remote Desktop / Terminal Services: session enumeration, session token retrieval, message sending.",
        functions=["WTSEnumerateSessionsW", "WTSQuerySessionInformationW", "WTSSendMessageW"],
        references=["https://learn.microsoft.com/en-us/windows/win32/api/wtsapi32/"],
    ),
}


#####################
# MAIN TOOL & LOGIC #
#####################
class DllResearchTool(BaseTool[DllResearchToolInputSchema, DllResearchToolOutputSchema]):
    """Lookup tool that returns what a Windows DLL provides."""

    def __init__(self, config: DllResearchToolConfig = DllResearchToolConfig()):
        super().__init__(config)
        self._lookup: Dict[str, DllEntry] = dict(_BUNDLED)
        if config.extra_lookup:
            self._lookup.update({_canonical(name): entry for name, entry in config.extra_lookup.items()})

    def run(self, params: DllResearchToolInputSchema) -> DllResearchToolOutputSchema:
        canonical = _canonical(params.dll_name)
        entry = self._lookup.get(canonical)
        if entry is None:
            search_url = (
                "https://learn.microsoft.com/en-us/search/?terms=" + canonical.replace(".dll", "")
            )
            return DllResearchToolOutputSchema(
                canonical_name=canonical,
                category="unknown",
                description=(
                    f"'{canonical}' is not in the bundled Windows DLL reference. "
                    "It may be a third-party DLL, a renamed system DLL, or simply not yet curated. "
                    "Pass the canonical_name to a web-search tool for live information."
                ),
                common_functions=[],
                references=[search_url],
                found=False,
            )

        return DllResearchToolOutputSchema(
            canonical_name=canonical,
            category=entry.category,
            description=entry.description,
            common_functions=list(entry.functions),
            references=list(entry.references),
            found=True,
        )


def _canonical(name: str) -> str:
    name = name.strip().lower()
    if not name.endswith(".dll"):
        name += ".dll"
    return name


#################
# EXAMPLE USAGE #
#################
if __name__ == "__main__":
    tool = DllResearchTool()
    for dll in ("kernel32", "USER32.DLL", "totally-fake.dll"):
        out = tool.run(DllResearchToolInputSchema(dll_name=dll))
        print(f"{out.canonical_name} [{out.category}] found={out.found}")
        print(f"  {out.description[:140]}...")
        if out.common_functions:
            print(f"  fns: {', '.join(out.common_functions[:5])}")
        print()
