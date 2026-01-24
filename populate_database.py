"""
Populate Finance Database with Dummy Data
This script creates sample data for all tables in the correct order (respecting foreign keys)
"""
import os
import sys
import django
from datetime import date, datetime, timedelta
from decimal import Decimal

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import User
from finance.models import (
    UserProfile, Company, Account, CostCenter, Budget,
    JournalEntry, Invoice, Supplier, Customer,
    TaxCategory, TaxItemTemplate, TaxRule,
    AccountingDimension, CostCenterAllocation,
    TaxWithholdingCategory, TaxCategoryAccount, DeductionCertificate
)

def create_users():
    """Create users and user profiles"""
    print("Creating users...")
    users_data = [
        {'username': 'admin', 'email': 'admin@finance.com', 'first_name': 'Admin', 'last_name': 'User', 'is_staff': True, 'is_superuser': True},
        {'username': 'john_doe', 'email': 'john@finance.com', 'first_name': 'John', 'last_name': 'Doe'},
        {'username': 'jane_smith', 'email': 'jane@finance.com', 'first_name': 'Jane', 'last_name': 'Smith'},
        {'username': 'bob_wilson', 'email': 'bob@finance.com', 'first_name': 'Bob', 'last_name': 'Wilson'},
    ]
    
    users = []
    for data in users_data:
        # Check if user exists (after cleanup it shouldn't, but safe to check)
        try:
            user = User.objects.get(username=data['username'])
        except User.DoesNotExist:
            user = User.objects.create(
                username=data['username'],
                email=data['email'],
                first_name=data['first_name'],
                last_name=data['last_name'],
                is_staff=data.get('is_staff', False),
                is_superuser=data.get('is_superuser', False)
            )
            user.set_password('password123')
            user.save()
            
            # Create user profile
            UserProfile.objects.create(
                user=user,
                phone_number=f'+1-555-{1000 + len(users):04d}',
                date_of_birth=date(1990, 1, 1) + timedelta(days=len(users) * 365)
            )
        
        users.append(user)
    
    print(f"Created {len(users)} users")
    return users

def create_companies(users):
    """Create companies"""
    print("Creating companies...")
    
    # Parent company
    parent = Company.objects.create(
        name="Global Corp International",
        abbreviation="GCI",
        country="USA",
        date_of_establishment=date(2010, 1, 15),
        default_currency="USD",
        tax_id="TAX-USA-001",
        is_parent_company=True,
        is_group=True,
        company_type="holding",
        created_by=users[0]
    )
    
    companies = [parent]
    
    # Subsidiary companies
    subsidiaries_data = [
        {
            'name': 'TechCorp Solutions USA',
            'abbreviation': 'TCS-USA',
            'country': 'USA',
            'currency': 'USD',
            'tax_id': 'TAX-USA-002',
            'type': 'subsidiary'
        },
        {
            'name': 'TechCorp India Pvt Ltd',
            'abbreviation': 'TCS-IND',
            'country': 'India',
            'currency': 'INR',
            'tax_id': 'GSTIN-IND-001',
            'type': 'subsidiary'
        },
        {
            'name': 'FinTech Services LLC',
            'abbreviation': 'FTS',
            'country': 'USA',
            'currency': 'USD',
            'tax_id': 'TAX-USA-003',
            'type': 'regular'
        },
        {
            'name': 'Retail Solutions Inc',
            'abbreviation': 'RSI',
            'country': 'USA',
            'currency': 'USD',
            'tax_id': 'TAX-USA-004',
            'type': 'regular'
        }
    ]
    
    for data in subsidiaries_data:
        company = Company.objects.create(
            name=data['name'],
            abbreviation=data['abbreviation'],
            country=data['country'],
            date_of_establishment=date(2015, 6, 1),
            default_currency=data['currency'],
            tax_id=data['tax_id'],
            parent_company=parent if data['type'] == 'subsidiary' else None,
            is_parent_company=False,
            company_type=data['type'],
            created_by=users[0]
        )
        companies.append(company)
    
    print(f"Created {len(companies)} companies")
    return companies

