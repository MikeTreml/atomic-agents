from typing import Dict, List, Optional

from pydantic import Field

from atomic_agents import BaseIOSchema, BaseTool, BaseToolConfig


################
# INPUT SCHEMA #
################
class D365MetadataLookupToolInputSchema(BaseIOSchema):
    """
    Tool for looking up well-known Microsoft Dynamics 365 Finance & Operations
    AOT objects — tables, classes, EDTs, base enums, frameworks — by name.
    Returns category, a one-paragraph description, key fields or methods, and
    Microsoft Learn references. Self-contained (no network) for ~45 of the
    most-used out-of-box objects. For anything outside the bundled table the
    tool returns category 'unknown' plus a Microsoft Learn search URL the
    agent can hand off to a web-search tool.

    Useful after `XppCodebaseScanTool` finds references to standard objects
    so a downstream review or authoring agent has accurate context.
    """

    object_name: str = Field(
        ...,
        description="Name of the AOT object to look up. Case-insensitive. Examples: 'CustTable', 'RunBaseBatch', 'ItemId', 'NoYes'.",
    )


#################
# OUTPUT SCHEMA #
#################
class D365MetadataLookupToolOutputSchema(BaseIOSchema):
    """Schema for the output of the D365MetadataLookupTool."""

    canonical_name: str = Field(..., description="The canonical AOT name (preserved camel-case).")
    category: str = Field(
        ...,
        description=(
            "One of: 'table', 'class', 'edt', 'base_enum', 'framework', 'form', 'unknown'."
        ),
    )
    description: str = Field(..., description="One-paragraph explanation of what the object provides.")
    key_members: List[str] = Field(
        default_factory=list,
        description="Notable fields (for tables), methods (for classes), or values (for enums). Illustrative, not exhaustive.",
    )
    references: List[str] = Field(
        default_factory=list, description="URLs for deeper reading (Microsoft Learn, AX/D365 docs)."
    )
    found: bool = Field(..., description="True if the object was in the bundled reference table.")


#################
# CONFIGURATION #
#################
class D365MetadataLookupToolConfig(BaseToolConfig):
    """
    Configuration for the D365MetadataLookupTool.

    Attributes:
        extra_lookup: Optional caller-supplied table of additional D365 objects, merged on top of the
            bundled reference data. Useful for project-specific or ISV-shipped objects.
    """

    extra_lookup: Optional[Dict[str, "MetadataEntry"]] = None


#####################
# REFERENCE DATA    #
#####################
class MetadataEntry:
    """Internal record shape for bundled D365 metadata."""

    __slots__ = ("category", "description", "members", "references")

    def __init__(
        self,
        category: str,
        description: str,
        members: List[str],
        references: List[str],
    ) -> None:
        self.category = category
        self.description = description
        self.members = members
        self.references = references


