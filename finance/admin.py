from django.contrib import admin

from finance.models import Account, AccountingDimension, Budget, Company, CostCenter, CostCenterAllocation, Customer, Invoice, JournalEntry, Supplier

admin.site.register(Invoice)
admin.site.register(Company)
admin.site.register(Account)
admin.site.register(JournalEntry)
admin.site.register(Supplier)
admin.site.register(Customer)
admin.site.register(Budget)
admin.site.register(CostCenter)
admin.site.register(AccountingDimension)
admin.site.register(CostCenterAllocation)

# Register your models here.
