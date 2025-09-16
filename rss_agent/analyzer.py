"""
AI-powered news analyzer using LangChain and GPT
"""
import logging
from typing import List, Dict
try:
    from langchain_openai import ChatOpenAI
except ImportError:
    from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate, ChatPromptTemplate
from langchain.chains import LLMChain
from langchain.schema import HumanMessage, SystemMessage
from .scraper import NewsArticle
from .config import config

logger = logging.getLogger(__name__)


class NewsAnalyzer:
    """AI-powered news analyzer for determining viral potential"""
    
    def __init__(self):
        """Initialize the news analyzer with LangChain and GPT"""
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            openai_api_key=config.openai_api_key,
            temperature=0.2
        )
        
        # Prompt for viral news analysis
        self.viral_analysis_prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""You are an expert news analyst specializing in identifying viral news content. 
            Analyze news articles and determine their viral potential based on:
            1. Emotional impact and engagement potential
            2. Relevance to current trends and events
            3. Shareability and discussion potential
            4. Uniqueness and novelty
            5. Public interest and importance
            
            Rate the viral potential on a scale of 0.0 to 1.0, where:
            - 0.0-0.3: Low viral potential
            - 0.4-0.6: Medium viral potential  
            - 0.7-0.8: High viral potential
            - 0.9-1.0: Extremely high viral potential
            
            Respond with ONLY a JSON object containing:
            {
                "viral_score": <float>,
                "reasoning": "<brief explanation>",
                "key_points": ["<point1>", "<point2>", "<point3>"]
            }"""),
            HumanMessage(content="""
            Title: {title}
            Source: {source}
            Description: {description}
            Content Preview: {content_preview}
            """)
        ])
        
        # Prompt for news summarization
        self.summary_prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""You are a professional news summarizer. Create concise, engaging summaries of news articles that:
            1. Capture the key facts and main points
            2. Maintain objectivity and accuracy
            3. Are easy to read and understand
            4. Highlight why the news is important or interesting
            
            Keep summaries to 2-3 sentences maximum."""),
            HumanMessage(content="""
            Title: {title}
            Source: {source}
            Description: {description}
            Content: {content}
            """)
        ])
    
    def analyze_viral_potential(self, article: NewsArticle) -> Dict:
        """
        Analyze the viral potential of a news article
        
        Args:
            article: NewsArticle object to analyze
            
        Returns:
            Dictionary with viral score and analysis
        """
        try:
            # Prepare content preview
            content_preview = article.content[:500] if article.content else article.description
            
            # Create the analysis chain
            chain = LLMChain(llm=self.llm, prompt=self.viral_analysis_prompt)
            
            # Run the analysis
            result = chain.run(
                title=article.title,
                source=article.source,
                description=article.description,
                content_preview=content_preview
            )
            
            # Parse the JSON response
            import json
            try:
                analysis = json.loads(result.strip())
                return analysis
            except json.JSONDecodeError:
                # Fallback parsing if JSON is malformed
                logger.warning(f"Failed to parse JSON response for article: {article.title}")
                return {
                    "viral_score": 0.5,
                    "reasoning": "Analysis parsing failed",
                    "key_points": ["Unable to analyze properly"]
                }
                
        except Exception as e:
            logger.error(f"Error analyzing viral potential for article '{article.title}': {e}")
            return {
                "viral_score": 0.0,
                "reasoning": f"Analysis failed: {str(e)}",
                "key_points": ["Error occurred during analysis"]
            }
    
    def summarize_article(self, article: NewsArticle) -> str:
        """
        Create a concise summary of the news article
        
        Args:
            article: NewsArticle object to summarize
            
        Returns:
            Article summary string
        """
        try:
            chain = LLMChain(llm=self.llm, prompt=self.summary_prompt)
            
            summary = chain.run(
                title=article.title,
                source=article.source,
                description=article.description,
                content=article.content or article.description
            )
            
            return summary.strip()
            
        except Exception as e:
            logger.error(f"Error summarizing article '{article.title}': {e}")
            return article.description
    
    def analyze_articles(self, articles: List[NewsArticle]) -> List[NewsArticle]:
        """
        Analyze a list of articles for viral potential and update them
        
        Args:
            articles: List of NewsArticle objects
            
        Returns:
            List of NewsArticle objects with updated viral scores
        """
        logger.info(f"Analyzing {len(articles)} articles for viral potential...")
        
        analyzed_articles = []
        
        for article in articles:
            try:
                # Analyze viral potential
                analysis = self.analyze_viral_potential(article)
                article.viral_score = analysis.get("viral_score", 0.0)
                
                # Store analysis results as additional attributes
                article.analysis_reasoning = analysis.get("reasoning", "")
                article.key_points = analysis.get("key_points", [])
                
                analyzed_articles.append(article)
                
                logger.debug(f"Article '{article.title}' - Viral Score: {article.viral_score}")
                
            except Exception as e:
                logger.error(f"Error analyzing article '{article.title}': {e}")
                # Keep article with default score
                article.viral_score = 0.0
                analyzed_articles.append(article)
        
        # Sort by viral score (highest first)
        analyzed_articles.sort(key=lambda x: x.viral_score, reverse=True)
        
        logger.info(f"Analysis complete. Top viral score: {analyzed_articles[0].viral_score if analyzed_articles else 0}")
        
        return analyzed_articles
    
    def filter_viral_articles(self, articles: List[NewsArticle], min_score: float = None) -> List[NewsArticle]:
        """
        Filter articles based on minimum viral score
        
        Args:
            articles: List of analyzed NewsArticle objects
            min_score: Minimum viral score threshold (uses config default if None)
            
        Returns:
            Filtered list of viral articles
        """
        if min_score is None:
            min_score = config.min_viral_score
        
        viral_articles = [article for article in articles if article.viral_score >= min_score]
        
        logger.info(f"Filtered {len(viral_articles)} viral articles from {len(articles)} total (min_score: {min_score})")
        
        return viral_articles