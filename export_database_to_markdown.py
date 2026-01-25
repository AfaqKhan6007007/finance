"""
Export all data from SQLite database to Markdown format
Creates a comprehensive ground truth document for testing chatbot queries
"""

import os
import sys
import django
from datetime import datetime

# Setup Django environment
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from finance.models import (
    Company, Account, Invoice, JournalEntry, Supplier, Customer,
    Budget, CostCenter, CostCenterAllocation, AccountingDimension,
    TaxItemTemplate, TaxCategory, TaxRule,
    TaxWithholdingCategory, TaxWithholdingRate, TaxCategoryAccount,
    DeductionCertificate, BankAccountType, BankAccountSubtype, BankAccount,
    UserProfile
)

def format_value(value):
    """Format field values for markdown display"""
    if value is None:
        return "_empty_"
    if isinstance(value, bool):
        return "✅ Yes" if value else "❌ No"
    if isinstance(value, (datetime)):
        return value.strftime("%Y-%m-%d %H:%M:%S")
    if isinstance(value, str) and value.strip() == "":
        return "_empty_"
    return str(value)

def export_model_to_markdown(model_class, md_file):
    """Export a single model's data to markdown"""
    model_name = model_class._meta.verbose_name_plural.title()
    table_name = model_class._meta.db_table
    
    # Get all records
    records = model_class.objects.all()
    count = records.count()
    
    md_file.write(f"\n## {model_name}\n\n")
    md_file.write(f"**Table:** `{table_name}`  \n")
    md_file.write(f"**Total Records:** {count}\n\n")
    
    if count == 0:
        md_file.write("_No records found_\n\n")
        return
    
    # Get all field names
    fields = [f for f in model_class._meta.fields]
    
    # Write each record
    for idx, record in enumerate(records, 1):
        md_file.write(f"### Record {idx}\n\n")
        
        for field in fields:
            field_name = field.name
            field_verbose = field.verbose_name.title()
            
            try:
                value = getattr(record, field_name)
                
                # Handle foreign keys - show both ID and string representation
                if field.is_relation and value is not None:
                    related_str = str(value)
                    value_display = f"{value.pk} ({related_str})"
                else:
                    value_display = format_value(value)
                
                md_file.write(f"- **{field_verbose}** (`{field_name}`): {value_display}\n")
            except Exception as e:
                md_file.write(f"- **{field_verbose}** (`{field_name}`): _error: {e}_\n")
        
        md_file.write("\n")
    
    md_file.write("---\n\n")

def main():
    """Main export function"""
    output_file = "database_ground_truth.md"
    
    print(f"Exporting database to {output_file}...")
    print("=" * 80)
    
    with open(output_file, 'w', encoding='utf-8') as md_file:
        # Write header
        md_file.write("# Database Ground Truth\n\n")
        md_file.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        md_file.write("This document contains all data from the SQLite database.\n")
        md_file.write("Use this as ground truth when testing chatbot queries.\n\n")
        md_file.write("---\n\n")
        
        # Table of contents
        md_file.write("## Table of Contents\n\n")
        
        models = [
            ("Core Business", [Company, Account, Invoice, JournalEntry, Supplier, Customer]),
            ("Planning & Budgeting", [Budget, CostCenter, CostCenterAllocation, AccountingDimension]),
            ("Tax Configuration", [
                TaxItemTemplate, TaxCategory, TaxRule,
                TaxWithholdingCategory, TaxWithholdingRate, 
                TaxCategoryAccount, DeductionCertificate
            ]),
            ("Banking", [BankAccountType, BankAccountSubtype, BankAccount]),
            ("Users", [UserProfile])
        ]
        
        for category, model_list in models:
            md_file.write(f"### {category}\n\n")
            for model in model_list:
                count = model.objects.count()
                model_name = model._meta.verbose_name_plural.title()
                md_file.write(f"- [{model_name}](#{model_name.lower().replace(' ', '-')}) ({count} records)\n")
            md_file.write("\n")
        
        md_file.write("---\n\n")
        
        # Export each model
        for category, model_list in models:
            md_file.write(f"\n# {category}\n\n")
            for model in model_list:
                print(f"Exporting {model._meta.verbose_name_plural}...")
                try:
                    export_model_to_markdown(model, md_file)
                except Exception as e:
                    print(f"  ⚠️ Error exporting {model.__name__}: {e}")
                    md_file.write(f"\n_Error exporting this model: {e}_\n\n")
        
        # Write summary statistics at the end
        md_file.write("\n---\n\n")
        md_file.write("## Summary Statistics\n\n")
        md_file.write("| Model | Record Count |\n")
        md_file.write("|-------|-------------|\n")
        
        total_records = 0
        for category, model_list in models:
            for model in model_list:
                count = model.objects.count()
                total_records += count
                model_name = model._meta.verbose_name_plural.title()
                md_file.write(f"| {model_name} | {count} |\n")
        
        md_file.write(f"| **TOTAL** | **{total_records}** |\n")
    
    print("=" * 80)
    print(f"✅ Export complete!")
    print(f"📄 Output file: {output_file}")
    print(f"📊 Total records exported: {total_records}")
    print("\nYou can now use this file as ground truth when testing chatbot queries.")

if __name__ == "__main__":
    main()
