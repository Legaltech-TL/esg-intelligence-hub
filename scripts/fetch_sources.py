#!/usr/bin/env python3
"""
Fetch news sources from SharePoint ESG_Sources list
"""
import os
import json
from office365.sharepoint.client_context import ClientContext
from office365.runtime.auth.client_credential import ClientCredential

def fetch_sources():
    """Fetch active sources from SharePoint"""
    
    site_url = os.environ.get('SHAREPOINT_SITE')
    client_id = os.environ.get('SHAREPOINT_CLIENT_ID')
    client_secret = os.environ.get('SHAREPOINT_CLIENT_SECRET')
    
    if not all([site_url, client_id, client_secret]):
        print("::warning::Missing SharePoint credentials, using local sources")
        return load_local_sources()
    
    try:
        # Authenticate
        credentials = ClientCredential(client_id, client_secret)
        ctx = ClientContext(site_url).with_credentials(credentials)
        
        # Get ESG_Sources list
        list_obj = ctx.web.lists.get_by_title("ESG_Sources")
        items = list_obj.items.filter("IsActive eq true").get().execute_query()
        
        sources = []
        for item in items:
            sources.append({
                'name': item.properties.get('Title', ''),
                'url': item.properties.get('SourceURL', {}).get('Url', ''),
                'type': item.properties.get('SourceType', 'RSS'),
                'category': item.properties.get('SourceCategory', 'News'),
                'selector': item.properties.get('CSSSelector', 'article')
            })
        
        # Save to file
        os.makedirs('data', exist_ok=True)
        with open('data/sources.json', 'w') as f:
            json.dump(sources, f, indent=2)
        
        print(f"✓ Fetched {len(sources)} sources from SharePoint")
        return sources
        
    except Exception as e:
        print(f"::warning::Failed to fetch from SharePoint: {e}")
        return load_local_sources()

def load_local_sources():
    """Load sources from local CSV as fallback"""
    import csv
    sources = []
    
    try:
        with open('config/sources.csv', 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('Active') == 'Yes':
                    sources.append({
                        'name': row['Title'],
                        'url': row['URL'],
                        'type': row['SourceType'],
                        'category': row['Category'],
                        'selector': row.get('CSSSelector', 'article')
                    })
        
        os.makedirs('data', exist_ok=True)
        with open('data/sources.json', 'w') as f:
            json.dump(sources, f, indent=2)
        
        print(f"✓ Loaded {len(sources)} sources from local file")
        return sources
        
    except Exception as e:
        print(f"::error::Failed to load sources: {e}")
        return []

if __name__ == "__main__":
    sources = fetch_sources()
    print(f"Total sources available: {len(sources)}")
