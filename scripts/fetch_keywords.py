#!/usr/bin/env python3
"""
Fetch keywords from local CSV file
"""
import json
import csv
import os

def load_keywords():
    """Load keywords from CSV"""
    keywords = []
    
    try:
        with open('config/keywords.csv', 'r', encoding='utf-8-sig') as f:
            content = f.read()
            print(f"DEBUG: File size: {len(content)} bytes")
            print(f"DEBUG: First 200 chars: {repr(content[:200])}")
        
        with open('config/keywords.csv', 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            
            # DEBUG: Print column names
            print(f"DEBUG: CSV columns: {reader.fieldnames}")
            
            row_count = 0
            for row in reader:
                row_count += 1
                
                # DEBUG: Print first 3 rows
                if row_count <= 3:
                    print(f"DEBUG: Row {row_count}: {row}")
                    print(f"DEBUG: Active value: '{row.get('Active')}' (type: {type(row.get('Active'))})")
                
                # Strip whitespace from all values AND keys
                row = {k.strip(): v.strip() if isinstance(v, str) else v for k, v in row.items()}
                
                # Check if active (case-insensitive)
                active_val = row.get('Active', '')
                if active_val.lower() == 'yes':
                    keywords.append({
                        'keyword': row['Keyword'],
                        'category': row['Category'],
                        'priority': row['Priority']
                    })
                elif row_count <= 3:
                    print(f"DEBUG: Row {row_count} NOT matched. Active='{active_val}', lower='{active_val.lower()}'")
            
            print(f"DEBUG: Total rows read: {row_count}")
            print(f"DEBUG: Keywords matched: {len(keywords)}")
        
        os.makedirs('data', exist_ok=True)
        with open('data/keywords.json', 'w') as f:
            json.dump(keywords, f, indent=2)
        
        print(f"✓ Loaded {len(keywords)} keywords from CSV")
        return keywords
        
    except Exception as e:
        print(f"::error::Failed to load keywords: {e}")
        import traceback
        traceback.print_exc()
        return []

if __name__ == "__main__":
    keywords = load_keywords()
    print(f"Total keywords available: {len(keywords)}")
