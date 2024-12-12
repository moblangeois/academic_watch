import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from ..models.schemas import DailyDigest
import logging
from ..api.openai_client import OpenAIClient
from ..models.schemas import ArticleSummary

class EmailSender:
    def __init__(self, smtp_server: str, smtp_port: int, sender_email: str, sender_password: str, openai_client: OpenAIClient):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.openai_client = openai_client

    def send_digest(self, recipient: str, digest: DailyDigest):
        try:
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = recipient
            msg['Subject'] = f"Academic Watch Digest - {digest.date}"

            # Create HTML content
            html_content = self._create_html_digest(digest)
            msg.attach(MIMEText(html_content, 'html'))

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
        except Exception as e:
            logging.error(f"Email sending error: {str(e)}")
            raise

    def _create_html_digest(self, digest: DailyDigest) -> str:
        if not digest.summaries:
            raise ValueError("The digest does not contain any article summaries.")

        # Generate literature review
        literature_review = self._generate_literature_review(digest)

        summaries_html = "".join(
            f"""
            <div class="article">
                <div class="article-title">
                    <a href="https://doi.org/{summary.doi}" target="_blank">{summary.title}</a>
                </div>
                <div class="article-summary">
                    <ul>
                        {"".join(f"<li>{point}</li>" for point in summary.key_points)}
                    </ul>
                    <ul>
                        {"".join(f"<li>{author}</li>" for author in summary.authors)}
                    </ul>
                    <p><strong>DOI:</strong> {summary.doi}</p>
                    <p><strong>Relevance Score:</strong> {summary.relevance_score}</p>
                    {f"<p><strong>Methodology:</strong> {summary.methodology}</p>" if summary.methodology else ""}
                    {f"<p><strong>Theoretical Framework:</strong> {summary.theoretical_framework}</p>" if summary.theoretical_framework else ""}
                </div>
            </div>
            """ for summary in digest.summaries
        )

        # Parse the JSON and convert markdown to HTML
        import json
        import markdown

        review_data = json.loads(literature_review)
        review_html = markdown.markdown(review_data["review"])

        return f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Daily Digest</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 0;
                    background-color: #f9f9f9;
                    color: #333;
                }}
                .container {{
                    max-width: 600px;
                    margin: 20px auto;
                    background: #ffffff;
                    border: 1px solid #ddd;
                    border-radius: 10px;
                    overflow: hidden;
                    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
                }}
                .header {{
                    background: #4caf50;
                    color: white;
                    padding: 20px;
                    text-align: center;
                    font-size: 24px;
                }}
                .content {{
                    padding: 20px;
                }}
                .article {{
                    margin-bottom: 20px;
                    padding-bottom: 20px;
                    border-bottom: 1px solid #ddd;
                }}
                .article:last-child {{
                    border-bottom: none;
                }}
                .article-title {{
                    font-size: 18px;
                    font-weight: bold;
                    color: #4caf50;
                    margin-bottom: 10px;
                }}
                .article-title a {{
                    color: #4caf50;
                    text-decoration: none;
                }}
                .article-title a:hover {{
                    text-decoration: underline;
                }}
                .article-summary {{
                    font-size: 14px;
                    line-height: 1.5;
                }}
                .footer {{
                    background: #f1f1f1;
                    color: #777;
                    text-align: center;
                    padding: 10px;
                    font-size: 12px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    Academic Watch Digest - {digest.date}
                </div>
                <div class="content">
                    <h2>Revue de la littérature</h2>
                    <div>{review_html}</div>
                    <h2>Résumé des études menées</h2>
                    {summaries_html}
                </div>
                <div class="footer">
                    This email was generated automatically by Academic Watch. For any inquiries, contact us at support@example.com.
                </div>
            </div>
        </body>
        </html>
        """

    def _generate_literature_review(self, digest: DailyDigest) -> str:
        try:
            articles_text = "\n\n".join([self._format_article_text(summary) for summary in digest.summaries])
            review = self.openai_client.generate_literature_review(articles_text)
            return review
        except Exception as e:
            logging.error(f"Error generating literature review: {str(e)}")
            return "Unable to generate literature review."

    def _format_article_text(self, summary: ArticleSummary) -> str:
        return f"""
Title: {summary.title}
DOI: {summary.doi}
Key Points: {', '.join(summary.key_points)}
Relevance Score: {summary.relevance_score}
Methodology: {summary.methodology if summary.methodology else 'N/A'}
Theoretical Framework: {summary.theoretical_framework if summary.theoretical_framework else 'N/A'}
"""
