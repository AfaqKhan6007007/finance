from django.db import models
from django.contrib.auth.models import User

# Remove the Login and Signup models - they're not needed! 
# Django's built-in User model handles this already

# If you need additional user information, create a Profile model: 
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # Add any extra fields you need
    phone_number = models.CharField(max_length=20, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)

class Company(models.Model):
    # Basic Information
    name = models.CharField(max_length=200, verbose_name="Company Name")
    abbreviation = models.CharField(max_length=50, blank=True, verbose_name="Abbreviation")
    country = models.CharField(max_length=100, verbose_name="Country")
    date_of_establishment = models.DateField(null=True, blank=True, verbose_name="Date of Establishment")
    
    # Currency and Financial
    default_currency = models.CharField(max_length=10, default="USD", verbose_name="Default Currency")
    tax_id = models.CharField(max_length=100, blank=True, verbose_name="Tax ID")
    
    # Company Details
    default_letter_head = models.CharField(max_length=200, blank=True, verbose_name="Default Letter Head")
    domain = models.CharField(max_length=200, blank=True, verbose_name="Domain")
    
    # Parent Company
    parent_company = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='subsidiaries',
        verbose_name="Parent Company"
    )
    is_parent_company = models.BooleanField(default=False, verbose_name="Is Parent Company (Group)")
    
    # Registration
    registration_details = models.TextField(blank=True, verbose_name="Registration Details")
    
    # Legacy fields (keep for backward compatibility)
    account_number = models.CharField(max_length=50, blank=True, verbose_name="Account Number")
    is_disabled = models.BooleanField(default=False, verbose_name="Disable")
    is_group = models.BooleanField(default=False, verbose_name="Is Group")
    
    company_type = models.CharField(
        max_length=20, 
        choices=[
            ('regular', 'Regular'),
            ('subsidiary', 'Subsidiary'),
            ('branch', 'Branch'),
            ('holding', 'Holding'),
        ],
        default='regular',
        blank=True
    )
    
    account_type = models.CharField(
        max_length=20,
        choices=[
            ('asset', 'Asset'),
            ('liability', 'Liability'),
            ('equity', 'Equity'),
            ('income', 'Income'),
            ('expense', 'Expense'),
        ],
        blank=True,
        verbose_name="Account Type"
    )
    
    tax_rate = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=0.00,
        blank=True,
        verbose_name="Tax Rate"
    )
    
    balance_must_be = models.CharField(
        max_length=10,
        choices=[
            ('debit', 'Debit'),
            ('credit', 'Credit'),
            ('both', 'Both'),
        ],
        default='both',
        blank=True,
        verbose_name="Balance Must Be"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        verbose_name_plural = "Companies"
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
class Account(models.Model):
    ACCOUNT_TYPE_CHOICES = [
        ('asset', 'Asset'),
        ('liability', 'Liability'),
        ('equity', 'Equity'),
        ('income', 'Income'),
        ('expense', 'Expense'),
    ]
    
    BALANCE_TYPE_CHOICES = [
        ('debit', 'Debit'),
        ('credit', 'Credit'),
        ('both', 'Both'),
    ]
    
    # Basic Information
    name = models.CharField(max_length=200, verbose_name="Account Name")
    account_number = models.CharField(max_length=50, blank=True, verbose_name="Account Number")
    is_disabled = models.BooleanField(default=False, verbose_name="Disable")
    is_group = models.BooleanField(default=False, verbose_name="Is Group")
    
    # Company Relationship
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='accounts',
        verbose_name="Company"
    )
    
    # Currency
    currency = models.CharField(max_length=10, default="USD", blank=True, verbose_name="Currency")
    
    # Parent Account
    parent_account = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sub_accounts',
        verbose_name="Parent Account"
    )
    
    # Account Type and Balance
    account_type = models.CharField(
        max_length=20,
        choices=ACCOUNT_TYPE_CHOICES,
        blank=True,
        verbose_name="Account Type"
    )
    
    tax_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        blank=True,
        verbose_name="Tax Rate"
    )
    
    balance_must_be = models.CharField(
        max_length=10,
        choices=BALANCE_TYPE_CHOICES,
        default='both',
        blank=True,
        verbose_name="Balance Must Be"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        verbose_name_plural = "Accounts"
        ordering = ['-created_at']
        unique_together = ['company', 'account_number']  # Prevent duplicate account numbers per company
    
    def __str__(self):
        if self.account_number:
            return f"{self.account_number} - {self.name}"
        return self.name
    
class Invoice(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
        ('return', 'Return'),
    ]
    
    # Basic Information
    invoice_id = models.CharField(max_length=50, unique=True, verbose_name="Invoice ID")
    invoice_number = models.CharField(max_length=50, verbose_name="Invoice Number")
    date = models.DateField(verbose_name="Invoice Date")
    
    # Supplier Information
    supplier = models.ForeignKey(
        'Supplier',
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name='invoices',
        verbose_name="Supplier",
    )
    supplier_vat = models.CharField(max_length=50, blank=True, verbose_name="Supplier VAT")
    
    # Customer Information
    customer = models.ForeignKey(
        'Customer',
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name='invoices',
        verbose_name="Customer",
    )
    customer_vat = models.CharField(max_length=50, blank=True, verbose_name="Customer VAT")
    
    # Financial Information
    amount_before_vat = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name="Amount Before VAT"
    )
    total_vat = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name="Total VAT"
    )
    total_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name="Total Amount"
    )
    
    # QR Code
    qr_code_present = models.BooleanField(default=False, verbose_name="QR Code Present")
    qr_code_data = models.TextField(blank=True, verbose_name="QR Code Data")
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name="Status"
    )
    
    # Company Relationship
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='invoices',
        null=True,
        blank=True,
        verbose_name="Company"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        verbose_name_plural = "Invoices"
        ordering = ['-date', '-created_at']
    
    def __str__(self):
        return f"{self.invoice_number} - {self.supplier.name if self.supplier else 'Unknown Supplier'}"
    
    def save(self, *args, **kwargs):
        # If supplier_vat blank and supplier has gstin_uin, copy it
        if self.supplier and not self.supplier_vat:
            gst = getattr(self.supplier, 'gstin_uin', None)
            if gst:
                self.supplier_vat = gst

        # If customer_vat blank and customer has gstin_uin, copy it
        if self.customer and not self.customer_vat:
            gst = getattr(self.customer, 'gstin_uin', None)
            if gst:
                self.customer_vat = gst

        # Auto-calculate total_amount if not provided
        if not self.total_amount:
            self.total_amount = (self.amount_before_vat or 0) + (self.total_vat or 0)

        super().save(*args, **kwargs)

