from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Company

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