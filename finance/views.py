from django.shortcuts import redirect, render, get_object_or_404
from django. views import View
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from .forms import LoginForm, SignupForm, CompanyForm, AccountForm, InvoiceForm, JournalEntryForm
from django.db import models
from .models import Company, Account, Invoice, JournalEntry
from django.contrib.messages import get_messages

class Accounts(View):
    """List all accounts"""
    @method_decorator(login_required)
    def get(self, request):
        accounts = Account.objects.select_related('company', 'parent_account').all()
        
        # Search functionality
        search_query = request.GET.get('search', '')
        if search_query:
            accounts = accounts.filter(name__icontains=search_query)
        
        # Filter by ID
        id_filter = request.GET.get('id', '')
        if id_filter: 
            accounts = accounts.filter(id=id_filter)
        
        # Filter by Account Number
        account_number_filter = request.GET.get('account_number', '')
        if account_number_filter:
            accounts = accounts.filter(account_number__icontains=account_number_filter)
        
        # Filter by Company
        company_filter = request.GET.get('company', '')
        if company_filter: 
            accounts = accounts.filter(company_id=company_filter)
        
        # Filter by Account Type
        account_type_filter = request.GET.get('account_type', '')
        if account_type_filter:
            accounts = accounts.filter(account_type=account_type_filter)
        
        context = {
            'accounts': accounts,
            'search_query': search_query,
            'id_filter': id_filter,
            'account_number_filter': account_number_filter,
            'company_filter': company_filter,
            'account_type_filter': account_type_filter,
            'total_count': Account.objects.count(),
            'companies': Company.objects.all(),  # For filter dropdown
        }
        return render(request, 'finance/accounts.html', context)


class AccountCreate(View):
    """Create new account"""
    @method_decorator(login_required)
    def get(self, request):
        form = AccountForm()
        return render(request, 'finance/account_form.html', {
            'form': form,
            'action': 'New',
            'is_edit': False
        })
    
    @method_decorator(login_required)
    def post(self, request):
        form = AccountForm(request.POST)
        if form.is_valid():
            account = form.save(commit=False)
            account.created_by = request.user
            account.save()
            messages.success(request, f'Account "{account.name}" created successfully!')
            return redirect('finance-accounts')
        else:
            messages.error(request, 'Please correct the errors below.')
        
        return render(request, 'finance/account_form.html', {
            'form': form,
            'action': 'New',
            'is_edit':  False
        })


class AccountEdit(View):
    """Edit existing account"""
    @method_decorator(login_required)
    def get(self, request, pk):
        account = get_object_or_404(Account, pk=pk)
        form = AccountForm(instance=account)
        return render(request, 'finance/account_form.html', {
            'form': form,
            'account': account,
            'action':  'Edit',
            'is_edit': True
        })
    
    @method_decorator(login_required)
    def post(self, request, pk):
        account = get_object_or_404(Account, pk=pk)
        form = AccountForm(request.POST, instance=account)
        if form.is_valid():
            form.save()
            messages.success(request, f'Account "{account.name}" updated successfully!')
            return redirect('finance-accounts')
        else:
            messages.error(request, 'Please correct the errors below.')
        
        return render(request, 'finance/account_form.html', {
            'form': form,
            'account': account,
            'action': 'Edit',
            'is_edit': True
        })


class AccountDelete(View):
    """Delete account"""
    @method_decorator(login_required)
    def post(self, request, pk):
        account = get_object_or_404(Account, pk=pk)
        account_name = account.name
        account.delete()
        messages.success(request, f'Account "{account_name}" deleted successfully!')
        return redirect('finance-accounts')

class Dashboard(View):
    @method_decorator(login_required)  # Require login to access
    def get(self, request):
        return render(request, 'finance/dashboard.html', {})

class Journal(View):
    """List all journal entries"""
    @method_decorator(login_required)
    def get(self, request):
        journal_entries = JournalEntry. objects.select_related('account', 'company').all()
        
        # Search functionality
        search_query = request.GET.get('search', '')
        if search_query:
            journal_entries = journal_entries.filter(
                models.Q(entry_number__icontains=search_query) |
                models. Q(account__name__icontains=search_query) |
                models.Q(description__icontains=search_query)
            )
        
        context = {
            'journal_entries': journal_entries,
            'search_query': search_query,
            'total_count': JournalEntry.objects.count(),
        }
        return render(request, 'finance/journal.html', context)


class JournalCreate(View):
    """Create new journal entry"""
    @method_decorator(login_required)
    def get(self, request):
        form = JournalEntryForm()
        return render(request, 'finance/journal_form.html', {
            'form': form,
            'action': 'New',
            'is_edit': False
        })
    
    @method_decorator(login_required)
    def post(self, request):
        form = JournalEntryForm(request.POST)
        if form.is_valid():
            journal_entry = form.save(commit=False)
            journal_entry.created_by = request.user
            journal_entry.save()
            messages.success(request, f'Journal Entry "{journal_entry.entry_number}" created successfully!')
            return redirect('finance-journal')
        else:
            messages.error(request, 'Please correct the errors below.')
        
        return render(request, 'finance/journal_form.html', {
            'form': form,
            'action': 'New',
            'is_edit': False
        })


class JournalEdit(View):
    """Edit existing journal entry"""
    @method_decorator(login_required)
    def get(self, request, pk):
        journal_entry = get_object_or_404(JournalEntry, pk=pk)
        form = JournalEntryForm(instance=journal_entry)
        return render(request, 'finance/journal_form.html', {
            'form':  form,
            'journal_entry': journal_entry,
            'action': 'Edit',
            'is_edit': True
        })
    
    @method_decorator(login_required)
    def post(self, request, pk):
        journal_entry = get_object_or_404(JournalEntry, pk=pk)
        form = JournalEntryForm(request.POST, instance=journal_entry)
        if form.is_valid():
            form.save()
            messages.success(request, f'Journal Entry "{journal_entry. entry_number}" updated successfully!')
            return redirect('finance-journal')
        else:
            messages. error(request, 'Please correct the errors below.')
        
        return render(request, 'finance/journal_form.html', {
            'form': form,
            'journal_entry': journal_entry,
            'action': 'Edit',
            'is_edit': True
        })


