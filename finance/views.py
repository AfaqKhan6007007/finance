import io
from xml.parsers.expat import model
import os
from django.conf import settings
from django.shortcuts import redirect, render, get_object_or_404
from django.views import View
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from .forms import AccountingDimensionForm, BankAccountForm, BudgetForm, CostCenterAllocationsForm, CostCenterForm, DeductionCertificateForm, LoginForm, SignupForm, CompanyForm, AccountForm, InvoiceForm, JournalEntryForm, SupplierForm, CustomerForm, TaxAccountFormSet, TaxCategoryForm, TaxItemTemplatesForm, TaxRateFormSet, TaxRuleForm, TaxWithholdingCategoryForm
from django.db import models, transaction
from .models import AccountingDimension, BankAccount, Budget, Company, Account, CostCenter, CostCenterAllocation, Customer, DeductionCertificate, Invoice, JournalEntry, Supplier, TaxCategory, TaxItemTemplate, TaxRule, TaxWithholdingCategory
from django.contrib.messages import get_messages
from django.db.models import Sum, Q
from datetime import datetime, timedelta
from django.utils import timezone
from decimal import Decimal
import math
from django.db.models.functions import Coalesce
from django.db.models import Value as V, DecimalField
from PIL import Image
import numpy as np
import base64
import cv2
import pdfplumber
import statistics
import fitz
import re
import json
from google.cloud import vision, storage
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import arabic_reshaper
from bidi.algorithm import get_display
from openai import OpenAI
from pdfminer.high_level import extract_text

client_openai = OpenAI(api_key=settings.OPENAI_API_KEY)

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

class Budgets(View):
    """List all budgets"""

    @method_decorator(login_required)
    def get(self, request):
        budgets = Budget.objects.select_related(
            'company',
            'account',
            'cost_center'
        ).all()

        # Search by series
        search_query = request.GET.get('search', '')
        if search_query:
            budgets = budgets.filter(series__icontains=search_query)

        # Filter by ID
        id_filter = request.GET.get('id', '')
        if id_filter:
            budgets = budgets.filter(id=id_filter)

        # Filter by Cost Center
        cost_center_filter = request.GET.get('cost_center', '')
        if cost_center_filter:
            budgets = budgets.filter(cost_center_id=cost_center_filter)

        # Filter by Company
        company_filter = request.GET.get('company', '')
        if company_filter:
            budgets = budgets.filter(company_id=company_filter)

        # Filter by Account
        account_filter = request.GET.get('account', '')
        if account_filter:
            budgets = budgets.filter(account_id=account_filter)

        # Filter by Budget Against
        budget_against_filter = request.GET.get('budget_against', '')
        if budget_against_filter:
            budgets = budgets.filter(budget_against=budget_against_filter)

        # Filter by Distribution
        distribution_filter = request.GET.get('distribution', '')
        if distribution_filter:
            budgets = budgets.filter(distribution=distribution_filter)

        context = {
            'budgets': budgets,
            'search_query': search_query,
            'id_filter': id_filter,
            'company_filter': company_filter,
            'account_filter': account_filter,
            'budget_against_filter': budget_against_filter,
            'distribution_filter': distribution_filter,
            'total_count': Budget.objects.count(),
            'companies': Company.objects.all(),
            'accounts': Account.objects.all(),
            'cost_centers': CostCenter.objects.filter(is_group=False, is_disabled=False),
            'cost_center_filter': cost_center_filter,
        }

        return render(request, 'finance/budgets.html', context)
    
class BudgetCreate(View):
    """Create new budget"""

    @method_decorator(login_required)
    def get(self, request):
        form = BudgetForm()
        return render(request, 'finance/budget_form.html', {
            'form': form,
            'action': 'New',
            'is_edit': False
        })

    @method_decorator(login_required)
    def post(self, request):
        form = BudgetForm(request.POST)

        # Debug
        print("POST data:", request.POST)

        if form.is_valid():
            budget = form.save()
            messages.success(
                request,
                f'Budget "{budget.series}" created successfully!'
            )
            return redirect('finance-budgets')
        else:
            print("Form errors:", form.errors)
            messages.error(request, 'Please correct the errors below.')

        return render(request, 'finance/budget_form.html', {
            'form': form,
            'action': 'New',
            'is_edit': False
        })
    
class BudgetEdit(View):
    """Edit existing budget"""

    @method_decorator(login_required)
    def get(self, request, pk):
        budget = get_object_or_404(Budget, pk=pk)
        form = BudgetForm(instance=budget)
        return render(request, 'finance/budget_form.html', {
            'form': form,
            'budget': budget,
            'action': 'Edit',
            'is_edit': True
        })

    @method_decorator(login_required)
    def post(self, request, pk):
        budget = get_object_or_404(Budget, pk=pk)
        form = BudgetForm(request.POST, instance=budget)

        # Debug
        print("POST data:", request.POST)

        if form.is_valid():
            form.save()
            messages.success(
                request,
                f'Budget "{budget.series}" updated successfully!'
            )
            return redirect('finance-budgets')
        else:
            print("Form errors:", form.errors)
            messages.error(request, 'Please correct the errors below.')

        return render(request, 'finance/budget_form.html', {
            'form': form,
            'budget': budget,
            'action': 'Edit',
            'is_edit': True
        })
    
class BudgetDelete(View):
    """Delete budget"""

    @method_decorator(login_required)
    def post(self, request, pk):
        budget = get_object_or_404(Budget, pk=pk)
        series = budget.series
        budget.delete()
        messages.success(
            request,
            f'Budget "{series}" deleted successfully!'
        )
        return redirect('finance-budgets')
    
class CostCenters(View):
    """List all Cost Centers"""

    @method_decorator(login_required)
    def get(self, request):
        cost_centers = CostCenter.objects.select_related(
            'company',
            'parent',
        ).order_by('-created_at')

        # Search by series
        search_query = request.GET.get('search', '')
        if search_query:
            cost_centers = cost_centers.filter(name__icontains=search_query)

        # Filter by Company
        company_filter = request.GET.get('company', '')
        if company_filter:
            cost_centers = cost_centers.filter(company_id=company_filter)

        # Filter by Parent
        parent_filter = request.GET.get('parent', '')
        if parent_filter:
            cost_centers = cost_centers.filter(parent_id=parent_filter)
        context = {
            'cost_centers': cost_centers,
            'search_query': search_query,
            'company_filter': company_filter,
            'parent_filter': parent_filter,
            'companies': Company.objects.all(),
            'parents': CostCenter.objects.all(),
            'total_count': CostCenter.objects.count(),
        }

        return render(request, 'finance/cost_centers.html', context)

class CostCenterCreate(View):
    """Create new cost center"""

    @method_decorator(login_required)
    def get(self, request):
        form = CostCenterForm()
        return render(request, 'finance/cost_center_form.html', {
            'form': form,
            'action': 'New',
            'is_edit': False
        })

    @method_decorator(login_required)
    def post(self, request):
        form = CostCenterForm(request.POST)
        # Debug
        print("POST data:", request.POST)

        if form.is_valid():
            cost_center = form.save()
            messages.success(
                request,
                f'Cost Center "{cost_center.name}" created successfully!'
            )
            return redirect('finance-cost-centers')
        else:
            print("Form errors:", form.errors)
            messages.error(request, 'Please correct the errors below.')

        return render(request, 'finance/cost_center_form.html', {
            'form': form,
            'action': 'New',
            'is_edit': False
        })
    
class CostCenterEdit(View):
    """Edit existing cost center"""

    @method_decorator(login_required)
    def get(self, request, pk):
        cost_center = get_object_or_404(CostCenter, pk=pk)
        form = CostCenterForm(instance=cost_center)
        return render(request, 'finance/cost_center_form.html', {
            'form': form,
            'cost_center': cost_center,
            'action': 'Edit',
            'is_edit': True
        })

    @method_decorator(login_required)
    def post(self, request, pk):
        cost_center = get_object_or_404(CostCenter, pk=pk)
        form = CostCenterForm(request.POST, instance=cost_center)

        # Debug
        print("POST data:", request.POST)

        if form.is_valid():
            form.save()
            messages.success(
                request,
                f'Cost Center "{cost_center.name}" updated successfully!'
            )
            return redirect('finance-cost-centers')
        else:
            print("Form errors:", form.errors)
            messages.error(request, 'Please correct the errors below.')

        return render(request, 'finance/cost_center_form.html', {
            'form': form,
            'cost_center': cost_center,
            'action': 'Edit',
            'is_edit': True
        })
    
