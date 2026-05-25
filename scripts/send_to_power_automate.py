#!/usr/bin/env python3
"""
Send scraped articles to Power Automate via HTTP webhook
(No AI summarization - Power Automate will handle it)
"""
import json
import os
import sys
import requests
from datetime import datetime

def load_articles():
    """Load scraped articles"""
    try:
        with open('data/articles.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"::error::Failed to load articles: {e}")
        return []

def send_to_power_automate(articles):
    """Send data to Power Automate webhook"""
    
    webhook_url = os.environ.get('POWER_AUTOMATE_WEBHOOK')
    
    if not webhook_url:
        print("::error::POWER_AUTOMATE_WEBHOOK not set")
        print("::warning::Skipping Power Automate integration")
        return False
    
    if not articles:
        print("::warning::No articles to send")
        return True
    
    print(f"Sending {len(articles)} articles to Power Automate...")
    
    # Prepare payload
    payload = {
        'timestamp': datetime.now().isoformat(),
        'total_articles': len(articles),
        'articles': articles
    }
    
    try:
        response = requests.post(
            webhook_url,
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=60
        )
        
        response.raise_for_status()
        
        print(f"✓ Successfully sent to Power Automate")
        print(f"  Status: {response.status_code}")
        
        return True
        
    except requests.RequestException as e:
        print(f"::error::Failed to send to Power Automate: {e}")
        return False

def main():
    """Main function"""
    articles = load_articles()
    
    if not articles:
        print("::error::No articles to send")
        sys.exit(1)
    
    success = send_to_power_automate(articles)
    
    if not success:
        print("::error::Failed to send data")
        sys.exit(1)
    
    print("\n✓ Workflow complete!")
    print(f"  Articles scraped: {len(articles)}")
    print(f"  Sent to Power Automate: Success")

if __name__ == "__main__":
    main()
