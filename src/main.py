import configparser
import logging
from pathlib import Path
from datetime import datetime, timedelta
import schedule
import time
import os

from api.clarivate_client import ClarivateClient
from api.openai_client import OpenAIClient
from api.ollama_client import OllamaClient
from utils.email_sender import EmailSender
from models.schemas import DailyDigest

class AcademicWatch:
    def __init__(self):
        # Créer les répertoires nécessaires
        self._create_directories()
        self.config = self._load_config()
        self._setup_logging()
        self._setup_clients()

    def _create_directories(self):
        # Créer les répertoires logs et temp s'ils n'existent pas
        base_dir = Path(__file__).parent.parent
        (base_dir / 'logs').mkdir(exist_ok=True)
        (base_dir / 'temp').mkdir(exist_ok=True)
        (base_dir / 'config').mkdir(exist_ok=True)

    def _load_config(self):
        config = configparser.ConfigParser()
        config_path = Path(__file__).parent.parent / 'config' / 'config.ini'
        
        # Si le fichier de configuration n'existe pas, créer un fichier par défaut
        if not config_path.exists():
            self._create_default_config(config_path)
            
        config.read(config_path)
        return config

    def _create_default_config(self, config_path):
        config = configparser.ConfigParser()
        config['API'] = {
            'clarivate_key': 'your_clarivate_key',
            'openai_key': 'your_openai_key'
        }
        config['LLM'] = {
            'provider': 'openai',
            'openai_model': 'gpt-4o-mini',
            'ollama_model': 'phi3.5'
        }
        config['EMAIL'] = {
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': '587',
            'sender_email': 'your-email-here@mail.com',
            'sender_password': 'your-email-password',
            'recipient_email': 'your-email-here@mail.com'
        }
        config['SEARCH'] = {
            'topics': '[\'machine learning\', \'deep learning\']',
            'days_lookback': '1'
        }
        config['SYSTEM'] = {
            'temp_dir': 'temp',
            'log_dir': 'logs'
        }
        
        with open(config_path, 'w') as configfile:
            config.write(configfile)

    def _setup_logging(self):
        log_path = Path(__file__).parent.parent / 'logs' / 'academic_watch.log'
        logging.basicConfig(
            filename=log_path,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def _setup_clients(self):
        self.clarivate = ClarivateClient(self.config['API']['clarivate_key'])
        
        if self.config['LLM']['provider'] == 'openai':
            self.llm = OpenAIClient(
                self.config['API']['openai_key'],
                self.config['LLM']['openai_model']
            )
        else:
            self.llm = OllamaClient(self.config['LLM']['ollama_model'])

        self.email_sender = EmailSender(
            self.config['EMAIL']['smtp_server'],
            int(self.config['EMAIL']['smtp_port']),
            self.config['EMAIL']['sender_email'],
            self.config['EMAIL']['sender_password'],
            self.llm
        )

    def run_daily_digest(self):
        try:
            logging.info("Starting daily digest run")
            
            # Fetch articles
            articles = self.clarivate.fetch_recent_articles(
                eval(self.config['SEARCH']['topics']),  # Convert string to list
                int(self.config['SEARCH']['days_lookback'])
            )
            logging.info(f"Fetched {len(articles)} articles")

            with open('config/ThesisSubject.md', 'r') as file:
                ThesisSubject = file.read()
            logging.info("Thesis subject loaded")

            # Summarize articles
            summaries = []
            for article in articles:
                logging.info(f"Summarizing article: {article.title}")
                summary = self.llm.summarize_article(article, ThesisSubject)
                summaries.append(summary)
                logging.info(f"Article summarized: {summary.title}")

            # Create digest
            digest = DailyDigest(
                date=datetime.now().strftime("%Y-%m-%d"),
                summaries=summaries,
                total_articles=len(articles)
            )
            logging.info("Digest created")

            # Send email
            self.email_sender.send_digest(
                self.config['EMAIL']['recipient_email'],
                digest
            )
            logging.info("Email sent successfully")

        except Exception as e:
            logging.error(f"Error in daily digest: {str(e)}")
            raise

    def run_once(self):
        self.run_daily_digest()

def main():
    watch = AcademicWatch()
    
    if os.getenv('GITHUB_ACTIONS'):
        watch.run_once()
    else:
        # Schedule daily run
        schedule.every().day.at("08:00").do(watch.run_daily_digest)
        
        # Run immediately for testing
        watch.run_daily_digest()
        
        # Keep running
        while True:
            schedule.run_pending()
            time.sleep(60)

if __name__ == "__main__":
    main()