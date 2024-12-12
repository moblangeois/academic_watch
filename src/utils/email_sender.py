import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from ..models.schemas import DailyDigest
import logging

class EmailSender:
    def __init__(self, smtp_server: str, smtp_port: int, sender_email: str, sender_password: str):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = sender_email
        self.sender_password = sender_password

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

        summaries_html = "".join(
            f"""
            <div class="article">
                <div class="article-title">{summary.title}</div>
                <div class="article-summary">
                    <ul>
                        {"".join(f"<li>{point}</li>" for point in summary.key_points)}
                    </ul>
                    <p><strong>Relevance Score:</strong> {summary.relevance_score}</p>
                    {f"<p><strong>Methodology:</strong> {summary.methodology}</p>" if summary.methodology else ""}
                    {f"<p><strong>Theoretical Framework:</strong> {summary.theoretical_framework}</p>" if summary.theoretical_framework else ""}
                </div>
            </div>
            """ for summary in digest.summaries
        )

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
                    {summaries_html}
                </div>
                <div class="footer">
                    This email was generated automatically by Academic Watch. For any inquiries, contact us at support@example.com.
                </div>
            </div>
        </body>
        </html>
        """
