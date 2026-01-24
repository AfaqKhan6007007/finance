"""
Schema Provider
Provides lightweight schema information to the chatbot at runtime
Minimizes token usage by returning only essential field information
"""
import json
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class SchemaProvider:
    """
    Provides database schema information on-demand.
    Caches schemas to reduce computation and improve response time.
    """
    
    def __init__(self, cache_ttl: int = 600):
        """
        Initialize schema provider with caching.
        
        Args:
            cache_ttl: Cache time-to-live in seconds (default: 10 minutes)
        """
        self.cache_ttl = cache_ttl
        self._cache = {}
        self._cache_timestamps = {}
    
    def _is_cache_valid(self, key: str) -> bool:
        """Check if cached value is still valid"""
        if key not in self._cache_timestamps:
            return False
        age = (datetime.now() - self._cache_timestamps[key]).total_seconds()
        return age < self.cache_ttl
    
    def _get_from_cache(self, key: str) -> Optional[Dict]:
        """Get value from cache if valid"""
        if self._is_cache_valid(key):
            return self._cache.get(key)
        return None
    
    def _set_cache(self, key: str, value: Dict) -> None:
        """Set cache value with timestamp"""
        self._cache[key] = value
        self._cache_timestamps[key] = datetime.now()
    
    def get_table_schema(self, table_name: str, minimal: bool = True) -> Dict:
        """
        Get schema for a specific table.
        
        Args:
            table_name: Name of the database table/model
            minimal: If True, returns only essential fields
            
        Returns:
            Dict with schema information
        """
        cache_key = f"schema_{table_name}_{'minimal' if minimal else 'full'}"
        
        # Check cache first
        cached = self._get_from_cache(cache_key)
        if cached:
            return cached
        
        # Get schema based on table name
        schema = self._get_schema_definition(table_name, minimal)
        
        # Cache the result
        self._set_cache(cache_key, schema)
        
        return schema
    
    def _get_schema_definition(self, table_name: str, minimal: bool) -> Dict:
        """Get the actual schema definition for a table"""
        schemas = {
            'company': self._get_company_schema(minimal),
            'account': self._get_account_schema(minimal),
            'invoice': self._get_invoice_schema(minimal),
            'journal_entry': self._get_journal_entry_schema(minimal),
            'supplier': self._get_supplier_schema(minimal),
            'customer': self._get_customer_schema(minimal),
            'budget': self._get_budget_schema(minimal),
            'cost_center': self._get_cost_center_schema(minimal),
            'tax_rule': self._get_tax_rule_schema(minimal),
        }
        
        schema = schemas.get(table_name.lower())
        if not schema:
            return {
                'success': False,
                'error': f'Unknown table: {table_name}',
                'available_tables': list(schemas.keys())
            }
        
        return {
            'success': True,
            'table': table_name,
            'schema': schema,
            'minimal': minimal
        }
    
    def _get_company_schema(self, minimal: bool) -> Dict:
        """Company table schema"""
        if minimal:
            return {
                'key_fields': ['id', 'name', 'abbreviation', 'country', 'is_active'],
                'description': 'Companies in the system with basic details',
                'relationships': {'accounts': 'one-to-many', 'invoices': 'one-to-many'}
            }
        return {
            'fields': {
                'id': 'integer (primary key)',
                'name': 'string (max 255)',
                'abbreviation': 'string (max 50)',
                'country': 'string (max 100)',
                'default_currency': 'string (max 10)',
                'fiscal_year_begins': 'date',
                'is_active': 'boolean',
                'created_at': 'datetime',
                'updated_at': 'datetime'
            },
            'filters': ['country', 'is_active', 'name__icontains'],
            'relationships': {
                'accounts': 'Company has many Accounts',
                'invoices': 'Company has many Invoices',
                'suppliers': 'Company has many Suppliers',
                'customers': 'Company has many Customers'
            }
        }
    
    def _get_account_schema(self, minimal: bool) -> Dict:
        """Account table schema"""
        if minimal:
            return {
                'key_fields': ['id', 'account_name', 'account_number', 'account_type', 'balance', 'company'],
                'description': 'Chart of accounts with balances',
                'types': ['Asset', 'Liability', 'Equity', 'Income', 'Expense']
            }
        return {
            'fields': {
                'id': 'integer (primary key)',
                'account_name': 'string (max 255)',
                'account_number': 'string (max 50, unique)',
                'account_type': 'choice (Asset/Liability/Equity/Income/Expense)',
                'balance': 'decimal (19,2)',
                'company': 'foreign key to Company',
                'parent_account': 'foreign key to Account (self)',
                'is_group': 'boolean',
                'is_active': 'boolean'
            },
            'filters': ['account_type', 'balance__gte', 'balance__lte', 'company__id', 'is_group', 'is_active'],
            'relationships': {
                'company': 'belongs to Company',
                'parent_account': 'optional parent Account',
                'journal_entries': 'many journal entries reference this account'
            }
        }
    
    def _get_invoice_schema(self, minimal: bool) -> Dict:
        """Invoice table schema"""
        if minimal:
            return {
                'key_fields': ['id', 'invoice_number', 'date', 'total_amount', 'status', 'supplier', 'customer'],
                'description': 'Purchase and sales invoices',
                'statuses': ['draft', 'pending', 'paid', 'cancelled']
            }
        return {
            'fields': {
                'id': 'integer (primary key)',
                'invoice_number': 'string (max 100, unique)',
                'date': 'date',
                'due_date': 'date',
                'total_amount': 'decimal (19,2)',
                'tax_amount': 'decimal (19,2)',
                'status': 'choice (draft/pending/paid/cancelled)',
                'supplier': 'foreign key to Supplier (nullable)',
                'customer': 'foreign key to Customer (nullable)',
                'company': 'foreign key to Company'
            },
            'filters': ['status', 'date__range', 'total_amount__gte', 'supplier__id', 'customer__id'],
            'aggregations': 'Can get stats: total_amount, count by status'
        }
    
    def _get_journal_entry_schema(self, minimal: bool) -> Dict:
        """Journal Entry table schema"""
        if minimal:
            return {
                'key_fields': ['id', 'entry_number', 'date', 'account', 'debit_amount', 'credit_amount'],
                'description': 'Double-entry bookkeeping journal entries',
                'note': 'Each transaction has balanced debits and credits'
            }
        return {
            'fields': {
                'id': 'integer (primary key)',
                'entry_number': 'string (max 100)',
                'date': 'date',
                'account': 'foreign key to Account',
                'debit_amount': 'decimal (19,2)',
                'credit_amount': 'decimal (19,2)',
                'description': 'text',
                'reference': 'string (max 255)'
            },
            'filters': ['date__year', 'date__range', 'account__id', 'debit_amount__gte', 'credit_amount__gte'],
            'aggregations': 'Can get balance: sum(debits) - sum(credits)'
        }
    
    def _get_supplier_schema(self, minimal: bool) -> Dict:
        """Supplier table schema"""
        if minimal:
            return {
                'key_fields': ['id', 'name', 'gstin_uin', 'gst_category', 'country', 'company'],
                'description': 'Vendor/supplier information',
                'gst_categories': ['registered', 'unregistered', 'composition', 'overseas']
            }
        return {
            'fields': {
                'id': 'integer (primary key)',
                'name': 'string (max 255)',
                'gstin_uin': 'string (max 50)',
                'gst_category': 'choice (registered/unregistered/composition/overseas)',
                'country': 'string (max 100)',
                'tax_id': 'string (max 100)',
                'company': 'foreign key to Company'
            },
            'filters': ['gst_category', 'country', 'name__icontains', 'company__id'],
            'relationships': {'invoices': 'has many purchase invoices'}
        }
    
    def _get_customer_schema(self, minimal: bool) -> Dict:
        """Customer table schema"""
        if minimal:
            return {
                'key_fields': ['id', 'name', 'gstin_uin', 'gst_category', 'country', 'company'],
                'description': 'Customer information',
                'gst_categories': ['registered', 'unregistered', 'composition', 'overseas']
            }
        return {
            'fields': {
                'id': 'integer (primary key)',
                'name': 'string (max 255)',
                'gstin_uin': 'string (max 50)',
                'gst_category': 'choice (registered/unregistered/composition/overseas)',
                'country': 'string (max 100)',
                'customer_type': 'choice (individual/company)',
                'company': 'foreign key to Company'
            },
            'filters': ['gst_category', 'country', 'customer_type', 'name__icontains'],
            'relationships': {'invoices': 'has many sales invoices'}
        }
    
    def _get_budget_schema(self, minimal: bool) -> Dict:
        """Budget table schema"""
        if minimal:
            return {
                'key_fields': ['id', 'series', 'fiscal_year_from', 'fiscal_year_to', 'monthly_distribution', 'company'],
                'description': 'Budget planning and tracking'
            }
        return {
            'fields': {
                'id': 'integer (primary key)',
                'series': 'string (max 100)',
                'fiscal_year_from': 'string (max 20)',
                'fiscal_year_to': 'string (max 20)',
                'monthly_distribution': 'boolean',
                'company': 'foreign key to Company',
                'cost_center': 'foreign key to CostCenter (nullable)'
            },
            'filters': ['fiscal_year_from', 'fiscal_year_to', 'company__id']
        }
    
    def _get_cost_center_schema(self, minimal: bool) -> Dict:
        """Cost Center table schema"""
        if minimal:
            return {
                'key_fields': ['id', 'cost_center_name', 'cost_center_number', 'is_group', 'is_disabled', 'company'],
                'description': 'Cost centers for expense tracking'
            }
        return {
            'fields': {
                'id': 'integer (primary key)',
                'cost_center_name': 'string (max 255)',
                'cost_center_number': 'string (max 50)',
                'is_group': 'boolean',
                'is_disabled': 'boolean',
                'company': 'foreign key to Company',
                'parent_cost_center': 'foreign key to CostCenter (self)'
            },
            'filters': ['is_group', 'is_disabled', 'company__id']
        }
    
    def _get_tax_rule_schema(self, minimal: bool) -> Dict:
        """Tax Rule table schema"""
        if minimal:
            return {
                'key_fields': ['id', 'item', 'tax_type', 'shipping_city', 'shipping_state', 'company'],
                'description': 'Tax calculation rules and rates',
                'tax_types': ['sales', 'purchase', 'both']
            }
        return {
            'fields': {
                'id': 'integer (primary key)',
                'item': 'string (max 255)',
                'tax_type': 'choice (sales/purchase/both)',
                'shipping_city': 'string (max 100)',
                'shipping_state': 'string (max 100)',
                'shipping_country': 'string (max 100)',
                'company': 'foreign key to Company'
            },
            'filters': ['tax_type', 'shipping_country', 'shipping_state', 'company__id']
        }
    
    def get_all_available_tables(self) -> List[str]:
        """Get list of all available tables"""
        return [
            'company', 'account', 'invoice', 'journal_entry',
            'supplier', 'customer', 'budget', 'cost_center', 'tax_rule'
        ]
    
    def get_relationship_info(self, table1: str, table2: str) -> Dict:
        """Get relationship information between two tables"""
        relationships = {
            ('company', 'account'): 'Company has many Accounts',
            ('company', 'invoice'): 'Company has many Invoices',
            ('company', 'supplier'): 'Company has many Suppliers',
            ('company', 'customer'): 'Company has many Customers',
            ('account', 'journal_entry'): 'Account has many Journal Entries',
            ('supplier', 'invoice'): 'Supplier has many Purchase Invoices',
            ('customer', 'invoice'): 'Customer has many Sales Invoices',
            ('account', 'account'): 'Account can have parent Account (hierarchical)',
            ('cost_center', 'budget'): 'Cost Center can have Budget',
        }
        
        key = (table1.lower(), table2.lower())
        reverse_key = (table2.lower(), table1.lower())
        
        if key in relationships:
            return {'success': True, 'relationship': relationships[key]}
        elif reverse_key in relationships:
            return {'success': True, 'relationship': relationships[reverse_key]}
        else:
            return {'success': False, 'error': f'No direct relationship between {table1} and {table2}'}
