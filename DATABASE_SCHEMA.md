# Finance Management System - Complete Database Schema

**Project:** Multi-Company Financial Management System with Tax Compliance
**Database:** SQLite (db.sqlite3)
**Django Version:** 6.0

---

## Table of Contents
1. [Authentication & User Management](#1-authentication--user-management)
2. [Core Company Structure](#2-core-company-structure)
3. [Chart of Accounts](#3-chart-of-accounts)
4. [Cost Centers & Budgets](#4-cost-centers--budgets)
5. [Transaction Recording](#5-transaction-recording)
6. [Parties (Suppliers & Customers)](#6-parties-suppliers--customers)
7. [Tax Management](#7-tax-management)
8. [Accounting Dimensions](#8-accounting-dimensions)
9. [Relationships Summary](#9-relationships-summary)
10. [Key Constraints & Rules](#10-key-constraints--rules)

---

## 1. AUTHENTICATION & USER MANAGEMENT

### UserProfile Table
**Purpose:** Extend Django's built-in User model with additional profile information

| Field | Type | Constraints | Notes |
|-------|------|-----------|-------|
| id | INTEGER | PRIMARY KEY | Auto-generated |
| user | INTEGER | FK → auth_user (UNIQUE) | One-to-One relationship |
| phone_number | VARCHAR(20) | NULL, BLANK OK | Contact information |
| date_of_birth | DATE | NULL, BLANK OK | Optional biographical data |

**Django's Built-in User Table (auth_user)**
| Field | Type | Notes |
|-------|------|-------|
| id | INTEGER | PRIMARY KEY |
| username | VARCHAR(150) | UNIQUE |
| email | VARCHAR(254) | |
| password | VARCHAR(128) | Hashed |
| first_name, last_name | VARCHAR(150) | |
| is_active, is_staff, is_superuser | BOOLEAN | Permissions |
| date_joined | DATETIME | Auto-populated |

---

## 2. CORE COMPANY STRUCTURE

### Company Table
**Purpose:** Master data for multiple legal entities in the system

| Field | Type | Constraints | Notes |
|-------|------|-----------|-------|
| id | INTEGER | PRIMARY KEY | Auto-generated |
| name | VARCHAR(200) | NOT NULL | Company legal name |
| abbreviation | VARCHAR(50) | NULL, BLANK OK | Short form |
| country | VARCHAR(100) | NOT NULL | Country of operation |
| date_of_establishment | DATE | NULL, BLANK OK | Registration date |
| default_currency | VARCHAR(10) | DEFAULT 'USD' | Primary currency (e.g., USD, INR) |
| tax_id | VARCHAR(100) | BLANK OK | Tax registration number |
| default_letter_head | VARCHAR(200) | BLANK OK | Letterhead template |
| domain | VARCHAR(200) | BLANK OK | Company website/domain |
| parent_company_id | INTEGER | FK → Company (NULL) | SelfFK for hierarchical companies |
| is_parent_company | BOOLEAN | DEFAULT False | Flag: Is group/holding company |
| registration_details | TEXT | BLANK OK | Full registration information |
| account_number | VARCHAR(50) | BLANK OK | Legacy field |
| is_disabled | BOOLEAN | DEFAULT False | Soft delete flag |
| is_group | BOOLEAN | DEFAULT False | Is part of a group |
| company_type | VARCHAR(20) | CHOICES | [regular, subsidiary, branch, holding] |
| account_type | VARCHAR(20) | CHOICES, BLANK OK | [asset, liability, equity, income, expense] |
| tax_rate | DECIMAL(5,2) | DEFAULT 0.00, BLANK OK | Base tax rate |
| balance_must_be | VARCHAR(10) | CHOICES, DEFAULT 'both', BLANK OK | [debit, credit, both] |
| created_at | DATETIME | AUTO_NOW_ADD | Creation timestamp |
| updated_at | DATETIME | AUTO_NOW | Last update timestamp |
| created_by_id | INTEGER | FK → auth_user (NULL) | User who created record |

**Key Relationships:**
- Has many: Accounts, CostCenters, Budgets, Invoices, JournalEntries, Suppliers, Customers, TaxRules
- Self-relationship: parent_company (hierarchical structure for group companies)

**Example Data:**
```
Company 1: "ABC Corporation" (Parent)
├── Company 2: "ABC USA" (Subsidiary)
└── Company 3: "ABC India" (Subsidiary)
```

---

## 3. CHART OF ACCOUNTS

### Account Table
**Purpose:** General Ledger - hierarchical chart of accounts for recording all transactions

| Field | Type | Constraints | Notes |
|-------|------|-----------|-------|
| id | INTEGER | PRIMARY KEY | Auto-generated |
| name | VARCHAR(200) | NOT NULL | Account name (e.g., "Cash", "Bank", "Sales") |
| account_number | VARCHAR(50) | BLANK OK | Accounting code (e.g., "1001", "2001") |
| is_disabled | BOOLEAN | DEFAULT False | Soft delete flag |
| is_group | BOOLEAN | DEFAULT False | If True: can't record transactions directly |
| company_id | INTEGER | FK → Company (NOT NULL) | Which company owns this account |
| currency | VARCHAR(10) | DEFAULT 'USD', BLANK OK | Account currency |
| parent_account_id | INTEGER | FK → Account (NULL) | SelfFK for sub-accounts |
| account_type | VARCHAR(20) | CHOICES, BLANK OK | [asset, liability, equity, income, expense] |
| tax_rate | DECIMAL(5,2) | DEFAULT 0.00, BLANK OK | Default tax rate |
| balance_must_be | VARCHAR(10) | CHOICES, DEFAULT 'both', BLANK OK | [debit, credit, both] |
| created_at | DATETIME | AUTO_NOW_ADD | Creation timestamp |
| updated_at | DATETIME | AUTO_NOW | Last update timestamp |
| created_by_id | INTEGER | FK → auth_user (NULL) | User who created record |

**Unique Constraint:** (company_id, account_number) - prevent duplicate account numbers per company

**Account Type Definitions:**
- **Asset:** What the company owns (Cash, Bank, Equipment, Inventory)
- **Liability:** What the company owes (Payables, Loans, Accruals)
- **Equity:** Owner's stake (Capital, Retained Earnings)
- **Income:** Money coming in (Sales, Service Revenue, Interest)
- **Expense:** Money going out (Salaries, Utilities, Rent, COGS)

**Example Hierarchy:**
```
Assets (Group) [is_group=True]
├── Current Assets (Group) [is_group=True]
│   ├── Cash (Leaf) [is_group=False] - can record transactions
│   ├── Bank Accounts (Leaf) - can record transactions
│   └── Inventory (Leaf) - can record transactions
├── Fixed Assets (Group) [is_group=True]
│   └── Equipment (Leaf) - can record transactions
└── Intangible Assets (Group) [is_group=True]
    └── Goodwill (Leaf) - can record transactions
```

---

## 4. COST CENTERS & BUDGETS

### CostCenter Table
**Purpose:** Dimensional analysis - categorize expenses by department, location, project, etc.

| Field | Type | Constraints | Notes |
|-------|------|-----------|-------|
| id | INTEGER | PRIMARY KEY | Auto-generated |
| name | VARCHAR(150) | NOT NULL | Cost center name (e.g., "Marketing", "Sales", "R&D") |
| cost_center_number | VARCHAR(50) | NULL | Accounting code/prefix |
| company_id | INTEGER | FK → Company (NOT NULL) | Which company |
| parent_id | INTEGER | FK → CostCenter (NULL) | SelfFK for hierarchical structure |
| is_group | BOOLEAN | DEFAULT False | If True: can't allocate transactions here |
| is_disabled | BOOLEAN | DEFAULT False | Soft delete flag |
| created_at | DATETIME | AUTO_NOW_ADD | Creation timestamp |
| updated_at | DATETIME | AUTO_NOW | Last update timestamp |

**Unique Constraint:** (company_id, name) - prevent duplicate names per company

**Example Hierarchy:**
```
Operations (Group) [is_group=True]
├── North Region (Group) [is_group=True]
│   ├── North-Delhi (Leaf) [is_group=False]
│   └── North-Punjab (Leaf) [is_group=False]
└── South Region (Group) [is_group=True]
    ├── South-Bangalore (Leaf) [is_group=False]
    └── South-Chennai (Leaf) [is_group=False]
```

---

### Budget Table
**Purpose:** Financial planning and budget allocation tracking

| Field | Type | Constraints | Notes |
|-------|------|-----------|-------|
| id | INTEGER | PRIMARY KEY | Auto-generated |
| series | VARCHAR(200) | NOT NULL | Budget identifier/name |
| budget_against | VARCHAR(200) | CHOICES | [cost_center, project] - dimension for budget |
| fiscal_year_from | VARCHAR(20) | CHOICES | [2025-2026] (hard-coded for now) |
| fiscal_year_to | VARCHAR(20) | CHOICES | [2025-2026] (hard-coded for now) |
| company_id | INTEGER | FK → Company (NOT NULL) | Which company |
| distribution | VARCHAR(200) | CHOICES | [monthly, quarterly, half-yearly, yearly] - breakdown frequency |
| cost_center_id | INTEGER | FK → CostCenter (NOT NULL) | Non-group cost center only |
| account_id | INTEGER | FK → Account (NOT NULL) | Which GL account to budget |
| budget_amount | DECIMAL(15,2) | NOT NULL | Total budget amount |

**Foreign Key Constraints:**
- cost_center must have is_group=False and is_disabled=False

**Example:**
```
Budget Series: "FY2025 Marketing Spend"
├── Department: Marketing (cost_center)
├── Account: Advertising Expense
├── Period: FY 2025-2026
├── Distribution: Monthly
└── Total Budget: 500,000 USD
    (12 months × 41,667 USD/month)
```

---

### CostCenterAllocation Table
**Purpose:** Link cost centers to companies for multi-company tracking

| Field | Type | Constraints | Notes |
|-------|------|-----------|-------|
| id | INTEGER | PRIMARY KEY | Auto-generated |
| cost_center_id | INTEGER | FK → CostCenter (NOT NULL) | Reference to cost center |
| company_id | INTEGER | FK → Company (NOT NULL) | Assigned to which company |
| valid_from | DATE | NOT NULL | When allocation becomes active |

**Unique Constraint:** (cost_center_id, company_id) - prevent duplicate allocations

---

## 5. TRANSACTION RECORDING

### JournalEntry Table
**Purpose:** Record all financial transactions using double-entry bookkeeping

| Field | Type | Constraints | Notes |
|-------|------|-----------|-------|
| id | INTEGER | PRIMARY KEY | Auto-generated |
| entry_number | VARCHAR(50) | UNIQUE, NOT NULL | Auto-generated (JE00001, JE00002...) |
| date | DATE | NOT NULL | Posting date |
| account_id | INTEGER | FK → Account (NOT NULL) | Which GL account |
| debit_amount | DECIMAL(15,2) | DEFAULT 0.00 | Amount on debit side |
| credit_amount | DECIMAL(15,2) | DEFAULT 0.00 | Amount on credit side |
| description | TEXT | BLANK OK | Narrative explanation |
| company_id | INTEGER | FK → Company (NULL) | Which company (optional but recommended) |
| created_at | DATETIME | AUTO_NOW_ADD | Creation timestamp |
| updated_at | DATETIME | AUTO_NOW | Last update timestamp |
| created_by_id | INTEGER | FK → auth_user (NULL) | User who created entry |

**Business Rules:**
- Either debit_amount OR credit_amount should be > 0 (not both zero)
- entry_number auto-generated on save if not provided
- For every debit entry, there should be a corresponding credit entry

**Accounting Principle:**
```
Double Entry Bookkeeping:
If cash received: DR Cash / CR Income (both entries need to exist somewhere)
If expense paid: DR Expense / CR Cash (or Bank)

Each JournalEntry record = ONE side of the transaction
```

**Example:**
```
Entry JE00001: Receipt from customer
├── DR Bank (1001): 10,000
└── CR Sales Revenue (4001): 10,000

Entry JE00002: Office rent paid
├── DR Rent Expense (5001): 5,000
└── CR Bank (1001): 5,000
```

---

### Invoice Table
**Purpose:** Manage invoices from suppliers (purchase) and to customers (sales)

| Field | Type | Constraints | Notes |
|-------|------|-----------|-------|
| id | INTEGER | PRIMARY KEY | Auto-generated |
| invoice_id | VARCHAR(50) | UNIQUE, NOT NULL | System-generated unique ID |
| invoice_number | VARCHAR(50) | NOT NULL | Supplier/Customer invoice number |
| date | DATE | NOT NULL | Invoice issue date |
| supplier_id | INTEGER | FK → Supplier (NULL) | If purchase invoice |
| supplier_vat | VARCHAR(50) | BLANK OK | Supplier's GST/VAT number (auto-populated) |
| customer_id | INTEGER | FK → Customer (NULL) | If sales invoice |
| customer_vat | VARCHAR(50) | BLANK OK | Customer's GST/VAT number (auto-populated) |
| amount_before_vat | DECIMAL(15,2) | NOT NULL | Subtotal before tax |
| total_vat | DECIMAL(15,2) | NOT NULL | Total VAT/GST amount |
| total_amount | DECIMAL(15,2) | NOT NULL | Final amount = amount_before_vat + total_vat (auto-calculated) |
| qr_code_present | BOOLEAN | DEFAULT False | Whether invoice has QR code |
| qr_code_data | TEXT | BLANK OK | Extracted QR code data |
| status | VARCHAR(20) | CHOICES, DEFAULT 'draft' | [draft, sent, paid, cancelled, return] |
| company_id | INTEGER | FK → Company (NULL) | Which company |
| created_at | DATETIME | AUTO_NOW_ADD | Creation timestamp |
| updated_at | DATETIME | AUTO_NOW | Last update timestamp |
| created_by_id | INTEGER | FK → auth_user (NULL) | User who created invoice |

**Auto-populated Fields on Save:**
- supplier_vat ← supplier.gstin_uin (if blank)
- customer_vat ← customer.gstin_uin (if blank)
- total_amount = amount_before_vat + total_vat (if blank)

**Status Workflow:**
```
Draft → Sent → Paid → Closed
        ↓
      Cancelled
      
or
Returned → ...
```

**AI/OCR Processing:**
- Can be uploaded as PDF/Image
- Google Vision API extracts data
- OpenAI GPT parses invoice details
- Populates all fields automatically

---

## 6. PARTIES (SUPPLIERS & CUSTOMERS)

### Supplier Table
**Purpose:** Manage vendor/supplier master data

| Field | Type | Constraints | Notes |
|-------|------|-----------|-------|
| id | INTEGER | PRIMARY KEY | Auto-generated |
| name | VARCHAR(200) | NOT NULL, UNIQUE per company | Supplier legal name |
| gstin_uin | VARCHAR(30) | BLANK OK | GST/UIN registration number |
| supplier_type | VARCHAR(20) | CHOICES, DEFAULT 'company' | [company, individual, partnership] |
| gst_category | VARCHAR(40) | CHOICES, DEFAULT 'unregistered' | [registered, unregistered, sez, overseas, etc.] |
| contact_first_name | VARCHAR(100) | BLANK OK | Primary contact first name |
| contact_last_name | VARCHAR(100) | BLANK OK | Primary contact last name |
| contact_email | VARCHAR(254) | BLANK OK | Contact email |
| contact_mobile | VARCHAR(30) | BLANK OK | Contact phone |
| preferred_billing | BOOLEAN | DEFAULT False | Default billing address |
| preferred_shipping | BOOLEAN | DEFAULT False | Default shipping address |
| address_line1 | VARCHAR(255) | BLANK OK | Street address |
| address_line2 | VARCHAR(255) | BLANK OK | Additional address line |
| city | VARCHAR(120) | BLANK OK | City/Town |
| postal_code | VARCHAR(20) | BLANK OK | ZIP/PIN code |
| state | VARCHAR(100) | BLANK OK | State/Province |
| country | VARCHAR(100) | DEFAULT 'Pakistan', BLANK OK | Country |
| company_id | INTEGER | FK → Company (NULL) | Optional: link to company |
| created_at | DATETIME | AUTO_NOW_ADD | Creation timestamp |
| updated_at | DATETIME | AUTO_NOW | Last update timestamp |
| created_by_id | INTEGER | FK → auth_user (NULL) | User who created record |

**Unique Constraint:** (company_id, name) - prevent duplicate supplier names per company

**GST Categories (India-specific):**
- Registered Regular
- Registered Composition (smaller businesses)
- Unregistered (small/informal)
- SEZ (Special Economic Zone)
- Overseas (foreign suppliers)
- Deemed Export
- UIN Holders
- Tax Deductor
- Tax Collector
- Input Service Distributor

---

### Customer Table
**Purpose:** Manage customer/buyer master data (identical structure to Supplier)

| Field | Type | Constraints | Notes |
|-------|------|-----------|-------|
| id | INTEGER | PRIMARY KEY | Auto-generated |
| name | VARCHAR(200) | NOT NULL, UNIQUE per company | Customer legal name |
| gstin_uin | VARCHAR(30) | BLANK OK | GST/UIN registration number |
| customer_type | VARCHAR(20) | CHOICES, DEFAULT 'company' | [company, individual, partnership] |
| gst_category | VARCHAR(40) | CHOICES, DEFAULT 'unregistered' | Same as supplier |
| contact_first_name | VARCHAR(100) | BLANK OK | Primary contact first name |
| contact_last_name | VARCHAR(100) | BLANK OK | Primary contact last name |
| contact_email | VARCHAR(254) | BLANK OK | Contact email |
| contact_mobile | VARCHAR(30) | BLANK OK | Contact phone |
| preferred_billing | BOOLEAN | DEFAULT False | Default billing address |
| preferred_shipping | BOOLEAN | DEFAULT False | Default shipping address |
| address_line1 | VARCHAR(255) | BLANK OK | Street address |
| address_line2 | VARCHAR(255) | BLANK OK | Additional address line |
| city | VARCHAR(120) | BLANK OK | City/Town |
| postal_code | VARCHAR(20) | BLANK OK | ZIP/PIN code |
| state | VARCHAR(100) | BLANK OK | State/Province |
| country | VARCHAR(100) | DEFAULT 'Pakistan', BLANK OK | Country |
| company_id | INTEGER | FK → Company (NULL) | Optional: link to company |
| created_at | DATETIME | AUTO_NOW_ADD | Creation timestamp |
| updated_at | DATETIME | AUTO_NOW | Last update timestamp |
| created_by_id | INTEGER | FK → auth_user (NULL) | User who created record |

**Unique Constraint:** (company_id, name) - prevent duplicate customer names per company

---

## 7. TAX MANAGEMENT

### TaxItemTemplate Table
**Purpose:** Define tax rates and treatments for tax line items

| Field | Type | Constraints | Notes |
|-------|------|-----------|-------|
| id | INTEGER | PRIMARY KEY | Auto-generated |
| title | VARCHAR(150) | NOT NULL | Template name (e.g., "Standard GST 18%") |
| company_id | INTEGER | FK → Company (NOT NULL) | Which company |
| gst_rate | DECIMAL(5,2) | NOT NULL | Tax percentage (e.g., 5, 12, 18, 28) |
| gst_treatment | VARCHAR(100) | CHOICES | [taxable, nil_rated, exempted, non_gst] |
| disabled | BOOLEAN | DEFAULT False | Soft delete flag |

**GST Treatment Types:**
- **Taxable:** Standard GST applies
- **Nil-Rated:** 0% GST (e.g., basic food items)
- **Exempted:** No GST but still tracked
- **Non-GST:** Not applicable (pre-GST goods)

---

### TaxCategory Table
**Purpose:** Grouping of tax rules (meta level)

| Field | Type | Constraints | Notes |
|-------|------|-----------|-------|
| id | INTEGER | PRIMARY KEY | Auto-generated |
| title | VARCHAR(150) | NULL, BLANK OK | Category name |

---

### TaxRule Table
**Purpose:** Define WHEN and HOW to apply tax based on conditions

| Field | Type | Constraints | Notes |
|-------|------|-----------|-------|
| id | INTEGER | PRIMARY KEY | Auto-generated |
| tax_type | VARCHAR(100) | CHOICES | [sales, purchase] - direction of transaction |
| sales_tax_template_id | INTEGER | FK → TaxItemTemplate (NOT NULL) | Which tax rate to apply |
| shopping_cart_use | BOOLEAN | DEFAULT False | Use in shopping cart mode |
| customer_id | INTEGER | FK → Customer (NOT NULL) | For which customer (purchase side) |
| customer_group | VARCHAR(100) | BLANK OK | Customer group/segment |
| item | VARCHAR(200) | BLANK OK | Specific item/product |
| item_group | VARCHAR(100) | BLANK OK | Item category |
| billing_city | VARCHAR(100) | BLANK OK | If delivery in this city |
| shipping_city | VARCHAR(100) | BLANK OK | If shipment from this city |
| billing_county | VARCHAR(100) | BLANK OK | If delivery in this county |
| shipping_county | VARCHAR(100) | BLANK OK | If shipment from this county |
| billing_state | VARCHAR(100) | BLANK OK | If delivery in this state |
| shipping_state | VARCHAR(100) | BLANK OK | If shipment from this state |
| billing_zipcode | VARCHAR(20) | BLANK OK | If delivery in this postal code |
| shipping_zipcode | VARCHAR(20) | BLANK OK | If shipment from this postal code |
| billing_country | VARCHAR(100) | BLANK OK | If delivery in this country |
| shipping_country | VARCHAR(100) | BLANK OK | If shipment from this country |
| tax_category_id | INTEGER | FK → TaxCategory (NOT NULL) | Category |
| from_date | DATE | NOT NULL | When rule becomes effective |
| to_date | DATE | NOT NULL | When rule expires |
| priority | INTEGER | DEFAULT 0 | Higher priority = applies first |
| company_id | INTEGER | FK → Company (NOT NULL) | Which company |

**Example Rule:**
```
Tax Rule 1:
├── For: Sales (tax_type=sales)
├── Apply: 18% GST (tax_template)
├── To: Customers in 'Electronics' group
├── In State: Maharashtra
├── Effective: 2025-01-01 to 2025-12-31
├── Priority: 10
└── If multiple rules match: Highest priority wins
```

---

### TaxWithholdingCategory Table
**Purpose:** Configure Tax Deducted at Source (TDS) / Tax Withheld (WHT) rules

| Field | Type | Constraints | Notes |
|-------|------|-----------|-------|
| id | INTEGER | PRIMARY KEY | Auto-generated |
| name | VARCHAR(255) | NOT NULL | Category name (e.g., "TDS on Contractors") |
| category_name | VARCHAR(255) | NULL | Alternate name |
| deduct_tax_on_basis | VARCHAR(50) | CHOICES, DEFAULT 'Net Total' | [Net Total, Gross Total] - what to calculate on |
| round_off_tax_amount | BOOLEAN | DEFAULT False | Round tax to nearest integer |
| section | VARCHAR(100) | BLANK OK | Tax code section (e.g., "194C", "194H") |
| only_deduct_on_excess | BOOLEAN | DEFAULT False | Only if amount exceeds threshold |
| entity | VARCHAR(50) | CHOICES, DEFAULT 'Company' | [Company, Individual, No PAN/Invalid PAN] - who pays |
| disable_cumulative_threshold | BOOLEAN | DEFAULT False | Disable yearly cumulative check |
| disable_transaction_threshold | BOOLEAN | DEFAULT False | Disable per-transaction check |

**India Tax Sections:**
- **194C:** Contractors, plumber, electrician, etc.
- **194H:** Commission/brokerage
- **194J:** Professional fees, consultation
- **194O:** E-commerce transactions

---

### TaxWithholdingRate Table
**Purpose:** Define tax rates and thresholds for withholding

| Field | Type | Constraints | Notes |
|-------|------|-----------|-------|
| id | INTEGER | PRIMARY KEY | Auto-generated |
| category_id | INTEGER | FK → TaxWithholdingCategory (NOT NULL) | Which category |
| from_date | DATE | NOT NULL | Effective from date |
| to_date | DATE | NOT NULL | Effective to date |
| tax_withholding_group | VARCHAR(100) | BLANK OK | Group identifier |
| tax_withholding_rate | DECIMAL(6,3) | DEFAULT 0.000 | Rate percentage (e.g., 2.0%, 5.0%) |
| cumulative_threshold | DECIMAL(12,2) | DEFAULT 0.00 | Yearly total before withholding triggers |
| transaction_threshold | DECIMAL(12,2) | DEFAULT 0.00 | Per-transaction amount before withholding triggers |

**Example:**
```
Rate Entry:
├── Category: "TDS on Contractors" (194C)
├── Rate: 1.0%
├── Cumulative Threshold: 30,000 (withhold only if yearly total > 30,000)
├── Transaction Threshold: 10,000 (withhold only if single bill > 10,000)
├── Valid: 2025-04-01 to 2026-03-31 (Indian FY)
└── Logic: If contractor gets multiple bills totaling 50,000,
           AND each bill is > 10,000,
           THEN withhold 1% from each bill
```

---

### TaxCategoryAccount Table
**Purpose:** Map tax categories to GL accounts for posting

| Field | Type | Constraints | Notes |
|-------|------|-----------|-------|
| id | INTEGER | PRIMARY KEY | Auto-generated |
| category_id | INTEGER | FK → TaxWithholdingCategory (NOT NULL) | Which tax category |
| company_id | INTEGER | FK → Company (NOT NULL) | In which company |
| account_id | INTEGER | FK → Account (NOT NULL) | Where to post the tax liability |

**Example:**
```
Mapping:
├── Category: "TDS on Contractors"
├── Company: "ABC Corp"
├── Account: "TDS Payable" (GL 2105)
└── When TDS is withheld: CR Account 2105 (TDS Payable)
                          DR Account 5001 (Contractor Expense reduced by TDS)
```

---

### DeductionCertificate Table
**Purpose:** Generate TDS/WHT deduction certificates for suppliers

| Field | Type | Constraints | Notes |
|-------|------|-----------|-------|
| id | INTEGER | PRIMARY KEY | Auto-generated |
| tax_withholding_category_id | INTEGER | FK → TaxWithholdingCategory (NOT NULL) | Which tax category |
| company_id | INTEGER | FK → Company (NOT NULL) | Issuing company |
| supplier_id | INTEGER | FK → Supplier (NOT NULL) | For which supplier |
| fiscal_year | VARCHAR(20) | CHOICES | [2025-2026] (hard-coded) |
| certificate_number | VARCHAR(100) | NOT NULL | Unique certificate ID |
| pan_number | VARCHAR(20) | BLANK OK | Supplier's PAN (for India) |
| valid_from | DATE | NOT NULL | Certificate start date |
| valid_to | DATE | NOT NULL | Certificate end date |
| rate_of_tdas | DECIMAL(6,3) | DEFAULT 0.000 | TDS rate applied |
| certificate_limit | DECIMAL(12,2) | DEFAULT 0.00 | Maximum amount covered |

**Purpose:** Official document showing how much tax was deducted from supplier payments

---

## 8. ACCOUNTING DIMENSIONS

### AccountingDimension Table
**Purpose:** Custom dimensions for dimensional analysis beyond cost centers

| Field | Type | Constraints | Notes |
|-------|------|-----------|-------|
| id | INTEGER | PRIMARY KEY | Auto-generated |
| name | VARCHAR(150) | NOT NULL | Dimension name (e.g., "Department", "Project", "Region") |
| created_at | DATETIME | AUTO_NOW_ADD | Creation timestamp |
| updated_at | DATETIME | AUTO_NOW | Last update timestamp |

**Note:** Currently minimal usage - potential for expansion for custom dimensional analysis

---

## 9. RELATIONSHIPS SUMMARY

```
┌─────────────────────────────────────────────────────────────┐
│                        COMPANY (Hub)                        │
└─────────────────────────────────────────────────────────────┘
                              │
         ┌────────────────────┼────────────────────┐
         │                    │                    │
    ┌────▼─────┐        ┌────▼────────┐    ┌────▼──────┐
    │ ACCOUNTS  │        │ COST CENTERS│    │ BUDGETS   │
    └────┬─────┘        └────┬────────┘    └───────────┘
         │                   │
         │              ┌────▼──────────┐
         │              │COST CENTER    │
         │              │ALLOCATION     │
         │              └───────────────┘
         │
    ┌────▼──────────────┐
    │JOURNAL ENTRIES    │
    │(Double-entry)     │
    └───────────────────┘


┌──────────────────┐         ┌──────────────────┐
│   SUPPLIERS      │         │   CUSTOMERS      │
└────────┬─────────┘         └────────┬─────────┘
         │                            │
         └────────────┬───────────────┘
                      │
                  ┌───▼────────┐
                  │  INVOICES  │
                  └────────────┘


┌────────────────────────────────────────────────────────┐
│          TAX MANAGEMENT SYSTEM                        │
│                                                      │
│  ┌──────────────────┐                               │
│  │ TaxItemTemplate  │ (Rate definitions)            │
│  └────────┬─────────┘                               │
│           │                                         │
│  ┌────────▼──────────────┐                         │
│  │    TaxRule            │ (When to apply)         │
│  │  TaxCategory          │                         │
│  └───────────────────────┘                         │
│                                                      │
│  ┌──────────────────────┐                          │
│  │ TaxWithholding       │ (TDS/WHT Config)         │
│  │ ├─ Rate             │                           │
│  │ ├─ CategoryAccount   │                          │
│  │ └─ Certificate       │                          │
│  └──────────────────────┘                          │
└────────────────────────────────────────────────────────┘
```

---

## 10. KEY CONSTRAINTS & RULES

### Unique Constraints
```
Account:                (company_id, account_number)
Supplier:               (company_id, name)
Customer:               (company_id, name)
CostCenter:             (company_id, name)
CostCenterAllocation:   (cost_center_id, company_id)
Invoice:                (invoice_id) globally
JournalEntry:           (entry_number) globally
TaxCategoryAccount:     (unique mapping per company-category-account)
```

### Foreign Key Constraints
```
All FK references require the parent record to exist.
ON DELETE CASCADE: Child records deleted when parent deleted
ON DELETE PROTECT: Parent can't be deleted if children exist
ON DELETE SET_NULL: Parent deleted, FK set to NULL
```

### Business Logic Rules

**1. Journal Entry:**
- Either debit_amount OR credit_amount > 0 (not both zero)
- entry_number auto-generated as JE00001, JE00002, etc.
- For balanced accounting: total debits = total credits across all entries

**2. Invoice:**
- total_amount = amount_before_vat + total_vat (auto-calculated on save)
- supplier_vat auto-populated from supplier.gstin_uin if blank
- customer_vat auto-populated from customer.gstin_uin if blank
- Status transitions: Draft → Sent → Paid (or Cancelled)

**3. Budget:**
- cost_center must have is_group=False and is_disabled=False
- amount is distributed based on 'distribution' field (monthly, quarterly, etc.)

**4. Account:**
- If is_group=True: Can't record transactions directly (parent account only)
- If is_group=False: Can record transactions (leaf account)

**5. Cost Center:**
- If is_group=True: Can't allocate transactions (parent only)
- If is_group=False: Can allocate transactions (leaf only)

**6. Tax Withholding:**
- Cumulative threshold: checks yearly total across all transactions
- Transaction threshold: checks individual transaction amount
- If only_deduct_on_excess=True: withhold only amount exceeding threshold

**7. Multi-Company:**
- Most records linked to company_id
- Supplier/Customer names unique per company (can have same name in different companies)
- Account numbers unique per company (can have same number in different companies)

---

## Field Type Reference

| Django Type | SQLite Type | Example |
|-------------|-------------|---------|
| CharField | VARCHAR(n) | VARCHAR(200) |
| TextField | TEXT | Full descriptions |
| DateField | DATE | 2025-12-31 |
| DateTimeField | DATETIME | 2025-12-31 14:30:00 |
| DecimalField(15,2) | DECIMAL(15,2) | 1234567.89 |
| BooleanField | BOOLEAN | True/False |
| ForeignKey | INTEGER | References id of other table |
| OneToOneField | INTEGER | Unique FK reference |
| Auto-increment | INTEGER PRIMARY KEY | Auto-generated 1,2,3... |

---

## Sample Transactions

### Example 1: Purchase Invoice + Journal Entry

```
Step 1: Create Invoice
├── Invoice ID: INV-SUP-001
├── Supplier: "XYZ Supplies"
├── Amount Before VAT: 10,000
├── Total VAT (18%): 1,800
└── Total Amount: 11,800

Step 2: Auto-generated Journal Entries
├── JE00001: DR Expense Account (5001) / CR Payable Account (2001)
│           Debit: 11,800 / Credit: 0
└── JE00002: DR Payable Account (2001) / CR Bank Account (1001)
            Debit: 0 / Credit: 11,800
            (When payment made)
```

### Example 2: Tax Withholding (TDS)

```
Step 1: Bill from Contractor
├── Amount: 50,000
├── TDS Category: 194C (1% rate)
└── Cumulative this FY: 50,000 (> threshold of 30,000)

Step 2: System Calculates TDS
├── TDS Amount: 50,000 × 1% = 500
├── Amount Payable to Contractor: 49,500
└── TDS Payable to Government: 500

Step 3: Journal Entries Generated
├── JE0001: DR Contractor Expense (5001): 50,000
│           CR Contractor Payable (2001): 49,500
│           CR TDS Payable (2105): 500
└── Certificate issued showing 500 TDS deducted
```

### Example 3: Multi-Company Budget Tracking

```
Company: "ABC Corporation"
└── Departments (Cost Centers)
    ├── Sales (CC001)
    └── Marketing (CC002)
        └── Budget FY2025
            ├── CC002-Marketing
            ├── Account: Advertising Expense (5005)
            ├── Amount: 100,000 USD
            └── Distribution: Monthly (8,333/month)

When expense recorded:
├── Actual Expense: 8,500 (higher than budget)
├── Variance: 167 over budget
└── Reports show variance analysis
```

---

## Quick Reference: Most Used Tables

| Table | Purpose | Primary Use |
|-------|---------|------------|
| Company | Multi-entity setup | Master company data |
| Account | GL account master | Recording all transactions |
| JournalEntry | Transaction recording | Daily bookkeeping |
| Invoice | Purchasing/Sales | Vendor/Customer billing |
| Supplier | Vendor master | Procurement |
| Customer | Customer master | Sales/receivables |
| Budget | Financial planning | Budget vs actual |
| CostCenter | Expense categorization | Departmental analysis |
| TaxItemTemplate | Tax rate definition | GST/VAT rates |
| TaxWithholding* | TDS/WHT processing | Tax compliance |

---

**Last Updated:** January 22, 2026
**Database:** SQLite (db.sqlite3)
**Django ORM:** Models defined in finance/models.py
