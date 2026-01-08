from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Company, Account, Invoice, JournalEntry

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
        widget=forms. TextInput(attrs={'placeholder': 'example@gmail.com'})
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
        self. fields['default_currency'].required = True
        
        # Set optional fields
        self.fields['parent_company'].required = False
        self.fields['parent_company'].empty_label = "Select parent company"
        
        # Customize widgets
        self.fields['date_of_establishment'].widget = forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
            'placeholder': 'Pick a date'
        })
        
        self.fields['registration_details'].widget = forms. Textarea(attrs={
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
        self.fields['name']. widget. attrs.update({
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
                company=self.instance. company
            ).exclude(pk=self.instance. pk)
        else:
            self.fields['parent_account'].queryset = Account. objects.none()

class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = [
            'invoice_id', 'invoice_number', 'date', 'supplier_name', 'supplier_vat',
            'customer_name', 'customer_vat', 'amount_before_vat', 'total_vat',
            'total_amount', 'qr_code_present', 'company', 'status'
        ]
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set required fields
        self.fields['invoice_id'].required = True
        self.fields['invoice_number']. required = True
        self.fields['date'].required = True
        self.fields['supplier_name']. required = True
        self.fields['amount_before_vat'].required = True
        self.fields['total_vat'].required = True
        
        # Set optional fields
        self.fields['customer_vat'].required = False
        self.fields['supplier_vat'].required = False
        self.fields['total_amount'].required = False
        self.fields['company'].required = False
        
        # Customize date widget
        self.fields['date']. widget = forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
            'placeholder': 'Pick a date'
        })
        
        # Add placeholders and classes
        self.fields['invoice_id'].widget.attrs. update({
            'class': 'form-control',
            'placeholder': 'Enter invoice ID'
        })
        
        self.fields['invoice_number'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter invoice number'
        })
        
        self.fields['supplier_name'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter supplier name'
        })
        
        self. fields['customer_name'].widget. attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter customer name'
        })
        
        self.fields['supplier_vat'].widget.attrs. update({
            'class': 'form-control',
            'placeholder': 'Supplier VAT'
        })
        
        self.fields['customer_vat'].widget.attrs. update({
            'class': 'form-control',
            'placeholder': 'Customer VAT'
        })
        
        self.fields['amount_before_vat'].widget.attrs.update({
            'class': 'form-control',
            'placeholder':  '0.00',
            'step': '0.01'
        })
        
        self.fields['total_vat'].widget.attrs. update({
            'class': 'form-control',
            'placeholder': '0.00',
            'step': '0.01'
        })
        
        self.fields['total_amount']. widget.attrs.update({
            'class': 'form-control',
            'placeholder': '0',
            'readonly': 'readonly'
        })

class JournalEntryForm(forms.ModelForm):
    class Meta:
        model = JournalEntry
        fields = ['entry_number', 'date', 'account', 'debit_amount', 'credit_amount', 'description', 'company']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set required fields
        self.fields['date'].required = True
        self. fields['account'].required = True
        
        # Set optional fields
        self.fields['entry_number'].required = False
        self.fields['company'].required = False
        self. fields['description'].required = False
        
        # Customize date widget
        self.fields['date']. widget = forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
        })
        
        # Add placeholders and classes
        self.fields['entry_number'].widget.attrs. update({
            'class': 'form-control',
            'placeholder': 'Auto-generated',
            'readonly': 'readonly'
        })
        
        self.fields['debit_amount'].widget.attrs. update({
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
        
        self.fields['account'].widget. attrs.update({
            'class': 'form-control'
        })
        
        self.fields['account'].empty_label = "Select account"