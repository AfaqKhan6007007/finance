"""
Comprehensive Schema Guide Tools for All 21 Tables
Each tool provides precise field definitions and foreign key relationships
Designed for scalable dynamic context retrieval
"""

from mcp import FastMCP


def register_prompt_tools(mcp: FastMCP):
    """Register all 21 schema-specific guide tools"""
    
    # ============================================
    # 1. COMPANY TABLE
    # ============================================
    @mcp.tool()
    def get_company_schema_guide() -> str:
        """
        Get complete schema information for Company table.
        Use when querying companies or business entities.
        """
        return """## Company Table Schema

**Purpose**: Stores business entities/organizations in the system.

**Fields**:
- id (PK): Auto-increment primary key
- name: Company legal name (required, max 200 chars)
- abbreviation: Short name (max 50 chars)
- country: Operating country (required, max 100 chars)
- date_of_establishment: Company founding date
- default_currency: Currency code (default "USD", max 10 chars)
- tax_id: Tax registration number (max 100 chars)
- default_letter_head: Letter head template (max 200 chars)
- domain: Company domain/website (max 200 chars)
- parent_company (FK): Self-reference to parent Company.id (nullable)
- is_parent_company: Boolean - is this a holding company
- registration_details: Text field for registration info
- account_number: Legacy field (max 50 chars)
- is_disabled: Boolean - is company disabled
- is_group: Boolean - is this a group company
- company_type: Choice - regular/subsidiary/branch/holding
- account_type: Choice - asset/liability/equity/income/expense
- tax_rate: Decimal (5,2) - default tax rate
- balance_must_be: Choice - debit/credit/both
- created_at: Timestamp (auto)
- updated_at: Timestamp (auto)
- created_by (FK): User.id who created (nullable)

**Foreign Keys**:
- parent_company → Company.id (self-reference, nullable)
- created_by → User.id (nullable)

**Reverse Relations**:
- subsidiaries: Companies where this is parent_company
- accounts: Account records for this company
- cost_centers: CostCenter records for this company
- budgets: Budget records for this company
- invoices: Invoice records for this company
- journal_entries: JournalEntry records for this company
- suppliers: Supplier records for this company
- customers: Customer records for this company
- tax_item_templates: TaxItemTemplate records
- tax_rules: TaxRule records
- cost_center_allocations: CostCenterAllocation records

**Unique Constraints**: None (name not enforced unique)

**Choices**:
- company_type: regular, subsidiary, branch, holding
- account_type: asset, liability, equity, income, expense
- balance_must_be: debit, credit, both"""

    # ============================================
    # 2. ACCOUNT TABLE
    # ============================================
    @mcp.tool()
    def get_account_schema_guide() -> str:
        """
        Get complete schema information for Account table (Chart of Accounts).
        Use when querying accounts, ledgers, or financial account structure.
        """
        return """## Account Table Schema

**Purpose**: Chart of Accounts - defines all financial accounts in the system.

**Fields**:
- id (PK): Auto-increment primary key
- name: Account name (required, max 200 chars)
- account_number: Account code/number (max 50 chars)
- is_disabled: Boolean - is account disabled
- is_group: Boolean - is this a parent/group account
- company (FK): Company.id (required)
- currency: Currency code (default "USD", max 10 chars)
- parent_account (FK): Self-reference to parent Account.id (nullable)
- account_type: Choice - asset/liability/equity/income/expense
- tax_rate: Decimal (5,2) - tax rate for this account
- balance_must_be: Choice - debit/credit/both
- created_at: Timestamp (auto)
- updated_at: Timestamp (auto)
- created_by (FK): User.id who created (nullable)

**Foreign Keys**:
- company → Company.id (required, CASCADE)
- parent_account → Account.id (self-reference, nullable, SET_NULL)
- created_by → User.id (nullable, SET_NULL)

**Reverse Relations**:
- sub_accounts: Child accounts where this is parent_account
- budgets: Budget records for this account
- journal_entries: JournalEntry records for this account

**Unique Constraints**:
- (company, account_number): Account number must be unique per company

**Choices**:
- account_type: asset, liability, equity, income, expense
- balance_must_be: debit, credit, both

**Accounting Rules**:
- Group accounts (is_group=True) cannot have transactions
- Asset/Expense: Normal debit balance
- Liability/Equity/Income: Normal credit balance"""

    # ============================================
    # 3. INVOICE TABLE
    # ============================================
    @mcp.tool()
    def get_invoice_schema_guide() -> str:
        """
        Get complete schema information for Invoice table.
        Use when querying invoices, bills, or sales/purchase documents.
        """
        return """## Invoice Table Schema

**Purpose**: Stores sales and purchase invoices.

**Fields**:
- id (PK): Auto-increment primary key
- invoice_id: Unique identifier (required, max 50 chars, unique)
- invoice_number: Display number (required, max 50 chars)
- date: Invoice date (required)
- supplier (FK): Supplier.id (nullable, for purchase invoices)
- supplier_vat: Supplier VAT/GST number (max 50 chars)
- customer (FK): Customer.id (nullable, for sales invoices)
- customer_vat: Customer VAT/GST number (max 50 chars)
- amount_before_vat: Decimal (15,2) - subtotal before tax
- total_vat: Decimal (15,2) - total tax amount
- total_amount: Decimal (15,2) - grand total
- qr_code_present: Boolean - has QR code
- qr_code_data: Text - QR code content
- status: Choice - draft/sent/paid/cancelled/return
- company (FK): Company.id (nullable)
- created_at: Timestamp (auto)
- updated_at: Timestamp (auto)
- created_by (FK): User.id who created (nullable)

**Foreign Keys**:
- supplier → Supplier.id (nullable, PROTECT)
- customer → Customer.id (nullable, PROTECT)
- company → Company.id (nullable, CASCADE)
- created_by → User.id (nullable, SET_NULL)

**Reverse Relations**: None

**Unique Constraints**:
- invoice_id: Must be globally unique

**Choices**:
- status: draft, sent, paid, cancelled, return

**Business Logic**:
- Either supplier OR customer should be set (not both)
- Purchase invoice: supplier is set
- Sales invoice: customer is set
- total_amount auto-calculated: amount_before_vat + total_vat"""

    # ============================================
    # 4. JOURNAL ENTRY TABLE
    # ============================================
    @mcp.tool()
    def get_journal_entry_schema_guide() -> str:
        """
        Get complete schema information for JournalEntry table.
        Use when querying journal entries or accounting transactions.
        """
        return """## JournalEntry Table Schema

**Purpose**: Records individual accounting transactions (double-entry bookkeeping).

**Fields**:
- id (PK): Auto-increment primary key
- entry_number: Unique entry ID (required, max 50 chars, unique)
- date: Posting date (required)
- account (FK): Account.id (required)
- debit_amount: Decimal (15,2) - debit amount
- credit_amount: Decimal (15,2) - credit amount
- description: Text - transaction description
- company (FK): Company.id (nullable)
- created_at: Timestamp (auto)
- updated_at: Timestamp (auto)
- created_by (FK): User.id who created (nullable)

**Foreign Keys**:
- account → Account.id (required, CASCADE)
- company → Company.id (nullable, CASCADE)
- created_by → User.id (nullable, SET_NULL)

**Reverse Relations**: None

**Unique Constraints**:
- entry_number: Must be globally unique

**Business Logic**:
- Auto-generates entry_number: "JE00001", "JE00002", etc.
- Each entry is ONE side of a double-entry transaction
- Debit and credit are mutually exclusive (one should be 0)
- Complete transaction needs paired entries with balanced debits/credits"""

    # ============================================
    # 5. SUPPLIER TABLE
    # ============================================
    @mcp.tool()
    def get_supplier_schema_guide() -> str:
        """
        Get complete schema information for Supplier table.
        Use when querying suppliers, vendors, or procurement entities.
        """
        return """## Supplier Table Schema

**Purpose**: Stores vendor/supplier information for procurement.

**Fields**:
- id (PK): Auto-increment primary key
- gstin_uin: GST/UIN number (max 30 chars)
- name: Supplier name (required, max 200 chars)
- supplier_type: Choice - company/individual/partnership
- gst_category: Choice - registered/unregistered/SEZ/overseas/etc
- contact_first_name: Contact person first name (max 100 chars)
- contact_last_name: Contact person last name (max 100 chars)
- contact_email: Email address (max 254 chars)
- contact_mobile: Mobile number (max 30 chars)
- preferred_billing: Boolean - is preferred billing address
- preferred_shipping: Boolean - is preferred shipping address
- postal_code: Postal/ZIP code (max 20 chars)
- city: City name (max 120 chars)
- address_line1: Address line 1 (max 255 chars)
- address_line2: Address line 2 (max 255 chars)
- state: State/province (max 100 chars)
- country: Country (max 100 chars, default "Pakistan")
- company (FK): Company.id (nullable)
- created_at: Timestamp (auto)
- updated_at: Timestamp (auto)
- created_by (FK): User.id who created (nullable)

**Foreign Keys**:
- company → Company.id (nullable, SET_NULL)
- created_by → User.id (nullable, SET_NULL)

**Reverse Relations**:
- invoices: Purchase invoices from this supplier
- deduction_certificates: DeductionCertificate records for this supplier

**Unique Constraints**:
- (company, name): Supplier name must be unique per company

**Choices**:
- supplier_type: company, individual, partnership
- gst_category: registered, registered_composition, unregistered, sez, overseas, deemed_export, uin, tax_deductor, tax_collector, input_service_distributor"""

    # ============================================
    # 6. CUSTOMER TABLE
    # ============================================
    @mcp.tool()
    def get_customer_schema_guide() -> str:
        """
        Get complete schema information for Customer table.
        Use when querying customers, clients, or sales entities.
        """
        return """## Customer Table Schema

**Purpose**: Stores customer/client information for sales.

**Fields**:
- id (PK): Auto-increment primary key
- gstin_uin: GST/UIN number (max 30 chars)
- name: Customer name (required, max 200 chars)
- customer_type: Choice - company/individual/partnership
- gst_category: Choice - registered/unregistered/SEZ/overseas/etc
- contact_first_name: Contact person first name (max 100 chars)
- contact_last_name: Contact person last name (max 100 chars)
- contact_email: Email address (max 254 chars)
- contact_mobile: Mobile number (max 30 chars)
- preferred_billing: Boolean - is preferred billing address
- preferred_shipping: Boolean - is preferred shipping address
- postal_code: Postal/ZIP code (max 20 chars)
- city: City name (max 120 chars)
- address_line1: Address line 1 (max 255 chars)
- address_line2: Address line 2 (max 255 chars)
- state: State/province (max 100 chars)
- country: Country (max 100 chars, default "Pakistan")
- company (FK): Company.id (nullable)
- created_at: Timestamp (auto)
- updated_at: Timestamp (auto)
- created_by (FK): User.id who created (nullable)

**Foreign Keys**:
- company → Company.id (nullable, SET_NULL)
- created_by → User.id (nullable, SET_NULL)

**Reverse Relations**:
- invoices: Sales invoices to this customer
- tax_rules: TaxRule records for this customer

**Unique Constraints**:
- (company, name): Customer name must be unique per company

**Choices**:
- customer_type: company, individual, partnership
- gst_category: registered, registered_composition, unregistered, sez, overseas, deemed_export, uin, tax_deductor, tax_collector, input_service_distributor"""

    # ============================================
    # 7. BUDGET TABLE
    # ============================================
    @mcp.tool()
    def get_budget_schema_guide() -> str:
        """
        Get complete schema information for Budget table.
        Use when querying budgets or financial planning data.
        """
        return """## Budget Table Schema

**Purpose**: Stores budget allocations for accounts and cost centers.

**Fields**:
- id (PK): Auto-increment primary key
- series: Budget series/name (required, max 200 chars)
- budget_against: Choice - cost_center/project
- fiscal_year_from: Fiscal year start (max 20 chars, choice)
- fiscal_year_to: Fiscal year end (max 20 chars, choice)
- company (FK): Company.id (required)
- distribution: Choice - monthly/quarterly/half-yearly/yearly
- cost_center (FK): CostCenter.id (required, non-group only)
- account (FK): Account.id (required)
- budget_amount: Decimal (15,2) - total budget amount

**Foreign Keys**:
- company → Company.id (required, CASCADE)
- cost_center → CostCenter.id (required, PROTECT, limit: is_group=False, is_disabled=False)
- account → Account.id (required, CASCADE)

**Reverse Relations**: None

**Unique Constraints**: None specified

**Choices**:
- budget_against: cost_center, project
- fiscal_year_from: 2025-2026 (extensible)
- fiscal_year_to: 2025-2026 (extensible)
- distribution: monthly, quarterly, half-yearly, yearly

**Business Logic**:
- Can only budget against non-group, enabled cost centers
- Distribution determines how budget_amount is split across periods"""

    # ============================================
    # 8. COST CENTER TABLE
    # ============================================
    @mcp.tool()
    def get_cost_center_schema_guide() -> str:
        """
        Get complete schema information for CostCenter table.
        Use when querying cost centers or departmental structures.
        """
        return """## CostCenter Table Schema

**Purpose**: Defines cost centers (departments/projects) for expense tracking.

**Fields**:
- id (PK): Auto-increment primary key
- name: Cost center name (required, max 150 chars)
- cost_center_number: Cost center code (max 50 chars, nullable)
- company (FK): Company.id (required)
- parent (FK): Self-reference to parent CostCenter.id (nullable)
- is_group: Boolean - is this a parent/group cost center
- is_disabled: Boolean - is cost center disabled
- created_at: Timestamp (auto)
- updated_at: Timestamp (auto)

**Foreign Keys**:
- company → Company.id (required, CASCADE)
- parent → CostCenter.id (self-reference, nullable, SET_NULL)

**Reverse Relations**:
- children: Child cost centers where this is parent
- budgets: Budget records for this cost center
- allocations: CostCenterAllocation records

**Unique Constraints**:
- (company, name): Cost center name must be unique per company

**Business Logic**:
- Group cost centers (is_group=True) cannot have direct entries
- Only non-group cost centers can be used in transactions/budgets
- Hierarchical structure supported via parent relationship"""

    # ============================================
    # 9. COST CENTER ALLOCATION TABLE
    # ============================================
    @mcp.tool()
    def get_cost_center_allocation_schema_guide() -> str:
        """
        Get complete schema information for CostCenterAllocation table.
        Use when querying cost center allocations or expense distributions.
        """
        return """## CostCenterAllocation Table Schema

**Purpose**: Allocates expenses to multiple cost centers (shared cost distribution).

**Fields**:
- id (PK): Auto-increment primary key
- cost_center (FK): CostCenter.id (required)
- company (FK): Company.id (required)
- valid_from: Date - allocation start date (required)

**Foreign Keys**:
- cost_center → CostCenter.id (required, CASCADE)
- company → Company.id (required, CASCADE)

**Reverse Relations**: None

**Unique Constraints**:
- (cost_center, company): One allocation per cost center per company

**Business Logic**:
- Used for splitting shared expenses across multiple cost centers
- valid_from determines when allocation rules take effect
- Typically used with percentage-based distributions"""

    # ============================================
    # 10. ACCOUNTING DIMENSION TABLE
    # ============================================
    @mcp.tool()
    def get_accounting_dimension_schema_guide() -> str:
        """
        Get complete schema information for AccountingDimension table.
        Use when querying custom accounting dimensions or analytics tags.
        """
        return """## AccountingDimension Table Schema

**Purpose**: Defines custom dimensions for multi-dimensional accounting analysis.

**Fields**:
- id (PK): Auto-increment primary key
- name: Dimension name (required, max 150 chars)
- created_at: Timestamp (auto)
- updated_at: Timestamp (auto)

**Foreign Keys**: None

**Reverse Relations**: None

**Unique Constraints**: None specified

**Business Logic**:
- Used for adding custom analytical dimensions beyond standard cost centers
- Examples: Project, Department, Region, Product Line, etc.
- Enables multi-dimensional financial reporting"""

    # ============================================
    # 11. TAX ITEM TEMPLATE TABLE
    # ============================================
    @mcp.tool()
    def get_tax_item_template_schema_guide() -> str:
        """
        Get complete schema information for TaxItemTemplate table.
        Use when querying tax templates or GST configurations.
        """
        return """## TaxItemTemplate Table Schema

**Purpose**: Stores reusable GST/tax rate templates.

**Fields**:
- id (PK): Auto-increment primary key
- title: Template name (required, max 150 chars)
- company (FK): Company.id (required)
- gst_rate: Decimal (5,2) - GST rate percentage
- gst_treatment: Choice - taxable/nil_rated/exempted/non_gst
- disabled: Boolean - is template disabled

**Foreign Keys**:
- company → Company.id (required, CASCADE)

**Reverse Relations**:
- sales_tax_rules: TaxRule records using this template

**Unique Constraints**: None specified

**Choices**:
- gst_treatment: taxable, nil_rated, exempted, non_gst

**Business Logic**:
- Reusable templates for common tax rates (0%, 5%, 12%, 18%, 28%)
- Can be disabled without deleting historical data"""

    # ============================================
    # 12. TAX CATEGORY TABLE
    # ============================================
    @mcp.tool()
    def get_tax_category_schema_guide() -> str:
        """
        Get complete schema information for TaxCategory table.
        Use when querying tax categories or tax groupings.
        """
        return """## TaxCategory Table Schema

**Purpose**: Groups taxes into categories for easier management.

**Fields**:
- id (PK): Auto-increment primary key
- title: Category name (required, max 150 chars, nullable)

**Foreign Keys**: None

**Reverse Relations**:
- tax_rules: TaxRule records in this category

**Unique Constraints**: None specified

**Business Logic**:
- Simple categorization/grouping mechanism for tax rules
- Examples: "Interstate GST", "Intrastate GST", "Export Tax", etc."""

    # ============================================
    # 13. TAX RULE TABLE
    # ============================================
    @mcp.tool()
    def get_tax_rule_schema_guide() -> str:
        """
        Get complete schema information for TaxRule table.
        Use when querying tax rules or tax calculation logic.
        """
        return """## TaxRule Table Schema

**Purpose**: Defines tax calculation rules based on various conditions.

**Fields**:
- id (PK): Auto-increment primary key
- tax_type: Choice - sales/purchase
- sales_tax_template (FK): TaxItemTemplate.id (required)
- shopping_cart_use: Boolean - use in e-commerce
- customer (FK): Customer.id (required)
- customer_group: Customer group (max 100 chars)
- item: Item name (max 200 chars)
- item_group: Item group (max 100 chars)
- billing_city: Billing city (max 100 chars)
- shipping_city: Shipping city (max 100 chars)
- billing_county: Billing county (max 100 chars)
- shipping_county: Shipping county (max 100 chars)
- billing_state: Billing state (max 100 chars)
- shipping_state: Shipping state (max 100 chars)
- billing_zipcode: Billing ZIP (max 20 chars)
- shipping_zipcode: Shipping ZIP (max 20 chars)
- billing_country: Billing country (max 100 chars)
- shipping_country: Shipping country (max 100 chars)
- tax_category (FK): TaxCategory.id (required)
- from_date: Rule start date (required)
- to_date: Rule end date (required)
- priority: Integer - rule priority (default 0)
- company (FK): Company.id (required)

**Foreign Keys**:
- sales_tax_template → TaxItemTemplate.id (required, CASCADE)
- customer → Customer.id (required, CASCADE)
- tax_category → TaxCategory.id (required, CASCADE)
- company → Company.id (required, CASCADE)

**Reverse Relations**: None

**Unique Constraints**: None specified

**Choices**:
- tax_type: sales, purchase

**Business Logic**:
- Rules applied based on customer, location, item, date range
- Higher priority rules override lower priority
- Enables complex tax logic (interstate vs intrastate, special zones)"""

    # ============================================
    # 14. TAX WITHHOLDING CATEGORY TABLE
    # ============================================
    @mcp.tool()
    def get_tax_withholding_category_schema_guide() -> str:
        """
        Get complete schema information for TaxWithholdingCategory table.
        Use when querying TDS/withholding tax categories.
        """
        return """## TaxWithholdingCategory Table Schema

**Purpose**: Defines TDS (Tax Deducted at Source) categories and rules.

**Fields**:
- id (PK): Auto-increment primary key
- name: Category name (required, max 255 chars)
- category_name: Alternative name (max 255 chars, nullable)
- deduct_tax_on_basis: Choice - Net Total/Gross Total
- round_off_tax_amount: Boolean - round to nearest integer
- section: Tax section code (max 100 chars, e.g., "194C", "194J")
- only_deduct_on_excess: Boolean - deduct only on excess amount
- entity: Choice - Company/Company Assessee/Individual/No PAN
- disable_cumulative_threshold: Boolean - ignore cumulative threshold
- disable_transaction_threshold: Boolean - ignore transaction threshold

**Foreign Keys**: None

**Reverse Relations**:
- rates: TaxWithholdingRate records for this category
- accounts: TaxCategoryAccount mappings
- deduction_certificates: DeductionCertificate records

**Unique Constraints**: None specified

**Choices**:
- deduct_tax_on_basis: Net Total, Gross Total
- entity: Company, Company Assessee, Individual, No PAN / Invalid PAN

**Business Logic**:
- TDS is withholding tax deducted at source
- Different rates for different entities (Company: 10%, Individual: 20%, No PAN: 30%)
- Threshold logic: deduct only if amount exceeds threshold
- Cumulative threshold: total payments in fiscal year
- Transaction threshold: per transaction amount"""

    # ============================================
    # 15. TAX WITHHOLDING RATE TABLE
    # ============================================
    @mcp.tool()
    def get_tax_withholding_rate_schema_guide() -> str:
        """
        Get complete schema information for TaxWithholdingRate table.
        Use when querying TDS rates or withholding tax percentages.
        """
        return """## TaxWithholdingRate Table Schema

**Purpose**: Stores TDS rate definitions with thresholds and date ranges.

**Fields**:
- id (PK): Auto-increment primary key
- category (FK): TaxWithholdingCategory.id (required)
- from_date: Rate effective from (required)
- to_date: Rate effective to (required)
- tax_withholding_group: Group name (max 100 chars)
- tax_withholding_rate: Decimal (6,3) - TDS rate percentage
- cumulative_threshold: Decimal (12,2) - total yearly threshold
- transaction_threshold: Decimal (12,2) - per transaction threshold

**Foreign Keys**:
- category → TaxWithholdingCategory.id (required, CASCADE)

**Reverse Relations**: None

**Unique Constraints**: None specified

**Business Logic**:
- Date range determines when rate is applicable
- Cumulative threshold: deduct only if total payments > threshold
- Transaction threshold: deduct only if single payment > threshold
- Example: Section 194C - threshold ₹30,000 single / ₹1,00,000 cumulative"""

    # ============================================
    # 16. TAX CATEGORY ACCOUNT TABLE
    # ============================================
    @mcp.tool()
    def get_tax_category_account_schema_guide() -> str:
        """
        Get complete schema information for TaxCategoryAccount table.
        Use when querying tax-to-account mappings.
        """
        return """## TaxCategoryAccount Table Schema

**Purpose**: Maps tax withholding categories to accounting accounts.

**Fields**:
- id (PK): Auto-increment primary key
- category (FK): TaxWithholdingCategory.id (required)
- company (FK): Company.id (required)
- account (FK): Account.id (required)

**Foreign Keys**:
- category → TaxWithholdingCategory.id (required, CASCADE)
- company → Company.id (required, CASCADE)
- account → Account.id (required, CASCADE)

**Reverse Relations**: None

**Unique Constraints**: None specified

**Business Logic**:
- Links TDS categories to liability accounts
- When TDS is deducted, amount posted to mapped account
- Example: Section 194C TDS → "TDS Payable 194C" account"""

    # ============================================
    # 17. DEDUCTION CERTIFICATE TABLE
    # ============================================
    @mcp.tool()
    def get_deduction_certificate_schema_guide() -> str:
        """
        Get complete schema information for DeductionCertificate table.
        Use when querying TDS certificates or lower deduction certificates.
        """
        return """## DeductionCertificate Table Schema

**Purpose**: Stores lower TDS deduction certificates (Form 13/15G/15H).

**Fields**:
- id (PK): Auto-increment primary key
- tax_withholding_category (FK): TaxWithholdingCategory.id (required)
- company (FK): Company.id (required)
- fiscal_year: Fiscal year (max 20 chars, choice)
- certificate_number: Certificate number (required, max 100 chars)
- supplier (FK): Supplier.id (required)
- pan_number: PAN number (max 20 chars)
- valid_from: Certificate start date (required)
- valid_to: Certificate end date (required)
- rate_of_tdas: Decimal (6,3) - lower TDS rate
- certificate_limit: Decimal (12,2) - certificate amount limit

**Foreign Keys**:
- tax_withholding_category → TaxWithholdingCategory.id (required, CASCADE)
- company → Company.id (required, CASCADE)
- supplier → Supplier.id (required, CASCADE)

**Reverse Relations**: None

**Unique Constraints**: None specified

**Choices**:
- fiscal_year: 2025-2026 (extensible)

**Business Logic**:
- Allows lower TDS deduction rate than standard
- Issued by income tax department
- Valid for specific period and amount limit
- Must be verified before applying lower rate"""

    # ============================================
    # 18. BANK ACCOUNT TYPE TABLE
    # ============================================
    @mcp.tool()
    def get_bank_account_type_schema_guide() -> str:
        """
        Get complete schema information for BankAccountType table.
        Use when querying bank account types or categories.
        """
        return """## BankAccountType Table Schema

**Purpose**: Defines bank account types (Savings, Current, etc.).

**Fields**:
- id (PK): Auto-increment primary key
- account_type: Type name (required, max 200 chars)

**Foreign Keys**: None

**Reverse Relations**:
- bank_accounts: BankAccount records of this type

**Unique Constraints**: None specified

**Business Logic**:
- Reference/lookup table for bank account types
- Examples: Savings Account, Current Account, Fixed Deposit, etc."""

    # ============================================
    # 19. BANK ACCOUNT SUBTYPE TABLE
    # ============================================
    @mcp.tool()
    def get_bank_account_subtype_schema_guide() -> str:
        """
        Get complete schema information for BankAccountSubtype table.
        Use when querying bank account subtypes.
        """
        return """## BankAccountSubtype Table Schema

**Purpose**: Defines bank account subtypes for finer categorization.

**Fields**:
- id (PK): Auto-increment primary key
- account_subtype: Subtype name (required, max 200 chars)

**Foreign Keys**: None

**Reverse Relations**:
- bank_accounts: BankAccount records of this subtype

**Unique Constraints**: None specified

**Business Logic**:
- Reference/lookup table for account subtypes
- Examples: Regular Savings, Salary Account, Business Current, etc."""

    # ============================================
    # 20. BANK ACCOUNT TABLE
    # ============================================
    @mcp.tool()
    def get_bank_account_schema_guide() -> str:
        """
        Get complete schema information for BankAccount table.
        Use when querying bank accounts or payment methods.
        """
        return """## BankAccount Table Schema

**Purpose**: Stores company's bank accounts and payment details.

**Fields**:
- id (PK): Auto-increment primary key
- name: Account name (required, max 200 chars)
- bank: Bank name (required, max 200 chars)
- account_type (FK): BankAccountType.id (nullable)
- account_subtype (FK): BankAccountSubtype.id (nullable)
- party_type: Choice - customer/supplier/employee/shareholder
- party: Party name (max 200 chars)
- iban: IBAN number (max 34 chars)
- branch_code: Branch code (max 20 chars)
- bank_account_number: Account number (max 50 chars)
- last_integration_date: Last sync date (nullable)

**Foreign Keys**:
- account_type → BankAccountType.id (nullable, CASCADE)
- account_subtype → BankAccountSubtype.id (nullable, CASCADE)

**Reverse Relations**: None

**Unique Constraints**: None specified

**Choices**:
- party_type: customer, supplier, employee, shareholder

**Business Logic**:
- Links to parties (customers/suppliers) for payment tracking
- IBAN for international transfers
- last_integration_date for bank statement reconciliation"""

    # ============================================
    # 21. USER PROFILE TABLE
    # ============================================
    @mcp.tool()
    def get_user_profile_schema_guide() -> str:
        """
        Get complete schema information for UserProfile table.
        Use when querying user profiles or extending user information.
        """
        return """## UserProfile Table Schema

**Purpose**: Extends Django's built-in User model with additional fields.

**Fields**:
- id (PK): Auto-increment primary key
- user (FK): User.id (required, one-to-one)
- phone_number: Phone number (max 20 chars)
- date_of_birth: Birth date (nullable)

**Foreign Keys**:
- user → User.id (required, CASCADE, one-to-one)

**Reverse Relations**: None (one-to-one with User)

**Unique Constraints**:
- user: Each User can have only one UserProfile

**Business Logic**:
- Extends standard User model (username, email, password)
- Use for additional user information not in base User model
- Access: user.userprofile.phone_number"""

    # ============================================
    # HELPER TOOL: FILTER SYNTAX GUIDE
    # ============================================
    @mcp.tool()
    def get_filter_syntax_guide() -> str:
        """
        Get comprehensive guide for constructing Django ORM filters.
        Use when building complex queries with filters.
        """
        return """## Django ORM Filter Syntax Guide

**Basic Filters** (Exact Match):
```python
{"field_name": "value"}
{"status": "paid"}
{"company_id": 5}
```

**Comparison Operators**:
```python
{"field__gte": value}     # Greater than or equal (>=)
{"field__gt": value}      # Greater than (>)
{"field__lte": value}     # Less than or equal (<=)
{"field__lt": value}      # Less than (<)
{"amount__gte": 10000}
{"balance__lt": 0}
```

**Range Queries**:
```python
{"field__range": [start, end]}    # Between (inclusive)
{"date__range": ["2025-01-01", "2025-12-31"]}
{"amount__range": [1000, 5000]}
```

**Text Search**:
```python
{"field__icontains": "text"}      # Case-insensitive contains
{"field__contains": "text"}       # Case-sensitive contains
{"field__startswith": "prefix"}   # Starts with
{"field__endswith": "suffix"}     # Ends with
{"name__icontains": "tech"}
```

**Null Checks**:
```python
{"field__isnull": True}           # IS NULL
{"field__isnull": False}          # IS NOT NULL
{"parent_account__isnull": True}  # Top-level accounts
```

**Multiple Values** (IN):
```python
{"field__in": [val1, val2, val3]}
{"status__in": ["draft", "sent"]}
{"company_id__in": [1, 2, 3]}
```

**Boolean Fields**:
```python
{"is_active": True}
{"is_disabled": False}
{"is_group": True}
```

**Foreign Key Lookups** (Spanning Relations):
```python
{"fk_field__related_field": value}
{"company__name": "ABC Corp"}
{"account__account_type": "asset"}
{"supplier__country": "India"}
```

**Combining Multiple Filters** (AND Logic):
```python
{
    "status": "paid",
    "total_amount__gte": 10000,
    "date__range": ["2025-01-01", "2025-12-31"]
}
```

**Common Filter Patterns**:
- Active records: `{"is_disabled": False}`
- Recent records: `{"created_at__gte": "2025-01-01"}`
- Non-group accounts: `{"is_group": False}`
- Specific company: `{"company_id": 1}`
- Date ranges: `{"date__range": ["start", "end"]}`"""

    # ============================================
    # CRUD OPERATION GUIDE TOOL
    # ============================================
    @mcp.tool()
    def get_crud_operation_guide(operation: str) -> str:
        """
        Get detailed guide with few-shot examples for a specific CRUD operation.
        ALWAYS call this before performing create/update/delete operations.
        
        Args:
            operation: One of "create", "update", "delete", "read" (or "get"/"query")
            
        Returns:
            Detailed guide with workflow and few-shot examples for that operation
            
        Usage:
            get_crud_operation_guide("create")  # Before creating records
            get_crud_operation_guide("update")  # Before updating records
            get_crud_operation_guide("delete")  # Before deleting records
            get_crud_operation_guide("read")    # For querying guidance
        """
        from tools.crud_prompt_templates import get_crud_operation_guide as get_guide
        return get_guide(operation)
    
    @mcp.tool()
    def list_available_tables() -> str:
        """
        List all available tables that can be queried with generic data tools.
        Use this to discover what tables exist in the system.
        
        Returns:
            List of table names with descriptions
        """
        from tools.generic_data_tools import list_available_tables as list_tables
        result = list_tables()
        if result.get("success"):
            tables = result["data"]["tables"]
            output = "## Available Tables\n\n"
            output += f"Total: {result['data']['total_tables']} tables\n\n"
            for name, info in tables.items():
                search_info = f" (searchable: {', '.join(info['search_fields'])})" if info['search_fields'] else ""
                output += f"- **{name}**: {info['model']}{search_info}\n"
            return output
        return "Error listing tables"


# Export function
__all__ = ['register_prompt_tools']