class CostCenterDelete(View):
    """Delete cost center"""

    @method_decorator(login_required)
    def post(self, request, pk):
        cost_center = get_object_or_404(CostCenter, pk=pk)
        name = cost_center.name
        cost_center.delete()
        messages.success(
            request,
            f'Cost Center "{name}" deleted successfully!'
        )
        return redirect('finance-cost-centers')
    

class AccountingDimensions(View):
    """List all Accounting Dimensions"""

    @method_decorator(login_required)
    def get(self, request):
        accounting_dimensions = AccountingDimension.objects.all()

        # Search by series
        search_query = request.GET.get('search', '')
        if search_query:
            accounting_dimensions = accounting_dimensions.filter(name__icontains=search_query)

        context = {
            'accounting_dimensions': accounting_dimensions,
            'search_query': search_query,
            'total_count': AccountingDimension.objects.count(),
        }

        return render(request, 'finance/accountingdimensions.html', context)

class AccountingDimensionCreate(View):
    """Create new accounting dimension"""

    @method_decorator(login_required)
    def get(self, request):
        form = AccountingDimensionForm()
        return render(request, 'finance/accounting_dimensions_form.html', {
            'form': form,
            'action': 'New',
            'is_edit': False
        })

    @method_decorator(login_required)
    def post(self, request):
        form = AccountingDimensionForm(request.POST)
        # Debug
        print("POST data:", request.POST)

        if form.is_valid():
            accounting_dimension = form.save()
            messages.success(
                request,
                f'Accounting Dimension "{accounting_dimension.name}" created successfully!'
            )
            return redirect('finance-accounting-dimensions')
        else:
            print("Form errors:", form.errors)
            messages.error(request, 'Please correct the errors below.')

        return render(request, 'finance/accounting_dimensions_form.html', {
            'form': form,
            'action': 'New',
            'is_edit': False
        })

class AccountingDimensionEdit(View):
    """Edit existing accounting dimension"""

    @method_decorator(login_required)
    def get(self, request, pk):
        accounting_dimension = get_object_or_404(AccountingDimension, pk=pk)
        form = AccountingDimensionForm(instance=accounting_dimension)
        return render(request, 'finance/accounting_dimensions_form.html', {
            'form': form,
            'accounting_dimension': accounting_dimension,
            'action': 'Edit',
            'is_edit': True
        })

    @method_decorator(login_required)
    def post(self, request, pk):
        accounting_dimension = get_object_or_404(AccountingDimension, pk=pk)
        form = AccountingDimensionForm(request.POST, instance=accounting_dimension)

        # Debug
        print("POST data:", request.POST)

        if form.is_valid():
            form.save()
            messages.success(
                request,
                f'Accounting Dimension "{accounting_dimension.name}" updated successfully!'
            )
            return redirect('finance-accounting-dimensions')
        else:
            print("Form errors:", form.errors)
            messages.error(request, 'Please correct the errors below.')

        return render(request, 'finance/accounting_dimensions_form.html', {
            'form': form,
            'accounting_dimension': accounting_dimension,
            'action': 'Edit',
            'is_edit': True
        })

class AccountingDimensionDelete(View):
    """Delete accounting dimension"""

    @method_decorator(login_required)
    def post(self, request, pk):
        accounting_dimension = get_object_or_404(AccountingDimension, pk=pk)
        name = accounting_dimension.name
        accounting_dimension.delete()
        messages.success(
            request,
            f'Accounting Dimension "{name}" deleted successfully!'
        )
        return redirect('finance-accounting-dimensions')


class TaxCategories(View):
    """List all Tax Categories"""

    @method_decorator(login_required)
    def get(self, request):
        tax_categories = TaxCategory.objects.all()

        # Search by series
        search_query = request.GET.get('search', '')
        if search_query:
            tax_categories = tax_categories.filter(title__icontains=search_query)

        context = {
            'tax_categories': tax_categories,
            'search_query': search_query,
            'total_count': TaxCategory.objects.count(),
        }

        return render(request, 'finance/taxcategories.html', context)

class TaxCategoryCreate(View):
    """Create new tax category"""

    @method_decorator(login_required)
    def get(self, request):
        form = TaxCategoryForm()
        return render(request, 'finance/taxcategories_form.html', {
            'form': form,
            'action': 'New',
            'is_edit': False
        })

    @method_decorator(login_required)
    def post(self, request):
        form = TaxCategoryForm(request.POST)
        # Debug
        print("POST data:", request.POST)

        if form.is_valid():
            tax_category = form.save()
            messages.success(
                request,
                f'Tax Category "{tax_category.title}" created successfully!'
            )
            return redirect('finance-tax-categories')
        else:
            print("Form errors:", form.errors)
            messages.error(request, 'Please correct the errors below.')

        return render(request, 'finance/taxcategories_form.html', {
            'form': form,
            'action': 'New',
            'is_edit': False
        })

class TaxCategoryEdit(View):
    """Edit existing tax category"""

    @method_decorator(login_required)
    def get(self, request, pk):
        tax_category = get_object_or_404(TaxCategory, pk=pk)
        form = TaxCategoryForm(instance=tax_category)
        return render(request, 'finance/taxcategories_form.html', {
            'form': form,
            'tax_category': tax_category,
            'action': 'Edit',
            'is_edit': True
        })

    @method_decorator(login_required)
    def post(self, request, pk):
        tax_category = get_object_or_404(TaxCategory, pk=pk)
        form = TaxCategoryForm(request.POST, instance=tax_category)

        # Debug
        print("POST data:", request.POST)

        if form.is_valid():
            form.save()
            messages.success(
                request,
                f'Tax Category "{tax_category.title}" updated successfully!'
            )
            return redirect('finance-tax-categories')
        else:
            print("Form errors:", form.errors)
            messages.error(request, 'Please correct the errors below.')

        return render(request, 'finance/taxcategories_form.html', {
            'form': form,
            'tax_category': tax_category,
            'action': 'Edit',
            'is_edit': True
        })

class TaxCategoryDelete(View):
    """Delete tax category"""

    @method_decorator(login_required)
    def post(self, request, pk):
        tax_category = get_object_or_404(TaxCategory, pk=pk)
        title = tax_category.title
        tax_category.delete()
        messages.success(
            request,
            f'Tax Category "{title}" deleted successfully!'
        )
        return redirect('finance-tax-categories')




class CostCenterAllocations(View):
    """List all Cost Center Allocations"""

    @method_decorator(login_required)
    def get(self, request):
        cost_center_allocations = CostCenterAllocation.objects.all()

        # Search by series
        search_query = request.GET.get('search', '')
        if search_query:
            cost_center_allocations = cost_center_allocations.filter(cost_center__name__icontains=search_query)
        context = {
            'cost_center_allocations': cost_center_allocations,
            'search_query': search_query,
            'total_count': CostCenterAllocation.objects.count(),
        }

        return render(request, 'finance/costcenterallocations.html', context)

class CostCenterAllocationsCreate(View):
    """Create new cost center allocation"""

    @method_decorator(login_required)
    def get(self, request):
        form = CostCenterAllocationsForm()
        return render(request, 'finance/cost_center_allocations_form.html', {
            'form': form,
            'action': 'New',
            'is_edit': False
        })

    @method_decorator(login_required)
    def post(self, request):
        form = CostCenterAllocationsForm(request.POST)
        # Debug
        print("POST data:", request.POST)

        if form.is_valid():
            cost_center_allocation = form.save()
            messages.success(
                request,
                f'Cost Center Allocation "{cost_center_allocation.cost_center}" created successfully!'
            )
            return redirect('finance-cost-center-allocations')
        else:
            print("Form errors:", form.errors)
            messages.error(request, 'Please correct the errors below.')

        return render(request, 'finance/cost_center_allocations_form.html', {
            'form': form,
            'action': 'New',
            'is_edit': False
        })

class CostCenterAllocationsEdit(View):
    """Edit existing cost center allocation"""

    @method_decorator(login_required)
    def get(self, request, pk):
        cost_center_allocation = get_object_or_404(CostCenterAllocation, pk=pk)
        form = CostCenterAllocationsForm(instance=cost_center_allocation)
        return render(request, 'finance/cost_center_allocations_form.html', {
            'form': form,
            'cost_center_allocation': cost_center_allocation,
            'action': 'Edit',
            'is_edit': True
        })

    @method_decorator(login_required)
    def post(self, request, pk):
        cost_center_allocation = get_object_or_404(CostCenterAllocation, pk=pk)
        form = CostCenterAllocationsForm(request.POST, instance=cost_center_allocation)

        # Debug
        print("POST data:", request.POST)

        if form.is_valid():
            form.save()
            messages.success(
                request,
                f'Cost Center Allocation "{cost_center_allocation.name}" updated successfully!'
            )
            return redirect('finance-cost-center-allocations')
        else:
            print("Form errors:", form.errors)
            messages.error(request, 'Please correct the errors below.')

        return render(request, 'finance/cost_center_allocations_form.html', {
            'form': form,
            'cost_center_allocation': cost_center_allocation,
            'action': 'Edit',
            'is_edit': True
        })