# Curated knowledge for ~45 of the most-imported D365 F&O AOT objects.
# Member lists are illustrative; each object exposes far more than what's shown.
_BUNDLED: Dict[str, MetadataEntry] = {
    # ─────────────────────── Tables ───────────────────────
    "CustTable": MetadataEntry(
        category="table",
        description="Customer master. One row per legal-entity customer. Anchor of the AR module; referenced from SalesTable, CustInvoiceJour, CustTrans.",
        members=["AccountNum", "CustGroup", "CurrencyCode", "PaymTermId", "InvoiceAccount", "Blocked"],
        references=["https://learn.microsoft.com/en-us/dynamics365/finance/accounts-receivable/customers-overview"],
    ),
    "VendTable": MetadataEntry(
        category="table",
        description="Vendor master. AP counterpart of CustTable; referenced from PurchTable, VendInvoiceJour, VendTrans.",
        members=["AccountNum", "VendGroup", "CurrencyCode", "PaymTermId", "InvoiceAccount", "Blocked"],
        references=["https://learn.microsoft.com/en-us/dynamics365/finance/accounts-payable/vendors-overview"],
    ),
    "InventTable": MetadataEntry(
        category="table",
        description="Released product master. Holds the item-master rows shared across companies via DataAreaId rules.",
        members=["ItemId", "Product", "ItemType", "ModelGroupId", "DimGroupId", "PurchModel"],
        references=["https://learn.microsoft.com/en-us/dynamics365/supply-chain/pim/product-information"],
    ),
    "SalesTable": MetadataEntry(
        category="table",
        description="Sales order header. One row per sales order; lines hang off via SalesId.",
        members=["SalesId", "CustAccount", "SalesStatus", "DeliveryDate", "CurrencyCode", "InvoiceAccount"],
        references=["https://learn.microsoft.com/en-us/dynamics365/supply-chain/sales-marketing/tasks/create-sales-order"],
    ),
    "SalesLine": MetadataEntry(
        category="table",
        description="Sales order line. One row per line on a sales order, with item/quantity/price.",
        members=["SalesId", "ItemId", "SalesQty", "SalesPrice", "InventDimId", "LineNum"],
        references=["https://learn.microsoft.com/en-us/dynamics365/supply-chain/sales-marketing/"],
    ),
    "PurchTable": MetadataEntry(
        category="table",
        description="Purchase order header.",
        members=["PurchId", "OrderAccount", "PurchStatus", "DeliveryDate", "CurrencyCode"],
        references=["https://learn.microsoft.com/en-us/dynamics365/supply-chain/procurement/purchase-orders-overview"],
    ),
    "PurchLine": MetadataEntry(
        category="table",
        description="Purchase order line.",
        members=["PurchId", "ItemId", "PurchQty", "PurchPrice", "InventDimId", "LineNumber"],
        references=["https://learn.microsoft.com/en-us/dynamics365/supply-chain/procurement/"],
    ),
    "LedgerJournalTable": MetadataEntry(
        category="table",
        description="Journal header for GL postings.",
        members=["JournalNum", "JournalName", "Posted", "BlockUserGroupId"],
        references=["https://learn.microsoft.com/en-us/dynamics365/finance/general-ledger/journals-and-vouchers"],
    ),
    "LedgerJournalTrans": MetadataEntry(
        category="table",
        description="Journal line — individual debit/credit transactions before posting.",
        members=["JournalNum", "Voucher", "AccountType", "LedgerDimension", "AmountCurDebit", "AmountCurCredit", "TransDate"],
        references=["https://learn.microsoft.com/en-us/dynamics365/finance/general-ledger/"],
    ),
    "DirPartyTable": MetadataEntry(
        category="table",
        description="Party master — root of the party hierarchy. People, organizations, customers, vendors, employees ultimately link back here via DirPerson, DirOrganization, etc.",
        members=["RecId", "PartyType", "Name", "NameAlias", "InstanceRelationType"],
        references=["https://learn.microsoft.com/en-us/dynamics365/finance/general-ledger/global-address-book-overview"],
    ),
    "HcmWorker": MetadataEntry(
        category="table",
        description="Worker (HR). Employees and contractors. References DirPerson via Person field.",
        members=["RecId", "PersonnelNumber", "Person", "PrimaryContactEmail"],
        references=["https://learn.microsoft.com/en-us/dynamics365/human-resources/"],
    ),
    "InventDim": MetadataEntry(
        category="table",
        description="Inventory dimensions — site, warehouse, location, batch, serial. Almost every inventory transaction references an InventDimId hash.",
        members=["InventDimId", "InventSiteId", "InventLocationId", "WMSLocationId", "inventBatchId", "inventSerialId"],
        references=["https://learn.microsoft.com/en-us/dynamics365/supply-chain/inventory/"],
    ),
    "MainAccount": MetadataEntry(
        category="table",
        description="Main accounts (chart of accounts) — financial dimension hierarchy anchor.",
        members=["MainAccountId", "Type", "LedgerChart", "Name"],
        references=["https://learn.microsoft.com/en-us/dynamics365/finance/general-ledger/main-accounts-overview"],
    ),
    "CompanyInfo": MetadataEntry(
        category="table",
        description="Company info. One row per legal entity. Singleton-ish — most code reads via CompanyInfo::find().",
        members=["DataArea", "Name", "CurrencyCode"],
        references=["https://learn.microsoft.com/en-us/dynamics365/finance/general-ledger/tasks/define-legal-entity"],
    ),
    # ─────────────────────── Classes ───────────────────────
    "RunBase": MetadataEntry(
        category="class",
        description="Legacy batch/dialog framework. Subclass to build a job with a dialog and optional batch behavior. Mostly superseded by SysOperation for new code.",
        members=["dialog()", "run()", "validate()", "pack()", "unpack()", "init()"],
        references=["https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/dev-ref/xpp-runbase-class"],
    ),
    "RunBaseBatch": MetadataEntry(
        category="class",
        description="RunBase + batch-server support. Subclass for jobs that should be runnable in batch.",
        members=["canGoBatchJournal()", "runsImpersonated()", "canRunInNewSession()"],
        references=["https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/dev-ref/xpp-runbasebatch-class"],
    ),
    "SysOperation": MetadataEntry(
        category="framework",
        description="Modern SysOperation framework (controller/service/data-contract pattern). Preferred over RunBaseBatch for new batch and operation jobs — better extensibility and reliable serialization.",
        members=["SysOperationServiceController", "SysOperationDataContractInfo", "SysOperationServiceBase"],
        references=["https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/sysop-framework/sysoperation-framework"],
    ),
    "Args": MetadataEntry(
        category="class",
        description="Argument object passed when opening menu items, forms, reports. Carries caller, record, parm string, dataset.",
        members=["caller()", "record()", "parm()", "menuItemName()", "dataset()"],
        references=["https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/dev-ref/xpp-args-class"],
    ),
    "Global": MetadataEntry(
        category="class",
        description="Global static helpers — type conversions, string formatting, info/warning/error messaging, validation. Methods are class-static.",
        members=["info()", "warning()", "error()", "strFmt()", "checkFailed()", "decimal2int()"],
        references=["https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/dev-ref/xpp-global-class"],
    ),
    "Info": MetadataEntry(
        category="class",
        description="Infolog API. Use to push user-facing messages from inside transactions or batch jobs.",
        members=["add()", "addInternal()", "writeException()", "num()"],
        references=["https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/dev-ref/xpp-info-class"],
    ),
    "xRecord": MetadataEntry(
        category="class",
        description="Base class for all tables. Provides insert/update/delete, validate*, init*, postLoad, RecId, etc.",
        members=["insert()", "update()", "delete()", "validateWrite()", "initValue()", "RecId"],
        references=["https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/dev-ref/xpp-xrecord-class"],
    ),
    "Common": MetadataEntry(
        category="class",
        description="Concrete base table class — every table buffer is a Common subclass at runtime. Use as a typeless parameter when you want any-table generality.",
        members=["TableId", "RecId", "selectForUpdate()", "joinChild()"],
        references=["https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/dev-ref/xpp-common-class"],
    ),
    "Query": MetadataEntry(
        category="class",
        description="In-memory query metadata: data sources, ranges, joins, ordering. Use with QueryRun to execute.",
        members=["addDataSource()", "dataSourceTable()", "dataSourceNo()", "saveUserSetup()"],
        references=["https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/dev-ref/xpp-query-class"],
    ),
    "QueryRun": MetadataEntry(
        category="class",
        description="Executes a Query and lets you iterate result rows via next() / get().",
        members=["next()", "get()", "prompt()", "query()"],
        references=["https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/dev-ref/xpp-queryrun-class"],
    ),
    "QueryBuildDataSource": MetadataEntry(
        category="class",
        description="A single data source on a Query. Holds ranges, joins, and child sources.",
        members=["addRange()", "addLink()", "addSortField()", "joinMode()"],
        references=["https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/dev-ref/xpp-querybuilddatasource-class"],
    ),
    "DictTable": MetadataEntry(
        category="class",
        description="Reflection helper for a table at runtime: list fields, indexes, relations. Use sparingly — expensive in hot paths.",
        members=["fieldName2Id()", "fieldObject()", "indexObject()", "relations()"],
        references=["https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/dev-ref/xpp-dicttable-class"],
    ),
    "DictClass": MetadataEntry(
        category="class",
        description="Reflection over an X++ class — methods, attributes, base class. Used by extension/DI infrastructure.",
        members=["callObject()", "callStatic()", "extends()", "objectMethodObject()"],
        references=["https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/dev-ref/xpp-dictclass-class"],
    ),
    "SrsReportRunController": MetadataEntry(
        category="class",
        description="Controller for SSRS reports. Subclass to handle parameter packing, data contracts, custom dialogs.",
        members=["parmReportName()", "parmReportContract()", "preRunModifyContract()"],
        references=["https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/analytics/srs-report-development"],
    ),
    "SysExtensionAttribute": MetadataEntry(
        category="framework",
        description="DI/extension attribute framework. Decorate a class with a subclass of SysExtensionAttribute and SysExtensionAppClassFactory resolves an implementation at runtime.",
        members=["SysExtensionAppClassFactory", "SysExtensionAttribute", "getInstance()"],
        references=["https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/extensibility/sysplugin-framework"],
    ),
    "FormDataSource_Extension": MetadataEntry(
        category="class",
        description="Naming convention for extending a form data source via class augmentation. Use [ExtensionOf(formDataSourceStr(FormName, DataSource))] and event/CoC methods.",
        members=["[ExtensionOf]", "init()", "executeQuery()", "linkActive()"],
        references=["https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/extensibility/customize-model-elements-extensions"],
    ),
    # ─────────────────────── EDTs ───────────────────────
    "ItemId": MetadataEntry(
        category="edt",
        description="Released product number. Identifier for InventTable rows.",
        members=["String", "Max length 20"],
        references=["https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/dev-ref/xpp-edts"],
    ),
    "CustAccount": MetadataEntry(
        category="edt",
        description="Customer account number — key into CustTable.AccountNum.",
        members=["String"],
        references=["https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/dev-ref/xpp-edts"],
    ),
    "VendAccount": MetadataEntry(
        category="edt",
        description="Vendor account number — key into VendTable.AccountNum.",
        members=["String"],
        references=["https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/dev-ref/xpp-edts"],
    ),
    "LedgerAccount": MetadataEntry(
        category="edt",
        description="Composite GL account string with main account plus financial-dimension segments.",
        members=["String", "Resolves to MainAccount via LedgerAccountContract"],
        references=["https://learn.microsoft.com/en-us/dynamics365/finance/general-ledger/financial-dimensions"],
    ),
    "TransDate": MetadataEntry(
        category="edt",
        description="Transaction date — UTC-stored date typically used as the accounting date on transactional tables.",
        members=["Date"],
        references=["https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/dev-ref/xpp-edts"],
    ),
    "Voucher": MetadataEntry(
        category="edt",
        description="Voucher number — string identifier shared by all rows in a single posting unit.",
        members=["String"],
        references=["https://learn.microsoft.com/en-us/dynamics365/finance/general-ledger/journals-and-vouchers"],
    ),
    "NoYesId": MetadataEntry(
        category="edt",
        description="Wrapper EDT around the NoYes base enum, used widely as boolean flags on tables.",
        members=["Backed by NoYes enum"],
        references=["https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/dev-ref/xpp-data-types"],
    ),
    # ─────────────────────── Base enums ───────────────────────
    "NoYes": MetadataEntry(
        category="base_enum",
        description="Two-value boolean base enum (No=0, Yes=1). Use NoYesId when persisting on a table.",
        members=["No=0", "Yes=1"],
        references=["https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/dev-ref/xpp-base-enums"],
    ),
    "Gender": MetadataEntry(
        category="base_enum",
        description="Person gender base enum. Used on DirPerson and HCM tables.",
        members=["None=0", "Male=1", "Female=2", "NonSpecific=3"],
        references=["https://learn.microsoft.com/en-us/dynamics365/human-resources/"],
    ),
    "SalesStatus": MetadataEntry(
        category="base_enum",
        description="Sales order status: None, Backorder, Delivered, Invoiced, Canceled.",
        members=["None=0", "Backorder=1", "Delivered=2", "Invoiced=3", "Canceled=4"],
        references=["https://learn.microsoft.com/en-us/dynamics365/supply-chain/sales-marketing/"],
    ),
    "PurchStatus": MetadataEntry(
        category="base_enum",
        description="Purchase order status: None, Backorder, Received, Invoiced, Canceled.",
        members=["None=0", "Backorder=1", "Received=2", "Invoiced=3", "Canceled=4"],
        references=["https://learn.microsoft.com/en-us/dynamics365/supply-chain/procurement/"],
    ),
    "LedgerPostingType": MetadataEntry(
        category="base_enum",
        description="Posting type for a journal line — drives which subledger / GL bucket the amount goes to.",
        members=["LedgerJournal", "Customer", "Vendor", "Bank", "FixedAsset", "Project"],
        references=["https://learn.microsoft.com/en-us/dynamics365/finance/general-ledger/"],
    ),
    "Module": MetadataEntry(
        category="base_enum",
        description="Functional module enum referenced by tax, posting, and parameter tables.",
        members=["Cust", "Vend", "Bank", "Ledger", "Proj", "Invent"],
        references=["https://learn.microsoft.com/en-us/dynamics365/finance/"],
    ),
    # ─────────────────────── Frameworks / infrastructure ───────────────────────
    "BatchHeader": MetadataEntry(
        category="framework",
        description="Batch job header. Used to enqueue tasks at runtime — `BatchHeader::construct().addTask(...).save()`.",
        members=["construct()", "addTask()", "save()", "addDependency()", "parmCaption()"],
        references=["https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/sysop-framework/sysoperation-framework"],
    ),
    "DataAreaId": MetadataEntry(
        category="framework",
        description="Company partition key. Every shared-by-default table has DataAreaId; `changecompany` switches scope at runtime.",
        members=["DataArea", "changecompany"],
        references=["https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/dev-ref/xpp-changecompany"],
    ),
    "SysSecKeys": MetadataEntry(
        category="framework",
        description="Conceptual umbrella for the security-key model: privileges, duties, roles, security policies.",
        members=["SecurityPrivilege", "SecurityDuty", "SecurityRole", "SecurityPolicy"],
        references=["https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/sysadmin/security-architecture"],
    ),
    "Workflow": MetadataEntry(
        category="framework",
        description="Workflow framework: types, configurations, providers, and the WorkflowDocument abstraction over a record.",
        members=["WorkflowTypeDispatcher", "WorkflowDocument", "WorkflowSubmitManager"],
        references=["https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/business-process-workflows/"],
    ),
    "DimensionAttribute": MetadataEntry(
        category="framework",
        description="Financial dimension framework. DimensionAttribute defines a dimension; DimensionAttributeValue holds an instance value.",
        members=["DimensionAttribute", "DimensionAttributeValue", "DimensionAttributeValueCombination", "LedgerDimensionAccount"],
        references=["https://learn.microsoft.com/en-us/dynamics365/finance/general-ledger/financial-dimensions"],
    ),
}


