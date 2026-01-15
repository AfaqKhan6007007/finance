from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Company, Account, Customer, Invoice, JournalEntry, Supplier, Budget
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