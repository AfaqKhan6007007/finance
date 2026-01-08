from django. db import models
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
    created_at = models. DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        verbose_name_plural = "Companies"
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name