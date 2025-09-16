"""
Example usage script for RSS News Agent
"""
import os
import sys

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_sample_env():
    """Create a sample .env file for demonstration"""
    sample_env = """# OpenAI API Configuration
OPENAI_API_KEY=sk-your-openai-api-key-here

# Email Configuration
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
MIN_VIRAL_SCORE=0.7"""
    
    with open('.env.sample', 'w') as f:
        f.write(sample_env)
    print("✓ Created .env.sample file")

def show_usage():
    """Show usage examples"""
    print("""
🔥 RSS News Agent - Usage Examples

1. Setup and Installation:
   ./setup.sh                    # Run setup script
   
2. Configuration:
   cp .env.example .env          # Copy template
   nano .env                     # Edit with your settings
   
3. Testing:
   python main.py --test         # Test configuration
   
4. Running:
   python main.py --run-once     # Run pipeline once
   python main.py --schedule     # Start scheduled agent
   
5. Help:
   python main.py --help         # Show all options

📋 Requirements:
- OpenAI API key (get from https://platform.openai.com/api-keys)
- Email with app password (Gmail recommended)
- RSS feed URLs (news sources)

🔧 Configuration Tips:
- Use app passwords for Gmail (not regular password)
- Lower MIN_VIRAL_SCORE for more articles (0.5-0.6)
- Add custom RSS feeds to RSS_FEEDS
- Adjust schedule with SCHEDULE_HOUR/SCHEDULE_MINUTE

🚀 Quick Start:
1. Get OpenAI API key
2. Setup Gmail app password
3. Run ./setup.sh
4. Edit .env file
5. Test with: python main.py --test
6. Run: python main.py --run-once
""")

if __name__ == "__main__":
    create_sample_env()
    show_usage()