def create_accounts(companies, users):
    """Create chart of accounts"""
    print("Creating accounts...")
    accounts = []
    
    for company in companies[:3]:  # Create accounts for first 3 companies
        # Asset accounts
        cash = Account.objects.create(
            company=company,
            name="Cash",
            account_number=f"{company.id}1001",
            account_type="asset",
            is_group=False,
            created_by=users[0]
        )
        accounts.append(cash)
        
        bank = Account.objects.create(
            company=company,
            name="Bank Account",
            account_number=f"{company.id}1002",
            account_type="asset",
            is_group=False,
            created_by=users[0]
        )
        accounts.append(bank)
        
        accounts_receivable = Account.objects.create(
            company=company,
            name="Accounts Receivable",
            account_number=f"{company.id}1100",
            account_type="asset",
            is_group=False,
            created_by=users[0]
        )
        accounts.append(accounts_receivable)
        
        # Liability accounts
        accounts_payable = Account.objects.create(
            company=company,
            name="Accounts Payable",
            account_number=f"{company.id}2001",
            account_type="liability",
            is_group=False,
            created_by=users[0]
        )
        accounts.append(accounts_payable)
        
        # Equity account
        capital = Account.objects.create(
            company=company,
            name="Owner's Capital",
            account_number=f"{company.id}3001",
            account_type="equity",
            is_group=False,
            created_by=users[0]
        )
        accounts.append(capital)
        
        # Income accounts
        sales = Account.objects.create(
            company=company,
            name="Sales Revenue",
            account_number=f"{company.id}4001",
            account_type="income",
            is_group=False,
            created_by=users[0]
        )
        accounts.append(sales)
        
        # Expense accounts
        expenses = Account.objects.create(
            company=company,
            name="Operating Expenses",
            account_number=f"{company.id}5001",
            account_type="expense",
            is_group=False,
            created_by=users[0]
        )
        accounts.append(expenses)
        
        salaries = Account.objects.create(
            company=company,
            name="Salaries & Wages",
            account_number=f"{company.id}5100",
            account_type="expense",
            is_group=False,
            created_by=users[0]
        )
        accounts.append(salaries)
    
    print(f"Created {len(accounts)} accounts")
    return accounts

def create_cost_centers(companies, users):
    """Create cost centers"""
    print("Creating cost centers...")
    cost_centers = []
    
    for company in companies[:3]:
        centers_data = [
            {'name': 'Operations', 'number': 'CC-001'},
            {'name': 'Marketing', 'number': 'CC-002'},
            {'name': 'IT Department', 'number': 'CC-003'},
            {'name': 'Sales', 'number': 'CC-004'},
        ]
        
        for data in centers_data:
            cc = CostCenter.objects.create(
                company=company,
                name=data['name'],
                cost_center_number=data['number'],
                is_group=False,
                is_disabled=False
            )
            cost_centers.append(cc)
    
    print(f"Created {len(cost_centers)} cost centers")
    return cost_centers

def create_budgets(companies, cost_centers, users, accounts):
    """Create budgets"""
    print("Creating budgets...")
    budgets = []
    
    # Get expense accounts for budgets
    expense_accounts = [acc for acc in accounts if acc.account_type == 'expense']
    
    for i, company in enumerate(companies[:3]):
        if i < len(cost_centers) and expense_accounts:
            budget = Budget.objects.create(
                company=company,
                series=f"BUD-{company.abbreviation}-2025",
                budget_against="cost_center",
                fiscal_year_from="2025-2026",
                fiscal_year_to="2025-2026",
                distribution="monthly",
                cost_center=cost_centers[i] if cost_centers else None,
                account=expense_accounts[i % len(expense_accounts)],
                budget_amount=Decimal(f"{100000 + (i * 50000)}.00")
            )
            budgets.append(budget)
    
    print(f"Created {len(budgets)} budgets")
    return budgets

