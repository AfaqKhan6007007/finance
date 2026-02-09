from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.forms import inlineformset_factory
from .models import AccountingDimension, BankAccount, BankAccountSubtype, BankAccountType, BankGuarantee, Company, Account, CostCenter, CostCenterAllocation, Customer, DeductionCertificate, Dunning, Invoice, JournalEntry, ProcessPaymentReconciliation, Supplier, Budget, TaxCategory, TaxCategoryAccount, TaxItemTemplate, TaxWithholdingCategory, TaxWithholdingRate, UnreconcilePayment
from django.core.exceptions import ValidationError

class SignupForm(UserCreationForm):
    first_name = forms.CharField(max_length=56, required=True)
    last_name = forms.CharField(max_length=56, required=True)
    email = forms.EmailField(max_length=56, required=True)
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2']
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user

class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label='Email or Username',
        widget=forms.TextInput(attrs={'placeholder': 'example@gmail.com'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': '••••••••••'})
    )

class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = [
            'name', 'abbreviation', 'country', 'date_of_establishment',
            'default_currency', 'tax_id', 'default_letter_head', 'domain',
            'parent_company', 'is_parent_company', 'registration_details'
        ]
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set required fields
        self.fields['name'].required = True
        self.fields['country'].required = True
        self.fields['default_currency'].required = True
        
        # Set optional fields
        self.fields['parent_company'].required = False
        self.fields['parent_company'].empty_label = "Select parent company"
        
        # Customize widgets
        self.fields['date_of_establishment'].widget = forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
            'placeholder': 'Pick a date'
        })
        
        self.fields['registration_details'].widget = forms.Textarea(attrs={
            'rows': 4,
            'class': 'form-control',
            'placeholder': 'Company registration numbers for your reference.  Tax numbers etc.'
        })

class AccountForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = [
            'is_disabled', 'name', 'account_number', 'is_group',
            'company', 'currency', 'parent_account', 'account_type',
            'tax_rate', 'balance_must_be'
        ]
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set required fields
        self.fields['name'].required = True
        self.fields['company'].required = True
        
        # Set optional fields
        self.fields['parent_account'].required = False
        self.fields['parent_account'].empty_label = "Select company first"
        
        # Customize widgets
        self.fields['name'].widget.attrs.update({
            'placeholder': 'Enter account name',
            'class': 'form-control'
        })
        
        self.fields['account_number'].widget.attrs.update({
            'placeholder': 'Enter account number',
            'class': 'form-control'
        })
        
        self.fields['tax_rate'].widget.attrs.update({
            'placeholder': 'Tax Value',
            'class': 'form-control'
        })
        
        # Filter parent accounts based on selected company
        if self.instance.pk and self.instance.company:
            self.fields['parent_account'].queryset = Account.objects.filter(
                company=self.instance.company
            ).exclude(pk=self.instance.pk)
        elif self.data.get('company'):
            # During POST with validation errors, keep the filtered accounts
            self.fields['parent_account'].queryset = Account.objects.filter(
                company=self.data.get('company')
            )
        else:
            # Show all accounts initially (or none)
            self.fields['parent_account'].queryset = Account.objects.all()

