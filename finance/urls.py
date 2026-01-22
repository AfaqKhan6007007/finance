from django.urls import path

from finance.models import TaxWithholdingCategory

from .views import AccountingDimensionCreate, AccountingDimensionDelete, AccountingDimensionEdit, AccountingDimensions, BankAccountCreate, BankAccountDelete, BankAccountEdit, BankAccounts, Budgets,BudgetCreate,BudgetEdit, BudgetDelete, CostCenterAllocations, CostCenterAllocationsCreate, CostCenterAllocationsDelete, CostCenterAllocationsEdit,CostCenterDelete, CostCenterCreate, CostCenterEdit, CostCenters, CustomerCreate, CustomerDelete, CustomerEdit, Customers, DeductionCertificateCreate, DeductionCertificateDelete, DeductionCertificateEdit, DeductionCertificateView, Login, Signup, Logout, Dashboard, Journal, TaxCategories, TaxCategoryCreate, TaxCategoryDelete, TaxCategoryEdit, TaxItemTemplates, TaxItemTemplatesCreate, TaxItemTemplatesEdit, TaxItemTemplatesDelete, TaxRuleView, TaxRulesCreate, TaxRulesDelete, TaxRulesEdit, TaxWithholdingCategoryCreate, TaxWithholdingCategoryDelete, TaxWithholdingCategoryEdit, TaxWithholdingCategoryList, TrialBalance, Ledger, Companies, Payables, Invoices, Receivables, InvoiceScan, Reports, CompanyCreate, CompanyEdit, CompanyDelete, Accounts,AccountCreate,AccountEdit, AccountDelete, InvoiceCreate, InvoiceEdit, InvoiceDelete, JournalCreate, JournalEdit, JournalDelete, Suppliers, SupplierCreate, SupplierEdit, SupplierDelete, create_invoice