def create_suppliers(companies, users):
    """Create suppliers"""
    print("Creating suppliers...")
    suppliers = []
    
    suppliers_data = [
        {
            'name': 'ABC Supplies Inc',
            'gstin': 'GSTIN-ABC-001',
            'type': 'company',
            'category': 'registered',
            'email': 'contact@abcsupplies.com',
            'country': 'USA'
        },
        {
            'name': 'XYZ Trading Co',
            'gstin': 'GSTIN-XYZ-002',
            'type': 'company',
            'category': 'registered',
            'email': 'sales@xyztrading.com',
            'country': 'India'
        },
        {
            'name': 'Tech Solutions Ltd',
            'gstin': 'GSTIN-TECH-003',
            'type': 'company',
            'category': 'registered_composition',
            'email': 'info@techsolutions.com',
            'country': 'USA'
        },
        {
            'name': 'Global Imports LLC',
            'gstin': 'GSTIN-GLB-004',
            'type': 'company',
            'category': 'registered',
            'email': 'orders@globalimports.com',
            'country': 'USA'
        },
        {
            'name': 'Office Supplies Pro',
            'gstin': '',
            'type': 'company',
            'category': 'unregistered',
            'email': 'contact@officesupplies.com',
            'country': 'USA'
        }
    ]
    
    for data in suppliers_data:
        supplier = Supplier.objects.create(
            company=companies[0],
            name=data['name'],
            gstin_uin=data['gstin'],
            supplier_type=data['type'],
            gst_category=data['category'],
            contact_email=data['email'],
            contact_first_name='Contact',
            contact_last_name='Person',
            contact_mobile='+1-555-1234',
            country=data['country'],
            city='Business City',
            address_line1='123 Business St',
            postal_code='12345',
            created_by=users[0]
        )
        suppliers.append(supplier)
    
    print(f"Created {len(suppliers)} suppliers")
    return suppliers

def create_customers(companies, users):
    """Create customers"""
    print("Creating customers...")
    customers = []
    
    customers_data = [
        {
            'name': 'Acme Corporation',
            'gstin': 'GSTIN-ACME-001',
            'type': 'company',
            'category': 'registered',
            'email': 'billing@acmecorp.com',
            'country': 'USA'
        },
        {
            'name': 'Retail Mart Inc',
            'gstin': 'GSTIN-RTL-002',
            'type': 'company',
            'category': 'registered',
            'email': 'accounts@retailmart.com',
            'country': 'USA'
        },
        {
            'name': 'Tech Innovations Pvt Ltd',
            'gstin': 'GSTIN-TECH-003',
            'type': 'company',
            'category': 'registered',
            'email': 'finance@techinnovations.in',
            'country': 'India'
        },
        {
            'name': 'Small Business LLC',
            'gstin': '',
            'type': 'company',
            'category': 'unregistered',
            'email': 'owner@smallbiz.com',
            'country': 'USA'
        }
    ]
    
    for data in customers_data:
        customer = Customer.objects.create(
            company=companies[0],
            name=data['name'],
            gstin_uin=data['gstin'],
            customer_type=data['type'],
            gst_category=data['category'],
            contact_email=data['email'],
            contact_first_name='Contact',
            contact_last_name='Person',
            contact_mobile='+1-555-5678',
            country=data['country'],
            city='Customer City',
            address_line1='456 Customer Ave',
            postal_code='54321',
            created_by=users[0]
        )
        customers.append(customer)
    
    print(f"Created {len(customers)} customers")
    return customers

def create_invoices(companies, suppliers, customers, users):
    """Create invoices"""
    print("Creating invoices...")
    invoices = []
    
    # Supplier invoices (purchases)
    for i in range(5):
        invoice = Invoice.objects.create(
            company=companies[0],
            invoice_id=f"INV-SUPP-{2025001 + i}",
            invoice_number=f"SUPP-{i+1}/2025",
            date=date(2025, 1, 1) + timedelta(days=i * 5),
            supplier=suppliers[i % len(suppliers)],
            supplier_vat=suppliers[i % len(suppliers)].gstin_uin,
            amount_before_vat=Decimal(str(1000 + i * 500)),
            total_vat=Decimal(str((1000 + i * 500) * 0.15)),
            total_amount=Decimal(str((1000 + i * 500) * 1.15)),
            status=['draft', 'sent', 'paid'][i % 3],
            qr_code_present=False,
            created_by=users[0]
        )
        invoices.append(invoice)
    
    # Customer invoices (sales)
    for i in range(5):
        invoice = Invoice.objects.create(
            company=companies[0],
            invoice_id=f"INV-CUST-{2025001 + i}",
            invoice_number=f"SALE-{i+1}/2025",
            date=date(2025, 1, 10) + timedelta(days=i * 7),
            customer=customers[i % len(customers)],
            customer_vat=customers[i % len(customers)].gstin_uin,
            amount_before_vat=Decimal(str(2000 + i * 800)),
            total_vat=Decimal(str((2000 + i * 800) * 0.15)),
            total_amount=Decimal(str((2000 + i * 800) * 1.15)),
            status=['sent', 'paid', 'paid'][i % 3],
            qr_code_present=True,
            created_by=users[0]
        )
        invoices.append(invoice)
    
    print(f"Created {len(invoices)} invoices")
    return invoices

