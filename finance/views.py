from django.shortcuts import redirect, render, get_object_or_404
from django. views import View
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from .forms import LoginForm, SignupForm, CompanyForm
from .models import Company

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
    """List all companies/accounts"""
    @method_decorator(login_required)
    def get(self, request):
        companies = Company.objects.all()
        
        # Search functionality
        search_query = request.GET.get('search', '')
        if search_query: 
            companies = companies.filter(name__icontains=search_query)
        
        # Filter by ID
        id_filter = request.GET.get('id', '')
        if id_filter: 
            companies = companies.filter(id=id_filter)
        
        context = {
            'companies': companies,
            'search_query':  search_query,
            'id_filter': id_filter,
            'total_count': Company.objects.count(),
        }
        return render(request, 'finance/companies.html', context)


class CompanyCreate(View):
    """Create new company/account"""
    @method_decorator(login_required)
    def get(self, request):
        form = CompanyForm()
        return render(request, 'finance/company_form.html', {
            'form': form,
            'action': 'New',
            'is_edit': False
        })
    
    @method_decorator(login_required)
    def post(self, request):
        form = CompanyForm(request.POST)
        if form.is_valid():
            company = form.save(commit=False)
            company. created_by = request.user
            company.save()
            messages.success(request, f'Company "{company.name}" created successfully!')
            return redirect('finance-companies')
        else:
            messages.error(request, 'Please correct the errors below.')
        
        return render(request, 'finance/company_form.html', {
            'form': form,
            'action': 'New',
            'is_edit': False
        })


class CompanyEdit(View):
    """Edit existing company/account"""
    @method_decorator(login_required)
    def get(self, request, pk):
        company = get_object_or_404(Company, pk=pk)
        form = CompanyForm(instance=company)
        return render(request, 'finance/company_form.html', {
            'form': form,
            'company': company,
            'action':  'Edit',
            'is_edit': True
        })
    
    @method_decorator(login_required)
    def post(self, request, pk):
        company = get_object_or_404(Company, pk=pk)
        form = CompanyForm(request.POST, instance=company)
        if form.is_valid():
            form.save()
            messages.success(request, f'Company "{company.name}" updated successfully!')
            return redirect('finance-companies')
        else:
            messages.error(request, 'Please correct the errors below.')
        
        return render(request, 'finance/company_form.html', {
            'form': form,
            'company':  company,
            'action': 'Edit',
            'is_edit': True
        })


class CompanyDelete(View):
    """Delete company/account"""
    @method_decorator(login_required)
    def post(self, request, pk):
        company = get_object_or_404(Company, pk=pk)
        company_name = company.name
        company.delete()
        messages.success(request, f'Company "{company_name}" deleted successfully!')
        return redirect('finance-companies')
class Payables(View):
    @method_decorator(login_required)  # Require login to access
    def get(self, request):
        return render(request, 'finance/payables.html', {})    

class Invoices(View):
    @method_decorator(login_required)  # Require login to access
    def get(self, request):
        return render(request, 'finance/invoices.html', {}) 

class Receivables(View):
    @method_decorator(login_required)  # Require login to access
    def get(self, request):
        return render(request, 'finance/receivables.html', {}) 
    
class InvoiceScan(View):
    @method_decorator(login_required)  # Require login to access
    def get(self, request):
        return render(request, 'finance/scan.html', {}) 
    
class Reports(View):
    @method_decorator(login_required)  # Require login to access
    def get(self, request):
        return render(request, 'finance/reports.html', {})

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