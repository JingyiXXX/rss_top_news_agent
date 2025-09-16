"""
RSS Feed Scraper for collecting news articles
"""
import feedparser
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class NewsArticle:
    """Data class for news articles"""
    title: str
    link: str
    description: str
    published: datetime
    source: str
    content: Optional[str] = None
    viral_score: float = 0.0


class RSScraper:
    """RSS feed scraper for news articles"""
    
    def __init__(self, feed_urls: List[str]):
        """
        Initialize RSS scraper with feed URLs
        
        Args:
            feed_urls: List of RSS feed URLs to scrape
        """
        self.feed_urls = feed_urls
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def scrape_feed(self, url: str) -> List[NewsArticle]:
        """
        Scrape a single RSS feed
        
        Args:
            url: RSS feed URL
            
        Returns:
            List of NewsArticle objects
        """
        articles = []
        
        try:
            logger.info(f"Scraping RSS feed: {url}")
            feed = feedparser.parse(url)
            
            if feed.bozo:
                logger.warning(f"RSS feed has parsing issues: {url}")
            
            source_name = feed.feed.get('title', 'Unknown Source')
            
            for entry in feed.entries:
                try:
                    # Parse published date
                    published = datetime.now()
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        published = datetime(*entry.published_parsed[:6])
                    elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                        published = datetime(*entry.updated_parsed[:6])
                    
                    # Only include articles from the last 24 hours
                    if published < datetime.now() - timedelta(days=1):
                        continue
                    
                    article = NewsArticle(
                        title=entry.get('title', ''),
                        link=entry.get('link', ''),
                        description=entry.get('summary', ''),
                        published=published,
                        source=source_name
                    )
                    
                    # Try to get full content
                    article.content = self._extract_article_content(article.link)
                    
                    articles.append(article)
                    
                except Exception as e:
                    logger.error(f"Error processing article from {url}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error scraping RSS feed {url}: {e}")
        
        logger.info(f"Scraped {len(articles)} articles from {url}")
        return articles
    
    def scrape_all_feeds(self) -> List[NewsArticle]:
        """
        Scrape all configured RSS feeds
        
        Returns:
            List of all NewsArticle objects
        """
        all_articles = []
        
        for url in self.feed_urls:
            articles = self.scrape_feed(url)
            all_articles.extend(articles)
        
        # Remove duplicates based on title and link
        unique_articles = []
        seen = set()
        
        for article in all_articles:
            key = (article.title.lower(), article.link)
            if key not in seen:
                seen.add(key)
                unique_articles.append(article)
        
        # Sort by published date (newest first)
        unique_articles.sort(key=lambda x: x.published, reverse=True)
        
        logger.info(f"Total unique articles scraped: {len(unique_articles)}")
        return unique_articles
    
    def _extract_article_content(self, url: str) -> Optional[str]:
        """
        Extract full article content from URL
        
        Args:
            url: Article URL
            
        Returns:
            Article content text or None
        """
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove unwanted elements
            for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
                element.decompose()
            
            # Try to find article content using common selectors
            content_selectors = [
                'article',
                '.article-content',
                '.story-body',
                '.post-content',
                '.entry-content',
                'main',
                '.content'
            ]
            
            content = ""
            for selector in content_selectors:
                elements = soup.select(selector)
                if elements:
                    content = elements[0].get_text(strip=True)
                    break
            
            if not content:
                # Fallback to body content
                body = soup.find('body')
                if body:
                    content = body.get_text(strip=True)
            
            # Clean up content
            content = ' '.join(content.split())
            
            # Limit content length
            if len(content) > 5000:
                content = content[:5000] + "..."
            
            return content if content else None
            
        except Exception as e:
            logger.warning(f"Failed to extract content from {url}: {e}")
            return None