class CostCenterAllocationsDelete(View):
    """Delete cost center allocation"""

    @method_decorator(login_required)
    def post(self, request, pk):
        cost_center_allocation = get_object_or_404(CostCenterAllocation, pk=pk)
    
        cost_center_allocation.delete()
        messages.success(
            request,
            f'Cost Center Allocation "{cost_center_allocation.cost_center}" deleted successfully!'
        )
        return redirect('finance-cost-center-allocations')

class TaxItemTemplates(View):
    """List all Tax Item Templates"""

    @method_decorator(login_required)
    def get(self, request):
        tax_item_templates = TaxItemTemplate.objects.select_related(
            'company',
        ).all()

        # Search by series
        search_query = request.GET.get('search', '')
        if search_query:
            tax_item_templates = tax_item_templates.filter(title__icontains=search_query)

        # Filter by Company
        company_filter = request.GET.get('company', '')
        if company_filter:
            tax_item_templates = tax_item_templates.filter(company_id=company_filter)

        context = {
            'tax_item_templates': tax_item_templates,
            'company_filter': company_filter,
            'search_query': search_query,
            'total_count': TaxItemTemplate.objects.count(),
        }

        return render(request, 'finance/tax_item_templates.html', context)

class TaxItemTemplatesCreate(View):
    """Create new tax item template"""

    @method_decorator(login_required)
    def get(self, request):
        form = TaxItemTemplatesForm()
        return render(request, 'finance/tax_item_templates_form.html', {
            'form': form,
            'action': 'New',
            'is_edit': False
        })

    @method_decorator(login_required)
    def post(self, request):
        form = TaxItemTemplatesForm(request.POST)
        # Debug
        print("POST data:", request.POST)

        if form.is_valid():
            tax_item_template = form.save()
            messages.success(
                request,
                f'Tax Item Template "{tax_item_template.title}" created successfully!'
            )
            return redirect('finance-tax-item-templates')
        else:
            print("Form errors:", form.errors)
            messages.error(request, 'Please correct the errors below.')

        return render(request, 'finance/tax_item_templates_form.html', {
            'form': form,
            'action': 'New',
            'is_edit': False
        })

class TaxItemTemplatesEdit(View):
    """Edit existing tax item template"""

    @method_decorator(login_required)
    def get(self, request, pk):
        tax_item_template = get_object_or_404(TaxItemTemplate, pk=pk)
        form = TaxItemTemplatesForm(instance=tax_item_template)
        return render(request, 'finance/tax_item_templates_form.html', {
            'form': form,
            'tax_item_template': tax_item_template,
            'action': 'Edit',
            'is_edit': True
        })

    @method_decorator(login_required)
    def post(self, request, pk):
        tax_item_template = get_object_or_404(TaxItemTemplate, pk=pk)
        form = TaxItemTemplatesForm(request.POST, instance=tax_item_template)

        # Debug
        print("POST data:", request.POST)

        if form.is_valid():
            form.save()
            messages.success(
                request,
                f'Tax Item Template "{tax_item_template.title}" updated successfully!'
            )
            return redirect('finance-tax-item-templates')
        else:
            print("Form errors:", form.errors)
            messages.error(request, 'Please correct the errors below.')

        return render(request, 'finance/tax_item_templates_form.html', {
            'form': form,
            'tax_item_template': tax_item_template,
            'action': 'Edit',
            'is_edit': True
        })

class TaxItemTemplatesDelete(View):
    """Delete tax item template"""

    @method_decorator(login_required)
    def post(self, request, pk):
        tax_item_template = get_object_or_404(TaxItemTemplate, pk=pk)

        tax_item_template.delete()
        messages.success(
            request,
            f'Tax Item Template "{tax_item_template.title}" deleted successfully!'
        )
        return redirect('finance-tax-item-templates')



class TaxRuleView(View):
    """List all Tax Rules"""

    @method_decorator(login_required)
    def get(self, request):
        tax_rules= TaxRule.objects.all()

        # Search by series
        search_query = request.GET.get('search', '')
        if search_query:
            tax_rules = tax_rules.filter(tax_type__icontains=search_query)

        # Filter by Company
        type_filter = request.GET.get('tax_type', '')
        if type_filter:
            tax_rules = tax_rules.filter(tax_type=type_filter)

        context = {
            'tax_rules': tax_rules,
            'type_filter': type_filter,
            'search_query': search_query,
            'total_count': TaxRule.objects.count(),
        }

        return render(request, 'finance/tax_rules.html', context)

class TaxRulesCreate(View):
    """Create new tax rule"""

    @method_decorator(login_required)
    def get(self, request):
        form = TaxRuleForm()
        return render(request, 'finance/tax_rules_form.html', {
            'form': form,
            'action': 'New',
            'is_edit': False
        })

    @method_decorator(login_required)
    def post(self, request):
        form = TaxRuleForm(request.POST)
        # Debug
        print("POST data:", request.POST)

        if form.is_valid():
            tax_rule = form.save()
            messages.success(
                request,
                f'Tax Rule "{tax_rule.id}" created successfully!'
            )
            return redirect('finance-tax-rules')
        else:
            print("Form errors:", form.errors)
            messages.error(request, 'Please correct the errors below.')

        return render(request, 'finance/tax_rules_form.html', {
            'form': form,
            'action': 'New',
            'is_edit': False
        })

class TaxRulesEdit(View):
    """Edit existing tax rule"""

    @method_decorator(login_required)
    def get(self, request, pk):
        tax_rule = get_object_or_404(TaxRule, pk=pk)
        form = TaxRuleForm(instance=tax_rule)
        return render(request, 'finance/tax_rules_form.html', {
            'form': form,
            'tax_rule': tax_rule,
            'action': 'Edit',
            'is_edit': True
        })

    @method_decorator(login_required)
    def post(self, request, pk):
        tax_rule = get_object_or_404(TaxRule, pk=pk)
        form = TaxRuleForm(request.POST, instance=tax_rule)

        # Debug
        print("POST data:", request.POST)

        if form.is_valid():
            form.save()
            messages.success(
                request,
                f'Tax Rule "{tax_rule.id}" updated successfully!'
            )
            return redirect('finance-tax-rules')
        else:
            print("Form errors:", form.errors)
            messages.error(request, 'Please correct the errors below.')

        return render(request, 'finance/tax_rules_form.html', {
            'form': form,
            'tax_rule': tax_rule,
            'action': 'Edit',
            'is_edit': True
        })

class TaxRulesDelete(View):
    """Delete tax rule"""

    @method_decorator(login_required)
    def post(self, request, pk):
        tax_rule = get_object_or_404(TaxRule, pk=pk)

        tax_rule.delete()
        messages.success(
            request,
            f'Tax Rule "{tax_rule.id}" deleted successfully!'
        )
        return redirect('finance-tax-rules')

class DeductionCertificateView(View):
    """List all Deduction Certificates"""

    @method_decorator(login_required)
    def get(self, request):
        certificates = DeductionCertificate.objects.select_related(
            'company', 'supplier', 'tax_withholding_category'
        ).all()

        # Search by certificate number
        search_query = request.GET.get('search', '')
        if search_query:
            certificates = certificates.filter(
                certificate_number__icontains=search_query
            )

        # Filter by Company
        company_filter = request.GET.get('company', '')
        if company_filter:
            certificates = certificates.filter(company_id=company_filter)

        context = {
            'certificates': certificates,
            'search_query': search_query,
            'company_filter': company_filter,
            'total_count': DeductionCertificate.objects.count(),
        }

        return render(
            request,
            'finance/deduction_certificates.html',
            context
        )

