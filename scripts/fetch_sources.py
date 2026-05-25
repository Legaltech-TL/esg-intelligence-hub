#!/usr/bin/env python3
"""
Fetch news sources from local CSV file
"""
import json
import csv
import os

def load_sources():
    """Load sources from CSV"""
    sources = []
    
    try:
        with open('config/sources.csv', 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                # Strip whitespace from keys and values
                row = {k.strip(): v.strip() if isinstance(v, str) else v for k, v in row.items()}
                
                # Check if active (case-insensitive)
                if row.get('Active', '').lower() == 'yes':
                    sources.append({
                        'name': row.get('Title', ''),
                        'url': row.get('URL', ''),
                        'type': row.get('SourceType', 'RSS'),
                        'category': row.get('Category', 'General'),
                        'selector': row.get('CSSSelector', 'article')
                    })
        
        # Save for next steps
        os.makedirs('data', exist_ok=True)
        with open('data/sources.json', 'w') as f:
            json.dump(sources, f, indent=2)
        
        print(f"✓ Loaded {len(sources)} sources from CSV")
        return sources
        
    except Exception as e:
        print(f"::error::Failed to load sources: {e}")
        import traceback
        traceback.print_exc()
        return []

if __name__ == "__main__":
    sources = load_sources()
    print(f"Total sources available: {len(sources)}")