class JournalDelete(View):
    """Delete journal entry"""
    @method_decorator(login_required)
    def post(self, request, pk):
        journal_entry = get_object_or_404(JournalEntry, pk=pk)
        entry_number = journal_entry.entry_number
        journal_entry.delete()
        messages.success(request, f'Journal Entry "{entry_number}" deleted successfully!')
        return redirect('finance-journal')

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
    """List all invoices"""
    @method_decorator(login_required)
    def get(self, request):
        invoices = Invoice. objects.select_related('company').all()
        
        # Search functionality
        search_query = request. GET.get('search', '')
        if search_query:
            invoices = invoices.filter(
                models.Q(invoice_number__icontains=search_query) |
                models.Q(customer_name__icontains=search_query) |
                models. Q(supplier_name__icontains=search_query)
            )
        
        context = {
            'invoices':  invoices,
            'search_query': search_query,
            'total_count': Invoice.objects.count(),
        }
        return render(request, 'finance/invoices.html', context)


class InvoiceCreate(View):
    """Create new invoice"""
    @method_decorator(login_required)
    def get(self, request):
        form = InvoiceForm()
        return render(request, 'finance/invoice_form.html', {
            'form': form,
            'action': 'New',
            'is_edit': False
        })
    
    @method_decorator(login_required)
    def post(self, request):
        form = InvoiceForm(request.POST)
        if form.is_valid():
            invoice = form.save(commit=False)
            invoice.created_by = request.user
            invoice.save()
            messages.success(request, f'Invoice "{invoice.invoice_number}" created successfully!')
            return redirect('finance-invoices')
        else:
            messages.error(request, 'Please correct the errors below.')
        
        return render(request, 'finance/invoice_form.html', {
            'form': form,
            'action': 'New',
            'is_edit':  False
        })


class InvoiceEdit(View):
    """Edit existing invoice"""
    @method_decorator(login_required)
    def get(self, request, pk):
        invoice = get_object_or_404(Invoice, pk=pk)
        form = InvoiceForm(instance=invoice)
        return render(request, 'finance/invoice_form.html', {
            'form': form,
            'invoice': invoice,
            'action':  'Edit',
            'is_edit': True
        })
    
    @method_decorator(login_required)
    def post(self, request, pk):
        invoice = get_object_or_404(Invoice, pk=pk)
        form = InvoiceForm(request.POST, instance=invoice)
        if form.is_valid():
            form.save()
            messages.success(request, f'Invoice "{invoice.invoice_number}" updated successfully!')
            return redirect('finance-invoices')
        else:
            messages. error(request, 'Please correct the errors below.')
        
        return render(request, 'finance/invoice_form.html', {
            'form': form,
            'invoice': invoice,
            'action': 'Edit',
            'is_edit': True
        })


class InvoiceDelete(View):
    """Delete invoice"""
    @method_decorator(login_required)
    def post(self, request, pk):
        invoice = get_object_or_404(Invoice, pk=pk)
        invoice_number = invoice.invoice_number
        invoice.delete()
        messages.success(request, f'Invoice "{invoice_number}" deleted successfully!')
        return redirect('finance-invoices')

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
        # If user is already logged in, redirect to accounts
        if request.user.is_authenticated:
            return redirect('finance-accounts')
        
        # Clear any existing messages when showing login page
        storage = get_messages(request)
        for _ in storage:
            pass  # This iterates through and clears messages
        
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
                # Clear any existing messages before login
                storage = get_messages(request)
                for _ in storage:
                    pass
                
                # Log the user in
                login(request, user)
                messages. success(request, f'Welcome back, {user.first_name}!')
                return redirect('finance-accounts')
            else:
                messages.error(request, 'Invalid username or password')
        else:
            messages.error(request, 'Please check your credentials and try again.')
        
        return render(request, 'finance/login.html', {'form':  form})


class Signup(View):
    def get(self, request):
        # If user is already logged in, redirect to accounts
        if request.user.is_authenticated:
            return redirect('finance-accounts')
        
        # Clear any existing messages
        storage = get_messages(request)
        for _ in storage: 
            pass
        
        form = SignupForm()
        return render(request, 'finance/signup.html', {'form': form})
    
    def post(self, request):
        form = SignupForm(request.POST)
        if form.is_valid():
            # Clear any existing messages before signup
            storage = get_messages(request)
            for _ in storage:
                pass
            
            # Create the user (password will be automatically hashed)
            user = form.save()
            
            # Log the user in automatically after signup
            login(request, user)
            
            messages.success(request, f'Account created successfully! Welcome, {user.first_name}!')
            return redirect('finance-accounts')
        else:
            # Display form errors
            for field, errors in form.errors. items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
        
        return render(request, 'finance/signup.html', {'form': form})


class Logout(View):
    def get(self, request):
        # Don't logout on GET, just redirect
        if request.user. is_authenticated:
            return redirect('finance-accounts')
        return redirect('finance-login')
    
    @method_decorator(login_required)
    def post(self, request):
        user_name = request.user.first_name or request.user.username
        
        # Store the message BEFORE logout
        logout(request)
        
        # Add message after logout (this should work with FallbackStorage)
        messages.success(request, f'Goodbye {user_name}! You have been logged out successfully.')
        return redirect('finance-login')