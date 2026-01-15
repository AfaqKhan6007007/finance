from django.contrib import admin

from finance.models import Account, Budget, Company, CostCenter, Customer, Invoice, JournalEntry, Supplier

admin.site.register(Invoice)
admin.site.register(Company)
admin.site.register(Account)
admin.site.register(JournalEntry)
admin.site.register(Supplier)
admin.site.register(Customer)
admin.site.register(Budget)
admin.site.register(CostCenter)

# Register your models here.