class JournalEntry(models.Model):
    # Entry Number (auto-generated)
    entry_number = models.CharField(max_length=50, unique=True, verbose_name="Entry Number")
    
    # Date
    date = models.DateField(verbose_name="Posting Date")
    
    # Account Relationship
    account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        related_name='journal_entries',
        verbose_name="Account"
    )
    
    # Amounts
    debit_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0.00,
        verbose_name="Debit Amount"
    )
    
    credit_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0.00,
        verbose_name="Credit Amount"
    )
    
    # Description
    description = models.TextField(blank=True, verbose_name="Description")
    
    # Company Relationship
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='journal_entries',
        null=True,
        blank=True,
        verbose_name="Company"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        verbose_name_plural = "Journal Entries"
        ordering = ['-date', '-created_at']
    
    def __str__(self):
        return f"{self.entry_number} - {self.account.name}"
    
    def save(self, *args, **kwargs):
        # Auto-generate entry number if not provided
        if not self.entry_number:
            last_entry = JournalEntry.objects.order_by('-id').first()
            if last_entry and last_entry.entry_number.startswith('JE'):
                try:
                    last_number = int(last_entry.entry_number[2:])
                    self.entry_number = f"JE{str(last_number + 1).zfill(5)}"
                except ValueError:
                    self.entry_number = "JE00001"
            else:
                self.entry_number = "JE00001"
        super().save(*args, **kwargs)

