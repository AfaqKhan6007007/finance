from django.shortcuts import redirect, render
from django. views import View
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from .forms import LoginForm, SignupForm

class Home(View):
    @method_decorator(login_required)  # Require login to access
    def get(self, request):
        return render(request, 'finance/home.html', {})

class Dashboard(View):
    @method_decorator(login_required)  # Require login to access
    def get(self, request):
        return render(request, 'finance/dashboard.html', {})

class Journal(View):
    @method_decorator(login_required)  # Require login to access
    def get(self, request):
        return render(request, 'finance/journal.html', {})

class TrialBalance(View):
    @method_decorator(login_required)  # Require login to access
    def get(self, request):
        return render(request, 'finance/trial.html', {})
    
class Ledger(View):
    @method_decorator(login_required)  # Require login to access
    def get(self, request):
        return render(request, 'finance/ledger.html', {})
    
class Companies(View):
    @method_decorator(login_required)  # Require login to access
    def get(self, request):
        return render(request, 'finance/companies.html', {})

class Payables(View):
    @method_decorator(login_required)  # Require login to access
    def get(self, request):
        return render(request, 'finance/payables.html', {})    

class Invoices(View):
    @method_decorator(login_required)  # Require login to access
    def get(self, request):
        return render(request, 'finance/invoices.html', {}) 

class Login(View):
    def get(self, request):
        # If user is already logged in, redirect to home
        if request.user.is_authenticated:
            return redirect('finance-home')
        
        form = LoginForm()
        return render(request, 'finance/login.html', {'form':  form})
    
    def post(self, request):
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            
            # Authenticate the user
            user = authenticate(username=username, password=password)
            
            if user is not None: 
                # Log the user in
                login(request, user)
                messages.success(request, f'Welcome back, {user.first_name}!')
                return redirect('finance-home')
            else:
                messages.error(request, 'Invalid username or password')
        
        return render(request, 'finance/login.html', {'form':  form})

class Signup(View):
    def get(self, request):
        # If user is already logged in, redirect to home
        if request.user.is_authenticated:
            return redirect('finance-home')
        
        form = SignupForm()
        return render(request, 'finance/signup.html', {'form': form})
    
    def post(self, request):
        form = SignupForm(request.POST)
        if form.is_valid():
            # Create the user (password will be automatically hashed)
            user = form.save()
            
            # Log the user in automatically after signup
            login(request, user)
            
            messages.success(request, f'Account created successfully! Welcome, {user.first_name}!')
            return redirect('finance-home')
        else:
            # Display form errors
            for field, errors in form.errors. items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
        
        return render(request, 'finance/signup.html', {'form': form})

class Logout(View):
    def get(self, request):
        logout(request)
        messages.info(request, 'You have been logged out.')
        return redirect('finance-login')