class DeductionCertificateCreate(View):
    """Create new Deduction Certificate"""

    @method_decorator(login_required)
    def get(self, request):
        form = DeductionCertificateForm()
        return render(request, 'finance/deduction_certificate_form.html', {
            'form': form,
            'action': 'New',
            'is_edit': False
        })

    @method_decorator(login_required)
    def post(self, request):
        form = DeductionCertificateForm(request.POST)

        # Debug
        print("POST data:", request.POST)

        if form.is_valid():
            certificate = form.save()
            messages.success(
                request,
                f'Deduction Certificate "{certificate.certificate_number}" created successfully!'
            )
            return redirect('finance-deduction-certificates')
        else:
            print("Form errors:", form.errors)
            messages.error(request, 'Please correct the errors below.')

        return render(request, 'finance/deduction_certificate_form.html', {
            'form': form,
            'action': 'New',
            'is_edit': False
        })
    
class DeductionCertificateEdit(View):
    """Edit existing Deduction Certificate"""

    @method_decorator(login_required)
    def get(self, request, pk):
        certificate = get_object_or_404(DeductionCertificate, pk=pk)
        form = DeductionCertificateForm(instance=certificate)

        return render(request, 'finance/deduction_certificate_form.html', {
            'form': form,
            'certificate': certificate,
            'action': 'Edit',
            'is_edit': True
        })

    @method_decorator(login_required)
    def post(self, request, pk):
        certificate = get_object_or_404(DeductionCertificate, pk=pk)
        form = DeductionCertificateForm(
            request.POST,
            instance=certificate
        )

        # Debug
        print("POST data:", request.POST)

        if form.is_valid():
            form.save()
            messages.success(
                request,
                f'Deduction Certificate "{certificate.certificate_number}" updated successfully!'
            )
            return redirect('finance-deduction-certificates')
        else:
            print("Form errors:", form.errors)
            messages.error(request, 'Please correct the errors below.')

        return render(request, 'finance/deduction_certificate_form.html', {
            'form': form,
            'certificate': certificate,
            'action': 'Edit',
            'is_edit': True
        })
    
class DeductionCertificateDelete(View):
    """Delete Deduction Certificate"""

    @method_decorator(login_required)
    def post(self, request, pk):
        certificate = get_object_or_404(DeductionCertificate, pk=pk)

        certificate.delete()
        messages.success(
            request,
            f'Deduction Certificate "{certificate.certificate_number}" deleted successfully!'
        )
        return redirect('finance-deduction-certificates')

class TaxWithholdingCategoryList(View):
    """List all Tax Withholding Categories"""

    @method_decorator(login_required)
    def get(self, request):
        categories = TaxWithholdingCategory.objects.all()

        # Search and Filter logic
        search_query = request.GET.get('search', '')
        if search_query:
            categories = categories.filter(name__icontains=search_query)

        basis_filter = request.GET.get('basis', '')
        if basis_filter:
            categories = categories.filter(deduct_tax_on_basis=basis_filter)

        context = {
            'categories': categories,
            'basis_filter': basis_filter,
            'search_query': search_query,
            'total_count': TaxWithholdingCategory.objects.count(),
        }

        # Make sure this template filename matches what is on your disk
        return render(request, 'finance/tax_category_list.html', context)


class TaxWithholdingCategoryCreate(View):
    """Create new Tax Withholding Category"""

    @method_decorator(login_required)
    def get(self, request):
        return render(request, 'finance/tax_category_form.html', {
            'form': TaxWithholdingCategoryForm(),
            'rates_formset': TaxRateFormSet(),
            'accounts_formset': TaxAccountFormSet(),
            'action': 'New',
            'is_edit': False
        })

    @method_decorator(login_required)
    def post(self, request):
        form = TaxWithholdingCategoryForm(request.POST)
        rates_formset = TaxRateFormSet(request.POST)
        accounts_formset = TaxAccountFormSet(request.POST)

        if form.is_valid() and rates_formset.is_valid() and accounts_formset.is_valid():
            try:
                with transaction.atomic():
                    category = form.save()
                    
                    rates_formset.instance = category
                    rates_formset.save()
                    
                    accounts_formset.instance = category
                    accounts_formset.save()
                    
                    messages.success(request, f'Tax Category "{category.name}" created successfully!')
                    # ✅ FIXED: Matches your urls.py name
                    return redirect('finance-tax-withholding-categories') 
            except Exception as e:
                messages.error(request, f'Error saving data: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')

        return render(request, 'finance/tax_category_form.html', {
            'form': form,
            'rates_formset': rates_formset,
            'accounts_formset': accounts_formset,
            'action': 'New',
            'is_edit': False
        })


class TaxWithholdingCategoryEdit(View):
    """Edit existing Tax Withholding Category"""

    @method_decorator(login_required)
    def get(self, request, pk):
        category = get_object_or_404(TaxWithholdingCategory, pk=pk)
        return render(request, 'finance/tax_category_form.html', {
            'form': TaxWithholdingCategoryForm(instance=category),
            'rates_formset': TaxRateFormSet(instance=category),
            'accounts_formset': TaxAccountFormSet(instance=category),
            'category': category,
            'action': 'Edit',
            'is_edit': True
        })

    @method_decorator(login_required)
    def post(self, request, pk):
        category = get_object_or_404(TaxWithholdingCategory, pk=pk)
        
        form = TaxWithholdingCategoryForm(request.POST, instance=category)
        rates_formset = TaxRateFormSet(request.POST, instance=category)
        accounts_formset = TaxAccountFormSet(request.POST, instance=category)

        if form.is_valid() and rates_formset.is_valid() and accounts_formset.is_valid():
            try:
                with transaction.atomic():
                    form.save()
                    rates_formset.save()
                    accounts_formset.save()
                    
                    messages.success(request, f'Tax Category "{category.name}" updated successfully!')
                    # ✅ FIXED: Matches your urls.py name
                    return redirect('finance-tax-withholding-categories')
            except Exception as e:
                messages.error(request, f'Error saving data: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')

        return render(request, 'finance/tax_category_form.html', {
            'form': form,
            'rates_formset': rates_formset,
            'accounts_formset': accounts_formset,
            'category': category,
            'action': 'Edit',
            'is_edit': True
        })


