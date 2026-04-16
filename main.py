import os
import feedparser
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
import re

# ==============================
# CONFIG
# ==============================

RSS_FEEDS = {
    # 🇧🇷 Brasil
    "Purepeople": "https://www.purepeople.com.br/rss/news.xml",
    "HugoGloss": "https://hugogloss.uol.com.br/feed/",
    "Terra": "https://www.terra.com.br/rss/diversao/gente.xml",
    "OFuxico": "https://feeds.feedburner.com/ofuxico",
    "Metropoles": "https://www.metropoles.com/entretenimento/feed",
    "UOL": "https://www.uol.com.br/splash/feed/",
    "IG": "https://www.ig.com.br/rss/gente.xml",
    "R7": "https://www.r7.com/rss/entretenimento",
    "F5": "https://feeds.folha.uol.com.br/f5/rss091.xml",
    "Gshow": "https://gshow.globo.com/rss/gshow/",
    "LeoDias": "https://portalleodias.com/feed/",
    "Metropoles 2": "https://www.metropoles.com/ultimas-noticias/feed/",

    # 🌐 Google News (celebridades BR)
    "GoogleNews": "https://news.google.com/rss/search?q=celebridades+brasil&hl=pt-BR&gl=BR&ceid=BR:pt-419",

    # 🇺🇸 EUA
    "TMZ": "https://www.tmz.com/rss.xml",
    "People": "https://people.com/feed/",
    "EOnline": "https://www.eonline.com/syndication/feeds/rssfeeds/topstories.xml",
    "Variety": "https://variety.com/feed/",
    "HollywoodReporter": "https://www.hollywoodreporter.com/feed/",

    # 🇬🇧 UK
    "DailyMail": "https://www.dailymail.co.uk/tvshowbiz/index.rss",
    "TheSun": "https://www.thesun.co.uk/tv/feed/",
    "Mirror": "https://www.mirror.co.uk/3am/rss.xml"
}

LIMIT_PER_SOURCE = 3
LIMIT_TOTAL = 25

# ==============================
# FUNÇÕES
# ==============================

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

            # Melhor lógica de resumo
            content = entry.get("content", [])

            if content:
                summary = content[0].value
            else:
                summary = entry.get("summary", "")

            summary = clean_html(summary)

            if summary:
                summary = summary[:200]
            else:
                summary = "Sem resumo disponível"

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
