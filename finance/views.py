from django.shortcuts import redirect, render, get_object_or_404
from django.views import View
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from .forms import LoginForm, SignupForm, CompanyForm, AccountForm, InvoiceForm, JournalEntryForm, SupplierForm
from django.db import models
from .models import Company, Account, Invoice, JournalEntry, Supplier
from django.contrib.messages import get_messages
from django.db.models import Sum, Q
from datetime import datetime, timedelta
from django.utils import timezone
from decimal import Decimal
import math
from django.db.models.functions import Coalesce
from django.db.models import Value as V, DecimalField

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
        asset_debits = JournalEntry.objects.filter(
            account__account_type='asset'
        ).aggregate(total=Sum('debit_amount'))['total'] or Decimal('0.00')
        
        asset_credits = JournalEntry.objects.filter(
            account__account_type='asset'
        ).aggregate(total=Sum('credit_amount'))['total'] or Decimal('0.00')
        
        cash_on_hand = asset_credits - asset_debits
        
        # Get previous month data for comparison
        today = datetime.now()
        first_day_current_month = today.replace(day=1)
        last_day_previous_month = first_day_current_month - timedelta(days=1)
        first_day_previous_month = last_day_previous_month.replace(day=1)
        
        # Current month revenue (for comparison)
        current_revenue = JournalEntry.objects.filter(
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
            circumference = 2 * math.pi * 40  # radius = 40
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
         # ===== DEBUG: ADD THIS BEFORE context = {...} =====
        print("\n" + "="*60)
        print("DASHBOARD DEBUG INFO")
        print("="*60)
        
        # Check account types
        from django.db.models import Count
        account_type_counts = Account.objects.values('account_type').annotate(count=Count('id'))
        print("\n📊 Accounts by Type:")
        for item in account_type_counts: 
            print(f"  {item['account_type'] or 'NO TYPE SET'}: {item['count']} accounts")
        
        # Check journal entries
        print(f"\n📝 Total Journal Entries: {JournalEntry.objects.count()}")
        
        # Check entries with income accounts
        income_entries = JournalEntry.objects.filter(account__account_type='income')
        print(f"\n💰 Income Entries: {income_entries.count()}")
        for entry in income_entries[: 3]: 
            print(f"  - {entry.entry_number}: {entry.account.name} | Credit: ${entry.credit_amount} | Debit: ${entry.debit_amount}")
        
        # Check entries with expense accounts
        expense_entries = JournalEntry.objects.filter(account__account_type='expense')
        print(f"\n💸 Expense Entries: {expense_entries.count()}")
        for entry in expense_entries[: 3]:
            print(f"  - {entry.entry_number}: {entry.account.name} | Debit: ${entry.debit_amount} | Credit: ${entry.credit_amount}")
        
        # Show ALL journal entries with their account types
        print(f"\n📋 First 5 Journal Entries:")
        for entry in JournalEntry.objects.all()[:5]:
            print(f"  {entry.entry_number}: Account={entry.account.name} (Type: {entry.account.account_type or 'NO TYPE'}) | Debit=${entry.debit_amount} | Credit=${entry.credit_amount}")
        
        print("\n" + "="*60 + "\n")
        # ===== END DEBUG =====
        
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
            
            if month_start.month == 12:
                month_end = month_start.replace(year=month_start.year + 1, month=1, day=1) - timedelta(days=1)
            else:
                month_end = month_start.replace(month=month_start.month + 1, day=1) - timedelta(days=1)
            
            income = JournalEntry.objects.filter(
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
    @method_decorator(login_required)
    def get(self, request):
        """
        Build a trial balance table using the correct related_name 'journal_entries'
        and ensure Coalesce uses a Decimal fallback and output_field=DecimalField().
        """
        # Annotate accounts with summed debits/credits (Coalesce to default 0.00 as Decimal)
        accounts_qs = Account.objects.all().annotate(
            total_debit=Coalesce(Sum('journal_entries__debit_amount'), V(Decimal('0.00')), output_field=DecimalField()),
            total_credit=Coalesce(Sum('journal_entries__credit_amount'), V(Decimal('0.00')), output_field=DecimalField()),
        ).order_by('account_number', 'name')

        accounts_list = []
        total_debits = Decimal('0.00')
        total_credits = Decimal('0.00')

        for acc in accounts_qs:
            # total_debit/total_credit are Decimal-compatible now
            debit = Decimal(acc.total_debit) if acc.total_debit is not None else Decimal('0.00')
            credit = Decimal(acc.total_credit) if acc.total_credit is not None else Decimal('0.00')

            accounts_list.append({
                'code': getattr(acc, 'account_number', '') or '',
                'name': acc.name,
                'type': (acc.account_type.capitalize() if acc.account_type else 'Unknown'),
                'debit': debit,
                'credit': credit,
                'balance': debit - credit,
            })

            total_debits += debit
            total_credits += credit

        discrepancy = total_debits - total_credits

        context = {
            'accounts_list': accounts_list,
            'total_debits': total_debits,
            'total_credits': total_credits,
            'discrepancy': discrepancy,
        }

        return render(request, 'finance/trial.html', context)
    
class Ledger(View):
    @method_decorator(login_required)  # Require login to access
    def get(self, request):
        """
        Render the ledger page with:
          - accounts: list for the account dropdown
          - selected_account: Account instance
          - entries: list of dicts {date, description, debit, credit, balance}
          - closing_balance: final running balance (Decimal)
          - currency_symbol: from account if available, else fallback '$'
        Balance calculation:
          - For asset/expense accounts: balance increases with debit, decreases with credit
          - For other account types (liability/equity/income): balance increases with credit, decreases with debit
        """
        account_id = request.GET.get('account')
        accounts = Account.objects.all().order_by('name')
        selected_account = None
        entries = []
        closing_balance = Decimal('0.00')
        currency_symbol = '$'

        # Select account (use provided account id or the first account)
        if account_id:
            try:
                selected_account = Account.objects.get(pk=account_id)
            except Account.DoesNotExist:
                selected_account = None

        if not selected_account and accounts.exists():
            selected_account = accounts.first()

        if selected_account:
            # Optional: if your Account model has a currency or symbol field
            currency_symbol = getattr(selected_account, 'currency_symbol', getattr(selected_account, 'currency', '$'))

            # Fetch journal entries ordered from oldest -> newest to compute running balance
            journal_qs = JournalEntry.objects.filter(account=selected_account).order_by('date', 'created_at')

            # Decide whether debits increase balance (typical for assets & expenses)
            increase_by_debit = (selected_account.account_type in ['asset', 'expense'])

            running = Decimal('0.00')

            for je in journal_qs:
                debit = je.debit_amount or Decimal('0.00')
                credit = je.credit_amount or Decimal('0.00')

                if increase_by_debit:
                    running = running + debit - credit
                else:
                    running = running + credit - debit

                entries.append({
                    'date': je.date,
                    'description': je.description,
                    'debit': debit,
                    'credit': credit,
                    'balance': running,
                })

            closing_balance = running

        context = {
            'accounts': accounts,
            'selected_account': selected_account,
            'entries': entries,
            'closing_balance': closing_balance,
            'currency_symbol': currency_symbol or '$',
        }

        return render(request, 'finance/ledger.html', context)
    
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
        all_invoices = Invoice.objects.select_related('company').all()
        
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
        status_filter = request.GET.get('status', 'All Invoices')
        
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
        for invoice in filtered_invoices.order_by('-date'):
            # Calculate due date (30 days from invoice date)
            due_date = invoice.date + timedelta(days=30)
            
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

class Suppliers(View):
    """List all suppliers"""
    @method_decorator(login_required)
    def get(self, request):
        suppliers = Supplier.objects.select_related('company', 'created_by').all().order_by('-created_at')

        search_query = request.GET.get('search', '')
        if search_query:
            suppliers = suppliers.filter(
                models.Q(name__icontains=search_query) |
                models.Q(contact_email__icontains=search_query) |
                models.Q(contact_mobile__icontains=search_query)
            )

        context = {
            'suppliers': suppliers,
            'search_query': search_query,
            'total_count': Supplier.objects.count(),
        }
        return render(request, 'finance/suppliers.html', context)


class SupplierCreate(View):
    """Create new supplier"""
    @method_decorator(login_required)
    def get(self, request):
        form = SupplierForm()
        return render(request, 'finance/supplier_form.html', {
            'form': form,
            'action': 'New',
            'is_modal': True,  # template can render as modal if desired
        })

    @method_decorator(login_required)
    def post(self, request):
        form = SupplierForm(request.POST)
        if form.is_valid():
            supplier = form.save(commit=False)
            supplier.created_by = request.user
            supplier.save()
            messages.success(request, f'Supplier "{supplier.name}" created successfully!')
            return redirect('finance-suppliers')
        else:
            messages.error(request, 'Please correct the errors below.')
        return render(request, 'finance/supplier_form.html', {
            'form': form,
            'action': 'New',
            'is_modal': True,
        })


class SupplierEdit(View):
    """Edit supplier"""
    @method_decorator(login_required)
    def get(self, request, pk):
        supplier = get_object_or_404(Supplier, pk=pk)
        form = SupplierForm(instance=supplier)
        return render(request, 'finance/supplier_form.html', {
            'form': form,
            'supplier': supplier,
            'action': 'Edit',
            'is_modal': False,
        })

    @method_decorator(login_required)
    def post(self, request, pk):
        supplier = get_object_or_404(Supplier, pk=pk)
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            messages.success(request, f'Supplier "{supplier.name}" updated successfully!')
            return redirect('finance-suppliers')
        else:
            messages.error(request, 'Please correct the errors below.')
        return render(request, 'finance/supplier_form.html', {
            'form': form,
            'supplier': supplier,
            'action': 'Edit',
            'is_modal': False,
        })


class SupplierDelete(View):
    @method_decorator(login_required)
    def post(self, request, pk):
        supplier = get_object_or_404(Supplier, pk=pk)
        name = supplier.name
        supplier.delete()
        messages.success(request, f'Supplier "{name}" deleted successfully!')
        return redirect('finance-suppliers')

class Receivables(View):
    @method_decorator(login_required)
    def get(self, request):
        from django.db.models import Sum, Count, Avg, Q, F, ExpressionWrapper, fields
        from datetime import datetime, timedelta
        from decimal import Decimal
        
        # Get all customer invoices (receivables are invoices FROM customers)
        all_invoices = Invoice.objects.select_related('company').filter(
            customer_name__isnull=False
        ).exclude(customer_name='')
        
        # If you don't have a field to distinguish, just use all invoices
        # all_invoices = Invoice.objects. select_related('company').all()
        
        # Calculate Total Receivables (unpaid invoices:  draft + sent)
        unpaid_invoices = all_invoices.filter(Q(status='draft') | Q(status='sent'))
        total_receivables = unpaid_invoices.aggregate(
            total=Sum('total_amount')
        )['total'] or Decimal('0.00')
        
        # Calculate Paid Invoices total
        paid_invoices_total = all_invoices. filter(status='paid').aggregate(
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
        avg_payment_period = 45  # Default value
        
        # Count invoices by status
        paid_count = all_invoices. filter(status='paid').count()
        pending_count = all_invoices.filter(Q(status='draft') | Q(status='sent')).count()
        overdue_count = overdue_invoices.count()
        
        # Filter by status from dropdown
        status_filter = request.GET. get('status', 'All Invoices')
        
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
            due_date = invoice.date + timedelta(days=30)
            
            # Determine status for display
            if invoice.status == 'paid':
                display_status = 'Paid'
            elif invoice.date < overdue_date and invoice.status != 'paid':
                display_status = 'Overdue'
            else:
                display_status = 'Pending'
            
            invoice_list.append({
                'invoice_number': invoice.invoice_number,
                'vendor':  invoice.customer_name or 'N/A',  # Customer name for receivables
                'date': invoice.date,
                'due_date': due_date,
                'amount': invoice.total_amount,
                'status': display_status,
                'payment_method': 'Bank Transfer',
            })
        
        # Get monthly receivables data for chart (last 6 months)
        monthly_chart_data = []
        for i in range(5, -1, -1):  # 6 months
            month_date = today - timedelta(days=30 * i)
            month_start = month_date.replace(day=1)
            
            if month_start.month == 12:
                month_end = month_start.replace(year=month_start.year + 1, month=1, day=1) - timedelta(days=1)
            else:
                month_end = month_start.replace(month=month_start.month + 1, day=1) - timedelta(days=1)
            
            month_receivables = all_invoices.filter(
                date__gte=month_start,
                date__lte=month_end
            ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
            
            monthly_chart_data.append({
                'month': month_start.strftime('%b'),
                'amount': float(month_receivables),
            })
        
        # Find max value for scaling
        max_amount = max([item['amount'] for item in monthly_chart_data]) if monthly_chart_data else 1
        if max_amount == 0:
            max_amount = 1
        
        # Calculate SVG path points (scale to 260 height, 1000 width)
        chart_height = 260
        chart_width = 1000
        points = []
        circles = []
        
        for idx, data in enumerate(monthly_chart_data):
            x = (idx / 5) * chart_width  # 6 points across 1000 width
            # Invert Y because SVG coordinates start from top
            y = chart_height - ((data['amount'] / max_amount) * chart_height)
            points.append(f"{x},{y}")
            circles.append({'x': x, 'y': y})
        
        polyline_points = ' '.join(points)
        
        context = {
            'total_receivables': total_receivables,
            'paid_invoices_total': paid_invoices_total,
            'overdue_total':  overdue_total,
            'avg_payment_period': avg_payment_period,
            'paid_count': paid_count,
            'pending_count': pending_count,
            'overdue_count': overdue_count,
            'invoice_list': invoice_list,
            'status_filter': status_filter,
            'polyline_points': polyline_points,
            'chart_circles': circles,
            'monthly_chart_data': monthly_chart_data,
        }
        
        return render(request, 'finance/receivables.html', context)   
class InvoiceScan(View):
    @method_decorator(login_required)  # Require login to access
    def get(self, request):
        return render(request, 'finance/scan.html', {}) 
class Reports(View):
    @method_decorator(login_required)  # Require login to access
    def get(self, request):
        """
        Compute dynamic data for the reports page (profit & loss, balance sheet, cash flow).
        Precompute label X positions for the cashflow chart to avoid template arithmetic.

        NOTE: totals passed for display are absolute (non-negative) to avoid showing
        a negative sign for aggregate totals. Individual account balances keep their sign.
        """
        now = timezone.now()
        # --- Profit & Loss (Income Statement) ---
        income_qs = JournalEntry.objects.filter(account__account_type='income')
        revenue_by_account = income_qs.values('account__name').annotate(
            total=Coalesce(Sum('credit_amount'), V(Decimal('0.00')), output_field=DecimalField())
        ).order_by('-total')

        revenue_items = []
        total_revenue = Decimal('0.00')
        for r in revenue_by_account:
            amt = Decimal(r['total'] or 0)
            revenue_items.append({'label': r['account__name'], 'amount': amt})
            total_revenue += amt

        expense_qs = JournalEntry.objects.filter(account__account_type='expense')
        expense_by_account = expense_qs.values('account__name').annotate(
            total=Coalesce(Sum('debit_amount'), V(Decimal('0.00')), output_field=DecimalField())
        ).order_by('-total')

        expense_items = []
        total_expenses = Decimal('0.00')
        for e in expense_by_account:
            amt = Decimal(e['total'] or 0)
            expense_items.append({'label': e['account__name'], 'amount': amt})
            total_expenses += amt

        net_profit = total_revenue - total_expenses

        revenue_display = revenue_items[:4] if revenue_items else [{'label': 'Sales Revenue', 'amount': Decimal('0.00')}]
        expense_display = expense_items[:5] if expense_items else [{'label': 'Salaries Expense', 'amount': Decimal('0.00')}]

        # --- Balance Sheet ---
        asset_qs = Account.objects.filter(account_type='asset').annotate(
            debit_sum=Coalesce(Sum('journal_entries__debit_amount'), V(Decimal('0.00')), output_field=DecimalField()),
            credit_sum=Coalesce(Sum('journal_entries__credit_amount'), V(Decimal('0.00')), output_field=DecimalField()),
        )

        assets_list = []
        total_assets = Decimal('0.00')
        for a in asset_qs:
            debit = Decimal(a.debit_sum or 0)
            credit = Decimal(a.credit_sum or 0)
            balance = debit - credit  # signed balance
            display_balance = abs(balance)
            assets_list.append({
                'name': a.name,
                'balance': balance,                    # keep raw signed value if needed
                'display_balance': display_balance,    # non-negative value for UI
                'is_negative': balance < 0,            # flag for styling/formatting
            })
            total_assets += balance

        liability_qs = Account.objects.filter(account_type='liability').annotate(
            debit_sum=Coalesce(Sum('journal_entries__debit_amount'), V(Decimal('0.00')), output_field=DecimalField()),
            credit_sum=Coalesce(Sum('journal_entries__credit_amount'), V(Decimal('0.00')), output_field=DecimalField()),
        )

        liabilities_list = []
        total_liabilities = Decimal('0.00')
        for l in liability_qs:
            debit = Decimal(l.debit_sum or 0)
            credit = Decimal(l.credit_sum or 0)
            balance = credit - debit  # signed balance (normal credit balance)
            display_balance = abs(balance)   # non-negative for UI
            liabilities_list.append({
                'name': l.name,
                'balance': balance,                # keep signed value if needed elsewhere
                'display_balance': display_balance,
                'is_negative': balance < 0,        # flag for styling
            })
            total_liabilities += balance

        equity_qs = Account.objects.filter(account_type='equity').annotate(
            debit_sum=Coalesce(Sum('journal_entries__debit_amount'), V(Decimal('0.00')), output_field=DecimalField()),
            credit_sum=Coalesce(Sum('journal_entries__credit_amount'), V(Decimal('0.00')), output_field=DecimalField()),
        )

        equity_list = []
        total_equity = Decimal('0.00')
        for q in equity_qs:
            debit = Decimal(q.debit_sum or 0)
            credit = Decimal(q.credit_sum or 0)
            balance = credit - debit
            display_balance = abs(balance)
            equity_list.append({
                'name': q.name,
                'balance': balance,
                'display_balance': display_balance,
                'is_negative': balance < 0,
            })
            total_equity += balance

        total_liabilities_and_equity = total_liabilities + total_equity

        # Make non-negative "display" totals so totals appear positive in the UI
        display_total_assets = abs(total_assets)
        display_total_liabilities = abs(total_liabilities)
        display_total_equity = abs(total_equity)
        display_total_liabilities_and_equity = abs(total_liabilities_and_equity)

        # --- Cash Flow (last 6 months) ---
        months = 6
        cashflow_months = []
        cashflow_operating = []
        cashflow_investing = []
        cashflow_financing = []

        def month_range_from_date(ref_date):
            start = ref_date.replace(day=1)
            if start.month == 12:
                end = start.replace(year=start.year + 1, month=1, day=1) - timedelta(days=1)
            else:
                end = start.replace(month=start.month + 1, day=1) - timedelta(days=1)
            return start, end

        for i in range(months - 1, -1, -1):
            month_date = (now - timedelta(days=30 * i)).date()
            m_start, m_end = month_range_from_date(month_date)

            income_month = JournalEntry.objects.filter(
                account__account_type='income',
                date__gte=m_start,
                date__lte=m_end
            ).aggregate(total=Coalesce(Sum('credit_amount'), V(Decimal('0.00')), output_field=DecimalField()))['total'] or Decimal('0.00')

            expense_month = JournalEntry.objects.filter(
                account__account_type='expense',
                date__gte=m_start,
                date__lte=m_end
            ).aggregate(total=Coalesce(Sum('debit_amount'), V(Decimal('0.00')), output_field=DecimalField()))['total'] or Decimal('0.00')

            operating = Decimal(income_month) - Decimal(expense_month)

            asset_debits = JournalEntry.objects.filter(
                account__account_type='asset',
                date__gte=m_start,
                date__lte=m_end
            ).aggregate(total=Coalesce(Sum('debit_amount'), V(Decimal('0.00')), output_field=DecimalField()))['total'] or Decimal('0.00')

            asset_credits = JournalEntry.objects.filter(
                account__account_type='asset',
                date__gte=m_start,
                date__lte=m_end
            ).aggregate(total=Coalesce(Sum('credit_amount'), V(Decimal('0.00')), output_field=DecimalField()))['total'] or Decimal('0.00')

            investing = Decimal(asset_debits) - Decimal(asset_credits)

            liab_debits = JournalEntry.objects.filter(
                account__account_type='liability',
                date__gte=m_start,
                date__lte=m_end
            ).aggregate(total=Coalesce(Sum('debit_amount'), V(Decimal('0.00')), output_field=DecimalField()))['total'] or Decimal('0.00')

            liab_credits = JournalEntry.objects.filter(
                account__account_type='liability',
                date__gte=m_start,
                date__lte=m_end
            ).aggregate(total=Coalesce(Sum('credit_amount'), V(Decimal('0.00')), output_field=DecimalField()))['total'] or Decimal('0.00')

            eq_debits = JournalEntry.objects.filter(
                account__account_type='equity',
                date__gte=m_start,
                date__lte=m_end
            ).aggregate(total=Coalesce(Sum('debit_amount'), V(Decimal('0.00')), output_field=DecimalField()))['total'] or Decimal('0.00')

            eq_credits = JournalEntry.objects.filter(
                account__account_type='equity',
                date__gte=m_start,
                date__lte=m_end
            ).aggregate(total=Coalesce(Sum('credit_amount'), V(Decimal('0.00')), output_field=DecimalField()))['total'] or Decimal('0.00')

            financing = (Decimal(liab_credits) - Decimal(liab_debits)) + (Decimal(eq_credits) - Decimal(eq_debits))

            cashflow_months.append(m_start.strftime('%b'))
            cashflow_operating.append(float(operating))
            cashflow_investing.append(float(investing))
            cashflow_financing.append(float(financing))

        # Prepare polylines
        def make_polyline(data_list, chart_width=1000, chart_height=260):
            if not data_list:
                return ''
            max_val = max(abs(v) for v in data_list) or 1
            points = []
            for idx, val in enumerate(data_list):
                x = (idx / (len(data_list) - 1)) * chart_width if len(data_list) > 1 else chart_width / 2
                mid = chart_height / 2
                y = mid - ((val / max_val) * (chart_height / 2))
                points.append(f"{int(x+150)},{int(y)}")  # offset by 150 to match SVG axis
            return ' '.join(points)

        poly_operating = make_polyline(cashflow_operating)
        poly_investing = make_polyline(cashflow_investing)
        poly_financing = make_polyline(cashflow_financing)

        operating_metric = Decimal(cashflow_operating[-1]) if cashflow_operating else Decimal('0.00')
        investing_metric = Decimal(cashflow_investing[-1]) if cashflow_investing else Decimal('0.00')
        financing_metric = Decimal(cashflow_financing[-1]) if cashflow_financing else Decimal('0.00')

        # Compute label X positions (no template math needed)
        label_positions = []
        n = len(cashflow_months) or 1
        for idx in range(n):
            x = int(150 + (idx / (n - 1) * 1000)) if n > 1 else int(150 + 1000 / 2)
            label_positions.append({'label': cashflow_months[idx], 'x': x})

        recent_entries = JournalEntry.objects.select_related('account', 'company').order_by('-date', '-created_at')[:10]
        display_financing_activities = abs(financing_metric)
        context = {
            'revenue_items': revenue_display,
            'expense_items': expense_display,
            'total_revenue': total_revenue,
            'total_expenses': total_expenses,
            'net_profit': net_profit,
            'assets_list': assets_list,
            'liabilities_list': liabilities_list,
            'equity_list': equity_list,
            # Keep raw totals if you need them for calculations, but pass display totals too
            'total_assets': total_assets,
            'total_liabilities': total_liabilities,
            'total_equity': total_equity,
            'total_liabilities_and_equity': total_liabilities_and_equity,
            'display_total_assets': display_total_assets,
            'display_total_liabilities': display_total_liabilities,
            'display_total_equity': display_total_equity,
            'display_total_liabilities_and_equity': display_total_liabilities_and_equity,
            'cashflow_months': cashflow_months,
            'cashflow_operating': cashflow_operating,
            'cashflow_investing': cashflow_investing,
            'cashflow_financing': cashflow_financing,
            'poly_operating': poly_operating,
            'poly_investing': poly_investing,
            'poly_financing': poly_financing,
            'operating_metric': operating_metric,
            'investing_metric': investing_metric,
            'financing_metric': display_financing_activities,
            'cashflow_labels': label_positions,
            'recent_entries': recent_entries,
        }

        return render(request, 'finance/reports.html', context)
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