class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = [
            'invoice_id', 'invoice_number', 'date', 'supplier', 'supplier_vat',
            'customer', 'customer_vat', 'amount_before_vat', 'total_vat',
            'total_amount', 'qr_code_present', 'company', 'status'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Supplier: choose from existing suppliers
        self.fields['supplier'].queryset = Supplier.objects.all().order_by('name')
        self.fields['supplier'].widget.attrs.update({'class': 'form-control'})
        self.fields['supplier'].required = True

        # Customer: choose from existing customers
        self.fields['customer'].queryset = Customer.objects.all().order_by('name')
        self.fields['customer'].widget.attrs.update({'class': 'form-control'})
        self.fields['customer'].required = True

        # Widgets and placeholders
        self.fields['invoice_id'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Enter invoice ID'})
        self.fields['invoice_number'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Enter invoice number'})
        self.fields['date'].widget = forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
        self.fields['supplier_vat'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Supplier VAT (autofilled)'})
        self.fields['customer_vat'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Customer VAT (autofilled)'})
        self.fields['amount_before_vat'].widget.attrs.update({'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'})
        self.fields['total_vat'].widget.attrs.update({'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'})
        self.fields['total_amount'].widget.attrs.update({'class': 'form-control', 'placeholder': '0.00', 'readonly': 'readonly'})
        self.fields['company'].widget.attrs.update({'class': 'form-control'})
class JournalEntryForm(forms.ModelForm):
    class Meta:
        model = JournalEntry
        fields = ['entry_number', 'date', 'account', 'debit_amount', 'credit_amount', 'description', 'company']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set required fields
        self.fields['date'].required = True
        self.fields['account'].required = True
        
        # Set optional fields
        self.fields['entry_number'].required = False
        self.fields['company'].required = False
        self.fields['description'].required = False
        
        # Customize date widget
        self.fields['date'].widget = forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
        })
        
        # Add placeholders and classes
        self.fields['entry_number'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Auto-generated',
            'readonly': 'readonly'
        })
        
        self.fields['debit_amount'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': '0.00',
            'step': '0.01'
        })
        
        self.fields['credit_amount'].widget.attrs.update({
            'class':  'form-control',
            'placeholder': '0.00',
            'step': '0.01'
        })
        
        self.fields['description'].widget = forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Enter description for this journal entry',
            'rows': 4
        })
        
        self.fields['account'].widget.attrs.update({
            'class': 'form-control'
        })
        
        self.fields['account'].empty_label = "Select account"


class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = [
            'gstin_uin', 'name', 'supplier_type', 'gst_category',
            'contact_first_name', 'contact_last_name', 'contact_email', 'contact_mobile',
            'preferred_billing', 'preferred_shipping',
            'postal_code', 'city', 'address_line1', 'address_line2', 'state', 'country',
            'company',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # enforce required fields server-side
        self.fields['name'].required = True
        self.fields['supplier_type'].required = True
        self.fields['gst_category'].required = True

        # keep other fields optional
        self.fields['gstin_uin'].required = False
        self.fields['contact_first_name'].required = False
        self.fields['contact_last_name'].required = False
        self.fields['contact_email'].required = False
        self.fields['contact_mobile'].required = False
        self.fields['company'].required = False

        # widgets / placeholders
        self.fields['gstin_uin'].widget = forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter GSTIN / UIN for autofill'})
        self.fields['name'].widget = forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Supplier name', 'required': 'required', 'aria-required': 'true'})
        self.fields['contact_first_name'].widget = forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'})
        self.fields['contact_last_name'].widget = forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'})
        self.fields['contact_email'].widget = forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email ID'})
        self.fields['contact_mobile'].widget = forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Mobile Number'})
        self.fields['postal_code'].widget = forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Postal Code'})
        self.fields['address_line1'].widget = forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Address Line 1'})
        self.fields['address_line2'].widget = forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Address Line 2'})
        self.fields['city'].widget = forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City/Town'})
        self.fields['state'].widget = forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'State/Province'})
        self.fields['country'].widget = forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Country'})

        # add required attrs for selects too
        self.fields['supplier_type'].widget = forms.Select(attrs={'class': 'form-control', 'required': 'required', 'aria-required': 'true'})
        self.fields['gst_category'].widget = forms.Select(attrs={'class': 'form-control', 'required': 'required', 'aria-required': 'true'})
        self.fields['company'].widget = forms.Select(attrs={'class': 'form-control'})

    def clean(self):
        cleaned = super().clean()

        # server-side enforcement (extra safety)
        name = cleaned.get('name')
        supplier_type = cleaned.get('supplier_type')
        gst_category = cleaned.get('gst_category')

        errors = {}
        if not name:
            errors['name'] = ValidationError('Supplier name is required.')
        if not supplier_type:
            errors['supplier_type'] = ValidationError('Supplier type is required.')
        if not gst_category:
            errors['gst_category'] = ValidationError('GST category is required.')

        if errors:
            raise ValidationError(errors)

        return cleaned
    