class Supplier(models.Model):
    SUPPLIER_TYPE_CHOICES = [
        ('company', 'Company'),
        ('individual', 'Individual'),
        ('partnership', 'Partnership'),
    ]

    GST_CATEGORY_CHOICES = [
        ('registered', 'Registered Regular'),
        ('registered_composition', 'Registered Composition'),
        ('unregistered', 'Unregistered'),
        ('sez', 'SEZ'),
        ('overseas', 'Overseas'),
        ('deemed_export', 'Deemed Export'),
        ('uin', 'UIN Holders'),
        ('tax_deductor', 'Tax Deductor'),
        ('tax_collector', 'Tax Collector'),
        ('input_service_distributor', 'Input Service Distributor'),
        
    ]

    # Basic
    gstin_uin = models.CharField(max_length=30, blank=True, verbose_name="GSTIN / UIN", help_text="Optional GSTIN for autofill")
    name = models.CharField(max_length=200, verbose_name="Supplier Name")
    supplier_type = models.CharField(max_length=20, choices=SUPPLIER_TYPE_CHOICES, default='company', verbose_name="Supplier Type")
    gst_category = models.CharField(max_length=40, choices=GST_CATEGORY_CHOICES, default='unregistered', verbose_name="GST Category")

    # Primary contact details
    contact_first_name = models.CharField(max_length=100, blank=True, verbose_name="First Name")
    contact_last_name = models.CharField(max_length=100, blank=True, verbose_name="Last Name")
    contact_email = models.EmailField(max_length=254, blank=True, verbose_name="Email ID")
    contact_mobile = models.CharField(max_length=30, blank=True, verbose_name="Mobile Number")

    # Address
    preferred_billing = models.BooleanField(default=False, verbose_name="Preferred Billing Address")
    preferred_shipping = models.BooleanField(default=False, verbose_name="Preferred Shipping Address")
    postal_code = models.CharField(max_length=20, blank=True, verbose_name="Postal Code")
    city = models.CharField(max_length=120, blank=True, verbose_name="City/Town")
    address_line1 = models.CharField(max_length=255, blank=True, verbose_name="Address Line 1")
    address_line2 = models.CharField(max_length=255, blank=True, verbose_name="Address Line 2")
    state = models.CharField(max_length=100, blank=True, verbose_name="State/Province")
    country = models.CharField(max_length=100, blank=True, default='Pakistan', verbose_name="Country")

    # Relationship to Company (optional)
    company = models.ForeignKey('Company', on_delete=models.SET_NULL, null=True, blank=True, related_name='suppliers')

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = "Supplier"
        verbose_name_plural = "Suppliers"
        ordering = ['-created_at']
        unique_together = [('company', 'name')]

    def __str__(self):
        return self.name
    

class Customer(models.Model):
    CUSTOMER_TYPE_CHOICES = [
        ('company', 'Company'),
        ('individual', 'Individual'),
        ('partnership', 'Partnership'),
    ]

    GST_CATEGORY_CHOICES = [
        ('registered', 'Registered Regular'),
        ('registered_composition', 'Registered Composition'),
        ('unregistered', 'Unregistered'),
        ('sez', 'SEZ'),
        ('overseas', 'Overseas'),
        ('deemed_export', 'Deemed Export'),
        ('uin', 'UIN Holders'),
        ('tax_deductor', 'Tax Deductor'),
        ('tax_collector', 'Tax Collector'),
        ('input_service_distributor', 'Input Service Distributor'),
        
    ]

    # Basic
    gstin_uin = models.CharField(max_length=30, blank=True, verbose_name="GSTIN / UIN", help_text="Optional GSTIN for autofill")
    name = models.CharField(max_length=200, verbose_name="Customer Name")
    customer_type = models.CharField(max_length=20, choices=CUSTOMER_TYPE_CHOICES, default='company', verbose_name="Customer Type")
    gst_category = models.CharField(max_length=40, choices=GST_CATEGORY_CHOICES, default='unregistered', verbose_name="GST Category")

    # Primary contact details
    contact_first_name = models.CharField(max_length=100, blank=True, verbose_name="First Name")
    contact_last_name = models.CharField(max_length=100, blank=True, verbose_name="Last Name")
    contact_email = models.EmailField(max_length=254, blank=True, verbose_name="Email ID")
    contact_mobile = models.CharField(max_length=30, blank=True, verbose_name="Mobile Number")

    # Address
    preferred_billing = models.BooleanField(default=False, verbose_name="Preferred Billing Address")
    preferred_shipping = models.BooleanField(default=False, verbose_name="Preferred Shipping Address")
    postal_code = models.CharField(max_length=20, blank=True, verbose_name="Postal Code")
    city = models.CharField(max_length=120, blank=True, verbose_name="City/Town")
    address_line1 = models.CharField(max_length=255, blank=True, verbose_name="Address Line 1")
    address_line2 = models.CharField(max_length=255, blank=True, verbose_name="Address Line 2")
    state = models.CharField(max_length=100, blank=True, verbose_name="State/Province")
    country = models.CharField(max_length=100, blank=True, default='Pakistan', verbose_name="Country")

    # Relationship to Company (optional)
    company = models.ForeignKey('Company', on_delete=models.SET_NULL, null=True, blank=True, related_name='customers')

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = "Customer"
        verbose_name_plural = "Customers"
        ordering = ['-created_at']
        unique_together = [('company', 'name')]

    def __str__(self):
        return self.name