class TaxWithholdingCategoryDelete(View):
    """Delete Tax Withholding Category"""

    @method_decorator(login_required)
    def post(self, request, pk):
        category = get_object_or_404(TaxWithholdingCategory, pk=pk)
        category.delete()
        messages.success(request, f'Tax Category "{category.name}" deleted successfully!')
        # ✅ FIXED: Matches your urls.py name
        return redirect('finance-tax-withholding-categories')

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

        # Eager-load supplier and company to avoid N+1 queries
        all_invoices = Invoice.objects.select_related('company', 'supplier').all()

        # Calculate Total Payables (unpaid invoices: draft + sent)
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

        # Calculate Average Payment Period (placeholder)
        avg_payment_period = 45  # Default value; calculate if you add payment_date

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

            # Use supplier FK (guard for None)
            vendor_name = invoice.supplier.name if invoice.supplier else 'Unknown Supplier'

            invoice_list.append({
                'invoice_number': invoice.invoice_number,
                'vendor': vendor_name,
                'date': invoice.date,
                'due_date': due_date,
                'amount': invoice.total_amount,
                'status': display_status,
                'payment_method': 'Bank Transfer',  # Optional field
            })

        # Get vendor breakdown for chart (top 6 vendors by payables)
        vendor_breakdown = unpaid_invoices.values('supplier__name').annotate(
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
                'name': vendor.get('supplier__name') or 'Unknown Supplier',
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
        # Eager-load supplier and company to avoid N+1 queries
        invoices = Invoice.objects.select_related('company', 'supplier', 'customer').all()

        # Search functionality
        search_query = request.GET.get('search', '')
        if search_query:
            invoices = invoices.filter(
                models.Q(invoice_number__icontains=search_query) |
                models.Q(customer__name__icontains=search_query) |
                models.Q(supplier__name__icontains=search_query)  # search supplier name via FK
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
        from django.db.models import Q
        from django.db.models import Count
        from decimal import Decimal

        # Base queryset (eager-load to avoid N+1)
        suppliers = Supplier.objects.select_related('company', 'created_by').all().order_by('-created_at')

        # Search functionality (include gstin)
        search_query = request.GET.get('search', '').strip()
        if search_query:
            suppliers = suppliers.filter(
                Q(name__icontains=search_query) |
                Q(gstin_uin__icontains=search_query) |
                Q(contact_email__icontains=search_query) |
                Q(contact_mobile__icontains=search_query)
            )

        # Company filter (expects company id)
        company_filter = request.GET.get('company', '').strip()
        if company_filter:
            # filter by company_id (works with string id from GET)
            suppliers = suppliers.filter(company_id=company_filter)

        # Supplier type filter — support both `supplier_type` and legacy `type` from the template
        type_filter = request.GET.get('supplier_type') or request.GET.get('type', '')
        if type_filter:
            suppliers = suppliers.filter(supplier_type=type_filter)

        # Pass companies for the dropdown
        companies = Company.objects.all()

        context = {
            'suppliers': suppliers,
            'search_query': search_query,
            'total_count': Supplier.objects.count(),
            'companies': companies,
            'company_filter': company_filter,
            'type_filter': type_filter,
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


class Customers(View):
    """List all customers"""
    @method_decorator(login_required)
    def get(self, request):
        from django.db.models import Q
        from django.db.models import Count
        from decimal import Decimal

        # Base queryset (eager-load to avoid N+1)
        customers = Customer.objects.select_related('company', 'created_by').all().order_by('-created_at')

        # Search functionality (include gstin)
        search_query = request.GET.get('search', '').strip()
        if search_query:
            customers = customers.filter(
                Q(name__icontains=search_query) |
                Q(gstin_uin__icontains=search_query) |
                Q(contact_email__icontains=search_query) |
                Q(contact_mobile__icontains=search_query)
            )

        # Company filter (expects company id)
        company_filter = request.GET.get('company', '').strip()
        if company_filter:
            # filter by company_id (works with string id from GET)
            customers = customers.filter(company_id=company_filter)

        # Customer type filter — support both `customer_type` and legacy `type` from the template
        type_filter = request.GET.get('customer_type') or request.GET.get('type', '')
        if type_filter:
            customers = customers.filter(customer_type=type_filter)

        # Pass companies for the dropdown
        companies = Company.objects.all()

        context = {
            'customers': customers,
            'search_query': search_query,
            'total_count': Customer.objects.count(),
            'companies': companies,
            'company_filter': company_filter,
            'type_filter': type_filter,
        }
        return render(request, 'finance/customers.html', context)

class CustomerCreate(View):
    """Create new customer"""
    @method_decorator(login_required)
    def get(self, request):
        form = CustomerForm()
        return render(request, 'finance/customer_form.html', {
            'form': form,
            'action': 'New',
            'is_modal': True,  # template can render as modal if desired
        })

    @method_decorator(login_required)
    def post(self, request):
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save(commit=False)
            customer.created_by = request.user
            customer.save()
            messages.success(request, f'Customer "{customer.name}" created successfully!')
            return redirect('finance-customers')
        else:
            messages.error(request, 'Please correct the errors below.')
        return render(request, 'finance/customer_form.html', {
            'form': form,
            'action': 'New',
            'is_modal': True,
        })


class CustomerEdit(View):
    """Edit customer"""
    @method_decorator(login_required)
    def get(self, request, pk):
        customer = get_object_or_404(Customer, pk=pk)
        form = CustomerForm(instance=customer)
        return render(request, 'finance/customer_form.html', {
            'form': form,
            'customer': customer,
            'action': 'Edit',
            'is_modal': False,
        })

    @method_decorator(login_required)
    def post(self, request, pk):
        customer = get_object_or_404(Customer, pk=pk)
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            messages.success(request, f'Customer "{customer.name}" updated successfully!')
            return redirect('finance-customers')
        else:
            messages.error(request, 'Please correct the errors below.')
        return render(request, 'finance/customer_form.html', {
            'form': form,
            'customer': customer,
            'action': 'Edit',
            'is_modal': False,
        })


class CustomerDelete(View):
    @method_decorator(login_required)
    def post(self, request, pk):
        customer = get_object_or_404(Customer, pk=pk)
        name = customer.name
        customer.delete()
        messages.success(request, f'Customer "{name}" deleted successfully!')
        return redirect('finance-customers')
    

class Receivables(View):
    @method_decorator(login_required)
    def get(self, request):
        from django.db.models import Sum, Count, Avg, Q, F, ExpressionWrapper, fields
        from datetime import datetime, timedelta
        from decimal import Decimal
        
        # Get all customer invoices (receivables are invoices FROM customers)
        all_invoices = Invoice.objects.select_related('company','customer')
        
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
            
            customer_name = invoice.customer.name if invoice.customer else 'Unknown Customer'
            invoice_list.append({
                'invoice_number': invoice.invoice_number,
                'customer':  customer_name,
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
        invoices = Invoice.objects.all().order_by('-date')
        return render(request, 'finance/scan.html', {'invoices': invoices}) 
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
    
def create_invoice(request):
    if request.method == 'POST':
        files = request.FILES.getlist('files')
        new_count = 0
        repeated_count = 0
        print(files)
        for  idx, file in enumerate(files):
            split_invoice_str = request.POST.get(f'split_flag_{idx}', 'false')
            split_invoice = split_invoice_str.lower() == 'true'
            try:
                result = upload_invoice_for_project(file,split_invoice)
                created = result.get("created", 0)
                duplicates = result.get("duplicates", 0)
                new_count = new_count + created
                repeated_count = repeated_count + duplicates
            except Exception as e:
                messages.warning(request, f"An error occurred while uploading the invoice")
                print(f"Error uploading invoice: {e}")
        messages.success(request, f"Invoices uploaded. New: {new_count}, Duplicates: {repeated_count}")
        return redirect('finance-invoice-scan')
    return redirect('finance-scan')

def is_qr_code_present(image_data):
    """
    Takes image data (bytes) and returns True if 'qr_code' class is detected.
    """
    image = Image.open(io.BytesIO(image_data)).convert('RGB')
    results = model(image)

    for box in results[0].boxes:
        class_id = int(box.cls[0].item())
        class_name = model.names[class_id]
        if class_name == 'qr_code':
            return True
    return False

def extract_qr_code(image_data):
    """Detects and extracts QR code content using OpenCV."""
    try:
        nparr = np.frombuffer(image_data, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        detector = cv2.QRCodeDetector()
        data, bbox, _ = detector.detectAndDecode(image)

        if bbox is not None and data:
            return data  # Already decoded string

    except Exception as e:
        print(f"Error extracting QR code: {e}")

    return None

def decode_tlv_qr(qr_string):
    """
    Decodes the extracted QR code data (Base64-encoded TLV format) 
    used in Saudi Arabia's E-Invoice QR system.
    """
    try:
        qr_bytes = base64.b64decode(qr_string)
        fields = []
        i = 0

        def to_float(value):
            """Convert a value to float safely."""
            try:
                return float(value) if value else None
            except ValueError:
                return None  # If conversion fails, return None instead of crashing
        
        while i < len(qr_bytes):
            tag = qr_bytes[i]
            length = qr_bytes[i + 1]
            value = qr_bytes[i + 2 : i + 2 + length].decode('utf-8')
            fields.append(value)
            i += 2 + length

        return {
            "Supplier Name": fields[0] if len(fields) > 0 else None,
            "Supplier VAT": fields[1] if len(fields) > 1 else None,
            "Invoice Date": fields[2] if len(fields) > 2 else None,
            "Total Amount After VAT": to_float(fields[3]) if len(fields) > 3 else None,
            "VAT Amount": to_float(fields[4]) if len(fields) > 4 else None
        }

    except Exception as e:
        return {"Error": str(e)}

def convert_date_format(date_str): 
    """Converts various date formats (e.g., DD-MM-YYYY, DD/MM/YYYY, YYYY-MM-DD) to YYYY-MM-DD."""
    for fmt in ("%d-%m-%Y", "%d/%m/%Y", "%Y-%m-%d", "%Y/%m/%d", "%d-%b-%Y"):
        try:
            return datetime.strptime(date_str, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return None

def extract_text_from_pdf(file_path):
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text

def pdf_to_images(pdf_bytes):
    """Convert PDF pages to images using PyMuPDF."""
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")  # Read PDF from memory
    images = []
    for page_num in range(len(doc)):
        pix = doc[page_num].get_pixmap(matrix=fitz.Matrix(2, 2))  # Increase DPI
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        images.append(img)
    return images

def initialize_vision_client():
    return vision.ImageAnnotatorClient()
def get_dominant_text_angle(response):
    angles = []
    for page in response.full_text_annotation.pages:
        for block in page.blocks:
            for paragraph in block.paragraphs:
                for word in paragraph.words:
                    vertices = word.bounding_box.vertices
                    if len(vertices) >= 2:
                        dx = vertices[1].x - vertices[0].x
                        dy = vertices[1].y - vertices[0].y
                        angle = math.degrees(math.atan2(dy, dx))
                        angles.append(angle)

    if not angles:
        return 0

    # Normalize angles to be between -90 and +90
    normalized_angles = [((a + 90) % 180) - 90 for a in angles]
    median_angle = statistics.median(normalized_angles)
    return median_angle
def correct_image_orientation(image_path, angle_threshold=45):
    from PIL import Image

    client = initialize_vision_client()
    response = detect_text_blocks(image_path, client)
    angle = get_dominant_text_angle(response)

    if abs(angle) > angle_threshold:
        with Image.open(image_path) as img:
            rotated_img = img.rotate(-90, expand=True)
            rotated_path = "rotated_temp_image.jpg"
            rotated_img.save(rotated_path)
        return rotated_path
    return image_path
def get_image_size(image_path):
    with Image.open(image_path) as img:
        return img.size

def detect_text_blocks(image_path, client):
    with io.open(image_path, 'rb') as image_file:
        content = image_file.read()
        image = vision.Image(content=content)
    response = client.document_text_detection(image=image)
    return response

def setup_pdf_canvas(image_width, image_height, output_pdf_path):    
    if image_width > image_height:
        page_size = landscape(A4)
    else:
        page_size = A4

    pdf_width, pdf_height = page_size
    scale_x = pdf_width / image_width
    scale_y = pdf_height / image_height

    c = canvas.Canvas(output_pdf_path, pagesize=page_size)
    return c, pdf_width, pdf_height, scale_x, scale_y

def register_font():
    print(settings.STATICFILES_DIRS)
    font_path = os.path.join(settings.STATICFILES_DIRS[0], 'assets', 'fonts', 'DejaVuSans.ttf')
    if os.path.exists(font_path):
        pdfmetrics.registerFont(TTFont("ArabicFont", font_path))
        return "ArabicFont"
    return "Helvetica"

def check_horizontal_overlap(x_left, x_right, line_y, registered_lines, threshold=5):
    for y, boxes in registered_lines:
        if abs(y - line_y) <= threshold:
            for existing_left, existing_right in boxes:
                if not (x_right < existing_left or x_left > existing_right):
                    return True
    return False


def register_box(x_left, x_right, line_y, registered_lines, threshold=5):
    for i, (y, boxes) in enumerate(registered_lines):
        if abs(y - line_y) <= threshold:
            boxes.append((x_left, x_right))
            return
    registered_lines.append((line_y, [(x_left, x_right)]))

def draw_text_blocks_on_canvas(response, canvas_obj, font_name, img_width, img_height, scale_x, scale_y):
    registered_lines = []
    for page in response.full_text_annotation.pages:
        for block in page.blocks:
            for paragraph in block.paragraphs:
                for word in paragraph.words:
                    text = ''.join([s.text for s in word.symbols])
                    reshaped_text = arabic_reshaper.reshape(text)
                    bidi_text = get_display(reshaped_text)

                    bbox = word.bounding_box.vertices
                    x_left = bbox[0].x * scale_x
                    x_right = bbox[1].x * scale_x
                    y_bottom = (img_height - bbox[1].y) * scale_y
                    box_width = abs(x_right - x_left)
                    box_height = abs(bbox[0].y - bbox[2].y) * scale_y
                    font_size = max(6, min(6, box_height))
                    canvas_obj.setFont(font_name, font_size)

                    # shift = 0
                    # max_shift = 50
                    # while shift < max_shift:
                    #     temp_x_right = x_right - shift
                    #     temp_x_left = temp_x_right - box_width
                    #     if not check_horizontal_overlap(temp_x_left, temp_x_right, y_bottom, registered_lines):
                    #         break
                    #     shift += 2

                    # final_x_right = x_right - shift
                    # final_x_left = final_x_right - box_width
                    register_box(x_left, x_right, y_bottom, registered_lines)

                    canvas_obj.drawRightString(x_right, y_bottom, bidi_text)

def generate_invoice_pdf(image_path):
    corrected_image_path = correct_image_orientation(image_path)
    client = initialize_vision_client()
    img_width, img_height = get_image_size(corrected_image_path)
    response = detect_text_blocks(corrected_image_path, client)

    # Ensure the invoices folder exists
    folder_path = os.path.join(settings.MEDIA_ROOT, 'invoices')
    os.makedirs(folder_path, exist_ok=True)

    # Generate filename if not provided
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"invoice_{timestamp}.pdf"

    output_pdf_path = os.path.join(folder_path, filename)

    c, pdf_width, pdf_height, scale_x, scale_y = setup_pdf_canvas(img_width, img_height, output_pdf_path)
    font_name = register_font()

    draw_text_blocks_on_canvas(response, c, font_name, img_width, img_height, scale_x, scale_y)

    c.save()
    return output_pdf_path

def process_invoice_digital(pdf_content, image_data):
    
    print("LLAMA")
    """
    Extract structured invoice data from a digital invoice (text-based PDF content) using Groq API.

    Args:
        pdf_content (str): Extracted text from the invoice PDF.
        groq_api_key (str): API key for authentication.

    Returns:
        dict: Extracted invoice data in a structured JSON format.
    """

    # Define prompt structure for JSON output
    messages = [{
        "role": "system",
        "content": (
            "You are an AI specialized in extracting structured data from invoices. "
            "Ensure the JSON response follows this structure:"
            "\n```json\n"
            "{"
            "\n  \"Invoice Number\": \"<string>\","
            "\n  \"Invoice Date\": \"<string>\","
            "\n  \"Supplier Name\": \"<string>\","
            "\n  \"Supplier VAT\": \"<string>\","
            "\n  \"Customer Name\": \"<string>\","
            "\n  \"Customer VAT\": \"<string>\","
            "\n  \"Amount Before VAT\": <float>,"
            "\n  \"VAT Amount\": <float>,"
            "\n  \"Total Amount After VAT\": <float>,"
            "\n  \"Line Items\": ["
            "\n    {"
            "\n      \"Item Name\": \"<string>\","
            "\n      \"Item Description\": \"<string>\","
            "\n      \"Quantity\": <int>,"
            "\n      \"Unit Price\": <float>,"
            "\n      \"Total Price\": <float>"
            "\n    }"
            "\n  ]"
            "\n}"
            "\n```"
        )
    },

    {
        "role": "user",
        "content": (
            "Extract the following details from this invoice and return them in JSON format:\n"
            "If any value is missing or cannot be determined, return it as null (None in Python):\n\n"
            "Match both English and Arabic keywords where available.Invoice contains English and Arabic only.\n\n"
            "- Invoice Number (رقم الفاتورة / Raqm Al Fatoora)/Receipt Number\n"
            "- Invoice Date (%d-%m-%Y). Start Date in Food Budget.\n"
            "- Supplier Name (may appear in English or Arabic at the top of the invoice. If in English return in English else return exact Arabic)\n"
            "- Supplier VAT Number (الرقم الضريبي / Raqm Al Dhareebi)\n"
            r"- Customer\Client Name (العميل)\n-"
            "- Customer VAT Number (الرقم الضريبي للعميل / Raqm Al Dhareebi lil-Ameel)\n"
            "- Amount Before VAT (مبلغ قبل الضريبة) / Total Amount Before VAT (الإجمالي قبل الضريبة)\n"
            "- VAT Amount"
            "- Total Amount After VAT / Total Amount"
            "Additionally, extract line items listed in the invoice. Each line item should include:\n"
            "- Item Name\n- Item Description (if available)\n- Quantity\n- Unit Price\n- Total Price\n"
            f"\n\nInvoice Text:\n{pdf_content}"
        )
    }]
    # response = client.chat.completions.create(
    #     model="gemma2-9b-it",
    #     messages=messages,
    #     temperature=1,
    #     max_completion_tokens=1024,
    #     top_p=1,
    #     stop=None,
    # )
    response = client_openai.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        max_tokens=800,
        temperature=0
    )

    # Access the response content
    response_text = response.choices[0].message.content

    # # Prepare API request
    # data = {
    #     "model": "meta-llama/llama-4-scout-17b-16e-instruct",
    #     "messages": [system_message, user_message],
    #     "max_tokens": 800
    # }

    # # Send request to Groq API
    # response = requests.post(url, headers=headers, data=json.dumps(data))

    # # Parse the response
    # response_text = response.json().get("choices", [{}])[0].get("message", {}).get("content", "").strip()

    # Extract JSON from response
    match = re.search(r"```json\s*(\{.*?\})\s*```", response_text, re.DOTALL)
    extracted_json = match.group(1).strip() if match else response_text.strip()

    invoice_data = json.loads(extracted_json)
    print(invoice_data)
    invoice_date_str = invoice_data["Invoice Date"]
    if invoice_date_str:
        invoice_data["Invoice Date"] = convert_date_format(invoice_date_str)
    qr_code_string = extract_qr_code(image_data)
    if qr_code_string:
        qr_data = decode_tlv_qr(qr_code_string)
        invoice_data['QR Code Present'] = True
    else:
        # qr_presence = is_qr_code_present(image_data)
        # invoice_data['QR Code Present'] = qr_presence
        invoice_data['QR Code Present'] = False
        qr_data = None

    if qr_data:
        print(qr_data)
        invoice_data['QR Code Valid'] = True
        # for key, qr_value in qr_data.items():
        #     if key in invoice_data and qr_value:
        #         if key == "Supplier Name":
        #             continue
        #         if invoice_data[key] != qr_value:
        #             # Update other fields normally
        #             print(f"Updating {key}: {invoice_data[key]} → {qr_value}")
        #             invoice_data[key] = qr_value
    else:
        invoice_data['QR Code Valid'] = False
    line_items = invoice_data.get("Line Items", [])
    if isinstance(line_items, str):  # If line items are stored as a string, convert them back
        try:
            line_items = json.loads(line_items)
        except json.JSONDecodeError:
            line_items = []  # If decoding fails, store an empty list
    invoice_data['Line Items'] = line_items
    supplier_str = invoice_data["Supplier Name"]
    PRESENTATION_FORMS = re.compile(r'[\uFB50-\uFDFF\uFE70-\uFEFF]')
    if supplier_str:
        print('supplier str',supplier_str)
        if PRESENTATION_FORMS.search(supplier_str):
            supplier_name = arabic_reshaper.reshape(supplier_str)
            supplier_name = get_display(supplier_name)
            invoice_data["Supplier Name"] = supplier_name
        else:
            supplier_name=supplier_str
            invoice_data["Supplier Name"] = supplier_name
    else:
        invoice_data["Supplier Name"] = None
    customer_str = invoice_data["Customer Name"]
    if customer_str:
        if PRESENTATION_FORMS.search(customer_str):
            customer_name = arabic_reshaper.reshape(customer_str)
            customer_name = get_display(customer_name)
            invoice_data["Customer Name"] = customer_name
        else:
            customer_name = customer_str
            invoice_data["Customer Name"] = customer_name
    else:
        invoice_data["Customer Name"] = None
    # Fix Line Items Item Names
    line_items = invoice_data["Line Items"]
    for item in line_items:
        if item.get("Item Name"):
            if PRESENTATION_FORMS.search(item["Item Name"]):
                item["Item Name"] = arabic_reshaper.reshape(item["Item Name"])
                item["Item Name"] = get_display(item["Item Name"])
        if item.get("Item Description"):
            if PRESENTATION_FORMS.search(item["Item Description"]):
                item["Item Description"] = arabic_reshaper.reshape(item["Item Description"])
                item["Item Description"] = get_display(item["Item Description"])
            print('Modified', item["Item Description"])
    return invoice_data

def upload_to_gcs(bucket_name, source_file_path, credentials_file):
    """
    Uploads a file to a specified Google Cloud Storage bucket
    and returns a signed URL valid for 7 days.

    Args:
        bucket_name (str): Name of the GCS bucket.
        source_file_path (str): Full local path to the file.
        credentials_file (str): Path to the GCP service account JSON file.

    Returns:
        str: Signed URL to access the uploaded file.
    """

    # Initialize the GCS client with the credentials file
    storage_client = storage.Client.from_service_account_json(credentials_file)

    # Get the target bucket
    bucket = storage_client.bucket(bucket_name)

    # Use the base name of the file as the blob name
    destination_blob_name = os.path.basename(source_file_path)

    # Create a blob object in the bucket
    blob = bucket.blob(destination_blob_name)
    blob.content_disposition = f'attachment; filename="{destination_blob_name}"'

    # Upload the file to GCS
    blob.upload_from_filename(source_file_path)

    # Generate a signed URL valid for 7 days
    url = blob.generate_signed_url(expiration=timedelta(days=7))

    # Log upload
    print(f"File {source_file_path} uploaded to gs://{bucket_name}/{destination_blob_name}")
    print(f"Download URL: {url}")

    return url
import os
import io
from django.conf import settings

def upload_invoice_for_project(invoice_file,split_invoice=True):
    """
    Handles invoice uploads (PDF or image) and saves them as individual or merged invoices.

    Args:
        invoice_file: InMemoryUploadedFile from request.FILES
        project_id: ID of the project/company the invoice belongs to
        split_invoice: If True, split multi-page PDFs into separate invoices

    Returns:
        dict: {
            "created": int,
            "duplicates": int,
            "pages": int,
            "details": list[dict]
        }
    """
    file_extension = invoice_file.name.lower().split('.')[-1]
    original_name_noext = os.path.splitext(invoice_file.name)[0]
    invoice_bytes = invoice_file.read()

    folder_name = os.path.join(settings.MEDIA_ROOT, 'invoices')
    os.makedirs(folder_name, exist_ok=True)

    filename = f"invoice_{invoice_file.name}"
    file_path = os.path.join(folder_name, filename)

    # Save uploaded file
    with open(file_path, 'wb') as fp:
        for chunk in invoice_file.chunks():
            fp.write(chunk)

    # ===========================
    # 1) Non-PDFs (images)
    # ===========================
    if file_extension != "pdf":
        tmp_image_path = os.path.join(folder_name, f"{original_name_noext}.png")
        with open(tmp_image_path, "wb") as f:
            f.write(invoice_bytes)

        page_pdf_path = generate_invoice_pdf(tmp_image_path)
        pdf_content = extract_text_from_pdf(page_pdf_path)
        extracted_data = process_invoice_digital(pdf_content, invoice_bytes)

        status = _save_single_invoice_record(
            
            local_source_path=file_path,
            extracted_data=extracted_data,
            fallback_basename=original_name_noext
        )

        os.remove(tmp_image_path)
        delete_file(page_pdf_path)
        if os.path.exists(file_path):
            os.remove(file_path)

        return {
            "created": 1 if status else 0,
            "duplicates": 1 if not status else 0,
            "pages": 1,
            "details": [{"status": status}]
        }

    # ===========================
    # 2) PDFs
    # ===========================
    # Determine if digital PDF
    is_digital = False
    try:
        full_text = extract_text(file_path)
        is_digital = bool(full_text.strip())
        print("Digital Invoice" if is_digital else "Scanned Invoice")
    except Exception as e:
        print("PDF parsing failed:", e)

    # For scanned PDFs, convert to images
    images = []
    if not is_digital:
        try:
            images = pdf_to_images(invoice_bytes)
        except Exception as e:
            print("Error converting PDF to images:", e)

    # -----------------------------
    # 2A) Digital PDF → process directly
    # -----------------------------
    if is_digital:
        pdf_content = extract_text_from_pdf(file_path)
        extracted_data = process_invoice_digital(pdf_content, invoice_bytes)

        status = _save_single_invoice_record(
            local_source_path=file_path,
            extracted_data=extracted_data,
            fallback_basename=original_name_noext
        )

        if os.path.exists(file_path):
            os.remove(file_path)

        return {
            "created": 1 if status else 0,
            "duplicates": 1 if not status else 0,
            "pages": 1,
            "details": [{"status": status}]
        }

    # -----------------------------
    # 2B) Scanned PDF → process images
    # -----------------------------
    if not images:
        # PDF has no images/pages
        if os.path.exists(file_path):
            os.remove(file_path)
        return {
            "created": 0,
            "duplicates": 0,
            "pages": 0,
            "details": [{"status": None, "error": "PDF contains no pages"}]
        }

    # ---- SPLIT MODE ----
    if split_invoice:
        results = []
        for idx, img in enumerate(images, start=1):
            page_tag = f"p{idx}"
            page_png = os.path.join(folder_name, f"invoice_{original_name_noext}_{page_tag}.png")
            img.save(page_png, format="PNG")

            page_pdf_path = generate_invoice_pdf(page_png)
            try:
                pdf_content = extract_text_from_pdf(page_pdf_path)
                with open(page_png, "rb") as fpng:
                    page_image_bytes = fpng.read()

                extracted_data = process_invoice_digital(pdf_content, page_image_bytes)

                status = _save_single_invoice_record(
                
                    local_source_path=page_png,
                    extracted_data=extracted_data,
                    fallback_basename=f"{original_name_noext}_{page_tag}"
                )

                results.append({"page": idx, "status": status})
            except Exception as e:
                print(f"Error processing page {idx}: {e}")
                results.append({"page": idx, "status": None, "error": str(e)})
            finally:
                if os.path.exists(page_png):
                    os.remove(page_png)
                if os.path.exists(page_pdf_path):
                    os.remove(page_pdf_path)

        if os.path.exists(file_path):
            os.remove(file_path)

        created = sum(1 for r in results if r["status"] is True)
        duplicates = sum(1 for r in results if r["status"] is False)
        return {"created": created, "duplicates": duplicates, "pages": len(results), "details": results}

    # ---- MERGE MODE ----
    image_list = []
    for img in images:
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        image_list.append(buf.getvalue())
    merged_image_bytes = merge_images_vertically(image_list)

    merged_png = os.path.join(folder_name, f"invoice_{original_name_noext}_merged.png")
    with open(merged_png, "wb") as f:
        f.write(merged_image_bytes)
    merged_pdf_path = generate_invoice_pdf(merged_png)
    pdf_content = extract_text_from_pdf(merged_pdf_path)

    extracted_data = process_invoice_digital(pdf_content, merged_image_bytes)

    status = _save_single_invoice_record(
        local_source_path=file_path,
        extracted_data=extracted_data,
        fallback_basename=original_name_noext
    )

    # Cleanup
    if os.path.exists(file_path):
        os.remove(file_path)
    if os.path.exists(merged_png):
        os.remove(merged_png)
    delete_file(merged_pdf_path)

    return {
        "created": 1 if status else 0,
        "duplicates": 1 if not status else 0,
        "pages": 1,
        "details": [{"status": status}]
    }

def delete_file(file_path):
    """
    Deletes the image at the given file path.
    """
    if os.path.exists(file_path):
        os.remove(file_path)


def _save_single_invoice_record(local_source_path, extracted_data, fallback_basename):
    """
    Normalizes fields, checks duplicates, uploads to GCS, and saves one Invoice row.

    Returns:
        True  -> invoice created
        False -> duplicate (skipped)
    """
    # Fallbacks & normalization
    invoice_number = extracted_data.get("Invoice Number")
    if not invoice_number:
        invoice_number = fallback_basename  # ensure uniqueness in split mode

    amount_before_vat = extracted_data.get("Amount Before VAT")
    total_after_vat = extracted_data.get("Total Amount After VAT")
    vat_amount = extracted_data.get("VAT Amount")
    supplier_name = extracted_data.get("Supplier Name")
    customer_name = extracted_data.get("Customer Name")

    if amount_before_vat is None:
        amount_before_vat = total_after_vat
    if vat_amount is None:
        vat_amount = 0
    if total_after_vat is None:
        total_after_vat = 0

    # Guard: amount_before_vat should not exceed (total - vat)
    try:
        if amount_before_vat > (total_after_vat - vat_amount):
            amount_before_vat = total_after_vat - vat_amount
    except Exception:
        pass

    amount_before_vat = round(amount_before_vat,2)
    # Duplicate check
    if Invoice.objects.filter(invoice_number=invoice_number).exists():
        print(f"Invoice with number {invoice_number} already exists. Skipping creation.")
        # Do NOT delete local_source_path here; caller cleans up
        return False

    # Upload source to GCS (page-PDF in split mode, original upload in merge mode)
    pdf_url = upload_to_gcs(
        bucket_name="alrashed-storage",
        source_file_path=local_source_path,
        credentials_file=settings.GOOGLE_CLOUD_PATH
    )
    supplier, _ = Supplier.objects.get_or_create(name=supplier_name)
    customer, _ = Customer.objects.get_or_create(name=customer_name)
    # Create DB record
    invoice = Invoice(
        invoice_number=invoice_number,
        date=extracted_data.get("Invoice Date"),
        supplier=supplier,
        supplier_vat=extracted_data.get("Supplier VAT"),
        customer=customer,
        customer_vat=extracted_data.get("Customer VAT"),
        amount_before_vat=amount_before_vat,
        total_vat=vat_amount,
        total_amount=total_after_vat,
        qr_code_present=extracted_data.get("QR Code Present"),
    )
    invoice.save()
    print(f"Invoice with number {invoice_number} created successfully.")
    return True

def merge_images_vertically(image_list):
    """Merges multiple invoice images into a single image."""
    images = [Image.open(io.BytesIO(img)) for img in image_list]
    max_width = max(img.width for img in images)
    total_height = sum(img.height for img in images)
    merged_image = Image.new("RGB", (max_width, total_height), "white")

    y_offset = 0
    for img in images:
        img = img.resize((max_width, int(img.height * (max_width / img.width)))) if img.width < max_width else img
        merged_image.paste(img, (0, y_offset))
        y_offset += img.height  

    img_byte_array = io.BytesIO()
    merged_image.save(img_byte_array, format="PNG")
    return img_byte_array.getvalue()

class BankAccounts(View):
    """List all Bank Accounts"""

    @method_decorator(login_required)
    def get(self, request):
        bank_accounts = BankAccount.objects.select_related(
            'account_type', 'account_subtype'
        )

        search_query = request.GET.get('search', '')
        if search_query:
            bank_accounts = bank_accounts.filter(
                name__icontains=search_query
            )

        context = {
            'bank_accounts': bank_accounts,
            'search_query': search_query,
            'total_count': BankAccount.objects.count(),
        }
        return render(request, 'finance/bank_accounts.html', context)
    
class BankAccountCreate(View):
    """Create new bank account"""

    @method_decorator(login_required)
    def get(self, request):
        form = BankAccountForm()
        return render(request, 'finance/bank_account_form.html', {
            'form': form,
            'action': 'New',
            'is_edit': False
        })

    @method_decorator(login_required)
    def post(self, request):
        form = BankAccountForm(request.POST)

        if form.is_valid():
            bank_account = form.save()
            messages.success(
                request,
                f'Bank Account "{bank_account.name}" created successfully!'
            )
            return redirect('finance-bank-accounts')

        messages.error(request, 'Please correct the errors below.')
        return render(request, 'finance/bank_account_form.html', {
            'form': form,
            'action': 'New',
            'is_edit': False
        })
    
class BankAccountEdit(View):
    """Edit existing bank account"""

    @method_decorator(login_required)
    def get(self, request, pk):
        bank_account = get_object_or_404(BankAccount, pk=pk)
        form = BankAccountForm(instance=bank_account)

        return render(request, 'finance/bank_account_form.html', {
            'form': form,
            'bank_account': bank_account,
            'action': 'Edit',
            'is_edit': True
        })

    @method_decorator(login_required)
    def post(self, request, pk):
        bank_account = get_object_or_404(BankAccount, pk=pk)
        form = BankAccountForm(request.POST, instance=bank_account)

        if form.is_valid():
            form.save()
            messages.success(
                request,
                f'Bank Account "{bank_account.name}" updated successfully!'
            )
            return redirect('finance-bank-accounts')

        messages.error(request, 'Please correct the errors below.')
        return render(request, 'finance/bank_account_form.html', {
            'form': form,
            'bank_account': bank_account,
            'action': 'Edit',
            'is_edit': True
        })
    
class BankAccountDelete(View):
    """Delete bank account"""

    @method_decorator(login_required)
    def post(self, request, pk):
        bank_account = get_object_or_404(BankAccount, pk=pk)
        bank_account.delete()

        messages.success(
            request,
            f'Bank Account "{bank_account.name}" deleted successfully!'
        )
        return redirect('finance-bank-accounts')

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


# ============================================
# CHATBOT VIEWS
# ============================================

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from .services.chatbot_service import ChatbotService
import json

@login_required
@require_http_methods(["POST"])
def chatbot_send_message(request):
    """
    Handle chatbot message sending.
    Receives user message, processes with OpenAI, returns response.
    """
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return JsonResponse({
                'success': False,
                'error': 'Message cannot be empty'
            }, status=400)
        
        # Initialize chatbot service
        chatbot = ChatbotService()
        
        # Send message and get response
        result = chatbot.send_message(user_message, request.session)
        
        return JsonResponse(result)
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON format'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["GET"])
def chatbot_get_history(request):
    """
    Retrieve conversation history from session.
    """
    try:
        chatbot = ChatbotService()
        conversation = chatbot.get_conversation_history(request.session)
        
        return JsonResponse({
            'success': True,
            'conversation': conversation
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["POST"])
def chatbot_clear_conversation(request):
    """
    Clear conversation history from session.
    """
    try:
        chatbot = ChatbotService()
        chatbot.clear_conversation(request.session)
        
        return JsonResponse({
            'success': True,
            'message': 'Conversation cleared successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)