class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = [
            'gstin_uin', 'name', 'customer_type', 'gst_category',
            'contact_first_name', 'contact_last_name', 'contact_email', 'contact_mobile',
            'preferred_billing', 'preferred_shipping',
            'postal_code', 'city', 'address_line1', 'address_line2', 'state', 'country',
            'company',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # enforce required fields server-side
        self.fields['name'].required = True
        self.fields['customer_type'].required = True
        self.fields['gst_category'].required = True

        # keep other fields optional
        self.fields['gstin_uin'].required = False
        self.fields['contact_first_name'].required = False
        self.fields['contact_last_name'].required = False
        self.fields['contact_email'].required = False
        self.fields['contact_mobile'].required = False
        self.fields['company'].required = False

        # widgets / placeholders
        self.fields['gstin_uin'].widget = forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter GSTIN / UIN for autofill'})
        self.fields['name'].widget = forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Customer name', 'required': 'required', 'aria-required': 'true'})
        self.fields['contact_first_name'].widget = forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'})
        self.fields['contact_last_name'].widget = forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'})
        self.fields['contact_email'].widget = forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email ID'})
        self.fields['contact_mobile'].widget = forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Mobile Number'})
        self.fields['postal_code'].widget = forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Postal Code'})
        self.fields['address_line1'].widget = forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Address Line 1'})
        self.fields['address_line2'].widget = forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Address Line 2'})
        self.fields['city'].widget = forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City/Town'})
        self.fields['state'].widget = forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'State/Province'})
        self.fields['country'].widget = forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Country'})

        # add required attrs for selects too
        self.fields['customer_type'].widget = forms.Select(attrs={'class': 'form-control', 'required': 'required', 'aria-required': 'true'})
        self.fields['gst_category'].widget = forms.Select(attrs={'class': 'form-control', 'required': 'required', 'aria-required': 'true'})
        self.fields['company'].widget = forms.Select(attrs={'class': 'form-control'})

    def clean(self):
        cleaned = super().clean()

        # server-side enforcement (extra safety)
        name = cleaned.get('name')
        customer_type = cleaned.get('customer_type')
        gst_category = cleaned.get('gst_category')

        errors = {}
        if not name:
            errors['name'] = ValidationError('Customer name is required.')
        if not customer_type:
            errors['customer_type'] = ValidationError('Customer type is required.')
        if not gst_category:
            errors['gst_category'] = ValidationError('GST category is required.')

        if errors:
            raise ValidationError(errors)

        return cleaned
    
class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = [
            'series',
            'budget_against',
            'fiscal_year_from',
            'fiscal_year_to',
            'company',
            'distribution',
            'cost_center',
            'account',
            'budget_amount',
        ]

        widgets = {
            'series': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Budget Series'
            }),
            'budget_against': forms.Select(attrs={
                'class': 'form-control'
            }),
            'fiscal_year_from': forms.Select(attrs={
                'class': 'form-control'
            }),
            'fiscal_year_to': forms.Select(attrs={
                'class': 'form-control'
            }),
            'company': forms.Select(attrs={
                'class': 'form-control'
            }),
            'distribution': forms.Select(attrs={
                'class': 'form-control'
            }),
            'cost_center': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Cost Center'
            }),
            'account': forms.Select(attrs={
                'class': 'form-control'
            }),
            'budget_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Total Budget Amount',
                'step': '0.01'
            }),
        }

        labels = {
            'series': 'Budget Series',
            'budget_against': 'Budget Against',
            'fiscal_year_from': 'Fiscal Year From',
            'fiscal_year_to': 'Fiscal Year To',
            'company': 'Company',
            'distribution': 'Distribution',
            'cost_center': 'Cost Center',
            'account': 'Account',
            'budget_amount': 'Total Budget Amount',
        }

class CostCenterForm(forms.ModelForm):
    class Meta:
        model = CostCenter
        fields = [
            'name',
            'cost_center_number',
            'company',
            'parent',
            'is_group',
            'is_disabled',
        ]

        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Cost Center Name'
            }),
            'cost_center_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Cost Center Number'
            }),
            'company': forms.Select(attrs={
                'class': 'form-control'
            }),
            'parent': forms.Select(attrs={
                'class': 'form-control'
            }),
            'is_group': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'is_disabled': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }

        labels = {
            'name': 'Cost Center Name',
            'cost_center_number': 'Cost Center Number',
            'company': 'Company',
            'parent': 'Parent Cost Center',
            'is_group': 'Is Group',
            'is_disabled': 'Is Disabled',
        }

class AccountingDimensionForm(forms.ModelForm):
    class Meta:
        model = AccountingDimension
        fields = [
            'name',

        ]

        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Accounting Dimension Name'
            }),
        }

        labels = {
            'name': 'Accounting Dimension Name',
        }

