#!/usr/bin/env python3
"""
Main scraping orchestrator - handles RSS and web sources
"""
import json
import os
import sys
from datetime import datetime, timedelta
import feedparser
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin

def load_data(filename):
    """Load JSON data file"""
    try:
        with open(f'data/{filename}', 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"::error::Failed to load {filename}: {e}")
        return []

def scrape_rss(source, keywords):
    """Scrape RSS feed and filter by keywords"""
    print(f"  Scraping RSS: {source['name']}")
    
    try:
        feed = feedparser.parse(source['url'])
        
        if feed.bozo:
            print(f"  ::warning::Feed parsing issues for {source['name']}")
        
        cutoff_time = datetime.now() - timedelta(hours=240)
        articles = []
        
        for entry in feed.entries[:50]:  # Limit to 50 entries
            try:
                title = entry.get('title', '')
                link = entry.get('link', '')
                summary = entry.get('summary', entry.get('description', ''))
                
                # Parse date
                published = None
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    published = datetime(*entry.published_parsed[:6])
                
                # Skip old articles
                if published and published < cutoff_time:
                    continue
                
                # Keyword matching
                content = f"{title} {summary}".lower()
                matched = [kw['keyword'] for kw in keywords if kw['keyword'].lower() in content]
                
                if not matched:
                    continue
                
                # Extract image
                image_url = None
                if hasattr(entry, 'media_content') and entry.media_content:
                    image_url = entry.media_content[0].get('url')
                
                articles.append({
                    'title': title,
                    'link': link,
                    'published': published.isoformat() if published else None,
                    'summary': summary[:500],
                    'matched_keywords': matched,
                    'image_url': image_url,
                    'source': source['name'],
                    'source_category': source['category']
                })
                
            except Exception as e:
                print(f"  ::debug::Error processing entry: {e}")
                continue
        
        print(f"  ✓ Found {len(articles)} articles")
        return articles
        
    except Exception as e:
        print(f"  ::error::Failed to scrape {source['name']}: {e}")
        return []

def scrape_web(source, keywords):
    """Scrape website using CSS selector"""
    print(f"  Scraping Web: {source['name']}")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(source['url'], headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'lxml')
        elements = soup.select(source['selector'])
        
        articles = []
        
        for element in elements[:30]:  # Limit to 30 articles
            try:
                # Extract title
                title_elem = (
                    element.find('h1') or 
                    element.find('h2') or 
                    element.find('h3') or
                    element.find(class_=['title', 'headline'])
                )
                
                if not title_elem:
                    continue
                
                title = title_elem.get_text(strip=True)
                
                # Extract link
                link_elem = element.find('a', href=True)
                link = urljoin(source['url'], link_elem['href']) if link_elem else source['url']
                
                # Extract summary
                summary = ''
                summary_elem = (
                    element.find(class_=['summary', 'excerpt', 'description']) or
                    element.find('p')
                )
                if summary_elem:
                    summary = summary_elem.get_text(strip=True)
                
                # Keyword matching
                content = f"{title} {summary}".lower()
                matched = [kw['keyword'] for kw in keywords if kw['keyword'].lower() in content]
                
                if not matched:
                    continue
                
                # Extract image
                image_url = None
                img_elem = element.find('img', src=True)
                if img_elem:
                    image_url = urljoin(source['url'], img_elem['src'])
                
                articles.append({
                    'title': title,
                    'link': link,
                    'published': None,  # Hard to extract reliably
                    'summary': summary[:500],
                    'matched_keywords': matched,
                    'image_url': image_url,
                    'source': source['name'],
                    'source_category': source['category']
                })
                
            except Exception as e:
                print(f"  ::debug::Error processing element: {e}")
                continue
        
        print(f"  ✓ Found {len(articles)} articles")
        return articles
        
    except Exception as e:
        print(f"  ::error::Failed to scrape {source['name']}: {e}")
        return []

def main():
    """Main scraping function"""
    print("Starting ESG news scraping...")
    
    # Load keywords and sources
    keywords = load_data('keywords.json')
    sources = load_data('sources.json')
    
    if not keywords:
        print("::error::No keywords loaded")
        sys.exit(1)
    
    if not sources:
        print("::error::No sources loaded")
        sys.exit(1)
    
    print(f"Loaded {len(keywords)} keywords and {len(sources)} sources")
    
    # Scrape all sources
    all_articles = []
    
    for source in sources:
        try:
            if source['type'] == 'RSS':
                articles = scrape_rss(source, keywords)
            elif source['type'] == 'Web':
                articles = scrape_web(source, keywords)
            else:
                print(f"  ::warning::Unknown source type: {source['type']}")
                continue
            
            all_articles.extend(articles)
            
        except Exception as e:
            print(f"::error::Failed processing {source['name']}: {e}")
            continue
    
    # Remove duplicates (same title and link)
    seen = set()
    unique_articles = []
    for article in all_articles:
        key = (article['title'], article['link'])
        if key not in seen:
            seen.add(key)
            unique_articles.append(article)
    
    # Save results
    os.makedirs('data', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    
    with open('data/articles.json', 'w') as f:
        json.dump(unique_articles, f, indent=2)
    
    # Log summary
    timestamp = datetime.now().isoformat()
    with open('logs/scraping.log', 'a') as f:
        f.write(f"\n{timestamp}: Scraped {len(unique_articles)} unique articles from {len(sources)} sources\n")
    
    print(f"\n✓ Scraping complete!")
    print(f"Total articles: {len(all_articles)}")
    print(f"Unique articles: {len(unique_articles)}")
    
    if len(unique_articles) == 0:
        print("::warning::No articles found. Check sources and keywords.")

if __name__ == "__main__":
    main()