urlpatterns = [
     # ============ Authentication ============
    path('login/', Login.as_view(), name='finance-login'),
    path('signup/', Signup.as_view(), name='finance-signup'),
    path('logout/', Logout.as_view(), name='finance-logout'),
    
    
     # ============ Account Management ============
    path('accounts/', Accounts.as_view(), name='finance-accounts'),
    path('accounts/add/', AccountCreate.as_view(), name='finance-account-create'),
    path('accounts/<int:pk>/edit/', AccountEdit.as_view(), name='finance-account-edit'),
    path('accounts/<int:pk>/delete/', AccountDelete.as_view(), name='finance-account-delete'),

    # ============ Supplier Management ============
    path('suppliers/', Suppliers.as_view(), name='finance-suppliers'),
    path('suppliers/new/', SupplierCreate.as_view(), name='finance-supplier-create'),
    path('suppliers/<int:pk>/edit/', SupplierEdit.as_view(), name='finance-supplier-edit'),
    path('suppliers/<int:pk>/delete/', SupplierDelete.as_view(), name='finance-supplier-delete'),
     
     
    # ============ Customer Management ============
    path('customers/', Customers.as_view(), name='finance-customers'),
    path('customers/new/', CustomerCreate.as_view(), name='finance-customer-create'),
    path('customers/<int:pk>/edit/', CustomerEdit.as_view(), name='finance-customer-edit'),
    path('customers/<int:pk>/delete/', CustomerDelete.as_view(), name='finance-customer-delete'),
     

     # ============ Journal Entry Management ============
    path('journal/', Journal.as_view(), name='finance-journal'),
    path('journal/add/', JournalCreate.as_view(), name='finance-journal-create'),
    path('journal/<int:pk>/edit/', JournalEdit.as_view(), name='finance-journal-edit'),
    path('journal/<int:pk>/delete/', JournalDelete.as_view(), name='finance-journal-delete'),

    # ============ Main Pages ============
    path('dashboard/', Dashboard.as_view(), name='finance-dashboard'),
    path('trial/', TrialBalance.as_view(), name='finance-trial'),
    path('ledger/', Ledger.as_view(), name='finance-ledger'),
    path('reports/', Reports.as_view(), name='finance-reports'),
    path('scan/', InvoiceScan.as_view(), name='finance-scan'),
    path('scan/scan/', create_invoice, name='finance-invoice-scan'),
    
    # ============ Company/Account Management ============
    path('companies/', Companies.as_view(), name='finance-companies'),
    path('companies/add/', CompanyCreate.as_view(), name='finance-company-create'),
    path('companies/<int:pk>/edit/', CompanyEdit.as_view(), name='finance-company-edit'),
    path('companies/<int:pk>/delete/', CompanyDelete.as_view(), name='finance-company-delete'),
    
    # ============ Invoice Management ============
    path('invoices/', Invoices.as_view(), name='finance-invoices'),
    path('invoices/add/', InvoiceCreate.as_view(), name='finance-invoice-create'),
    path('invoices/<int:pk>/edit/', InvoiceEdit.as_view(), name='finance-invoice-edit'),
    path('invoices/<int:pk>/delete/', InvoiceDelete.as_view(), name='finance-invoice-delete'),
    
    # ============ Accounting Modules ============
    path('payables/', Payables.as_view(), name='finance-payables'),
    path('receivables/', Receivables.as_view(), name='finance-receivables'),

    path('budgets/', Budgets.as_view(), name='finance-budgets'),
    path('budgets/new/', BudgetCreate.as_view(), name='finance-budget-create'),
    path('budgets/<int:pk>/edit/', BudgetEdit.as_view(), name='finance-budget-edit'),
    path('budgets/<int:pk>/delete/', BudgetDelete.as_view(), name='finance-budget-delete'),

    path('cost-center/', CostCenters.as_view(), name='finance-cost-centers'),
    path('cost-center/new/', CostCenterCreate.as_view(), name='finance-cost-center-create'),
    path('cost-center/<int:pk>/edit/', CostCenterEdit.as_view(), name='finance-cost-center-edit'),
    path('cost-center/<int:pk>/delete/', CostCenterDelete.as_view(), name='finance-cost-center-delete'),

    path('accounting-dimensions/', AccountingDimensions.as_view(), name='finance-accounting-dimensions'),
    path('accounting-dimensions/new/', AccountingDimensionCreate.as_view(), name='finance-accounting-dimension-create'),
    path('accounting-dimensions/<int:pk>/edit/', AccountingDimensionEdit.as_view(), name='finance-accounting-dimension-edit'),
    path('accounting-dimensions/<int:pk>/delete/', AccountingDimensionDelete.as_view(), name='finance-accounting-dimension-delete'),

    path('cost-center-allocations/', CostCenterAllocations.as_view(), name='finance-cost-center-allocations'),
    path('cost-center-allocations/new/', CostCenterAllocationsCreate.as_view(), name='finance-cost-center-allocation-create'),
    path('cost-center-allocations/<int:pk>/edit/', CostCenterAllocationsEdit.as_view(), name='finance-cost-center-allocation-edit'),
    path('cost-center-allocations/<int:pk>/delete/', CostCenterAllocationsDelete.as_view(), name='finance-cost-center-allocation-delete'),


    path('tax-item-templates/', TaxItemTemplates.as_view(), name='finance-tax-item-templates'),
    path('tax-item-templates/new/', TaxItemTemplatesCreate.as_view(), name='finance-tax-item-template-create'),
    path('tax-item-templates/<int:pk>/edit/', TaxItemTemplatesEdit.as_view(), name='finance-tax-item-template-edit'),
    path('tax-item-templates/<int:pk>/delete/', TaxItemTemplatesDelete.as_view(), name='finance-tax-item-template-delete'),

    path('tax-category/', TaxCategories.as_view(), name='finance-tax-categories'),
    path('tax-category/new/', TaxCategoryCreate.as_view(), name='finance-tax-category-create'),
    path('tax-category/<int:pk>/edit/', TaxCategoryEdit.as_view(), name='finance-tax-category-edit'),
    path('tax-category/<int:pk>/delete/', TaxCategoryDelete.as_view(), name='finance-tax-category-delete'),

    path('tax-rules/', TaxRuleView.as_view(), name='finance-tax-rules'),
    path('tax-rules/new/', TaxRulesCreate.as_view(), name='finance-tax-rule-create'),
    path('tax-rules/<int:pk>/edit/', TaxRulesEdit.as_view(), name='finance-tax-rule-edit'),
    path('tax-rules/<int:pk>/delete/', TaxRulesDelete.as_view(), name='finance-tax-rule-delete'),

    path('tax-withholding-categories/', TaxWithholdingCategoryList.as_view(), name='finance-tax-withholding-categories'),
    path('tax-withholding-categories/new/', TaxWithholdingCategoryCreate.as_view(), name='finance-tax-withholding-category-create'),
    path('tax-withholding-categories/<int:pk>/edit/', TaxWithholdingCategoryEdit.as_view(), name='finance-tax-withholding-category-edit'),
    path('tax-withholding-categories/<int:pk>/delete/', TaxWithholdingCategoryDelete.as_view(), name='finance-tax-withholding-category-delete'),

    path(
        'deduction-certificates/',
        DeductionCertificateView.as_view(),
        name='finance-deduction-certificates'
    ),
    path(
        'deduction-certificates/new/',
        DeductionCertificateCreate.as_view(),
        name='finance-deduction-certificate-create'
    ),
    path(
        'deduction-certificates/<int:pk>/edit/',
        DeductionCertificateEdit.as_view(),
        name='finance-deduction-certificate-edit'
    ),
    path(
        'deduction-certificates/<int:pk>/delete/',
        DeductionCertificateDelete.as_view(),
        name='finance-deduction-certificate-delete'
    ),

    path('bank-accounts/', BankAccounts.as_view(), name='finance-bank-accounts'),
    path('bank-accounts/new/', BankAccountCreate.as_view(), name='finance-bank-account-create'),
    path('bank-accounts/<int:pk>/edit/', BankAccountEdit.as_view(), name='finance-bank-account-edit'),
    path('bank-accounts/<int:pk>/delete/', BankAccountDelete.as_view(), name='finance-bank-account-delete'),
]