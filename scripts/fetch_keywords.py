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
            reader = csv.DictReader(f)
            for row in reader:
                # Strip whitespace from all values
                row = {k: v.strip() if isinstance(v, str) else v for k, v in row.items()}
                
                # Check if active (case-insensitive)
                if row.get('Active', '').lower() == 'yes':
                    keywords.append({
                        'keyword': row['Keyword'],
                        'category': row['Category'],
                        'priority': row['Priority']
                    })
        
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
