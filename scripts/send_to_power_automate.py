#!/usr/bin/env python3
"""
Send summarized articles to Power Automate via HTTP webhook
"""
import json
import os
import sys
import requests
from datetime import datetime

def load_summaries():
    """Load summarized articles"""
    try:
        with open('data/summaries.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"::error::Failed to load summaries: {e}")
        return None

def send_to_power_automate(data):
    """Send data to Power Automate webhook"""
    
    webhook_url = os.environ.get('POWER_AUTOMATE_WEBHOOK')
    
    if not webhook_url:
        print("::error::POWER_AUTOMATE_WEBHOOK not set")
        print("::warning::Skipping Power Automate integration")
        return False
    
    print(f"Sending {data['total_count']} articles to Power Automate...")
    
    # Prepare payload
    payload = {
        'timestamp': datetime.now().isoformat(),
        'executive_summary': data['executive_summary'],
        'total_articles': data['total_count'],
        'articles': data['articles']
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
    data = load_summaries()
    
    if not data:
        print("::error::No data to send")
        sys.exit(1)
    
    if data['total_count'] == 0:
        print("::warning::No articles to send")
        sys.exit(0)
    
    success = send_to_power_automate(data)
    
    if not success:
        print("::error::Failed to send data")
        sys.exit(1)
    
    print("\n✓ Workflow complete!")
    print(f"  Articles scraped: {data['total_count']}")
    print(f"  Sent to Power Automate: Success")

if __name__ == "__main__":
    main()