def create_journal_entries(companies, accounts, users):
    """Create journal entries"""
    print("Creating journal entries...")
    entries = []
    
    for i in range(10):
        company = companies[i % len(companies[:3])]
        company_accounts = [acc for acc in accounts if acc.company == company]
        
        if len(company_accounts) >= 2:
            # Debit entry
            debit_entry = JournalEntry.objects.create(
                company=company,
                entry_number=f"JE-{company.abbreviation}-{2025001 + i}",
                date=date(2025, 1, 1) + timedelta(days=i * 3),
                account=company_accounts[i % len(company_accounts)],
                debit_amount=Decimal(str(500 + i * 100)),
                credit_amount=Decimal('0.00'),
                description=f"Journal entry debit #{i+1}",
                created_by=users[0]
            )
            entries.append(debit_entry)
            
            # Corresponding credit entry
            credit_entry = JournalEntry.objects.create(
                company=company,
                entry_number=f"JE-{company.abbreviation}-{2025001 + i + 100}",
                date=date(2025, 1, 1) + timedelta(days=i * 3),
                account=company_accounts[(i + 1) % len(company_accounts)],
                debit_amount=Decimal('0.00'),
                credit_amount=Decimal(str(500 + i * 100)),
                description=f"Journal entry credit #{i+1}",
                created_by=users[0]
            )
            entries.append(credit_entry)
    
    print(f"Created {len(entries)} journal entries")
    return entries

def create_tax_data(companies, customers):
    """Create tax categories, templates, and rules"""
    print("Creating tax data...")
    
    # Tax Categories
    tax_categories = []
    for title in ['Standard Rate', 'Reduced Rate', 'Zero Rate', 'Exempt']:
        category = TaxCategory.objects.create(title=title)
        tax_categories.append(category)
    
    # Tax Templates
    tax_templates = []
    templates_data = [
        {'title': 'Sales Tax 15%', 'rate': 15.0, 'treatment': 'taxable'},
        {'title': 'VAT Standard 20%', 'rate': 20.0, 'treatment': 'taxable'},
        {'title': 'GST 18%', 'rate': 18.0, 'treatment': 'taxable'},
        {'title': 'Nil Rated', 'rate': 0.0, 'treatment': 'nil_rated'},
    ]
    
    for data in templates_data:
        template = TaxItemTemplate.objects.create(
            company=companies[0],
            title=data['title'],
            gst_rate=Decimal(str(data['rate'])),
            gst_treatment=data['treatment']
        )
        tax_templates.append(template)
    
    # Tax Rules
    tax_rules = []
    for i, customer in enumerate(customers[:3]):
        rule = TaxRule.objects.create(
            company=companies[0],
            tax_type='sales',
            sales_tax_template=tax_templates[i % len(tax_templates)],
            customer=customer,
            tax_category=tax_categories[i % len(tax_categories)],
            billing_country=customer.country,
            from_date=date(2025, 1, 1),
            to_date=date(2025, 12, 31),
            priority=i + 1
        )
        tax_rules.append(rule)
    
    print(f"Created {len(tax_categories)} tax categories, {len(tax_templates)} templates, {len(tax_rules)} rules")
    return tax_categories, tax_templates, tax_rules

