from .models import Login, Signup
from django import forms

class LoginForm(forms.ModelForm):
    class Meta:
        model = Login
        fields = ['email', 'password']

class SignupForm(forms.ModelForm):
    class Meta:
        model = Signup
        fields = ['first_name', 'last_name', 'username', 'email', 'password', 'confirm_password']