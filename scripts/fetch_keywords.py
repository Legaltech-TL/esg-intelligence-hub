#!/usr/bin/env python3
"""
Fetch keywords from SharePoint ESG_Keywords list
"""
import os
import json
from office365.sharepoint.client_context import ClientContext
from office365.runtime.auth.client_credential import ClientCredential

def fetch_keywords():
    """Fetch active keywords from SharePoint"""
    
    # SharePoint credentials from environment
    site_url = os.environ.get('SHAREPOINT_SITE')
    client_id = os.environ.get('SHAREPOINT_CLIENT_ID')
    client_secret = os.environ.get('SHAREPOINT_CLIENT_SECRET')
    
    if not all([site_url, client_id, client_secret]):
        print("::error::Missing SharePoint credentials")
        # Fallback to local keywords if SharePoint unavailable
        return load_local_keywords()
    
    try:
        # Authenticate
        credentials = ClientCredential(client_id, client_secret)
        ctx = ClientContext(site_url).with_credentials(credentials)
        
        # Get ESG_Keywords list
        list_obj = ctx.web.lists.get_by_title("ESG_Keywords")
        items = list_obj.items.filter("IsActive eq true").get().execute_query()
        
        keywords = []
        for item in items:
            keywords.append({
                'keyword': item.properties.get('KeywordText', ''),
                'category': item.properties.get('KeywordCategory', 'General'),
                'priority': item.properties.get('KeywordPriority', 'Medium')
            })
        
        # Save to file for next steps
        os.makedirs('data', exist_ok=True)
        with open('data/keywords.json', 'w') as f:
            json.dump(keywords, f, indent=2)
        
        print(f"✓ Fetched {len(keywords)} keywords from SharePoint")
        return keywords
        
    except Exception as e:
        print(f"::warning::Failed to fetch from SharePoint: {e}")
        print("Using local keywords fallback")
        return load_local_keywords()

def load_local_keywords():
    """Load keywords from local CSV as fallback"""
    import csv
    keywords = []
    
    try:
        with open('config/keywords.csv', 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('Active') == 'Yes':
                    keywords.append({
                        'keyword': row['Keyword'],
                        'category': row['Category'],
                        'priority': row['Priority']
                    })
        
        # Save for next steps
        os.makedirs('data', exist_ok=True)
        with open('data/keywords.json', 'w') as f:
            json.dump(keywords, f, indent=2)
        
        print(f"✓ Loaded {len(keywords)} keywords from local file")
        return keywords
        
    except Exception as e:
        print(f"::error::Failed to load keywords: {e}")
        return []

if __name__ == "__main__":
    keywords = fetch_keywords()
    print(f"Total keywords available: {len(keywords)}")
