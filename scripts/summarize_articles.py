#!/usr/bin/env python3
"""
AI Summarization using Claude API
"""
import json
import os
import sys
from anthropic import Anthropic

def load_articles():
    """Load scraped articles"""
    try:
        with open('data/articles.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"::error::Failed to load articles: {e}")
        return []

def summarize_articles(articles):
    """Summarize articles using Claude AI"""
    
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        print("::error::ANTHROPIC_API_KEY not set")
        sys.exit(1)
    
    if not articles:
        print("::warning::No articles to summarize")
        return []
    
    print(f"Summarizing {len(articles)} articles with Claude AI...")
    
    client = Anthropic(api_key=api_key)
    
    # Prepare articles for Claude
    articles_text = []
    for i, article in enumerate(articles, 1):
        articles_text.append(f"""
Article {i}:
Title: {article['title']}
Source: {article['source']}
Summary: {article['summary']}
Keywords: {', '.join(article['matched_keywords'][:10])}
Link: {article['link']}
""")
    
    # Create prompt
    prompt = f"""You are an ESG intelligence analyst for a law firm. Analyze these ESG-related articles and provide:

1. A brief executive summary (2-3 sentences) of key developments across all articles
2. For each article:
   - A concise 2-sentence summary highlighting legal/regulatory implications for Indian companies
   - Primary category from: Carbon Markets, ESG Disclosure, Climate Action, Greenhouse Gases, Renewable Energy, Green Finance, CBAM, Voluntary Carbon Market, Green Bonds, Plastic & Circular Economy, ESG Rating, Biomass & Bioenergy, Biodiversity, Water Stewardship, Tenders, SEBI Regulations, Other
   - Relevance score (0.0 to 1.0) based on importance to Indian corporate legal practice
   - Key action items or implications for Indian companies (if any)

Articles to analyze:

{''.join(articles_text[:50])}

Return your response as a JSON object with this structure:
{{
  "executive_summary": "...",
  "articles": [
    {{
      "article_number": 1,
      "ai_summary": "...",
      "category": "...",
      "relevance_score": 0.85,
      "action_items": ["..."],
      "key_entities": ["..."]
    }}
  ]
}}
"""
    
    try:
        # Call Claude API
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=8000,
            temperature=0.3,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        response_text = message.content[0].text
        
        # Extract JSON from response
        if '```json' in response_text:
            json_start = response_text.find('```json') + 7
            json_end = response_text.find('```', json_start)
            response_text = response_text[json_start:json_end].strip()
        elif '```' in response_text:
            json_start = response_text.find('```') + 3
            json_end = response_text.find('```', json_start)
            response_text = response_text[json_start:json_end].strip()
        
        ai_analysis = json.loads(response_text)
        
        # Merge AI data back into articles
        enriched_articles = []
        for i, article in enumerate(articles):
            enriched = article.copy()
            
            if i < len(ai_analysis.get('articles', [])):
                ai_data = ai_analysis['articles'][i]
                enriched['ai_summary'] = ai_data.get('ai_summary', article['summary'])
                enriched['category'] = ai_data.get('category', 'Other')
                enriched['relevance_score'] = ai_data.get('relevance_score', 0.5)
                enriched['action_items'] = ai_data.get('action_items', [])
                enriched['key_entities'] = ai_data.get('key_entities', [])
            else:
                # Fallback for articles beyond Claude's response
                enriched['ai_summary'] = article['summary']
                enriched['category'] = 'Other'
                enriched['relevance_score'] = 0.5
                enriched['action_items'] = []
                enriched['key_entities'] = []
            
            enriched_articles.append(enriched)
        
        # Save enriched articles
        result = {
            'executive_summary': ai_analysis.get('executive_summary', ''),
            'articles': enriched_articles,
            'total_count': len(enriched_articles)
        }
        
        with open('data/summaries.json', 'w') as f:
            json.dump(result, f, indent=2)
        
        print(f"✓ Summarized {len(enriched_articles)} articles")
        print(f"Executive Summary: {result['executive_summary'][:100]}...")
        
        return result
        
    except Exception as e:
        print(f"::error::AI summarization failed: {e}")
        
        # Fallback: return articles without AI enhancement
        fallback = {
            'executive_summary': f"Found {len(articles)} ESG-related articles today.",
            'articles': articles,
            'total_count': len(articles)
        }
        
        with open('data/summaries.json', 'w') as f:
            json.dump(fallback, f, indent=2)
        
        return fallback

def main():
    """Main function"""
    articles = load_articles()
    
    if not articles:
        print("::warning::No articles to summarize")
        sys.exit(0)
    
    result = summarize_articles(articles)
    print(f"\nTotal articles processed: {result['total_count']}")

if __name__ == "__main__":
    main()
