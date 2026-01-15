from django.contrib import admin

from finance.models import Account, Budget, Company, Customer, Invoice, JournalEntry, Supplier

admin.site.register(Invoice)
admin.site.register(Company)
admin.site.register(Account)
admin.site.register(JournalEntry)
admin.site.register(Supplier)
admin.site.register(Customer)
admin.site.register(Budget)

# Register your models here.