#####################
# MAIN TOOL & LOGIC #
#####################
class D365MetadataLookupTool(
    BaseTool[D365MetadataLookupToolInputSchema, D365MetadataLookupToolOutputSchema]
):
    """Lookup tool returning what well-known D365 F&O AOT objects provide."""

    def __init__(self, config: D365MetadataLookupToolConfig = D365MetadataLookupToolConfig()):
        super().__init__(config)
        self._lookup: Dict[str, MetadataEntry] = dict(_BUNDLED)
        if config.extra_lookup:
            self._lookup.update(config.extra_lookup)

    def run(
        self, params: D365MetadataLookupToolInputSchema
    ) -> D365MetadataLookupToolOutputSchema:
        # Case-insensitive lookup but preserve the canonical (original) name in output.
        target = params.object_name.strip()
        canonical_match = _find_canonical(self._lookup, target)
        if canonical_match is None:
            search_url = f"https://learn.microsoft.com/en-us/search/?terms={target}"
            return D365MetadataLookupToolOutputSchema(
                canonical_name=target,
                category="unknown",
                description=(
                    f"'{target}' is not in the bundled D365 F&O reference table. "
                    "It may be an ISV-shipped object, a project-specific extension, or simply not yet curated. "
                    "Pass canonical_name to a web-search tool for live information."
                ),
                key_members=[],
                references=[search_url],
                found=False,
            )

        canonical_name, entry = canonical_match
        return D365MetadataLookupToolOutputSchema(
            canonical_name=canonical_name,
            category=entry.category,
            description=entry.description,
            key_members=list(entry.members),
            references=list(entry.references),
            found=True,
        )


def _find_canonical(table: Dict[str, MetadataEntry], name: str) -> Optional[tuple]:
    if name in table:
        return name, table[name]
    lowered = name.lower()
    for key, entry in table.items():
        if key.lower() == lowered:
            return key, entry
    return None


#################
# EXAMPLE USAGE #
#################
if __name__ == "__main__":
    tool = D365MetadataLookupTool()
    for obj in ("CustTable", "RUNBASEBATCH", "NoYes", "MadeUpObject"):
        out = tool.run(D365MetadataLookupToolInputSchema(object_name=obj))
        print(f"{out.canonical_name} [{out.category}] found={out.found}")
        print(f"  {out.description[:140]}...")
        if out.key_members:
            print(f"  members: {', '.join(out.key_members[:5])}")
        print()