class CostCenterAllocationsForm(forms.ModelForm):
    class Meta:
        model = CostCenterAllocation
        fields = [
            'cost_center',
            'company',
            'valid_from',

        ]

        widgets = {
            'cost_center': forms.Select(attrs={
                'class': 'form-control'
            }),
            'company': forms.Select(attrs={
                'class': 'form-control'
            }),
            'valid_from': forms.DateInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Cost Center Allocation Name'
            }),
        }

        labels = {
            'cost_center': 'Cost Center',
            'company': 'Company',
            'valid_from': 'Valid From',
        }

class TaxItemTemplatesForm(forms.ModelForm):
    class Meta:
        model = TaxItemTemplate
        fields = [
            'title',
            'company',
            'gst_rate',
            'gst_treatment',
            'disabled',
        ]

        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Title'
            }),
            'company': forms.Select(attrs={
                'class': 'form-control'
            }),
            'gst_rate': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Tax Rate (%)',
                'step': '0.01'
            }),
            'gst_treatment': forms.Select(attrs={
                'class': 'form-control'
            }),
            'disabled': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }

        labels = {
            'title': 'Tax Item Template Title',
            'company': 'Company',
            'gst_rate': 'GST Rate (%)',
            'gst_treatment': 'GST Treatment',
            'disabled': 'Disabled',
        }

class TaxCategoryForm(forms.ModelForm):
    class Meta:
        model = TaxCategory
        fields = [
            'title',
        ]

        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Tax Category Title'
            }),
        }

        labels = {
            'title': 'Tax Category Title',
        }

from django import forms
from .models import TaxRule


class TaxRuleForm(forms.ModelForm):
    class Meta:
        model = TaxRule
        fields = "__all__"

        widgets = {
            "tax_type": forms.Select(attrs={"class": "form-control"}),
            "sales_tax_template": forms.Select(attrs={"class": "form-control"}),
            "shopping_cart_use": forms.CheckboxInput(attrs={"class": "form-check-input"}),

            "customer": forms.Select(attrs={"class": "form-control"}),
            "customer_group": forms.TextInput(attrs={"class": "form-control"}),
            "item": forms.TextInput(attrs={"class": "form-control"}),
            "item_group": forms.TextInput(attrs={"class": "form-control"}),

            "billing_city": forms.TextInput(attrs={"class": "form-control"}),
            "shipping_city": forms.TextInput(attrs={"class": "form-control"}),
            "billing_county": forms.TextInput(attrs={"class": "form-control"}),
            "shipping_county": forms.TextInput(attrs={"class": "form-control"}),

            "billing_state": forms.TextInput(attrs={"class": "form-control"}),
            "shipping_state": forms.TextInput(attrs={"class": "form-control"}),
            "billing_zipcode": forms.TextInput(attrs={"class": "form-control"}),
            "shipping_zipcode": forms.TextInput(attrs={"class": "form-control"}),

            "billing_country": forms.TextInput(attrs={"class": "form-control"}),
            "shipping_country": forms.TextInput(attrs={"class": "form-control"}),

            "tax_category": forms.Select(attrs={"class": "form-control"}),
            "from_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "to_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "priority": forms.NumberInput(attrs={"class": "form-control"}),

            "company": forms.Select(attrs={"class": "form-control"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        from_date = cleaned_data.get("from_date")
        to_date = cleaned_data.get("to_date")

        if from_date and to_date and from_date > to_date:
            raise forms.ValidationError(
                "From Date cannot be later than To Date."
            )

        return cleaned_data


class TaxWithholdingCategoryForm(forms.ModelForm):
    class Meta:
        model = TaxWithholdingCategory
        fields = '__all__'
        widgets = {
            # --- Text Inputs ---
            'name': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Enter Name'
            }),
            'category_name': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Enter Category Name'
            }),
            'section': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'e.g. 194C'
            }),

            # --- Select Dropdowns ---
            'deduct_tax_on_basis': forms.Select(attrs={
                'class': 'form-select'
            }),
            'entity': forms.Select(attrs={
                'class': 'form-select'
            }),

            # --- Checkboxes ---
            'round_off_tax_amount': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'only_deduct_on_excess': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'disable_cumulative_threshold': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'disable_transaction_threshold': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }

