from django.shortcuts import redirect, render, get_object_or_404
from django.views import View
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from .forms import LoginForm, SignupForm, CompanyForm, AccountForm, InvoiceForm, JournalEntryForm
from django.db import models
from .models import Company, Account, Invoice, JournalEntry
from django.contrib.messages import get_messages
from django.db. models import Sum, Q
from datetime import datetime, timedelta
from decimal import Decimal
import math

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
        
        # Debug: Print the POST data
        print("POST data:", request.POST)
        
        if form.is_valid():
            account = form.save(commit=False)
            account.created_by = request.user
            account.save()
            messages.success(request, f'Account "{account.name}" created successfully!')
            return redirect('finance-accounts')
        else:
            # Debug: Print form errors
            print("Form errors:", form.errors)
            messages.error(request, 'Please correct the errors below.')
        
        return render(request, 'finance/account_form.html', {
            'form': form,
            'action': 'New',
            'is_edit': False
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
        
        # Debug: Print the POST data
        print("POST data:", request.POST)
        
        if form.is_valid():
            form.save()
            messages.success(request, f'Account "{account.name}" updated successfully!')
            return redirect('finance-accounts')
        else:
            # Debug:  Print form errors
            print("Form errors:", form.errors)
            messages.error(request, 'Please correct the errors below.')
        
        return render(request, 'finance/account_form.html', {
            'form': form,
            'account': account,
            'action': 'Edit',
            'is_edit':  True
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
    @method_decorator(login_required)
    def get(self, request):
        
        
        # Calculate Total Revenue (Income accounts - credit side)
        total_revenue = JournalEntry.objects.filter(
            account__account_type='income'
        ).aggregate(
            total=Sum('credit_amount')
        )['total'] or Decimal('0.00')
        
        # Calculate Total Expenses (Expense accounts - debit side)
        total_expenses = JournalEntry.objects.filter(
            account__account_type='expense'
        ).aggregate(
            total=Sum('debit_amount')
        )['total'] or Decimal('0.00')
        
        # Calculate Net Profit
        net_profit = total_revenue - total_expenses
        
        # Calculate Cash on Hand (Asset accounts balance)
        asset_debits = JournalEntry.objects. filter(
            account__account_type='asset'
        ).aggregate(total=Sum('debit_amount'))['total'] or Decimal('0.00')
        
        asset_credits = JournalEntry. objects.filter(
            account__account_type='asset'
        ).aggregate(total=Sum('credit_amount'))['total'] or Decimal('0.00')
        
        cash_on_hand = asset_debits - asset_credits
        
        # Get previous month data for comparison
        today = datetime.now()
        first_day_current_month = today.replace(day=1)
        last_day_previous_month = first_day_current_month - timedelta(days=1)
        first_day_previous_month = last_day_previous_month.replace(day=1)
        
        # Current month revenue (for comparison)
        current_revenue = JournalEntry.objects. filter(
            account__account_type='income',
            date__gte=first_day_current_month
        ).aggregate(total=Sum('credit_amount'))['total'] or Decimal('0.00')
        
        # Previous month revenue
        prev_revenue = JournalEntry.objects.filter(
            account__account_type='income',
            date__gte=first_day_previous_month,
            date__lte=last_day_previous_month
        ).aggregate(total=Sum('credit_amount'))['total'] or Decimal('0.00')
        
        # Current month expenses
        current_expenses = JournalEntry.objects.filter(
            account__account_type='expense',
            date__gte=first_day_current_month
        ).aggregate(total=Sum('debit_amount'))['total'] or Decimal('0.00')
        
        # Previous month expenses
        prev_expenses = JournalEntry.objects.filter(
            account__account_type='expense',
            date__gte=first_day_previous_month,
            date__lte=last_day_previous_month
        ).aggregate(total=Sum('debit_amount'))['total'] or Decimal('0.00')
        
        # Calculate percentage changes
        revenue_change = self.calculate_percentage_change(prev_revenue, current_revenue)
        expense_change = self.calculate_percentage_change(prev_expenses, current_expenses)
        
        prev_profit = prev_revenue - prev_expenses
        current_profit = current_revenue - current_expenses
        profit_change = self.calculate_percentage_change(prev_profit, current_profit)
        
        # Get monthly income vs expense data (last 6 months)
        monthly_data = self.get_monthly_data(6)
        
        # Get expense breakdown by category (for pie chart)
        expense_breakdown = JournalEntry.objects.filter(
            account__account_type='expense'
        ).values(
            'account__name'
        ).annotate(
            total=Sum('debit_amount')
        ).order_by('-total')[:4]  # Top 4 categories
        
        # Calculate total for percentages
        total_expense_sum = sum(item['total'] for item in expense_breakdown) if expense_breakdown else 0
        
        # Prepare pie chart data
        pie_chart_data = []
        colors = ['#52c77c', '#4a7cff', '#f5a623', '#ff6b6b']
        positions = [
            {'top': '1%', 'left': '50%', 'transform': 'translateX(-50%)'},
            {'bottom': '30%', 'left': '20%'},
            {'right': '15%', 'bottom': '35%'},
            {'right': '10%', 'top': '40%'}
        ]
        
        cumulative_percent = 0
        for idx, item in enumerate(expense_breakdown):
            if total_expense_sum > 0:
                percentage = (float(item['total']) / float(total_expense_sum)) * 100
            else:
                percentage = 0
            
            # Calculate SVG circle parameters
            circumference = 2 * math. pi * 40  # radius = 40
            dash_length = (percentage / 100) * circumference
            dash_offset = -cumulative_percent / 100 * circumference
            
            pie_chart_data.append({
                'name': item['account__name'],
                'total': item['total'],
                'percentage': round(percentage, 0),
                'color': colors[idx] if idx < len(colors) else '#999',
                'position': positions[idx] if idx < len(positions) else positions[0],
                'dash_array': f"{dash_length:.2f} {circumference:.2f}",
                'dash_offset': f"{dash_offset:.2f}",
            })
            
            cumulative_percent += percentage
        
        # Get recent journal entries (last 10)
        recent_entries = JournalEntry.objects.select_related(
            'account', 'company'
        ).order_by('-date', '-created_at')[:10]
        
        context = {
            'total_revenue': total_revenue,
            'total_expenses': total_expenses,
            'net_profit': net_profit,
            'cash_on_hand': cash_on_hand,
            'revenue_change': revenue_change,
            'expense_change': expense_change,
            'profit_change': profit_change,
            'monthly_data': monthly_data,
            'pie_chart_data': pie_chart_data,
            'recent_entries': recent_entries,
        }
        
        return render(request, 'finance/dashboard.html', context)
    
    def calculate_percentage_change(self, old_value, new_value):
        """Calculate percentage change between two values"""
        if old_value == 0:
            if new_value > 0:
                return 100.0
            return 0.0
        
        change = ((new_value - old_value) / old_value) * 100
        return round(change, 1)
    
    def get_monthly_data(self, months=6):
        """Get income and expense data for the last N months"""
        from datetime import datetime, timedelta
        from decimal import Decimal
        
        monthly_data = []
        today = datetime.now()
        
        # Find max values for scaling
        max_income = Decimal('1')
        max_expense = Decimal('1')
        
        # First pass: collect data and find max values
        temp_data = []
        for i in range(months - 1, -1, -1):
            month_date = today - timedelta(days=30 * i)
            month_start = month_date.replace(day=1)
            
            if month_start. month == 12:
                month_end = month_start.replace(year=month_start.year + 1, month=1, day=1) - timedelta(days=1)
            else:
                month_end = month_start.replace(month=month_start.month + 1, day=1) - timedelta(days=1)
            
            income = JournalEntry.objects. filter(
                account__account_type='income',
                date__gte=month_start,
                date__lte=month_end
            ).aggregate(total=Sum('credit_amount'))['total'] or Decimal('0.00')
            
            expense = JournalEntry.objects.filter(
                account__account_type='expense',
                date__gte=month_start,
                date__lte=month_end
            ).aggregate(total=Sum('debit_amount'))['total'] or Decimal('0.00')
            
            max_income = max(max_income, income)
            max_expense = max(max_expense, expense)
            
            temp_data.append({
                'month': month_start.strftime('%b'),
                'income': income,
                'expense': expense,
            })
        
        # Second pass: calculate heights as percentages
        max_value = max(max_income, max_expense)
        
        for data in temp_data:
            income_height = int((float(data['income']) / float(max_value)) * 100) if max_value > 0 else 5
            expense_height = int((float(data['expense']) / float(max_value)) * 100) if max_value > 0 else 5
            
            # Ensure minimum height of 5% for visibility
            income_height = max(income_height, 5) if data['income'] > 0 else 0
            expense_height = max(expense_height, 5) if data['expense'] > 0 else 0
            
            monthly_data.append({
                'month': data['month'],
                'income_height': income_height,
                'expense_height':  expense_height,
            })
        
        return monthly_data
class Journal(View):
    """List all journal entries"""
    @method_decorator(login_required)
    def get(self, request):
        journal_entries = JournalEntry.objects.select_related('account', 'company').all()
        
        # Search functionality
        search_query = request.GET.get('search', '')
        if search_query:
            journal_entries = journal_entries.filter(
                models.Q(entry_number__icontains=search_query) |
                models.Q(account__name__icontains=search_query) |
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
            messages.success(request, f'Journal Entry "{journal_entry.entry_number}" updated successfully!')
            return redirect('finance-journal')
        else:
            messages.error(request, 'Please correct the errors below.')
        
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
            company.created_by = request.user
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
    @method_decorator(login_required)
    def get(self, request):
        from django.db.models import Sum, Count, Avg, Q, F, ExpressionWrapper, fields
        from datetime import datetime, timedelta
        from decimal import Decimal
        
        # Get all invoices
        all_invoices = Invoice.objects. select_related('company').all()
        
        # Calculate Total Payables (unpaid invoices:  draft + sent)
        unpaid_invoices = all_invoices.filter(Q(status='draft') | Q(status='sent'))
        total_payables = unpaid_invoices.aggregate(
            total=Sum('total_amount')
        )['total'] or Decimal('0.00')
        
        # Calculate Paid Invoices total
        paid_invoices_total = all_invoices.filter(status='paid').aggregate(
            total=Sum('total_amount')
        )['total'] or Decimal('0.00')
        
        # Calculate Overdue Invoices (assuming 30 days payment term)
        today = datetime.now().date()
        overdue_date = today - timedelta(days=30)
        overdue_invoices = unpaid_invoices.filter(date__lt=overdue_date)
        overdue_total = overdue_invoices.aggregate(
            total=Sum('total_amount')
        )['total'] or Decimal('0.00')
        
        # Calculate Average Payment Period
        # For paid invoices, calculate days between invoice date and when it was marked paid
        # This is a simplified calculation - you might want to add a payment_date field
        avg_payment_period = 45  # Default value, you can calculate this if you add payment_date field
        
        # Count invoices by status
        paid_count = all_invoices.filter(status='paid').count()
        pending_count = all_invoices.filter(Q(status='draft') | Q(status='sent')).count()
        overdue_count = overdue_invoices.count()
        
        # Filter by status from dropdown
        status_filter = request. GET.get('status', 'All Invoices')
        
        if status_filter == 'Paid':
            filtered_invoices = all_invoices.filter(status='paid')
        elif status_filter == 'Pending':
            filtered_invoices = unpaid_invoices.filter(date__gte=overdue_date)
        elif status_filter == 'Overdue':
            filtered_invoices = overdue_invoices
        else: 
            filtered_invoices = all_invoices
        
        # Prepare invoice list with due dates
        invoice_list = []
        for invoice in filtered_invoices. order_by('-date'):
            # Calculate due date (30 days from invoice date)
            due_date = invoice. date + timedelta(days=30)
            
            # Determine status for display
            if invoice.status == 'paid':
                display_status = 'Paid'
            elif invoice.date < overdue_date and invoice.status != 'paid':
                display_status = 'Overdue'
            else:
                display_status = 'Pending'
            
            invoice_list.append({
                'invoice_number': invoice.invoice_number,
                'vendor': invoice.supplier_name,
                'date':  invoice.date,
                'due_date': due_date,
                'amount':  invoice.total_amount,
                'status': display_status,
                'payment_method': 'Bank Transfer',  # You can add this field to your model
            })
        
        # Get vendor breakdown for chart (top 6 vendors by payables)
        vendor_breakdown = unpaid_invoices.values('supplier_name').annotate(
            total=Sum('total_amount'),
            count=Count('id')
        ).order_by('-total')[:6]
        
        # Calculate max value for chart scaling
        max_vendor_amount = vendor_breakdown[0]['total'] if vendor_breakdown else 0
        
        # Prepare vendor chart data with percentages
        vendor_chart_data = []
        for vendor in vendor_breakdown:
            if max_vendor_amount > 0:
                percentage = (float(vendor['total']) / float(max_vendor_amount)) * 100
            else:
                percentage = 0
            
            vendor_chart_data.append({
                'name': vendor['supplier_name'],
                'total': vendor['total'],
                'percentage': percentage,
            })
        
        # Pad with empty vendors if less than 6
        while len(vendor_chart_data) < 6:
            vendor_chart_data.append({
                'name': f'Vendor {len(vendor_chart_data) + 1}',
                'total': 0,
                'percentage': 0,
            })
        
        context = {
            'total_payables': total_payables,
            'paid_invoices_total': paid_invoices_total,
            'overdue_total': overdue_total,
            'avg_payment_period': avg_payment_period,
            'paid_count': paid_count,
            'pending_count': pending_count,
            'overdue_count': overdue_count,
            'invoice_list': invoice_list,
            'vendor_chart_data': vendor_chart_data,
            'status_filter': status_filter,
        }
        
        return render(request, 'finance/payables.html', context)
class Invoices(View):
    """List all invoices"""
    @method_decorator(login_required)
    def get(self, request):
        invoices = Invoice.objects.select_related('company').all()
        
        # Search functionality
        search_query = request.GET.get('search', '')
        if search_query:
            invoices = invoices.filter(
                models.Q(invoice_number__icontains=search_query) |
                models.Q(customer_name__icontains=search_query) |
                models.Q(supplier_name__icontains=search_query)
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
            messages.error(request, 'Please correct the errors below.')
        
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
                messages.success(request, f'Welcome back, {user.first_name}!')
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
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
        
        return render(request, 'finance/signup.html', {'form': form})


class Logout(View):
    def get(self, request):
        # Don't logout on GET, just redirect
        if request.user.is_authenticated:
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