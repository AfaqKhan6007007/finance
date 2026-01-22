# MCP Server Configuration
import os
import sys
from pathlib import Path

# Add Django project to Python path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# Initialize Django
import django
django.setup()

# Server Metadata (MCP Best Practice)
SERVER_NAME = "finance-management-mcp"
SERVER_VERSION = "1.0.0"
SERVER_DESCRIPTION = "MCP Server for Finance Management System - Query companies, accounts, invoices, suppliers, customers, budgets, and financial reports"

# Tool Configuration
MAX_RESULTS_PER_QUERY = 100  # Limit results to prevent context overflow
DEFAULT_PAGE_SIZE = 20

# Database Schema Path
SCHEMA_DOC_PATH = BASE_DIR / "DATABASE_SCHEMA.md"
