# src/api/clarivate_client.py

from datetime import datetime, timedelta
import logging
import clarivate.wos_starter.client
from clarivate.wos_starter.client.rest import ApiException
from src.models.schemas import Article

# Pour les abstracts
import requests
from bs4 import BeautifulSoup

class ClarivateClient:
    def __init__(self, api_key: str):
        self.configuration = clarivate.wos_starter.client.Configuration(
            host="https://api.clarivate.com/apis/wos-starter/v1"
        )
        self.configuration.api_key['ClarivateApiKeyAuth'] = api_key

    def _build_query(self, topics: list[str], days: int) -> str:
        # Construire la requête pour chaque sujet
        topic_queries = []
        for topic in topics:
            # Convertir le sujet en requête WoS
            topic_query = f'TS=("{topic}")'
            topic_queries.append(topic_query)
        
        # Calculer la date pour les derniers X jours
        date_from = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        
        # Combiner les requêtes avec OR et ajouter le filtre de date
        combined_query = f"({' OR '.join(topic_queries)}) AND PY=2024"
        return combined_query

    def fetch_recent_articles(self, topics: list[str], days: int = 1) -> list[Article]:
        try:
            with clarivate.wos_starter.client.ApiClient(self.configuration) as api_client:
                api_instance = clarivate.wos_starter.client.DocumentsApi(api_client)
                
                # Construire la requête
                q = self._build_query(topics, days)
                logging.info(f"WoS Query: {q}")
                
                # Paramètres de la requête
                params = {
                    'db': 'WOS',
                    'limit': 10,
                    'page': 1,
                    'sort_field': 'LD+D',  # Load Date Descending
                    'detail': 'full'
                }
                
                # Faire la requête
                api_response = api_instance.documents_get(q, **params)
                logging.info(f"Found {len(api_response.hits)} articles")
                
                # Convertir les résultats en objets Article
                articles = []
                for doc in api_response.hits:
                    try:
                        article = Article(
                            title=doc.title if hasattr(doc, 'title') else "",
                            authors=[
                                author.display_name 
                                for author in (doc.names.authors if hasattr(doc.names, 'authors') else [])
                            ] if hasattr(doc, 'names') else [],
                            abstract=ClarivateClient._get_abstract(
                                doc.identifiers.doi if hasattr(doc, 'identifiers') and hasattr(doc.identifiers, 'doi') else None
                            ),
                            doi=doc.identifiers.doi 
                                if hasattr(doc, 'identifiers') and hasattr(doc.identifiers, 'doi') 
                                else None,
                            publication_date=str(doc.source.publish_year) 
                                if hasattr(doc, 'source') and hasattr(doc.source, 'publish_year') 
                                else "",
                            source=doc.source.source_title 
                                if hasattr(doc, 'source') and hasattr(doc.source, 'source_title') 
                                else ""
                        )
                        articles.append(article)
                        logging.info(f"Processed article: {article.title}")
                    except Exception as e:
                        logging.error(f"Error processing article: {str(e)}")
                        continue
                
                return articles

        except ApiException as e:
            logging.error(f"Clarivate API error: {str(e)}")
            raise
        except Exception as e:
            logging.error(f"Unexpected error: {str(e)}")
            raise
    
    def _get_abstract(doi):
        if doi is None:
            return "DOI non trouvé."

        # On essaie d'abord avec l'API Crossref
        base_url = "https://api.crossref.org/works/"
        try:
            response = requests.get(base_url + doi)
            if response.status_code == 200:
                data = response.json()
                abstract = data["message"].get("abstract")
                if abstract:
                    clean_abstract = " ".join(abstract.split())
                    clean_abstract = clean_abstract.replace("<jats:title>", "").replace("</jats:title>", "")
                    clean_abstract = clean_abstract.replace("<jats:italic>", "").replace("</jats:italic>", "")
                    clean_abstract = clean_abstract.replace("<jats:bold>", "").replace("</jats:bold>", "")
                    clean_abstract = clean_abstract.replace("<jats:underline>", "").replace("</jats:underline>", "")
                    clean_abstract = clean_abstract.replace("<jats:sub>", "").replace("</jats:sub>", "")
                    clean_abstract = clean_abstract.replace("<jats:sec>", "").replace("</jats:sec>", "")
                    clean_abstract = clean_abstract.replace("<jats:p>", "").replace("</jats:p>", "")
                    return clean_abstract
        except requests.exceptions.RequestException as e:
            print(f"Erreur lors de la requête à l'API Crossref: {str(e)}")

        # Si l'abstract n'est pas trouvé avec le Crossref API, on essaie avec le PubMed Central API
        base_url = "https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/"
        try:
            response = requests.get(base_url, params={"ids": doi, "format": "json"})
            if response.status_code == 200:
                data = response.json()
                pmc_id = data["records"][0].get("pmcid")
                if pmc_id:
                    article_url = f"https://www.ncbi.nlm.nih.gov/pmc/articles/{pmc_id}/"
                    article_response = requests.get(article_url)
                    if article_response.status_code == 200:
                        soup = BeautifulSoup(article_response.text, "html.parser")
                        abstract_element = soup.find("div", class_="abstract")
                        if abstract_element:
                            abstract_text = abstract_element.get_text(strip=True)
                            return abstract_text
        except requests.exceptions.RequestException as e:
            print(f"Erreur lors de la requête à l'API PubMed Central: {str(e)}")

        return "Abstract not found."