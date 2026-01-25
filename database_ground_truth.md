# Database Ground Truth

**Generated:** 2026-01-25 22:19:35

This document contains all data from the SQLite database.
Use this as ground truth when testing chatbot queries.

---

## Table of Contents

### Core Business

- [Companies](#companies) (5 records)
- [Accounts](#accounts) (24 records)
- [Invoices](#invoices) (10 records)
- [Journal Entries](#journal-entries) (20 records)
- [Suppliers](#suppliers) (5 records)
- [Customers](#customers) (4 records)

### Planning & Budgeting

- [Budgets](#budgets) (3 records)
- [Cost Centers](#cost-centers) (12 records)
- [Cost Center Allocations](#cost-center-allocations) (3 records)
- [Accounting Dimensions](#accounting-dimensions) (3 records)

### Tax Configuration

- [Tax Item Templates](#tax-item-templates) (4 records)
- [Tax Categorys](#tax-categorys) (4 records)
- [Tax Rules](#tax-rules) (3 records)
- [Tax Withholding Categorys](#tax-withholding-categorys) (4 records)
- [Tax Withholding Rates](#tax-withholding-rates) (0 records)
- [Category Account Mappings](#category-account-mappings) (0 records)
- [Deduction Certificates](#deduction-certificates) (0 records)

### Banking

- [Bank Account Types](#bank-account-types) (0 records)
- [Bank Account Subtypes](#bank-account-subtypes) (0 records)
- [Bank Accounts](#bank-accounts) (0 records)

### Users

- [User Profiles](#user-profiles) (3 records)

---


# Core Business


## Companies

**Table:** `finance_company`  
**Total Records:** 5

### Record 1

- **Id** (`id`): 25
- **Company Name** (`name`): Retail Solutions Inc
- **Abbreviation** (`abbreviation`): RSI
- **Country** (`country`): USA
- **Date Of Establishment** (`date_of_establishment`): 2015-06-01
- **Default Currency** (`default_currency`): USD
- **Tax Id** (`tax_id`): TAX-USA-004
- **Default Letter Head** (`default_letter_head`): _empty_
- **Domain** (`domain`): _empty_
- **Parent Company** (`parent_company`): _empty_
- **Is Parent Company (Group)** (`is_parent_company`): ❌ No
- **Registration Details** (`registration_details`): _empty_
- **Account Number** (`account_number`): _empty_
- **Disable** (`is_disabled`): ❌ No
- **Is Group** (`is_group`): ❌ No
- **Company Type** (`company_type`): regular
- **Account Type** (`account_type`): _empty_
- **Tax Rate** (`tax_rate`): 0.00
- **Balance Must Be** (`balance_must_be`): both
- **Created At** (`created_at`): 2026-01-22 16:48:47
- **Updated At** (`updated_at`): 2026-01-22 16:48:47
- **Created By** (`created_by`): 1 (admin)

### Record 2

- **Id** (`id`): 24
- **Company Name** (`name`): FinTech Services LLC
- **Abbreviation** (`abbreviation`): FTS
- **Country** (`country`): USA
- **Date Of Establishment** (`date_of_establishment`): 2015-06-01
- **Default Currency** (`default_currency`): USD
- **Tax Id** (`tax_id`): TAX-USA-003
- **Default Letter Head** (`default_letter_head`): _empty_
- **Domain** (`domain`): _empty_
- **Parent Company** (`parent_company`): _empty_
- **Is Parent Company (Group)** (`is_parent_company`): ❌ No
- **Registration Details** (`registration_details`): _empty_
- **Account Number** (`account_number`): _empty_
- **Disable** (`is_disabled`): ❌ No
- **Is Group** (`is_group`): ❌ No
- **Company Type** (`company_type`): regular
- **Account Type** (`account_type`): _empty_
- **Tax Rate** (`tax_rate`): 0.00
- **Balance Must Be** (`balance_must_be`): both
- **Created At** (`created_at`): 2026-01-22 16:48:47
- **Updated At** (`updated_at`): 2026-01-22 16:48:47
- **Created By** (`created_by`): 1 (admin)

### Record 3

- **Id** (`id`): 23
- **Company Name** (`name`): TechCorp India Pvt Ltd
- **Abbreviation** (`abbreviation`): TCS-IND
- **Country** (`country`): India
- **Date Of Establishment** (`date_of_establishment`): 2015-06-01
- **Default Currency** (`default_currency`): INR
- **Tax Id** (`tax_id`): GSTIN-IND-001
- **Default Letter Head** (`default_letter_head`): _empty_
- **Domain** (`domain`): _empty_
- **Parent Company** (`parent_company`): 21 (Global Corp International)
- **Is Parent Company (Group)** (`is_parent_company`): ❌ No
- **Registration Details** (`registration_details`): _empty_
- **Account Number** (`account_number`): _empty_
- **Disable** (`is_disabled`): ❌ No
- **Is Group** (`is_group`): ❌ No
- **Company Type** (`company_type`): subsidiary
- **Account Type** (`account_type`): _empty_
- **Tax Rate** (`tax_rate`): 0.00
- **Balance Must Be** (`balance_must_be`): both
- **Created At** (`created_at`): 2026-01-22 16:48:47
- **Updated At** (`updated_at`): 2026-01-22 16:48:47
- **Created By** (`created_by`): 1 (admin)

### Record 4

- **Id** (`id`): 22
- **Company Name** (`name`): TechCorp Solutions USA
- **Abbreviation** (`abbreviation`): TCS-USA
- **Country** (`country`): USA
- **Date Of Establishment** (`date_of_establishment`): 2015-06-01
- **Default Currency** (`default_currency`): USD
- **Tax Id** (`tax_id`): TAX-USA-002
- **Default Letter Head** (`default_letter_head`): _empty_
- **Domain** (`domain`): _empty_
- **Parent Company** (`parent_company`): 21 (Global Corp International)
- **Is Parent Company (Group)** (`is_parent_company`): ❌ No
- **Registration Details** (`registration_details`): _empty_
- **Account Number** (`account_number`): _empty_
- **Disable** (`is_disabled`): ❌ No
- **Is Group** (`is_group`): ❌ No
- **Company Type** (`company_type`): subsidiary
- **Account Type** (`account_type`): _empty_
- **Tax Rate** (`tax_rate`): 0.00
- **Balance Must Be** (`balance_must_be`): both
- **Created At** (`created_at`): 2026-01-22 16:48:47
- **Updated At** (`updated_at`): 2026-01-22 16:48:47
- **Created By** (`created_by`): 1 (admin)

### Record 5

- **Id** (`id`): 21
- **Company Name** (`name`): Global Corp International
- **Abbreviation** (`abbreviation`): GCI
- **Country** (`country`): USA
- **Date Of Establishment** (`date_of_establishment`): 2010-01-15
- **Default Currency** (`default_currency`): USD
- **Tax Id** (`tax_id`): TAX-USA-001
- **Default Letter Head** (`default_letter_head`): _empty_
- **Domain** (`domain`): _empty_
- **Parent Company** (`parent_company`): _empty_
- **Is Parent Company (Group)** (`is_parent_company`): ✅ Yes
- **Registration Details** (`registration_details`): _empty_
- **Account Number** (`account_number`): _empty_
- **Disable** (`is_disabled`): ❌ No
- **Is Group** (`is_group`): ✅ Yes
- **Company Type** (`company_type`): holding
- **Account Type** (`account_type`): _empty_
- **Tax Rate** (`tax_rate`): 0.00
- **Balance Must Be** (`balance_must_be`): both
- **Created At** (`created_at`): 2026-01-22 16:48:47
- **Updated At** (`updated_at`): 2026-01-22 16:48:47
- **Created By** (`created_by`): 1 (admin)

---


## Accounts

**Table:** `finance_account`  
**Total Records:** 24

### Record 1

- **Id** (`id`): 96
- **Account Name** (`name`): Salaries & Wages
- **Account Number** (`account_number`): 235100
- **Disable** (`is_disabled`): ❌ No
- **Is Group** (`is_group`): ❌ No
- **Company** (`company`): 23 (TechCorp India Pvt Ltd)
- **Currency** (`currency`): USD
- **Parent Account** (`parent_account`): _empty_
- **Account Type** (`account_type`): expense
- **Tax Rate** (`tax_rate`): 0.00
- **Balance Must Be** (`balance_must_be`): both
- **Created At** (`created_at`): 2026-01-22 16:48:47
- **Updated At** (`updated_at`): 2026-01-22 16:48:47
- **Created By** (`created_by`): 1 (admin)

### Record 2

- **Id** (`id`): 95
- **Account Name** (`name`): Operating Expenses
- **Account Number** (`account_number`): 235001
- **Disable** (`is_disabled`): ❌ No
- **Is Group** (`is_group`): ❌ No
- **Company** (`company`): 23 (TechCorp India Pvt Ltd)
- **Currency** (`currency`): USD
- **Parent Account** (`parent_account`): _empty_
- **Account Type** (`account_type`): expense
- **Tax Rate** (`tax_rate`): 0.00
- **Balance Must Be** (`balance_must_be`): both
- **Created At** (`created_at`): 2026-01-22 16:48:47
- **Updated At** (`updated_at`): 2026-01-22 16:48:47
- **Created By** (`created_by`): 1 (admin)

### Record 3

- **Id** (`id`): 93
- **Account Name** (`name`): Owner's Capital
- **Account Number** (`account_number`): 233001
- **Disable** (`is_disabled`): ❌ No
- **Is Group** (`is_group`): ❌ No
- **Company** (`company`): 23 (TechCorp India Pvt Ltd)
- **Currency** (`currency`): USD
- **Parent Account** (`parent_account`): _empty_
- **Account Type** (`account_type`): equity
- **Tax Rate** (`tax_rate`): 0.00
- **Balance Must Be** (`balance_must_be`): both
- **Created At** (`created_at`): 2026-01-22 16:48:47
- **Updated At** (`updated_at`): 2026-01-22 16:48:47
- **Created By** (`created_by`): 1 (admin)

### Record 4

- **Id** (`id`): 94
- **Account Name** (`name`): Sales Revenue
- **Account Number** (`account_number`): 234001
- **Disable** (`is_disabled`): ❌ No
- **Is Group** (`is_group`): ❌ No
- **Company** (`company`): 23 (TechCorp India Pvt Ltd)
- **Currency** (`currency`): USD
- **Parent Account** (`parent_account`): _empty_
- **Account Type** (`account_type`): income
- **Tax Rate** (`tax_rate`): 0.00
- **Balance Must Be** (`balance_must_be`): both
- **Created At** (`created_at`): 2026-01-22 16:48:47
- **Updated At** (`updated_at`): 2026-01-22 16:48:47
- **Created By** (`created_by`): 1 (admin)

### Record 5

- **Id** (`id`): 92
- **Account Name** (`name`): Accounts Payable
- **Account Number** (`account_number`): 232001
- **Disable** (`is_disabled`): ❌ No
- **Is Group** (`is_group`): ❌ No
- **Company** (`company`): 23 (TechCorp India Pvt Ltd)
- **Currency** (`currency`): USD
- **Parent Account** (`parent_account`): _empty_
- **Account Type** (`account_type`): liability
- **Tax Rate** (`tax_rate`): 0.00
- **Balance Must Be** (`balance_must_be`): both
- **Created At** (`created_at`): 2026-01-22 16:48:47
- **Updated At** (`updated_at`): 2026-01-22 16:48:47
- **Created By** (`created_by`): 1 (admin)

### Record 6

- **Id** (`id`): 89
- **Account Name** (`name`): Cash
- **Account Number** (`account_number`): 231001
- **Disable** (`is_disabled`): ❌ No
- **Is Group** (`is_group`): ❌ No
- **Company** (`company`): 23 (TechCorp India Pvt Ltd)
- **Currency** (`currency`): USD
- **Parent Account** (`parent_account`): _empty_
- **Account Type** (`account_type`): asset
- **Tax Rate** (`tax_rate`): 0.00
- **Balance Must Be** (`balance_must_be`): both
- **Created At** (`created_at`): 2026-01-22 16:48:47
- **Updated At** (`updated_at`): 2026-01-22 16:48:47
- **Created By** (`created_by`): 1 (admin)

### Record 7

- **Id** (`id`): 90
- **Account Name** (`name`): Bank Account
- **Account Number** (`account_number`): 231002
- **Disable** (`is_disabled`): ❌ No
- **Is Group** (`is_group`): ❌ No
- **Company** (`company`): 23 (TechCorp India Pvt Ltd)
- **Currency** (`currency`): USD
- **Parent Account** (`parent_account`): _empty_
- **Account Type** (`account_type`): asset
- **Tax Rate** (`tax_rate`): 0.00
- **Balance Must Be** (`balance_must_be`): both
- **Created At** (`created_at`): 2026-01-22 16:48:47
- **Updated At** (`updated_at`): 2026-01-22 16:48:47
- **Created By** (`created_by`): 1 (admin)

### Record 8

- **Id** (`id`): 91
- **Account Name** (`name`): Accounts Receivable
- **Account Number** (`account_number`): 231100
- **Disable** (`is_disabled`): ❌ No
- **Is Group** (`is_group`): ❌ No
- **Company** (`company`): 23 (TechCorp India Pvt Ltd)
- **Currency** (`currency`): USD
- **Parent Account** (`parent_account`): _empty_
- **Account Type** (`account_type`): asset
- **Tax Rate** (`tax_rate`): 0.00
- **Balance Must Be** (`balance_must_be`): both
- **Created At** (`created_at`): 2026-01-22 16:48:47
- **Updated At** (`updated_at`): 2026-01-22 16:48:47
- **Created By** (`created_by`): 1 (admin)

### Record 9

- **Id** (`id`): 88
- **Account Name** (`name`): Salaries & Wages
- **Account Number** (`account_number`): 225100
- **Disable** (`is_disabled`): ❌ No
- **Is Group** (`is_group`): ❌ No
- **Company** (`company`): 22 (TechCorp Solutions USA)
- **Currency** (`currency`): USD
- **Parent Account** (`parent_account`): _empty_
- **Account Type** (`account_type`): expense
- **Tax Rate** (`tax_rate`): 0.00
- **Balance Must Be** (`balance_must_be`): both
- **Created At** (`created_at`): 2026-01-22 16:48:47
- **Updated At** (`updated_at`): 2026-01-22 16:48:47
- **Created By** (`created_by`): 1 (admin)

### Record 10

- **Id** (`id`): 87
- **Account Name** (`name`): Operating Expenses
- **Account Number** (`account_number`): 225001
- **Disable** (`is_disabled`): ❌ No
- **Is Group** (`is_group`): ❌ No
- **Company** (`company`): 22 (TechCorp Solutions USA)
- **Currency** (`currency`): USD
- **Parent Account** (`parent_account`): _empty_
- **Account Type** (`account_type`): expense
- **Tax Rate** (`tax_rate`): 0.00
- **Balance Must Be** (`balance_must_be`): both
- **Created At** (`created_at`): 2026-01-22 16:48:47
- **Updated At** (`updated_at`): 2026-01-22 16:48:47
- **Created By** (`created_by`): 1 (admin)

### Record 11

- **Id** (`id`): 86
- **Account Name** (`name`): Sales Revenue
- **Account Number** (`account_number`): 224001
- **Disable** (`is_disabled`): ❌ No
- **Is Group** (`is_group`): ❌ No
- **Company** (`company`): 22 (TechCorp Solutions USA)
- **Currency** (`currency`): USD
- **Parent Account** (`parent_account`): _empty_
- **Account Type** (`account_type`): income
- **Tax Rate** (`tax_rate`): 0.00
- **Balance Must Be** (`balance_must_be`): both
- **Created At** (`created_at`): 2026-01-22 16:48:47
- **Updated At** (`updated_at`): 2026-01-22 16:48:47
- **Created By** (`created_by`): 1 (admin)

### Record 12

- **Id** (`id`): 85
- **Account Name** (`name`): Owner's Capital
- **Account Number** (`account_number`): 223001
- **Disable** (`is_disabled`): ❌ No
- **Is Group** (`is_group`): ❌ No
- **Company** (`company`): 22 (TechCorp Solutions USA)
- **Currency** (`currency`): USD
- **Parent Account** (`parent_account`): _empty_
- **Account Type** (`account_type`): equity
- **Tax Rate** (`tax_rate`): 0.00
- **Balance Must Be** (`balance_must_be`): both
- **Created At** (`created_at`): 2026-01-22 16:48:47
- **Updated At** (`updated_at`): 2026-01-22 16:48:47
- **Created By** (`created_by`): 1 (admin)

### Record 13

- **Id** (`id`): 83
- **Account Name** (`name`): Accounts Receivable
- **Account Number** (`account_number`): 221100
- **Disable** (`is_disabled`): ❌ No
- **Is Group** (`is_group`): ❌ No
- **Company** (`company`): 22 (TechCorp Solutions USA)
- **Currency** (`currency`): USD
- **Parent Account** (`parent_account`): _empty_
- **Account Type** (`account_type`): asset
- **Tax Rate** (`tax_rate`): 0.00
- **Balance Must Be** (`balance_must_be`): both
- **Created At** (`created_at`): 2026-01-22 16:48:47
- **Updated At** (`updated_at`): 2026-01-22 16:48:47
- **Created By** (`created_by`): 1 (admin)

### Record 14

- **Id** (`id`): 84
- **Account Name** (`name`): Accounts Payable
- **Account Number** (`account_number`): 222001
- **Disable** (`is_disabled`): ❌ No
- **Is Group** (`is_group`): ❌ No
- **Company** (`company`): 22 (TechCorp Solutions USA)
- **Currency** (`currency`): USD
- **Parent Account** (`parent_account`): _empty_
- **Account Type** (`account_type`): liability
- **Tax Rate** (`tax_rate`): 0.00
- **Balance Must Be** (`balance_must_be`): both
- **Created At** (`created_at`): 2026-01-22 16:48:47
- **Updated At** (`updated_at`): 2026-01-22 16:48:47
- **Created By** (`created_by`): 1 (admin)

### Record 15

- **Id** (`id`): 82
- **Account Name** (`name`): Bank Account
- **Account Number** (`account_number`): 221002
- **Disable** (`is_disabled`): ❌ No
- **Is Group** (`is_group`): ❌ No
- **Company** (`company`): 22 (TechCorp Solutions USA)
- **Currency** (`currency`): USD
- **Parent Account** (`parent_account`): _empty_
- **Account Type** (`account_type`): asset
- **Tax Rate** (`tax_rate`): 0.00
- **Balance Must Be** (`balance_must_be`): both
- **Created At** (`created_at`): 2026-01-22 16:48:47
- **Updated At** (`updated_at`): 2026-01-22 16:48:47
- **Created By** (`created_by`): 1 (admin)

### Record 16

- **Id** (`id`): 81
- **Account Name** (`name`): Cash
- **Account Number** (`account_number`): 221001
- **Disable** (`is_disabled`): ❌ No
- **Is Group** (`is_group`): ❌ No
- **Company** (`company`): 22 (TechCorp Solutions USA)
- **Currency** (`currency`): USD
- **Parent Account** (`parent_account`): _empty_
- **Account Type** (`account_type`): asset
- **Tax Rate** (`tax_rate`): 0.00
- **Balance Must Be** (`balance_must_be`): both
- **Created At** (`created_at`): 2026-01-22 16:48:47
- **Updated At** (`updated_at`): 2026-01-22 16:48:47
- **Created By** (`created_by`): 1 (admin)

### Record 17

- **Id** (`id`): 80
- **Account Name** (`name`): Salaries & Wages
- **Account Number** (`account_number`): 215100
- **Disable** (`is_disabled`): ❌ No
- **Is Group** (`is_group`): ❌ No
- **Company** (`company`): 21 (Global Corp International)
- **Currency** (`currency`): USD
- **Parent Account** (`parent_account`): _empty_
- **Account Type** (`account_type`): expense
- **Tax Rate** (`tax_rate`): 0.00
- **Balance Must Be** (`balance_must_be`): both
- **Created At** (`created_at`): 2026-01-22 16:48:47
- **Updated At** (`updated_at`): 2026-01-22 16:48:47
- **Created By** (`created_by`): 1 (admin)

### Record 18

- **Id** (`id`): 79
- **Account Name** (`name`): Operating Expenses
- **Account Number** (`account_number`): 215001
- **Disable** (`is_disabled`): ❌ No
- **Is Group** (`is_group`): ❌ No
- **Company** (`company`): 21 (Global Corp International)
- **Currency** (`currency`): USD
- **Parent Account** (`parent_account`): _empty_
- **Account Type** (`account_type`): expense
- **Tax Rate** (`tax_rate`): 0.00
- **Balance Must Be** (`balance_must_be`): both
- **Created At** (`created_at`): 2026-01-22 16:48:47
- **Updated At** (`updated_at`): 2026-01-22 16:48:47
- **Created By** (`created_by`): 1 (admin)

### Record 19

- **Id** (`id`): 78
- **Account Name** (`name`): Sales Revenue
- **Account Number** (`account_number`): 214001
- **Disable** (`is_disabled`): ❌ No
- **Is Group** (`is_group`): ❌ No
- **Company** (`company`): 21 (Global Corp International)
- **Currency** (`currency`): USD
- **Parent Account** (`parent_account`): _empty_
- **Account Type** (`account_type`): income
- **Tax Rate** (`tax_rate`): 0.00
- **Balance Must Be** (`balance_must_be`): both
- **Created At** (`created_at`): 2026-01-22 16:48:47
- **Updated At** (`updated_at`): 2026-01-22 16:48:47
- **Created By** (`created_by`): 1 (admin)

### Record 20

- **Id** (`id`): 77
- **Account Name** (`name`): Owner's Capital
- **Account Number** (`account_number`): 213001
- **Disable** (`is_disabled`): ❌ No
- **Is Group** (`is_group`): ❌ No
- **Company** (`company`): 21 (Global Corp International)
- **Currency** (`currency`): USD
- **Parent Account** (`parent_account`): _empty_
- **Account Type** (`account_type`): equity
- **Tax Rate** (`tax_rate`): 0.00
- **Balance Must Be** (`balance_must_be`): both
- **Created At** (`created_at`): 2026-01-22 16:48:47
- **Updated At** (`updated_at`): 2026-01-22 16:48:47
- **Created By** (`created_by`): 1 (admin)

### Record 21

- **Id** (`id`): 76
- **Account Name** (`name`): Accounts Payable
- **Account Number** (`account_number`): 212001
- **Disable** (`is_disabled`): ❌ No
- **Is Group** (`is_group`): ❌ No
- **Company** (`company`): 21 (Global Corp International)
- **Currency** (`currency`): USD
- **Parent Account** (`parent_account`): _empty_
- **Account Type** (`account_type`): liability
- **Tax Rate** (`tax_rate`): 0.00
- **Balance Must Be** (`balance_must_be`): both
- **Created At** (`created_at`): 2026-01-22 16:48:47
- **Updated At** (`updated_at`): 2026-01-22 16:48:47
- **Created By** (`created_by`): 1 (admin)

### Record 22

- **Id** (`id`): 75
- **Account Name** (`name`): Accounts Receivable
- **Account Number** (`account_number`): 211100
- **Disable** (`is_disabled`): ❌ No
- **Is Group** (`is_group`): ❌ No
- **Company** (`company`): 21 (Global Corp International)
- **Currency** (`currency`): USD
- **Parent Account** (`parent_account`): _empty_
- **Account Type** (`account_type`): asset
- **Tax Rate** (`tax_rate`): 0.00
- **Balance Must Be** (`balance_must_be`): both
- **Created At** (`created_at`): 2026-01-22 16:48:47
- **Updated At** (`updated_at`): 2026-01-22 16:48:47
- **Created By** (`created_by`): 1 (admin)

### Record 23

- **Id** (`id`): 74
- **Account Name** (`name`): Bank Account
- **Account Number** (`account_number`): 211002
- **Disable** (`is_disabled`): ❌ No
- **Is Group** (`is_group`): ❌ No
- **Company** (`company`): 21 (Global Corp International)
- **Currency** (`currency`): USD
- **Parent Account** (`parent_account`): _empty_
- **Account Type** (`account_type`): asset
- **Tax Rate** (`tax_rate`): 0.00
- **Balance Must Be** (`balance_must_be`): both
- **Created At** (`created_at`): 2026-01-22 16:48:47
- **Updated At** (`updated_at`): 2026-01-22 16:48:47
- **Created By** (`created_by`): 1 (admin)

### Record 24

- **Id** (`id`): 73
- **Account Name** (`name`): Cash
- **Account Number** (`account_number`): 211001
- **Disable** (`is_disabled`): ❌ No
- **Is Group** (`is_group`): ❌ No
- **Company** (`company`): 21 (Global Corp International)
- **Currency** (`currency`): USD
- **Parent Account** (`parent_account`): _empty_
- **Account Type** (`account_type`): asset
- **Tax Rate** (`tax_rate`): 0.00
- **Balance Must Be** (`balance_must_be`): both
- **Created At** (`created_at`): 2026-01-22 16:48:47
- **Updated At** (`updated_at`): 2026-01-22 16:48:47
- **Created By** (`created_by`): 1 (admin)

---


## Invoices

**Table:** `finance_invoice`  
**Total Records:** 10

### Record 1

- **Id** (`id`): 20
- **Invoice Id** (`invoice_id`): INV-CUST-2025005
- **Invoice Number** (`invoice_number`): SALE-5/2025
- **Invoice Date** (`date`): 2025-02-07
- **Supplier** (`supplier`): _empty_
- **Supplier Vat** (`supplier_vat`): _empty_
- **Customer** (`customer`): 9 (Acme Corporation)
- **Customer Vat** (`customer_vat`): GSTIN-ACME-001
- **Amount Before Vat** (`amount_before_vat`): 5200.00
- **Total Vat** (`total_vat`): 780.00
- **Total Amount** (`total_amount`): 5980.00
- **Qr Code Present** (`qr_code_present`): ✅ Yes
- **Qr Code Data** (`qr_code_data`): _empty_
- **Status** (`status`): paid
- **Company** (`company`): 21 (Global Corp International)
- **Created At** (`created_at`): 2026-01-22 16:48:47
- **Updated At** (`updated_at`): 2026-01-22 16:48:47
- **Created By** (`created_by`): 1 (admin)

### Record 2

- **Id** (`id`): 19
- **Invoice Id** (`invoice_id`): INV-CUST-2025004
- **Invoice Number** (`invoice_number`): SALE-4/2025
- **Invoice Date** (`date`): 2025-01-31
- **Supplier** (`supplier`): _empty_
- **Supplier Vat** (`supplier_vat`): _empty_
- **Customer** (`customer`): 12 (Small Business LLC)
- **Customer Vat** (`customer_vat`): _empty_
- **Amount Before Vat** (`amount_before_vat`): 4400.00
- **Total Vat** (`total_vat`): 660.00
- **Total Amount** (`total_amount`): 5060.00
- **Qr Code Present** (`qr_code_present`): ✅ Yes
- **Qr Code Data** (`qr_code_data`): _empty_
- **Status** (`status`): sent
- **Company** (`company`): 21 (Global Corp International)
- **Created At** (`created_at`): 2026-01-22 16:48:47
- **Updated At** (`updated_at`): 2026-01-22 16:48:47
- **Created By** (`created_by`): 1 (admin)

### Record 3

- **Id** (`id`): 18
- **Invoice Id** (`invoice_id`): INV-CUST-2025003
- **Invoice Number** (`invoice_number`): SALE-3/2025
- **Invoice Date** (`date`): 2025-01-24
- **Supplier** (`supplier`): _empty_
- **Supplier Vat** (`supplier_vat`): _empty_
- **Customer** (`customer`): 11 (Tech Innovations Pvt Ltd)
- **Customer Vat** (`customer_vat`): GSTIN-TECH-003
- **Amount Before Vat** (`amount_before_vat`): 3600.00
- **Total Vat** (`total_vat`): 540.00
- **Total Amount** (`total_amount`): 4140.00
- **Qr Code Present** (`qr_code_present`): ✅ Yes
- **Qr Code Data** (`qr_code_data`): _empty_
- **Status** (`status`): paid
- **Company** (`company`): 21 (Global Corp International)
- **Created At** (`created_at`): 2026-01-22 16:48:47
- **Updated At** (`updated_at`): 2026-01-22 16:48:47
- **Created By** (`created_by`): 1 (admin)

### Record 4

- **Id** (`id`): 15
- **Invoice Id** (`invoice_id`): INV-SUPP-2025005
- **Invoice Number** (`invoice_number`): SUPP-5/2025
- **Invoice Date** (`date`): 2025-01-21
- **Supplier** (`supplier`): 15 (Office Supplies Pro)
- **Supplier Vat** (`supplier_vat`): _empty_
- **Customer** (`customer`): _empty_
- **Customer Vat** (`customer_vat`): _empty_
- **Amount Before Vat** (`amount_before_vat`): 3000.00
- **Total Vat** (`total_vat`): 450.00
- **Total Amount** (`total_amount`): 3450.00
- **Qr Code Present** (`qr_code_present`): ❌ No
- **Qr Code Data** (`qr_code_data`): _empty_
- **Status** (`status`): sent
- **Company** (`company`): 21 (Global Corp International)
- **Created At** (`created_at`): 2026-01-22 16:48:47
- **Updated At** (`updated_at`): 2026-01-22 16:48:47
- **Created By** (`created_by`): 1 (admin)

### Record 5

- **Id** (`id`): 17
- **Invoice Id** (`invoice_id`): INV-CUST-2025002
- **Invoice Number** (`invoice_number`): SALE-2/2025
- **Invoice Date** (`date`): 2025-01-17
- **Supplier** (`supplier`): _empty_
- **Supplier Vat** (`supplier_vat`): _empty_
- **Customer** (`customer`): 10 (Retail Mart Inc)
- **Customer Vat** (`customer_vat`): GSTIN-RTL-002
- **Amount Before Vat** (`amount_before_vat`): 2800.00
- **Total Vat** (`total_vat`): 420.00
- **Total Amount** (`total_amount`): 3220.00
- **Qr Code Present** (`qr_code_present`): ✅ Yes
- **Qr Code Data** (`qr_code_data`): _empty_
- **Status** (`status`): paid
- **Company** (`company`): 21 (Global Corp International)
- **Created At** (`created_at`): 2026-01-22 16:48:47
- **Updated At** (`updated_at`): 2026-01-22 16:48:47
- **Created By** (`created_by`): 1 (admin)

### Record 6

- **Id** (`id`): 14
- **Invoice Id** (`invoice_id`): INV-SUPP-2025004
- **Invoice Number** (`invoice_number`): SUPP-4/2025
- **Invoice Date** (`date`): 2025-01-16
- **Supplier** (`supplier`): 14 (Global Imports LLC)
- **Supplier Vat** (`supplier_vat`): GSTIN-GLB-004
- **Customer** (`customer`): _empty_
- **Customer Vat** (`customer_vat`): _empty_
- **Amount Before Vat** (`amount_before_vat`): 2500.00
- **Total Vat** (`total_vat`): 375.00
- **Total Amount** (`total_amount`): 2875.00
- **Qr Code Present** (`qr_code_present`): ❌ No
- **Qr Code Data** (`qr_code_data`): _empty_
- **Status** (`status`): draft
- **Company** (`company`): 21 (Global Corp International)
- **Created At** (`created_at`): 2026-01-22 16:48:47
- **Updated At** (`updated_at`): 2026-01-22 16:48:47
- **Created By** (`created_by`): 1 (admin)

### Record 7

- **Id** (`id`): 13
- **Invoice Id** (`invoice_id`): INV-SUPP-2025003
- **Invoice Number** (`invoice_number`): SUPP-3/2025
- **Invoice Date** (`date`): 2025-01-11
- **Supplier** (`supplier`): 13 (Tech Solutions Ltd)
- **Supplier Vat** (`supplier_vat`): GSTIN-TECH-003
- **Customer** (`customer`): _empty_
- **Customer Vat** (`customer_vat`): _empty_
- **Amount Before Vat** (`amount_before_vat`): 2000.00
- **Total Vat** (`total_vat`): 300.00
- **Total Amount** (`total_amount`): 2300.00
- **Qr Code Present** (`qr_code_present`): ❌ No
- **Qr Code Data** (`qr_code_data`): _empty_
- **Status** (`status`): paid
- **Company** (`company`): 21 (Global Corp International)
- **Created At** (`created_at`): 2026-01-22 16:48:47
- **Updated At** (`updated_at`): 2026-01-22 16:48:47
- **Created By** (`created_by`): 1 (admin)

### Record 8

- **Id** (`id`): 16
- **Invoice Id** (`invoice_id`): INV-CUST-2025001
- **Invoice Number** (`invoice_number`): SALE-1/2025
- **Invoice Date** (`date`): 2025-01-10
- **Supplier** (`supplier`): _empty_
- **Supplier Vat** (`supplier_vat`): _empty_
- **Customer** (`customer`): 9 (Acme Corporation)
- **Customer Vat** (`customer_vat`): GSTIN-ACME-001
- **Amount Before Vat** (`amount_before_vat`): 2000.00
- **Total Vat** (`total_vat`): 300.00
- **Total Amount** (`total_amount`): 2300.00
- **Qr Code Present** (`qr_code_present`): ✅ Yes
- **Qr Code Data** (`qr_code_data`): _empty_
- **Status** (`status`): sent
- **Company** (`company`): 21 (Global Corp International)
- **Created At** (`created_at`): 2026-01-22 16:48:47
- **Updated At** (`updated_at`): 2026-01-22 16:48:47
- **Created By** (`created_by`): 1 (admin)

### Record 9

- **Id** (`id`): 12
- **Invoice Id** (`invoice_id`): INV-SUPP-2025002
- **Invoice Number** (`invoice_number`): SUPP-2/2025
- **Invoice Date** (`date`): 2025-01-06
- **Supplier** (`supplier`): 12 (XYZ Trading Co)
- **Supplier Vat** (`supplier_vat`): GSTIN-XYZ-002
- **Customer** (`customer`): _empty_
- **Customer Vat** (`customer_vat`): _empty_
- **Amount Before Vat** (`amount_before_vat`): 1500.00
- **Total Vat** (`total_vat`): 225.00
- **Total Amount** (`total_amount`): 1725.00
- **Qr Code Present** (`qr_code_present`): ❌ No
- **Qr Code Data** (`qr_code_data`): _empty_
- **Status** (`status`): sent
- **Company** (`company`): 21 (Global Corp International)
- **Created At** (`created_at`): 2026-01-22 16:48:47
- **Updated At** (`updated_at`): 2026-01-22 16:48:47
- **Created By** (`created_by`): 1 (admin)

### Record 10

- **Id** (`id`): 11
- **Invoice Id** (`invoice_id`): INV-SUPP-2025001
- **Invoice Number** (`invoice_number`): SUPP-1/2025
- **Invoice Date** (`date`): 2025-01-01
- **Supplier** (`supplier`): 11 (ABC Supplies Inc)
- **Supplier Vat** (`supplier_vat`): GSTIN-ABC-001
- **Customer** (`customer`): _empty_
- **Customer Vat** (`customer_vat`): _empty_
- **Amount Before Vat** (`amount_before_vat`): 1000.00
- **Total Vat** (`total_vat`): 150.00
- **Total Amount** (`total_amount`): 1150.00
- **Qr Code Present** (`qr_code_present`): ❌ No
- **Qr Code Data** (`qr_code_data`): _empty_
- **Status** (`status`): draft
- **Company** (`company`): 21 (Global Corp International)
- **Created At** (`created_at`): 2026-01-22 16:48:47
- **Updated At** (`updated_at`): 2026-01-22 16:48:47
- **Created By** (`created_by`): 1 (admin)

---


## Journal Entries

**Table:** `finance_journalentry`  
**Total Records:** 20

### Record 1

- **Id** (`id`): 40
- **Entry Number** (`entry_number`): JE-GCI-2025110
- **Posting Date** (`date`): 2025-01-28
- **Account** (`account`): 75 (211100 - Accounts Receivable)
- **Debit Amount** (`debit_amount`): 0.00
- **Credit Amount** (`credit_amount`): 1400.00
- **Description** (`description`): Journal entry credit #10
- **Company** (`company`): 21 (Global Corp International)
- **Created At** (`created_at`): 2026-01-22 16:48:47
- **Updated At** (`updated_at`): 2026-01-22 16:48:47
- **Created By** (`created_by`): 1 (admin)

### Record 2

- **Id** (`id`): 39
- **Entry Number** (`entry_number`): JE-GCI-2025010
- **Posting Date** (`date`): 2025-01-28
- **Account** (`account`): 74 (211002 - Bank Account)
- **Debit Amount** (`debit_amount`): 1400.00
- **Credit Amount** (`credit_amount`): 0.00
- **Description** (`description`): Journal entry debit #10
- **Company** (`company`): 21 (Global Corp International)
- **Created At** (`created_at`): 2026-01-22 16:48:47
- **Updated At** (`updated_at`): 2026-01-22 16:48:47
- **Created By** (`created_by`): 1 (admin)

### Record 3

- **Id** (`id`): 38
- **Entry Number** (`entry_number`): JE-TCS-IND-2025109
- **Posting Date** (`date`): 2025-01-25
- **Account** (`account`): 90 (231002 - Bank Account)
- **Debit Amount** (`debit_amount`): 0.00
- **Credit Amount** (`credit_amount`): 1300.00
- **Description** (`description`): Journal entry credit #9
- **Company** (`company`): 23 (TechCorp India Pvt Ltd)
- **Created At** (`created_at`): 2026-01-22 16:48:47
- **Updated At** (`updated_at`): 2026-01-22 16:48:47
- **Created By** (`created_by`): 1 (admin)

### Record 4

- **Id** (`id`): 37
- **Entry Number** (`entry_number`): JE-TCS-IND-2025009
- **Posting Date** (`date`): 2025-01-25
- **Account** (`account`): 89 (231001 - Cash)
- **Debit Amount** (`debit_amount`): 1300.00
- **Credit Amount** (`credit_amount`): 0.00
- **Description** (`description`): Journal entry debit #9
- **Company** (`company`): 23 (TechCorp India Pvt Ltd)
- **Created At** (`created_at`): 2026-01-22 16:48:47
- **Updated At** (`updated_at`): 2026-01-22 16:48:47
- **Created By** (`created_by`): 1 (admin)

### Record 5

- **Id** (`id`): 36
- **Entry Number** (`entry_number`): JE-TCS-USA-2025108
- **Posting Date** (`date`): 2025-01-22
- **Account** (`account`): 81 (221001 - Cash)
- **Debit Amount** (`debit_amount`): 0.00
- **Credit Amount** (`credit_amount`): 1200.00
- **Description** (`description`): Journal entry credit #8
- **Company** (`company`): 22 (TechCorp Solutions USA)
- **Created At** (`created_at`): 2026-01-22 16:48:47
- **Updated At** (`updated_at`): 2026-01-22 16:48:47
- **Created By** (`created_by`): 1 (admin)

### Record 6

- **Id** (`id`): 35
- **Entry Number** (`entry_number`): JE-TCS-USA-2025008
- **Posting Date** (`date`): 2025-01-22
- **Account** (`account`): 88 (225100 - Salaries & Wages)
- **Debit Amount** (`debit_amount`): 1200.00
- **Credit Amount** (`credit_amount`): 0.00
- **Description** (`description`): Journal entry debit #8
- **Company** (`company`): 22 (TechCorp Solutions USA)
- **Created At** (`created_at`): 2026-01-22 16:48:47
- **Updated At** (`updated_at`): 2026-01-22 16:48:47
- **Created By** (`created_by`): 1 (admin)

### Record 7

- **Id** (`id`): 34
- **Entry Number** (`entry_number`): JE-GCI-2025107
- **Posting Date** (`date`): 2025-01-19
- **Account** (`account`): 80 (215100 - Salaries & Wages)
- **Debit Amount** (`debit_amount`): 0.00
- **Credit Amount** (`credit_amount`): 1100.00
- **Description** (`description`): Journal entry credit #7
- **Company** (`company`): 21 (Global Corp International)
- **Created At** (`created_at`): 2026-01-22 16:48:47
- **Updated At** (`updated_at`): 2026-01-22 16:48:47
- **Created By** (`created_by`): 1 (admin)

### Record 8

- **Id** (`id`): 33
- **Entry Number** (`entry_number`): JE-GCI-2025007
- **Posting Date** (`date`): 2025-01-19
- **Account** (`account`): 79 (215001 - Operating Expenses)
- **Debit Amount** (`debit_amount`): 1100.00
- **Credit Amount** (`credit_amount`): 0.00
- **Description** (`description`): Journal entry debit #7
- **Company** (`company`): 21 (Global Corp International)
- **Created At** (`created_at`): 2026-01-22 16:48:47
- **Updated At** (`updated_at`): 2026-01-22 16:48:47
- **Created By** (`created_by`): 1 (admin)

### Record 9

- **Id** (`id`): 32
- **Entry Number** (`entry_number`): JE-TCS-IND-2025106
- **Posting Date** (`date`): 2025-01-16
- **Account** (`account`): 95 (235001 - Operating Expenses)
- **Debit Amount** (`debit_amount`): 0.00
- **Credit Amount** (`credit_amount`): 1000.00
- **Description** (`description`): Journal entry credit #6
- **Company** (`company`): 23 (TechCorp India Pvt Ltd)
- **Created At** (`created_at`): 2026-01-22 16:48:47
- **Updated At** (`updated_at`): 2026-01-22 16:48:47
- **Created By** (`created_by`): 1 (admin)

### Record 10

- **Id** (`id`): 31
- **Entry Number** (`entry_number`): JE-TCS-IND-2025006
- **Posting Date** (`date`): 2025-01-16
- **Account** (`account`): 94 (234001 - Sales Revenue)
- **Debit Amount** (`debit_amount`): 1000.00
- **Credit Amount** (`credit_amount`): 0.00
- **Description** (`description`): Journal entry debit #6
- **Company** (`company`): 23 (TechCorp India Pvt Ltd)
- **Created At** (`created_at`): 2026-01-22 16:48:47
- **Updated At** (`updated_at`): 2026-01-22 16:48:47
- **Created By** (`created_by`): 1 (admin)

### Record 11

- **Id** (`id`): 30
- **Entry Number** (`entry_number`): JE-TCS-USA-2025105
- **Posting Date** (`date`): 2025-01-13
- **Account** (`account`): 86 (224001 - Sales Revenue)
- **Debit Amount** (`debit_amount`): 0.00
- **Credit Amount** (`credit_amount`): 900.00
- **Description** (`description`): Journal entry credit #5
- **Company** (`company`): 22 (TechCorp Solutions USA)
- **Created At** (`created_at`): 2026-01-22 16:48:47
- **Updated At** (`updated_at`): 2026-01-22 16:48:47
- **Created By** (`created_by`): 1 (admin)

### Record 12

- **Id** (`id`): 29
- **Entry Number** (`entry_number`): JE-TCS-USA-2025005
- **Posting Date** (`date`): 2025-01-13
- **Account** (`account`): 85 (223001 - Owner's Capital)
- **Debit Amount** (`debit_amount`): 900.00
- **Credit Amount** (`credit_amount`): 0.00
- **Description** (`description`): Journal entry debit #5
- **Company** (`company`): 22 (TechCorp Solutions USA)
- **Created At** (`created_at`): 2026-01-22 16:48:47
- **Updated At** (`updated_at`): 2026-01-22 16:48:47
- **Created By** (`created_by`): 1 (admin)

### Record 13

- **Id** (`id`): 28
- **Entry Number** (`entry_number`): JE-GCI-2025104
- **Posting Date** (`date`): 2025-01-10
- **Account** (`account`): 77 (213001 - Owner's Capital)
- **Debit Amount** (`debit_amount`): 0.00
- **Credit Amount** (`credit_amount`): 800.00
- **Description** (`description`): Journal entry credit #4
- **Company** (`company`): 21 (Global Corp International)
- **Created At** (`created_at`): 2026-01-22 16:48:47
- **Updated At** (`updated_at`): 2026-01-22 16:48:47
- **Created By** (`created_by`): 1 (admin)

### Record 14

- **Id** (`id`): 27
- **Entry Number** (`entry_number`): JE-GCI-2025004
- **Posting Date** (`date`): 2025-01-10
- **Account** (`account`): 76 (212001 - Accounts Payable)
- **Debit Amount** (`debit_amount`): 800.00
- **Credit Amount** (`credit_amount`): 0.00
- **Description** (`description`): Journal entry debit #4
- **Company** (`company`): 21 (Global Corp International)
- **Created At** (`created_at`): 2026-01-22 16:48:47
- **Updated At** (`updated_at`): 2026-01-22 16:48:47
- **Created By** (`created_by`): 1 (admin)

### Record 15

- **Id** (`id`): 26
- **Entry Number** (`entry_number`): JE-TCS-IND-2025103
- **Posting Date** (`date`): 2025-01-07
- **Account** (`account`): 92 (232001 - Accounts Payable)
- **Debit Amount** (`debit_amount`): 0.00
- **Credit Amount** (`credit_amount`): 700.00
- **Description** (`description`): Journal entry credit #3
- **Company** (`company`): 23 (TechCorp India Pvt Ltd)
- **Created At** (`created_at`): 2026-01-22 16:48:47
- **Updated At** (`updated_at`): 2026-01-22 16:48:47
- **Created By** (`created_by`): 1 (admin)

### Record 16

- **Id** (`id`): 25
- **Entry Number** (`entry_number`): JE-TCS-IND-2025003
- **Posting Date** (`date`): 2025-01-07
- **Account** (`account`): 91 (231100 - Accounts Receivable)
- **Debit Amount** (`debit_amount`): 700.00
- **Credit Amount** (`credit_amount`): 0.00
- **Description** (`description`): Journal entry debit #3
- **Company** (`company`): 23 (TechCorp India Pvt Ltd)
- **Created At** (`created_at`): 2026-01-22 16:48:47
- **Updated At** (`updated_at`): 2026-01-22 16:48:47
- **Created By** (`created_by`): 1 (admin)

### Record 17

- **Id** (`id`): 24
- **Entry Number** (`entry_number`): JE-TCS-USA-2025102
- **Posting Date** (`date`): 2025-01-04
- **Account** (`account`): 83 (221100 - Accounts Receivable)
- **Debit Amount** (`debit_amount`): 0.00
- **Credit Amount** (`credit_amount`): 600.00
- **Description** (`description`): Journal entry credit #2
- **Company** (`company`): 22 (TechCorp Solutions USA)
- **Created At** (`created_at`): 2026-01-22 16:48:47
- **Updated At** (`updated_at`): 2026-01-22 16:48:47
- **Created By** (`created_by`): 1 (admin)

### Record 18

- **Id** (`id`): 23
- **Entry Number** (`entry_number`): JE-TCS-USA-2025002
- **Posting Date** (`date`): 2025-01-04
- **Account** (`account`): 82 (221002 - Bank Account)
- **Debit Amount** (`debit_amount`): 600.00
- **Credit Amount** (`credit_amount`): 0.00
- **Description** (`description`): Journal entry debit #2
- **Company** (`company`): 22 (TechCorp Solutions USA)
- **Created At** (`created_at`): 2026-01-22 16:48:47
- **Updated At** (`updated_at`): 2026-01-22 16:48:47
- **Created By** (`created_by`): 1 (admin)

### Record 19

- **Id** (`id`): 22
- **Entry Number** (`entry_number`): JE-GCI-2025101
- **Posting Date** (`date`): 2025-01-01
- **Account** (`account`): 74 (211002 - Bank Account)
- **Debit Amount** (`debit_amount`): 0.00
- **Credit Amount** (`credit_amount`): 500.00
- **Description** (`description`): Journal entry credit #1
- **Company** (`company`): 21 (Global Corp International)
- **Created At** (`created_at`): 2026-01-22 16:48:47
- **Updated At** (`updated_at`): 2026-01-22 16:48:47
- **Created By** (`created_by`): 1 (admin)

### Record 20

- **Id** (`id`): 21
- **Entry Number** (`entry_number`): JE-GCI-2025001
- **Posting Date** (`date`): 2025-01-01
- **Account** (`account`): 73 (211001 - Cash)
- **Debit Amount** (`debit_amount`): 500.00
- **Credit Amount** (`credit_amount`): 0.00
- **Description** (`description`): Journal entry debit #1
- **Company** (`company`): 21 (Global Corp International)
- **Created At** (`created_at`): 2026-01-22 16:48:47
- **Updated At** (`updated_at`): 2026-01-22 16:48:47
- **Created By** (`created_by`): 1 (admin)

---


## Suppliers

**Table:** `finance_supplier`  
**Total Records:** 5

### Record 1

- **Id** (`id`): 15
- **Gstin / Uin** (`gstin_uin`): _empty_
- **Supplier Name** (`name`): Office Supplies Pro
- **Supplier Type** (`supplier_type`): company
- **Gst Category** (`gst_category`): unregistered
- **First Name** (`contact_first_name`): Contact
- **Last Name** (`contact_last_name`): Person
- **Email Id** (`contact_email`): contact@officesupplies.com
- **Mobile Number** (`contact_mobile`): +1-555-1234
- **Preferred Billing Address** (`preferred_billing`): ❌ No
- **Preferred Shipping Address** (`preferred_shipping`): ❌ No
- **Postal Code** (`postal_code`): 12345
- **City/Town** (`city`): Business City
- **Address Line 1** (`address_line1`): 123 Business St
- **Address Line 2** (`address_line2`): _empty_
- **State/Province** (`state`): _empty_
- **Country** (`country`): USA
- **Company** (`company`): 21 (Global Corp International)
- **Created At** (`created_at`): 2026-01-22 16:48:47
- **Updated At** (`updated_at`): 2026-01-22 16:48:47
- **Created By** (`created_by`): 1 (admin)

### Record 2

- **Id** (`id`): 14
- **Gstin / Uin** (`gstin_uin`): GSTIN-GLB-004
- **Supplier Name** (`name`): Global Imports LLC
- **Supplier Type** (`supplier_type`): company
- **Gst Category** (`gst_category`): registered
- **First Name** (`contact_first_name`): Contact
- **Last Name** (`contact_last_name`): Person
- **Email Id** (`contact_email`): orders@globalimports.com
- **Mobile Number** (`contact_mobile`): +1-555-1234
- **Preferred Billing Address** (`preferred_billing`): ❌ No
- **Preferred Shipping Address** (`preferred_shipping`): ❌ No
- **Postal Code** (`postal_code`): 12345
- **City/Town** (`city`): Business City
- **Address Line 1** (`address_line1`): 123 Business St
- **Address Line 2** (`address_line2`): _empty_
- **State/Province** (`state`): _empty_
- **Country** (`country`): USA
- **Company** (`company`): 21 (Global Corp International)
- **Created At** (`created_at`): 2026-01-22 16:48:47
- **Updated At** (`updated_at`): 2026-01-22 16:48:47
- **Created By** (`created_by`): 1 (admin)

### Record 3

- **Id** (`id`): 13
- **Gstin / Uin** (`gstin_uin`): GSTIN-TECH-003
- **Supplier Name** (`name`): Tech Solutions Ltd
- **Supplier Type** (`supplier_type`): company
- **Gst Category** (`gst_category`): registered_composition
- **First Name** (`contact_first_name`): Contact
- **Last Name** (`contact_last_name`): Person
- **Email Id** (`contact_email`): info@techsolutions.com
- **Mobile Number** (`contact_mobile`): +1-555-1234
- **Preferred Billing Address** (`preferred_billing`): ❌ No
- **Preferred Shipping Address** (`preferred_shipping`): ❌ No
- **Postal Code** (`postal_code`): 12345
- **City/Town** (`city`): Business City
- **Address Line 1** (`address_line1`): 123 Business St
- **Address Line 2** (`address_line2`): _empty_
- **State/Province** (`state`): _empty_
- **Country** (`country`): USA
- **Company** (`company`): 21 (Global Corp International)
- **Created At** (`created_at`): 2026-01-22 16:48:47
- **Updated At** (`updated_at`): 2026-01-22 16:48:47
- **Created By** (`created_by`): 1 (admin)

### Record 4

- **Id** (`id`): 12
- **Gstin / Uin** (`gstin_uin`): GSTIN-XYZ-002
- **Supplier Name** (`name`): XYZ Trading Co
- **Supplier Type** (`supplier_type`): company
- **Gst Category** (`gst_category`): registered
- **First Name** (`contact_first_name`): Contact
- **Last Name** (`contact_last_name`): Person
- **Email Id** (`contact_email`): sales@xyztrading.com
- **Mobile Number** (`contact_mobile`): +1-555-1234
- **Preferred Billing Address** (`preferred_billing`): ❌ No
- **Preferred Shipping Address** (`preferred_shipping`): ❌ No
- **Postal Code** (`postal_code`): 12345
- **City/Town** (`city`): Business City
- **Address Line 1** (`address_line1`): 123 Business St
- **Address Line 2** (`address_line2`): _empty_
- **State/Province** (`state`): _empty_
- **Country** (`country`): India
- **Company** (`company`): 21 (Global Corp International)
- **Created At** (`created_at`): 2026-01-22 16:48:47
- **Updated At** (`updated_at`): 2026-01-22 16:48:47
- **Created By** (`created_by`): 1 (admin)

### Record 5

- **Id** (`id`): 11
- **Gstin / Uin** (`gstin_uin`): GSTIN-ABC-001
- **Supplier Name** (`name`): ABC Supplies Inc
- **Supplier Type** (`supplier_type`): company
- **Gst Category** (`gst_category`): registered
- **First Name** (`contact_first_name`): Contact
- **Last Name** (`contact_last_name`): Person
- **Email Id** (`contact_email`): contact@abcsupplies.com
- **Mobile Number** (`contact_mobile`): +1-555-1234
- **Preferred Billing Address** (`preferred_billing`): ❌ No
- **Preferred Shipping Address** (`preferred_shipping`): ❌ No
- **Postal Code** (`postal_code`): 12345
- **City/Town** (`city`): Business City
- **Address Line 1** (`address_line1`): 123 Business St
- **Address Line 2** (`address_line2`): _empty_
- **State/Province** (`state`): _empty_
- **Country** (`country`): USA
- **Company** (`company`): 21 (Global Corp International)
- **Created At** (`created_at`): 2026-01-22 16:48:47
- **Updated At** (`updated_at`): 2026-01-22 16:48:47
- **Created By** (`created_by`): 1 (admin)

---


## Customers

**Table:** `finance_customer`  
**Total Records:** 4

### Record 1

- **Id** (`id`): 12
- **Gstin / Uin** (`gstin_uin`): _empty_
- **Customer Name** (`name`): Small Business LLC
- **Customer Type** (`customer_type`): company
- **Gst Category** (`gst_category`): unregistered
- **First Name** (`contact_first_name`): Contact
- **Last Name** (`contact_last_name`): Person
- **Email Id** (`contact_email`): owner@smallbiz.com
- **Mobile Number** (`contact_mobile`): +1-555-5678
- **Preferred Billing Address** (`preferred_billing`): ❌ No
- **Preferred Shipping Address** (`preferred_shipping`): ❌ No
- **Postal Code** (`postal_code`): 54321
- **City/Town** (`city`): Customer City
- **Address Line 1** (`address_line1`): 456 Customer Ave
- **Address Line 2** (`address_line2`): _empty_
- **State/Province** (`state`): _empty_
- **Country** (`country`): USA
- **Company** (`company`): 21 (Global Corp International)
- **Created At** (`created_at`): 2026-01-22 16:48:47
- **Updated At** (`updated_at`): 2026-01-22 16:48:47
- **Created By** (`created_by`): 1 (admin)

### Record 2

- **Id** (`id`): 11
- **Gstin / Uin** (`gstin_uin`): GSTIN-TECH-003
- **Customer Name** (`name`): Tech Innovations Pvt Ltd
- **Customer Type** (`customer_type`): company
- **Gst Category** (`gst_category`): registered
- **First Name** (`contact_first_name`): Contact
- **Last Name** (`contact_last_name`): Person
- **Email Id** (`contact_email`): finance@techinnovations.in
- **Mobile Number** (`contact_mobile`): +1-555-5678
- **Preferred Billing Address** (`preferred_billing`): ❌ No
- **Preferred Shipping Address** (`preferred_shipping`): ❌ No
- **Postal Code** (`postal_code`): 54321
- **City/Town** (`city`): Customer City
- **Address Line 1** (`address_line1`): 456 Customer Ave
- **Address Line 2** (`address_line2`): _empty_
- **State/Province** (`state`): _empty_
- **Country** (`country`): India
- **Company** (`company`): 21 (Global Corp International)
- **Created At** (`created_at`): 2026-01-22 16:48:47
- **Updated At** (`updated_at`): 2026-01-22 16:48:47
- **Created By** (`created_by`): 1 (admin)

### Record 3

- **Id** (`id`): 10
- **Gstin / Uin** (`gstin_uin`): GSTIN-RTL-002
- **Customer Name** (`name`): Retail Mart Inc
- **Customer Type** (`customer_type`): company
- **Gst Category** (`gst_category`): registered
- **First Name** (`contact_first_name`): Contact
- **Last Name** (`contact_last_name`): Person
- **Email Id** (`contact_email`): accounts@retailmart.com
- **Mobile Number** (`contact_mobile`): +1-555-5678
- **Preferred Billing Address** (`preferred_billing`): ❌ No
- **Preferred Shipping Address** (`preferred_shipping`): ❌ No
- **Postal Code** (`postal_code`): 54321
- **City/Town** (`city`): Customer City
- **Address Line 1** (`address_line1`): 456 Customer Ave
- **Address Line 2** (`address_line2`): _empty_
- **State/Province** (`state`): _empty_
- **Country** (`country`): USA
- **Company** (`company`): 21 (Global Corp International)
- **Created At** (`created_at`): 2026-01-22 16:48:47
- **Updated At** (`updated_at`): 2026-01-22 16:48:47
- **Created By** (`created_by`): 1 (admin)

### Record 4

- **Id** (`id`): 9
- **Gstin / Uin** (`gstin_uin`): GSTIN-ACME-001
- **Customer Name** (`name`): Acme Corporation
- **Customer Type** (`customer_type`): company
- **Gst Category** (`gst_category`): registered
- **First Name** (`contact_first_name`): Contact
- **Last Name** (`contact_last_name`): Person
- **Email Id** (`contact_email`): billing@acmecorp.com
- **Mobile Number** (`contact_mobile`): +1-555-5678
- **Preferred Billing Address** (`preferred_billing`): ❌ No
- **Preferred Shipping Address** (`preferred_shipping`): ❌ No
- **Postal Code** (`postal_code`): 54321
- **City/Town** (`city`): Customer City
- **Address Line 1** (`address_line1`): 456 Customer Ave
- **Address Line 2** (`address_line2`): _empty_
- **State/Province** (`state`): _empty_
- **Country** (`country`): USA
- **Company** (`company`): 21 (Global Corp International)
- **Created At** (`created_at`): 2026-01-22 16:48:47
- **Updated At** (`updated_at`): 2026-01-22 16:48:47
- **Created By** (`created_by`): 1 (admin)

---


# Planning & Budgeting


## Budgets

**Table:** `finance_budget`  
**Total Records:** 3

### Record 1

- **Id** (`id`): 7
- **Budget Series** (`series`): BUD-GCI-2025
- **Budget Against** (`budget_against`): cost_center
- **Fiscal Year From** (`fiscal_year_from`): 2025-2026
- **Fiscal Year To** (`fiscal_year_to`): 2025-2026
- **Company** (`company`): 21 (Global Corp International)
- **Distribution** (`distribution`): monthly
- **Cost Center** (`cost_center`): 37 (CC-001 - Operations)
- **Account** (`account`): 79 (215001 - Operating Expenses)
- **Total Budget Amount** (`budget_amount`): 100000.00

### Record 2

- **Id** (`id`): 9
- **Budget Series** (`series`): BUD-TCS-IND-2025
- **Budget Against** (`budget_against`): cost_center
- **Fiscal Year From** (`fiscal_year_from`): 2025-2026
- **Fiscal Year To** (`fiscal_year_to`): 2025-2026
- **Company** (`company`): 23 (TechCorp India Pvt Ltd)
- **Distribution** (`distribution`): monthly
- **Cost Center** (`cost_center`): 39 (CC-003 - IT Department)
- **Account** (`account`): 87 (225001 - Operating Expenses)
- **Total Budget Amount** (`budget_amount`): 200000.00

### Record 3

- **Id** (`id`): 8
- **Budget Series** (`series`): BUD-TCS-USA-2025
- **Budget Against** (`budget_against`): cost_center
- **Fiscal Year From** (`fiscal_year_from`): 2025-2026
- **Fiscal Year To** (`fiscal_year_to`): 2025-2026
- **Company** (`company`): 22 (TechCorp Solutions USA)
- **Distribution** (`distribution`): monthly
- **Cost Center** (`cost_center`): 38 (CC-002 - Marketing)
- **Account** (`account`): 80 (215100 - Salaries & Wages)
- **Total Budget Amount** (`budget_amount`): 150000.00

---


## Cost Centers

**Table:** `finance_costcenter`  
**Total Records:** 12

### Record 1

- **Id** (`id`): 39
- **Cost Center Name** (`name`): IT Department
- **Cost Center Number** (`cost_center_number`): CC-003
- **Company** (`company`): 21 (Global Corp International)
- **Parent Cost Center** (`parent`): _empty_
- **Is Group** (`is_group`): ❌ No
- **Disabled** (`is_disabled`): ❌ No
- **Created At** (`created_at`): 2026-01-22 16:48:47
- **Updated At** (`updated_at`): 2026-01-22 16:48:47

### Record 2

- **Id** (`id`): 43
- **Cost Center Name** (`name`): IT Department
- **Cost Center Number** (`cost_center_number`): CC-003
- **Company** (`company`): 22 (TechCorp Solutions USA)
- **Parent Cost Center** (`parent`): _empty_
- **Is Group** (`is_group`): ❌ No
- **Disabled** (`is_disabled`): ❌ No
- **Created At** (`created_at`): 2026-01-22 16:48:47
- **Updated At** (`updated_at`): 2026-01-22 16:48:47

### Record 3

- **Id** (`id`): 47
- **Cost Center Name** (`name`): IT Department
- **Cost Center Number** (`cost_center_number`): CC-003
- **Company** (`company`): 23 (TechCorp India Pvt Ltd)
- **Parent Cost Center** (`parent`): _empty_
- **Is Group** (`is_group`): ❌ No
- **Disabled** (`is_disabled`): ❌ No
- **Created At** (`created_at`): 2026-01-22 16:48:47
- **Updated At** (`updated_at`): 2026-01-22 16:48:47

### Record 4

- **Id** (`id`): 38
- **Cost Center Name** (`name`): Marketing
- **Cost Center Number** (`cost_center_number`): CC-002
- **Company** (`company`): 21 (Global Corp International)
- **Parent Cost Center** (`parent`): _empty_
- **Is Group** (`is_group`): ❌ No
- **Disabled** (`is_disabled`): ❌ No
- **Created At** (`created_at`): 2026-01-22 16:48:47
- **Updated At** (`updated_at`): 2026-01-22 16:48:47

### Record 5

- **Id** (`id`): 42
- **Cost Center Name** (`name`): Marketing
- **Cost Center Number** (`cost_center_number`): CC-002
- **Company** (`company`): 22 (TechCorp Solutions USA)
- **Parent Cost Center** (`parent`): _empty_
- **Is Group** (`is_group`): ❌ No
- **Disabled** (`is_disabled`): ❌ No
- **Created At** (`created_at`): 2026-01-22 16:48:47
- **Updated At** (`updated_at`): 2026-01-22 16:48:47

### Record 6

- **Id** (`id`): 46
- **Cost Center Name** (`name`): Marketing
- **Cost Center Number** (`cost_center_number`): CC-002
- **Company** (`company`): 23 (TechCorp India Pvt Ltd)
- **Parent Cost Center** (`parent`): _empty_
- **Is Group** (`is_group`): ❌ No
- **Disabled** (`is_disabled`): ❌ No
- **Created At** (`created_at`): 2026-01-22 16:48:47
- **Updated At** (`updated_at`): 2026-01-22 16:48:47

### Record 7

- **Id** (`id`): 37
- **Cost Center Name** (`name`): Operations
- **Cost Center Number** (`cost_center_number`): CC-001
- **Company** (`company`): 21 (Global Corp International)
- **Parent Cost Center** (`parent`): _empty_
- **Is Group** (`is_group`): ❌ No
- **Disabled** (`is_disabled`): ❌ No
- **Created At** (`created_at`): 2026-01-22 16:48:47
- **Updated At** (`updated_at`): 2026-01-22 16:48:47

### Record 8

- **Id** (`id`): 41
- **Cost Center Name** (`name`): Operations
- **Cost Center Number** (`cost_center_number`): CC-001
- **Company** (`company`): 22 (TechCorp Solutions USA)
- **Parent Cost Center** (`parent`): _empty_
- **Is Group** (`is_group`): ❌ No
- **Disabled** (`is_disabled`): ❌ No
- **Created At** (`created_at`): 2026-01-22 16:48:47
- **Updated At** (`updated_at`): 2026-01-22 16:48:47

### Record 9

- **Id** (`id`): 45
- **Cost Center Name** (`name`): Operations
- **Cost Center Number** (`cost_center_number`): CC-001
- **Company** (`company`): 23 (TechCorp India Pvt Ltd)
- **Parent Cost Center** (`parent`): _empty_
- **Is Group** (`is_group`): ❌ No
- **Disabled** (`is_disabled`): ❌ No
- **Created At** (`created_at`): 2026-01-22 16:48:47
- **Updated At** (`updated_at`): 2026-01-22 16:48:47

### Record 10

- **Id** (`id`): 40
- **Cost Center Name** (`name`): Sales
- **Cost Center Number** (`cost_center_number`): CC-004
- **Company** (`company`): 21 (Global Corp International)
- **Parent Cost Center** (`parent`): _empty_
- **Is Group** (`is_group`): ❌ No
- **Disabled** (`is_disabled`): ❌ No
- **Created At** (`created_at`): 2026-01-22 16:48:47
- **Updated At** (`updated_at`): 2026-01-22 16:48:47

### Record 11

- **Id** (`id`): 44
- **Cost Center Name** (`name`): Sales
- **Cost Center Number** (`cost_center_number`): CC-004
- **Company** (`company`): 22 (TechCorp Solutions USA)
- **Parent Cost Center** (`parent`): _empty_
- **Is Group** (`is_group`): ❌ No
- **Disabled** (`is_disabled`): ❌ No
- **Created At** (`created_at`): 2026-01-22 16:48:47
- **Updated At** (`updated_at`): 2026-01-22 16:48:47

### Record 12

- **Id** (`id`): 48
- **Cost Center Name** (`name`): Sales
- **Cost Center Number** (`cost_center_number`): CC-004
- **Company** (`company`): 23 (TechCorp India Pvt Ltd)
- **Parent Cost Center** (`parent`): _empty_
- **Is Group** (`is_group`): ❌ No
- **Disabled** (`is_disabled`): ❌ No
- **Created At** (`created_at`): 2026-01-22 16:48:47
- **Updated At** (`updated_at`): 2026-01-22 16:48:47

---


## Cost Center Allocations

**Table:** `finance_costcenterallocation`  
**Total Records:** 3

### Record 1

- **Id** (`id`): 3
- **Cost Center** (`cost_center`): 39 (CC-003 - IT Department)
- **Company** (`company`): 21 (Global Corp International)
- **Valid From** (`valid_from`): 2025-01-01

### Record 2

- **Id** (`id`): 2
- **Cost Center** (`cost_center`): 38 (CC-002 - Marketing)
- **Company** (`company`): 21 (Global Corp International)
- **Valid From** (`valid_from`): 2025-01-01

### Record 3

- **Id** (`id`): 1
- **Cost Center** (`cost_center`): 37 (CC-001 - Operations)
- **Company** (`company`): 21 (Global Corp International)
- **Valid From** (`valid_from`): 2025-01-01

---


## Accounting Dimensions

**Table:** `finance_accountingdimension`  
**Total Records:** 3

### Record 1

- **Id** (`id`): 1
- **Dimension Name** (`name`): Department
- **Created At** (`created_at`): 2026-01-22 16:48:47
- **Updated At** (`updated_at`): 2026-01-22 16:48:47

### Record 2

- **Id** (`id`): 2
- **Dimension Name** (`name`): Project
- **Created At** (`created_at`): 2026-01-22 16:48:47
- **Updated At** (`updated_at`): 2026-01-22 16:48:47

### Record 3

- **Id** (`id`): 3
- **Dimension Name** (`name`): Region
- **Created At** (`created_at`): 2026-01-22 16:48:47
- **Updated At** (`updated_at`): 2026-01-22 16:48:47

---


# Tax Configuration


## Tax Item Templates

**Table:** `finance_taxitemtemplate`  
**Total Records:** 4

### Record 1

- **Id** (`id`): 3
- **Tax Item Template Title** (`title`): GST 18%
- **Company** (`company`): 21 (Global Corp International)
- **Gst Rate (%)** (`gst_rate`): 18.00
- **Gst Treatment** (`gst_treatment`): taxable
- **Disabled** (`disabled`): ❌ No

### Record 2

- **Id** (`id`): 4
- **Tax Item Template Title** (`title`): Nil Rated
- **Company** (`company`): 21 (Global Corp International)
- **Gst Rate (%)** (`gst_rate`): 0.00
- **Gst Treatment** (`gst_treatment`): nil_rated
- **Disabled** (`disabled`): ❌ No

### Record 3

- **Id** (`id`): 1
- **Tax Item Template Title** (`title`): Sales Tax 15%
- **Company** (`company`): 21 (Global Corp International)
- **Gst Rate (%)** (`gst_rate`): 15.00
- **Gst Treatment** (`gst_treatment`): taxable
- **Disabled** (`disabled`): ❌ No

### Record 4

- **Id** (`id`): 2
- **Tax Item Template Title** (`title`): VAT Standard 20%
- **Company** (`company`): 21 (Global Corp International)
- **Gst Rate (%)** (`gst_rate`): 20.00
- **Gst Treatment** (`gst_treatment`): taxable
- **Disabled** (`disabled`): ❌ No

---


## Tax Categorys

**Table:** `finance_taxcategory`  
**Total Records:** 4

### Record 1

- **Id** (`id`): 4
- **Tax Category Title** (`title`): Exempt

### Record 2

- **Id** (`id`): 2
- **Tax Category Title** (`title`): Reduced Rate

### Record 3

- **Id** (`id`): 1
- **Tax Category Title** (`title`): Standard Rate

### Record 4

- **Id** (`id`): 3
- **Tax Category Title** (`title`): Zero Rate

---


## Tax Rules

**Table:** `finance_taxrule`  
**Total Records:** 3

### Record 1

- **Id** (`id`): 1
- **Tax Type** (`tax_type`): sales
- **Sales Tax Template** (`sales_tax_template`): 1 (Sales Tax 15% (15.00%))
- **Shopping Cart Use** (`shopping_cart_use`): ❌ No
- **Customer** (`customer`): 9 (Acme Corporation)
- **Customer Group** (`customer_group`): _empty_
- **Item** (`item`): _empty_
- **Item Group** (`item_group`): _empty_
- **Billing City** (`billing_city`): _empty_
- **Shipping City** (`shipping_city`): _empty_
- **Billing County** (`billing_county`): _empty_
- **Shipping County** (`shipping_county`): _empty_
- **Billing State** (`billing_state`): _empty_
- **Shipping State** (`shipping_state`): _empty_
- **Billing Zipcode** (`billing_zipcode`): _empty_
- **Shipping Zipcode** (`shipping_zipcode`): _empty_
- **Billing Country** (`billing_country`): USA
- **Shipping Country** (`shipping_country`): _empty_
- **Tax Category** (`tax_category`): 1 (Standard Rate)
- **From Date** (`from_date`): 2025-01-01
- **To Date** (`to_date`): 2025-12-31
- **Priority** (`priority`): 1
- **Company** (`company`): 21 (Global Corp International)

### Record 2

- **Id** (`id`): 2
- **Tax Type** (`tax_type`): sales
- **Sales Tax Template** (`sales_tax_template`): 2 (VAT Standard 20% (20.00%))
- **Shopping Cart Use** (`shopping_cart_use`): ❌ No
- **Customer** (`customer`): 10 (Retail Mart Inc)
- **Customer Group** (`customer_group`): _empty_
- **Item** (`item`): _empty_
- **Item Group** (`item_group`): _empty_
- **Billing City** (`billing_city`): _empty_
- **Shipping City** (`shipping_city`): _empty_
- **Billing County** (`billing_county`): _empty_
- **Shipping County** (`shipping_county`): _empty_
- **Billing State** (`billing_state`): _empty_
- **Shipping State** (`shipping_state`): _empty_
- **Billing Zipcode** (`billing_zipcode`): _empty_
- **Shipping Zipcode** (`shipping_zipcode`): _empty_
- **Billing Country** (`billing_country`): USA
- **Shipping Country** (`shipping_country`): _empty_
- **Tax Category** (`tax_category`): 2 (Reduced Rate)
- **From Date** (`from_date`): 2025-01-01
- **To Date** (`to_date`): 2025-12-31
- **Priority** (`priority`): 2
- **Company** (`company`): 21 (Global Corp International)

### Record 3

- **Id** (`id`): 3
- **Tax Type** (`tax_type`): sales
- **Sales Tax Template** (`sales_tax_template`): 3 (GST 18% (18.00%))
- **Shopping Cart Use** (`shopping_cart_use`): ❌ No
- **Customer** (`customer`): 11 (Tech Innovations Pvt Ltd)
- **Customer Group** (`customer_group`): _empty_
- **Item** (`item`): _empty_
- **Item Group** (`item_group`): _empty_
- **Billing City** (`billing_city`): _empty_
- **Shipping City** (`shipping_city`): _empty_
- **Billing County** (`billing_county`): _empty_
- **Shipping County** (`shipping_county`): _empty_
- **Billing State** (`billing_state`): _empty_
- **Shipping State** (`shipping_state`): _empty_
- **Billing Zipcode** (`billing_zipcode`): _empty_
- **Shipping Zipcode** (`shipping_zipcode`): _empty_
- **Billing Country** (`billing_country`): India
- **Shipping Country** (`shipping_country`): _empty_
- **Tax Category** (`tax_category`): 3 (Zero Rate)
- **From Date** (`from_date`): 2025-01-01
- **To Date** (`to_date`): 2025-12-31
- **Priority** (`priority`): 3
- **Company** (`company`): 21 (Global Corp International)

---


## Tax Withholding Categorys

**Table:** `finance_taxwithholdingcategory`  
**Total Records:** 4

### Record 1

- **Id** (`id`): 1
- **Name** (`name`): TDS on Salary
- **Category Name** (`category_name`): TDS on Salary
- **Deduct Tax On Basis** (`deduct_tax_on_basis`): Net Total
- **Round Off Tax Amount** (`round_off_tax_amount`): ✅ Yes
- **Section** (`section`): _empty_
- **Only Deduct Tax On Excess Amount** (`only_deduct_on_excess`): ❌ No
- **Entity** (`entity`): Company
- **Disable Cumulative Threshold** (`disable_cumulative_threshold`): ❌ No
- **Disable Transaction Threshold** (`disable_transaction_threshold`): ❌ No

### Record 2

- **Id** (`id`): 2
- **Name** (`name`): TDS on Professional Services
- **Category Name** (`category_name`): TDS on Professional Services
- **Deduct Tax On Basis** (`deduct_tax_on_basis`): Net Total
- **Round Off Tax Amount** (`round_off_tax_amount`): ✅ Yes
- **Section** (`section`): _empty_
- **Only Deduct Tax On Excess Amount** (`only_deduct_on_excess`): ❌ No
- **Entity** (`entity`): Company
- **Disable Cumulative Threshold** (`disable_cumulative_threshold`): ❌ No
- **Disable Transaction Threshold** (`disable_transaction_threshold`): ❌ No

### Record 3

- **Id** (`id`): 3
- **Name** (`name`): TDS on Rent
- **Category Name** (`category_name`): TDS on Rent
- **Deduct Tax On Basis** (`deduct_tax_on_basis`): Net Total
- **Round Off Tax Amount** (`round_off_tax_amount`): ✅ Yes
- **Section** (`section`): _empty_
- **Only Deduct Tax On Excess Amount** (`only_deduct_on_excess`): ❌ No
- **Entity** (`entity`): Company
- **Disable Cumulative Threshold** (`disable_cumulative_threshold`): ❌ No
- **Disable Transaction Threshold** (`disable_transaction_threshold`): ❌ No

### Record 4

- **Id** (`id`): 4
- **Name** (`name`): TCS on Sales
- **Category Name** (`category_name`): TCS on Sales
- **Deduct Tax On Basis** (`deduct_tax_on_basis`): Net Total
- **Round Off Tax Amount** (`round_off_tax_amount`): ✅ Yes
- **Section** (`section`): _empty_
- **Only Deduct Tax On Excess Amount** (`only_deduct_on_excess`): ❌ No
- **Entity** (`entity`): Company
- **Disable Cumulative Threshold** (`disable_cumulative_threshold`): ❌ No
- **Disable Transaction Threshold** (`disable_transaction_threshold`): ❌ No

---


## Tax Withholding Rates

**Table:** `finance_taxwithholdingrate`  
**Total Records:** 0

_No records found_


## Category Account Mappings

**Table:** `finance_taxcategoryaccount`  
**Total Records:** 0

_No records found_


## Deduction Certificates

**Table:** `finance_deductioncertificate`  
**Total Records:** 0

_No records found_


# Banking


## Bank Account Types

**Table:** `finance_bankaccounttype`  
**Total Records:** 0

_No records found_


## Bank Account Subtypes

**Table:** `finance_bankaccountsubtype`  
**Total Records:** 0

_No records found_


## Bank Accounts

**Table:** `finance_bankaccount`  
**Total Records:** 0

_No records found_


# Users


## User Profiles

**Table:** `finance_userprofile`  
**Total Records:** 3

### Record 1

- **Id** (`id`): 4
- **User** (`user`): 5 (john_doe)
- **Phone Number** (`phone_number`): +1-555-1001
- **Date Of Birth** (`date_of_birth`): 1991-01-01

### Record 2

- **Id** (`id`): 5
- **User** (`user`): 6 (jane_smith)
- **Phone Number** (`phone_number`): +1-555-1002
- **Date Of Birth** (`date_of_birth`): 1992-01-01

### Record 3

- **Id** (`id`): 6
- **User** (`user`): 7 (bob_wilson)
- **Phone Number** (`phone_number`): +1-555-1003
- **Date Of Birth** (`date_of_birth`): 1992-12-31

---


---

## Summary Statistics

| Model | Record Count |
|-------|-------------|
| Companies | 5 |
| Accounts | 24 |
| Invoices | 10 |
| Journal Entries | 20 |
| Suppliers | 5 |
| Customers | 4 |
| Budgets | 3 |
| Cost Centers | 12 |
| Cost Center Allocations | 3 |
| Accounting Dimensions | 3 |
| Tax Item Templates | 4 |
| Tax Categorys | 4 |
| Tax Rules | 3 |
| Tax Withholding Categorys | 4 |
| Tax Withholding Rates | 0 |
| Category Account Mappings | 0 |
| Deduction Certificates | 0 |
| Bank Account Types | 0 |
| Bank Account Subtypes | 0 |
| Bank Accounts | 0 |
| User Profiles | 3 |
| **TOTAL** | **107** |
