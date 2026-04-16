import os
import feedparser
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
import re

RSS_FEEDS = {
    "Purepeople": "https://www.purepeople.com.br/rss/news.xml",
    "OFuxico": "https://feeds.feedburner.com/ofuxico",
    "Terra": "https://www.terra.com.br/rss/diversao/gente.xml"
}

LIMIT_PER_SOURCE = 5
LIMIT_TOTAL = 20


def clean_html(raw_html):
    clean = re.sub('<.*?>', '', raw_html)
    return clean.strip()


def fetch_news():
    all_news = []

    for source, url in RSS_FEEDS.items():
        feed = feedparser.parse(url)

        count = 0
        for entry in feed.entries:
            if count >= LIMIT_PER_SOURCE:
                break

            summary = entry.get("summary", "")
            summary = clean_html(summary)[:140]

            all_news.append({
                "source": source.upper(),
                "title": entry.title,
                "summary": summary,
                "link": entry.link
            })

            count += 1

    return all_news[:LIMIT_TOTAL]


def format_email(news):
    today = datetime.now().strftime("%d/%m")

    message = f"📰 Pautas do dia — {today}\n\n"

    current_source = None

    for n in news:
        if n["source"] != current_source:
            message += f"{n['source']}\n"
            current_source = n["source"]

        message += f"- {n['title']}\n"

        if n["summary"]:
            message += f"  👉 {n['summary']}\n"

        message += f"  🔗 {n['link']}\n\n"

    return message


def send_email(content):
    sender = os.getenv("EMAIL_USER")
    password = os.getenv("EMAIL_PASS")
    receiver = os.getenv("EMAIL_TO")

    msg = MIMEText(content)
    msg["Subject"] = f"Pautas do dia — {datetime.now().strftime('%d/%m')}"
    msg["From"] = sender
    msg["To"] = receiver

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender, password)
        server.send_message(msg)


def main():
    news = fetch_news()

    if not news:
        send_email("Nenhuma pauta encontrada hoje.")
        return

    content = format_email(news)
    send_email(content)


if __name__ == "__main__":
    main()
