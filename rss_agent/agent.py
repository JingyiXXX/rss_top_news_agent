"""
Main RSS News Agent that orchestrates scraping, analysis, and email forwarding
"""
import logging
import schedule
import time
from typing import List
from datetime import datetime
from .scraper import RSScraper, NewsArticle
from .analyzer import NewsAnalyzer
from .email_service import EmailService
from .config import config
from .mcp_integration import mcp_agent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('rss_news_agent.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class RSSNewsAgent:
    """Main RSS News Agent class"""
    
    def __init__(self):
        """Initialize the RSS News Agent"""
        self.scraper = RSScraper(config.rss_feeds)
        self.analyzer = NewsAnalyzer()
        self.email_service = EmailService()
        self.is_running = False
        
        logger.info("RSS News Agent initialized")
        logger.info(f"Configured RSS feeds: {len(config.rss_feeds)}")
        logger.info(f"Schedule: {config.schedule_hour:02d}:{config.schedule_minute:02d}")
        logger.info(f"Min viral score: {config.min_viral_score}")
        logger.info(f"Max articles per run: {config.max_articles_per_run}")
    
    def run_news_pipeline(self) -> dict:
        """
        Run the complete news pipeline: scrape, analyze, and email
        
        Returns:
            Dictionary with pipeline results
        """
        start_time = datetime.now()
        logger.info("=" * 60)
        logger.info("Starting RSS News Agent pipeline...")
        
        try:
            # Step 1: Scrape RSS feeds
            logger.info("Step 1: Scraping RSS feeds...")
            articles = self.scraper.scrape_all_feeds()
            
            if not articles:
                logger.warning("No articles found from RSS feeds")
                return {
                    "success": True,
                    "articles_scraped": 0,
                    "viral_articles": 0,
                    "email_sent": False,
                    "message": "No articles found"
                }
            
            # Limit articles for analysis
            articles = articles[:config.max_articles_per_run]
            logger.info(f"Processing {len(articles)} articles...")
            
            # Step 2: Analyze viral potential
            logger.info("Step 2: Analyzing viral potential with AI...")
            analyzed_articles = self.analyzer.analyze_articles(articles)
            
            # Step 3: Filter viral articles
            logger.info("Step 3: Filtering viral articles...")
            viral_articles = self.analyzer.filter_viral_articles(
                analyzed_articles, 
                config.min_viral_score
            )
            
            if not viral_articles:
                logger.info("No viral articles found meeting the threshold")
                return {
                    "success": True,
                    "articles_scraped": len(articles),
                    "viral_articles": 0,
                    "email_sent": False,
                    "message": "No viral articles found"
                }
            
            # Step 4: Send email
            logger.info(f"Step 4: Sending email with {len(viral_articles)} viral articles...")
            email_success = self.email_service.send_email(viral_articles)
            
            # Log results
            duration = (datetime.now() - start_time).total_seconds()
            logger.info(f"Pipeline completed in {duration:.2f} seconds")
            logger.info(f"Articles scraped: {len(articles)}")
            logger.info(f"Viral articles found: {len(viral_articles)}")
            logger.info(f"Email sent: {email_success}")
            
            # Log top viral articles
            for i, article in enumerate(viral_articles[:3], 1):
                logger.info(f"Top {i}: {article.title} (Score: {article.viral_score:.2f})")
            
            return {
                "success": True,
                "articles_scraped": len(articles),
                "viral_articles": len(viral_articles),
                "email_sent": email_success,
                "duration_seconds": duration,
                "top_articles": [
                    {
                        "title": article.title,
                        "viral_score": article.viral_score,
                        "source": article.source
                    }
                    for article in viral_articles[:5]
                ]
            }
            
        except Exception as e:
            logger.error(f"Error in news pipeline: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "articles_scraped": 0,
                "viral_articles": 0,
                "email_sent": False
            }
        
        finally:
            logger.info("=" * 60)
    
    def test_configuration(self) -> bool:
        """
        Test all configuration and connections
        
        Returns:
            True if all tests pass, False otherwise
        """
        logger.info("Testing RSS News Agent configuration...")
        
        all_tests_passed = True
        
        # Test OpenAI API
        try:
            logger.info("Testing OpenAI API connection...")
            # Create a simple test with the analyzer
            test_article = NewsArticle(
                title="Test Article",
                link="https://example.com",
                description="This is a test article",
                published=datetime.now(),
                source="Test Source"
            )
            analysis = self.analyzer.analyze_viral_potential(test_article)
            if analysis.get("viral_score") is not None:
                logger.info("✓ OpenAI API test passed")
            else:
                logger.error("✗ OpenAI API test failed")
                all_tests_passed = False
        except Exception as e:
            logger.error(f"✗ OpenAI API test failed: {e}")
            all_tests_passed = False
        
        # Test email connection
        try:
            logger.info("Testing email connection...")
            if self.email_service.test_email_connection():
                logger.info("✓ Email connection test passed")
            else:
                logger.error("✗ Email connection test failed")
                all_tests_passed = False
        except Exception as e:
            logger.error(f"✗ Email connection test failed: {e}")
            all_tests_passed = False
        
        # Test RSS feeds
        try:
            logger.info("Testing RSS feeds...")
            test_articles = []
            for feed_url in config.rss_feeds[:2]:  # Test first 2 feeds
                articles = self.scraper.scrape_feed(feed_url)
                test_articles.extend(articles)
            
            if test_articles:
                logger.info(f"✓ RSS feeds test passed ({len(test_articles)} articles found)")
            else:
                logger.warning("⚠ RSS feeds test warning: No articles found")
        except Exception as e:
            logger.error(f"✗ RSS feeds test failed: {e}")
            all_tests_passed = False
        
        if all_tests_passed:
            logger.info("✓ All configuration tests passed!")
        else:
            logger.error("✗ Some configuration tests failed")
        
        return all_tests_passed
    
    def start_scheduler(self):
        """Start the scheduled news agent"""
        logger.info(f"Starting RSS News Agent scheduler...")
        logger.info(f"Scheduled to run daily at {config.schedule_hour:02d}:{config.schedule_minute:02d}")
        
        # Schedule the daily job
        schedule.every().day.at(f"{config.schedule_hour:02d}:{config.schedule_minute:02d}").do(
            self.run_news_pipeline
        )
        
        self.is_running = True
        
        try:
            while self.is_running:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
                
        except KeyboardInterrupt:
            logger.info("Scheduler stopped by user")
        except Exception as e:
            logger.error(f"Scheduler error: {e}")
        finally:
            self.is_running = False
    
    def stop_scheduler(self):
        """Stop the scheduler"""
        self.is_running = False
        logger.info("RSS News Agent scheduler stopped")
    
    def run_once(self) -> dict:
        """
        Run the news pipeline once (for testing or manual execution)
        
        Returns:
            Pipeline execution results
        """
        logger.info("Running RSS News Agent pipeline once...")
        return self.run_news_pipeline()
    
    def get_status(self) -> dict:
        """
        Get current agent status
        
        Returns:
            Status information
        """
        return {
            "is_running": self.is_running,
            "scheduled_time": f"{config.schedule_hour:02d}:{config.schedule_minute:02d}",
            "rss_feeds_count": len(config.rss_feeds),
            "min_viral_score": config.min_viral_score,
            "max_articles_per_run": config.max_articles_per_run,
            "next_run": schedule.next_run() if schedule.jobs else None
        }


# Global agent instance
agent = RSSNewsAgent()


def main():
    """Main entry point for the RSS News Agent"""
    import argparse
    
    parser = argparse.ArgumentParser(description="RSS News Agent - AI-powered viral news detection and email forwarding")
    parser.add_argument("--test", action="store_true", help="Test configuration and connections")
    parser.add_argument("--run-once", action="store_true", help="Run the pipeline once and exit")
    parser.add_argument("--schedule", action="store_true", help="Start the scheduled agent (default)")
    parser.add_argument("--mcp", action="store_true", help="Start MCP server mode")
    
    args = parser.parse_args()
    
    if args.test:
        logger.info("Running configuration tests...")
        success = agent.test_configuration()
        exit(0 if success else 1)
    
    elif args.run_once:
        logger.info("Running pipeline once...")
        result = agent.run_once()
        if result["success"]:
            logger.info("Pipeline completed successfully")
            exit(0)
        else:
            logger.error("Pipeline failed")
            exit(1)
    
    elif args.mcp:
        logger.info("Starting MCP server mode...")
        # MCP server implementation would go here
        logger.info("MCP mode not fully implemented yet")
        exit(1)
    
    else:
        # Default: start scheduler
        logger.info("Starting RSS News Agent scheduler...")
        agent.start_scheduler()


if __name__ == "__main__":
    main()