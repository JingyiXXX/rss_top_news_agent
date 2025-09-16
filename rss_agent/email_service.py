"""
Email service for forwarding viral news
"""
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import List
from datetime import datetime
from .scraper import NewsArticle
from .analyzer import NewsAnalyzer
from .config import config

logger = logging.getLogger(__name__)


class EmailService:
    """Email service for sending viral news summaries"""
    
    def __init__(self):
        """Initialize email service with configuration"""
        self.smtp_server = config.smtp_server
        self.smtp_port = config.smtp_port
        self.email_user = config.email_user
        self.email_password = config.email_password
        self.to_email = config.to_email
        self.analyzer = NewsAnalyzer()
    
    def create_news_email(self, articles: List[NewsArticle]) -> MIMEMultipart:
        """
        Create an HTML email with viral news articles
        
        Args:
            articles: List of viral NewsArticle objects
            
        Returns:
            MIMEMultipart email message
        """
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"🔥 Viral News Update - {datetime.now().strftime('%B %d, %Y')}"
        msg['From'] = self.email_user
        msg['To'] = self.to_email
        
        # Create HTML content
        html_content = self._generate_html_content(articles)
        
        # Create plain text version
        text_content = self._generate_text_content(articles)
        
        # Attach both versions
        part1 = MIMEText(text_content, 'plain')
        part2 = MIMEText(html_content, 'html')
        
        msg.attach(part1)
        msg.attach(part2)
        
        return msg
    
    def _generate_html_content(self, articles: List[NewsArticle]) -> str:
        """Generate HTML email content"""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Viral News Update</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f5f5f5;
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                    border-radius: 10px;
                    margin-bottom: 30px;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 28px;
                }}
                .subtitle {{
                    margin: 10px 0 0 0;
                    opacity: 0.9;
                    font-size: 16px;
                }}
                .article {{
                    background: white;
                    margin-bottom: 25px;
                    padding: 25px;
                    border-radius: 10px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    border-left: 4px solid #667eea;
                }}
                .article-title {{
                    font-size: 20px;
                    font-weight: bold;
                    margin-bottom: 10px;
                    color: #2c3e50;
                }}
                .article-title a {{
                    color: #2c3e50;
                    text-decoration: none;
                }}
                .article-title a:hover {{
                    color: #667eea;
                }}
                .article-meta {{
                    color: #7f8c8d;
                    font-size: 14px;
                    margin-bottom: 15px;
                    display: flex;
                    align-items: center;
                    gap: 15px;
                }}
                .viral-score {{
                    background: #e74c3c;
                    color: white;
                    padding: 4px 12px;
                    border-radius: 20px;
                    font-size: 12px;
                    font-weight: bold;
                }}
                .viral-score.high {{
                    background: #e74c3c;
                }}
                .viral-score.medium {{
                    background: #f39c12;
                }}
                .article-summary {{
                    color: #555;
                    margin-bottom: 15px;
                    font-size: 16px;
                    line-height: 1.6;
                }}
                .read-more {{
                    display: inline-block;
                    background: #667eea;
                    color: white;
                    padding: 10px 20px;
                    text-decoration: none;
                    border-radius: 5px;
                    font-weight: bold;
                    transition: background 0.3s;
                }}
                .read-more:hover {{
                    background: #5a6fd8;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 40px;
                    padding: 20px;
                    color: #7f8c8d;
                    font-size: 14px;
                }}
                .stats {{
                    background: white;
                    padding: 20px;
                    border-radius: 10px;
                    margin-bottom: 30px;
                    text-align: center;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🔥 Viral News Update</h1>
                <div class="subtitle">{datetime.now().strftime('%B %d, %Y at %I:%M %p')}</div>
            </div>
            
            <div class="stats">
                <strong>{len(articles)} viral articles</strong> detected from multiple sources
            </div>
        """
        
        for i, article in enumerate(articles, 1):
            # Generate summary using AI
            summary = self.analyzer.summarize_article(article)
            
            # Determine viral score class
            score_class = "high" if article.viral_score >= 0.7 else "medium"
            
            html += f"""
            <div class="article">
                <div class="article-title">
                    <a href="{article.link}" target="_blank">{article.title}</a>
                </div>
                <div class="article-meta">
                    <span><strong>Source:</strong> {article.source}</span>
                    <span class="viral-score {score_class}">🔥 {article.viral_score:.1f}</span>
                    <span><strong>Published:</strong> {article.published.strftime('%I:%M %p')}</span>
                </div>
                <div class="article-summary">
                    {summary}
                </div>
                <a href="{article.link}" target="_blank" class="read-more">Read Full Article →</a>
            </div>
            """
        
        html += """
            <div class="footer">
                <p>This email was generated by your AI-powered RSS News Agent</p>
                <p>Powered by OpenAI GPT and LangChain</p>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def _generate_text_content(self, articles: List[NewsArticle]) -> str:
        """Generate plain text email content"""
        content = f"🔥 VIRAL NEWS UPDATE - {datetime.now().strftime('%B %d, %Y')}\n"
        content += "=" * 60 + "\n\n"
        content += f"Found {len(articles)} viral articles from multiple sources:\n\n"
        
        for i, article in enumerate(articles, 1):
            summary = self.analyzer.summarize_article(article)
            
            content += f"{i}. {article.title}\n"
            content += f"   Source: {article.source} | Viral Score: {article.viral_score:.1f}/1.0\n"
            content += f"   Published: {article.published.strftime('%I:%M %p')}\n"
            content += f"   Summary: {summary}\n"
            content += f"   Link: {article.link}\n\n"
        
        content += "-" * 60 + "\n"
        content += "This email was generated by your AI-powered RSS News Agent\n"
        content += "Powered by OpenAI GPT and LangChain"
        
        return content
    
    def send_email(self, articles: List[NewsArticle]) -> bool:
        """
        Send viral news email
        
        Args:
            articles: List of viral NewsArticle objects
            
        Returns:
            True if email sent successfully, False otherwise
        """
        if not articles:
            logger.info("No viral articles to send")
            return True
        
        try:
            logger.info(f"Preparing to send email with {len(articles)} viral articles...")
            
            # Create email message
            msg = self.create_news_email(articles)
            
            # Connect to SMTP server and send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_user, self.email_password)
                
                text = msg.as_string()
                server.sendmail(self.email_user, self.to_email, text)
            
            logger.info(f"Successfully sent email with {len(articles)} viral articles to {self.to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False
    
    def test_email_connection(self) -> bool:
        """
        Test email connection and credentials
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_user, self.email_password)
            
            logger.info("Email connection test successful")
            return True
            
        except Exception as e:
            logger.error(f"Email connection test failed: {e}")
            return False