# --- Rate Form (For the Inline Table) ---
class TaxWithholdingRateForm(forms.ModelForm):
    class Meta:
        model = TaxWithholdingRate
        fields = '__all__'
        widgets = {
            # --- Date Pickers (Critical for the table) ---
            'from_date': forms.DateInput(attrs={
                'class': 'form-control', 
                'type': 'date'  # This triggers the HTML5 date picker
            }),
            'to_date': forms.DateInput(attrs={
                'class': 'form-control', 
                'type': 'date'
            }),
            
            # --- Text/Number Inputs ---
            'tax_withholding_group': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Code'
            }),
            'tax_withholding_rate': forms.NumberInput(attrs={
                'class': 'form-control', 
                'step': '0.001', # Allows 3 decimal places
                'placeholder': '0.000'
            }),
            'cumulative_threshold': forms.NumberInput(attrs={
                'class': 'form-control', 
                'step': '0.01',
                'placeholder': '0.00'
            }),
            'transaction_threshold': forms.NumberInput(attrs={
                'class': 'form-control', 
                'step': '0.01',
                'placeholder': '0.00'
            }),
        }

# --- Account Form (For the Inline Table) ---
class TaxCategoryAccountForm(forms.ModelForm):
    class Meta:
        model = TaxCategoryAccount
        fields = '__all__'
        widgets = {
            'company': forms.Select(attrs={
                'class': 'form-select'
            }),
            'account': forms.Select(attrs={
                'class': 'form-select'
            }),
        }

# --- Formset Definitions ---

# 1. Rates Table Formset
TaxRateFormSet = inlineformset_factory(
    parent_model=TaxWithholdingCategory,
    model=TaxWithholdingRate,
    form=TaxWithholdingRateForm, # We pass the custom form here to apply widgets
    extra=1,          # Show 1 empty row by default
    can_delete=True   # Allow deleting rows
)

# 2. Accounts Table Formset
TaxAccountFormSet = inlineformset_factory(
    parent_model=TaxWithholdingCategory,
    model=TaxCategoryAccount,
    form=TaxCategoryAccountForm, # We pass the custom form here to apply widgets
    extra=1,
    can_delete=True
)

class DeductionCertificateForm(forms.ModelForm):
    class Meta:
        model = DeductionCertificate
        fields = [
            'tax_withholding_category',
            'company',
            'fiscal_year',
            'certificate_number',
            'supplier',
            'pan_number',
            'valid_from',
            'valid_to',
            'rate_of_tdas',
            'certificate_limit',
        ]
        widgets = {
            'valid_from': forms.DateInput(attrs={'type': 'date'}),
            'valid_to': forms.DateInput(attrs={'type': 'date'}),
        }

class BankAccountForm(forms.ModelForm):
    class Meta:
        model = BankAccount
        fields = [
            'name',
            'bank',
            'account_type',
            'account_subtype',
            'party_type',
            'party',
            'iban',
            'branch_code',
            'bank_account_number',
            'last_integration_date',
        ]

        widgets = {
            'last_integration_date': forms.DateInput(
                attrs={'type': 'date'}
            ),
        }

    def clean(self):
        cleaned_data = super().clean()
        party_type = cleaned_data.get('party_type')
        party = cleaned_data.get('party')

        # If party_type is selected, party should be provided
        if party_type and not party:
            self.add_error(
                'party',
                'Party is required when Party Type is selected.'
            )

        return cleaned_data
    
class BankAccountTypeForm(forms.ModelForm):
    class Meta:
        model = BankAccountType
        fields = ['account_type']

class BankAccountSubTypeForm(forms.ModelForm):
    class Meta:
        model = BankAccountSubtype
        fields = ['account_subtype']

class BankGuaranteeForm(forms.ModelForm):
    class Meta:
        model = BankGuarantee
        fields = ['type', 'amount', 'start_date']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': '0.00',
            }),
        }


class UnreconcilePaymentForm(forms.ModelForm):
    class Meta:
        model = UnreconcilePayment
        fields = ['company','voucher_type','voucher_number']
        widgets = {
            'company': forms.Select(attrs={'class': 'form-control'}),
            'voucher_type': forms.Select(attrs={'class': 'form-control'}),
            'voucher_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Voucher Number'
            }),
        }

class ProcessPaymentReconciliationForm(forms.Form):
    class Meta:
        model = ProcessPaymentReconciliation
        fields = ['company','party','party_type','receivable_account',]

class DunningForm(forms.ModelForm):
    class Meta:
        model = Dunning
        fields = ['customer', 'company', 'date']