def create_accounting_dimensions(companies):
    """Create accounting dimensions"""
    print("Creating accounting dimensions...")
    dimensions = []
    
    dimensions_data = [
        'Department',
        'Project',
        'Region',
    ]
    
    for name in dimensions_data:
        dimension = AccountingDimension.objects.create(
            name=name
        )
        dimensions.append(dimension)
    
    print(f"Created {len(dimensions)} accounting dimensions")
    return dimensions

def create_cost_center_allocations(cost_centers, companies):
    """Create cost center allocations"""
    print("Creating cost center allocations...")
    allocations = []
    
    if len(cost_centers) >= 3 and len(companies) >= 1:
        for i in range(3):
            allocation = CostCenterAllocation.objects.create(
                cost_center=cost_centers[i],
                company=companies[0],
                valid_from=date(2025, 1, 1)
            )
            allocations.append(allocation)
    
    print(f"Created {len(allocations)} cost center allocations")
    return allocations

def create_tax_withholding_data():
    """Create tax withholding categories and accounts"""
    print("Creating tax withholding data...")
    
    # Tax Withholding Categories
    categories = []
    for name in ['TDS on Salary', 'TDS on Professional Services', 'TDS on Rent', 'TCS on Sales']:
        category = TaxWithholdingCategory.objects.create(
            name=name,
            category_name=name,
            deduct_tax_on_basis='Net Total',
            round_off_tax_amount=True
        )
        categories.append(category)
    
    print(f"Created {len(categories)} tax withholding categories")
    return categories

def main():
    """Main function to populate all data"""
    print("=" * 60)
    print("Starting database population...")
    print("=" * 60)
    
    # Clear existing data to avoid duplicates
    print("Clearing existing data...")
    
    # Delete in reverse order of dependencies
    for model in [DeductionCertificate, TaxCategoryAccount, TaxWithholdingCategory,
                  CostCenterAllocation, AccountingDimension, TaxRule, TaxItemTemplate,
                  TaxCategory, JournalEntry, Invoice, Customer, Supplier, Budget,
                  CostCenter, Account, Company]:
        count = model.objects.count()
        if count > 0:
            model.objects.all().delete()
            print(f"  Deleted {count} {model.__name__} records")
    
    # Delete user profiles and users (except superuser if you want to keep it)
    UserProfile.objects.all().delete()
    User.objects.filter(is_superuser=False).delete()
    print(f"  Deleted all UserProfiles and non-superuser Users")
    
    # Create data in correct order (respecting foreign keys)
    users = create_users()
    companies = create_companies(users)
    accounts = create_accounts(companies, users)
    cost_centers = create_cost_centers(companies, users)
    budgets = create_budgets(companies, cost_centers, users, accounts)
    suppliers = create_suppliers(companies, users)
    customers = create_customers(companies, users)
    invoices = create_invoices(companies, suppliers, customers, users)
    journal_entries = create_journal_entries(companies, accounts, users)
    tax_categories, tax_templates, tax_rules = create_tax_data(companies, customers)
    dimensions = create_accounting_dimensions(companies)
    allocations = create_cost_center_allocations(cost_centers, companies)
    withholding_categories = create_tax_withholding_data()
    
    print("=" * 60)
    print("Database population completed successfully!")
    print("=" * 60)
    print(f"\nSummary:")
    print(f"  Users: {len(users)}")
    print(f"  Companies: {len(companies)}")
    print(f"  Accounts: {len(accounts)}")
    print(f"  Cost Centers: {len(cost_centers)}")
    print(f"  Budgets: {len(budgets)}")
    print(f"  Suppliers: {len(suppliers)}")
    print(f"  Customers: {len(customers)}")
    print(f"  Invoices: {len(invoices)}")
    print(f"  Journal Entries: {len(journal_entries)}")
    print(f"  Tax Categories: {len(tax_categories)}")
    print(f"  Tax Templates: {len(tax_templates)}")
    print(f"  Tax Rules: {len(tax_rules)}")
    print(f"  Accounting Dimensions: {len(dimensions)}")
    print(f"  Cost Center Allocations: {len(allocations)}")
    print(f"  Tax Withholding Categories: {len(withholding_categories)}")
    print("\nYou can now run the Django server and test the MCP server!")

if __name__ == '__main__':
    main()
