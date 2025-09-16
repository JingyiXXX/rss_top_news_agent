"""
MCP (Model Context Protocol) integration for the RSS News Agent
"""
import asyncio
import logging
from typing import List, Dict, Any, Optional
from dataclasses import asdict
import json
from datetime import datetime

# MCP imports (using basic structure for now)
try:
    from mcp import server
    from mcp.types import Resource, Tool
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    logging.warning("MCP not available, running without MCP integration")

from .scraper import NewsArticle, RSScraper
from .analyzer import NewsAnalyzer
from .email_service import EmailService
from .config import config

logger = logging.getLogger(__name__)


class MCPNewsAgent:
    """MCP-enabled RSS News Agent"""
    
    def __init__(self):
        """Initialize MCP News Agent"""
        self.scraper = RSScraper(config.rss_feeds)
        self.analyzer = NewsAnalyzer()
        self.email_service = EmailService()
        self.last_run_time: Optional[datetime] = None
        self.cached_articles: List[NewsArticle] = []
    
    def get_mcp_tools(self) -> List[Dict[str, Any]]:
        """
        Define MCP tools available for the news agent
        
        Returns:
            List of MCP tool definitions
        """
        return [
            {
                "name": "scrape_news",
                "description": "Scrape latest news from configured RSS feeds",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "max_articles": {
                            "type": "integer",
                            "description": "Maximum number of articles to scrape",
                            "default": config.max_articles_per_run
                        }
                    }
                }
            },
            {
                "name": "analyze_viral_potential",
                "description": "Analyze articles for viral potential using AI",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "articles": {
                            "type": "array",
                            "description": "List of articles to analyze"
                        },
                        "min_viral_score": {
                            "type": "number",
                            "description": "Minimum viral score threshold",
                            "default": config.min_viral_score
                        }
                    }
                }
            },
            {
                "name": "send_viral_news",
                "description": "Send viral news via email",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "articles": {
                            "type": "array",
                            "description": "List of viral articles to send"
                        },
                        "to_email": {
                            "type": "string",
                            "description": "Override recipient email address",
                            "default": config.to_email
                        }
                    }
                }
            },
            {
                "name": "get_news_summary",
                "description": "Get a summary of recent news activity",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "run_full_pipeline",
                "description": "Run the complete news scraping, analysis, and email pipeline",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "force_send": {
                            "type": "boolean",
                            "description": "Force sending email even if no viral articles found",
                            "default": False
                        }
                    }
                }
            }
        ]
    
    def get_mcp_resources(self) -> List[Dict[str, Any]]:
        """
        Define MCP resources available for the news agent
        
        Returns:
            List of MCP resource definitions
        """
        return [
            {
                "uri": "news://cached-articles",
                "name": "Cached News Articles",
                "description": "Recently scraped and analyzed news articles",
                "mimeType": "application/json"
            },
            {
                "uri": "news://config",
                "name": "Agent Configuration", 
                "description": "Current configuration settings for the news agent",
                "mimeType": "application/json"
            },
            {
                "uri": "news://stats",
                "name": "Agent Statistics",
                "description": "Statistics about recent news agent activity",
                "mimeType": "application/json"
            }
        ]
    
    async def handle_mcp_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle MCP tool calls
        
        Args:
            tool_name: Name of the tool to execute
            arguments: Tool arguments
            
        Returns:
            Tool execution result
        """
        try:
            if tool_name == "scrape_news":
                return await self._handle_scrape_news(arguments)
            elif tool_name == "analyze_viral_potential":
                return await self._handle_analyze_viral_potential(arguments)
            elif tool_name == "send_viral_news":
                return await self._handle_send_viral_news(arguments)
            elif tool_name == "get_news_summary":
                return await self._handle_get_news_summary(arguments)
            elif tool_name == "run_full_pipeline":
                return await self._handle_run_full_pipeline(arguments)
            else:
                return {"error": f"Unknown tool: {tool_name}"}
                
        except Exception as e:
            logger.error(f"Error handling MCP tool call {tool_name}: {e}")
            return {"error": str(e)}
    
    async def handle_mcp_resource_request(self, uri: str) -> Dict[str, Any]:
        """
        Handle MCP resource requests
        
        Args:
            uri: Resource URI
            
        Returns:
            Resource content
        """
        try:
            if uri == "news://cached-articles":
                return {
                    "contents": [
                        {
                            "uri": uri,
                            "mimeType": "application/json",
                            "text": json.dumps([asdict(article) for article in self.cached_articles], default=str)
                        }
                    ]
                }
            elif uri == "news://config":
                return {
                    "contents": [
                        {
                            "uri": uri,
                            "mimeType": "application/json",
                            "text": json.dumps({
                                "rss_feeds": config.rss_feeds,
                                "max_articles_per_run": config.max_articles_per_run,
                                "min_viral_score": config.min_viral_score,
                                "schedule_hour": config.schedule_hour,
                                "schedule_minute": config.schedule_minute,
                                "to_email": config.to_email
                            })
                        }
                    ]
                }
            elif uri == "news://stats":
                stats = {
                    "last_run_time": self.last_run_time.isoformat() if self.last_run_time else None,
                    "cached_articles_count": len(self.cached_articles),
                    "viral_articles_count": len([a for a in self.cached_articles if a.viral_score >= config.min_viral_score]),
                    "avg_viral_score": sum(a.viral_score for a in self.cached_articles) / len(self.cached_articles) if self.cached_articles else 0
                }
                return {
                    "contents": [
                        {
                            "uri": uri,
                            "mimeType": "application/json",
                            "text": json.dumps(stats)
                        }
                    ]
                }
            else:
                return {"error": f"Unknown resource: {uri}"}
                
        except Exception as e:
            logger.error(f"Error handling MCP resource request {uri}: {e}")
            return {"error": str(e)}
    
    async def _handle_scrape_news(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle scrape_news tool call"""
        max_articles = arguments.get("max_articles", config.max_articles_per_run)
        
        # Run scraping in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        articles = await loop.run_in_executor(None, self.scraper.scrape_all_feeds)
        
        # Limit articles
        articles = articles[:max_articles]
        self.cached_articles = articles
        self.last_run_time = datetime.now()
        
        return {
            "success": True,
            "articles_found": len(articles),
            "articles": [asdict(article) for article in articles]
        }
    
    async def _handle_analyze_viral_potential(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle analyze_viral_potential tool call"""
        articles_data = arguments.get("articles", [])
        min_viral_score = arguments.get("min_viral_score", config.min_viral_score)
        
        # Convert dict data back to NewsArticle objects
        articles = []
        for article_data in articles_data:
            if isinstance(article_data, dict):
                article = NewsArticle(**article_data)
                articles.append(article)
        
        # If no articles provided, use cached articles
        if not articles:
            articles = self.cached_articles
        
        # Run analysis in thread pool
        loop = asyncio.get_event_loop()
        analyzed_articles = await loop.run_in_executor(None, self.analyzer.analyze_articles, articles)
        
        # Filter viral articles
        viral_articles = self.analyzer.filter_viral_articles(analyzed_articles, min_viral_score)
        
        # Update cache
        self.cached_articles = analyzed_articles
        
        return {
            "success": True,
            "total_articles": len(analyzed_articles),
            "viral_articles": len(viral_articles),
            "viral_articles_data": [asdict(article) for article in viral_articles]
        }
    
    async def _handle_send_viral_news(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle send_viral_news tool call"""
        articles_data = arguments.get("articles", [])
        to_email = arguments.get("to_email", config.to_email)
        
        # Convert dict data back to NewsArticle objects
        articles = []
        for article_data in articles_data:
            if isinstance(article_data, dict):
                article = NewsArticle(**article_data)
                articles.append(article)
        
        # Run email sending in thread pool
        loop = asyncio.get_event_loop()
        success = await loop.run_in_executor(None, self.email_service.send_email, articles)
        
        return {
            "success": success,
            "articles_sent": len(articles),
            "recipient": to_email
        }
    
    async def _handle_get_news_summary(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get_news_summary tool call"""
        viral_articles = [a for a in self.cached_articles if a.viral_score >= config.min_viral_score]
        
        summary = {
            "last_run": self.last_run_time.isoformat() if self.last_run_time else None,
            "total_articles": len(self.cached_articles),
            "viral_articles": len(viral_articles),
            "avg_viral_score": sum(a.viral_score for a in self.cached_articles) / len(self.cached_articles) if self.cached_articles else 0,
            "top_articles": [
                {
                    "title": article.title,
                    "source": article.source,
                    "viral_score": article.viral_score,
                    "published": article.published.isoformat()
                }
                for article in sorted(self.cached_articles, key=lambda x: x.viral_score, reverse=True)[:5]
            ]
        }
        
        return {"success": True, "summary": summary}
    
    async def _handle_run_full_pipeline(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle run_full_pipeline tool call"""
        force_send = arguments.get("force_send", False)
        
        try:
            # Step 1: Scrape news
            scrape_result = await self._handle_scrape_news({"max_articles": config.max_articles_per_run})
            if not scrape_result["success"]:
                return scrape_result
            
            # Step 2: Analyze viral potential
            analyze_result = await self._handle_analyze_viral_potential({"min_viral_score": config.min_viral_score})
            if not analyze_result["success"]:
                return analyze_result
            
            # Step 3: Send email if viral articles found or forced
            viral_articles = analyze_result["viral_articles_data"]
            if viral_articles or force_send:
                send_result = await self._handle_send_viral_news({"articles": viral_articles})
                if not send_result["success"]:
                    return send_result
            
            return {
                "success": True,
                "pipeline_completed": True,
                "articles_scraped": scrape_result["articles_found"],
                "viral_articles_found": analyze_result["viral_articles"],
                "email_sent": len(viral_articles) > 0 or force_send
            }
            
        except Exception as e:
            logger.error(f"Error in full pipeline: {e}")
            return {"success": False, "error": str(e)}


# Global MCP agent instance
mcp_agent = MCPNewsAgent()


def get_mcp_server():
    """Get MCP server instance if available"""
    if not MCP_AVAILABLE:
        return None
    
    # This would be implemented with actual MCP server setup
    # For now, returning a placeholder
    return None