# 🔥 RSS Top News Agent

An AI-powered news scraping and email forwarding system that automatically detects viral news from RSS feeds and sends personalized email summaries using GPT and LangChain.

## ✨ Features

- **🤖 AI-Powered Analysis**: Uses OpenAI GPT via LangChain to analyze news articles for viral potential
- **📰 Multi-Source RSS Scraping**: Scrapes multiple RSS feeds for the latest news
- **📧 Beautiful Email Reports**: Sends HTML-formatted email summaries with viral news
- **⏰ Automated Scheduling**: Runs on a configurable schedule to deliver daily news updates
- **🔗 MCP Integration**: Model Context Protocol support for advanced AI agent interactions
- **📊 Viral Scoring**: Smart algorithm to identify trending and shareable content
- **🎨 Responsive Design**: Mobile-friendly email templates with modern styling

## 🚀 Quick Start

### 1. Clone and Setup

```bash
git clone https://github.com/JingyiXXX/rss_top_news_agent.git
cd rss_top_news_agent
chmod +x setup.sh
./setup.sh
```

### 2. Configure Environment

Edit the `.env` file with your credentials:

```env
# OpenAI API Configuration
OPENAI_API_KEY=sk-your-openai-api-key-here

# Email Configuration (Gmail example)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_USER=your-email@gmail.com
EMAIL_PASSWORD=your-app-password-here
TO_EMAIL=recipient@example.com

# RSS Feed URLs (comma-separated)
RSS_FEEDS=https://feeds.reuters.com/reuters/topNews,https://rss.cnn.com/rss/edition.rss,https://feeds.bbci.co.uk/news/rss.xml

# Schedule Configuration
SCHEDULE_HOUR=9
SCHEDULE_MINUTE=0

# News Processing Configuration
MAX_ARTICLES_PER_RUN=10
MIN_VIRAL_SCORE=0.7
```

### 3. Test Configuration

```bash
python main.py --test
```

### 4. Run the Agent

```bash
# Run once for testing
python main.py --run-once

# Start scheduled agent (runs daily)
python main.py --schedule

# View help
python main.py --help
```

## 📋 Requirements

- Python 3.8+
- OpenAI API key
- Email account with app password (Gmail recommended)
- Internet connection for RSS feeds

## 🏗️ Architecture

### Core Components

1. **RSS Scraper** (`rss_agent/scraper.py`)
   - Fetches articles from multiple RSS feeds
   - Extracts full article content
   - Handles duplicate detection and filtering

2. **AI Analyzer** (`rss_agent/analyzer.py`)
   - Uses LangChain + GPT for viral potential analysis
   - Generates article summaries
   - Scores content based on engagement factors

3. **Email Service** (`rss_agent/email_service.py`)
   - Creates beautiful HTML email templates
   - Sends personalized news digests
   - Handles SMTP authentication

4. **MCP Integration** (`rss_agent/mcp_integration.py`)
   - Model Context Protocol support
   - Exposes agent capabilities as tools/resources
   - Enables advanced AI agent interactions

5. **Main Agent** (`rss_agent/agent.py`)
   - Orchestrates the complete pipeline
   - Handles scheduling and error management
   - Provides CLI interface

### Data Flow

```
RSS Feeds → Scraper → AI Analyzer → Email Service → Your Inbox
     ↓         ↓           ↓            ↓
  Articles  Content   Viral Scores  HTML Email
```

## 🎯 Viral Scoring Algorithm

The AI analyzer evaluates articles based on:

- **Emotional Impact**: Content that evokes strong emotions
- **Current Relevance**: Alignment with trending topics
- **Shareability**: Potential for social media engagement
- **Uniqueness**: Novel or exclusive information
- **Public Interest**: Broad appeal and importance

Scores range from 0.0 to 1.0:
- 0.0-0.3: Low viral potential
- 0.4-0.6: Medium viral potential
- 0.7-0.8: High viral potential
- 0.9-1.0: Extremely high viral potential

## 📧 Email Configuration

### Gmail Setup

1. Enable 2-factor authentication
2. Generate an app password:
   - Google Account → Security → App passwords
   - Select app: Mail
   - Copy the generated password

3. Use app password in `.env` file (not your regular password)

### Other Email Providers

Update SMTP settings in `.env`:
- **Outlook**: `smtp-mail.outlook.com:587`
- **Yahoo**: `smtp.mail.yahoo.com:587`
- **Custom SMTP**: Use your provider's settings

## 🔧 Advanced Configuration

### Custom RSS Feeds

Add your preferred news sources to `RSS_FEEDS` in `.env`:

```env
RSS_FEEDS=https://feeds.reuters.com/reuters/topNews,https://rss.cnn.com/rss/edition.rss,https://feeds.bbci.co.uk/news/rss.xml,https://your-custom-feed.com/rss
```

### Scheduling

Modify schedule in `.env`:

```env
SCHEDULE_HOUR=9    # 24-hour format
SCHEDULE_MINUTE=30 # Minutes past the hour
```

### Viral Threshold

Adjust sensitivity:

```env
MIN_VIRAL_SCORE=0.6  # Lower = more articles, Higher = fewer but more viral
```

## 🖥️ Command Line Interface

```bash
# Test all configurations
python main.py --test

# Run pipeline once
python main.py --run-once

# Start scheduled agent
python main.py --schedule

# Start MCP server mode
python main.py --mcp

# View help
python main.py --help
```

## 📊 Logging

The agent creates detailed logs in `rss_news_agent.log`:

- Scraping results
- AI analysis outputs
- Email delivery status
- Error tracking

## 🔗 MCP Integration

The agent supports Model Context Protocol for advanced AI interactions:

### Available Tools
- `scrape_news`: Fetch latest articles
- `analyze_viral_potential`: AI analysis of articles
- `send_viral_news`: Email delivery
- `get_news_summary`: Status and statistics
- `run_full_pipeline`: Complete workflow

### Available Resources
- `news://cached-articles`: Recent articles data
- `news://config`: Agent configuration
- `news://stats`: Performance statistics

## 🛡️ Security Best Practices

- Store API keys in `.env` file (never commit to git)
- Use app passwords for email (not main passwords)
- Regularly rotate API keys
- Monitor usage and costs
- Review RSS feed sources for reliability

## 🐛 Troubleshooting

### Common Issues

1. **OpenAI API Errors**
   - Check API key validity
   - Verify account has credits
   - Monitor rate limits

2. **Email Delivery Issues**
   - Verify SMTP settings
   - Check app password (not regular password)
   - Ensure 2FA is enabled for Gmail

3. **RSS Feed Errors**
   - Test individual feed URLs
   - Check internet connectivity
   - Verify feed format is valid RSS/XML

4. **No Viral Articles Found**
   - Lower `MIN_VIRAL_SCORE` threshold
   - Check RSS feeds have recent content
   - Review AI analysis in logs

### Debug Mode

Run with verbose logging:

```bash
python -c "
import logging
logging.basicConfig(level=logging.DEBUG)
from rss_agent.agent import agent
agent.run_once()
"
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- OpenAI for GPT API
- LangChain for AI framework
- Beautiful email templates inspired by modern design
- RSS feed providers for news content

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review logs in `rss_news_agent.log`
3. Open an issue on GitHub

---

**Built with ❤️ for automated news discovery and delivery**
