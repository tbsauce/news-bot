from bs4 import BeautifulSoup
import requests
import os

SEEN_TICKERS_FILE = 'seen_tickers.txt'

def extract_ticker_info(soup):
    results = []
    news_items = soup.find_all('div', class_='news-feed-content small lh-sm col')

    for item in news_items:
        ticker_link = item.find('a', class_='symbol-link notranslate')
        if not ticker_link:
            continue
        ticker = ticker_link.text.strip()

        tags_div = item.find('div', class_='news-list-tags')
        tag_texts = [span.text.strip().lower() for span in tags_div.find_all('span', class_='badge tag-special')] if tags_div else []

        has_penny = 'penny stock' in tag_texts
        has_lowfloat = 'low float' in tag_texts

        value = 0
        if has_penny and has_lowfloat:
            value = 3
        elif has_lowfloat:
            value = 2
        elif has_penny:
            value = 1

        results.append((ticker, value))

    return results

def get_seen_tickers():
    if not os.path.exists(SEEN_TICKERS_FILE):
        return set()
    with open(SEEN_TICKERS_FILE, 'r') as f:
        return set(line.strip() for line in f.readlines())

def save_seen_tickers(tickers):
    with open(SEEN_TICKERS_FILE, 'a') as f:
        for ticker in tickers:
            f.write(f"{ticker}\n")

def get_new_high_priority_tickers():
    # Fetch both pages
    clinic_trials_page = requests.get('https://www.stocktitan.net/news/clinical-trials.html')
    clinic_trials_soup = BeautifulSoup(clinic_trials_page.content, 'html.parser')

    fda_approvals_page = requests.get('https://www.stocktitan.net/news/fda-approvals.html')
    fda_approvals_soup = BeautifulSoup(fda_approvals_page.content, 'html.parser')

    # Extract and combine
    fda_ticker_info = extract_ticker_info(fda_approvals_soup)
    trials_ticker_info = extract_ticker_info(clinic_trials_soup)
    all_ticker_info = fda_ticker_info + trials_ticker_info

    # Filter for score 2 or 3
    high_priority = [ticker for ticker, score in all_ticker_info if score >= 2]

    # Load already seen tickers
    seen = get_seen_tickers()

    # Filter out already seen
    new_tickers = [ticker for ticker in high_priority if ticker not in seen]

    # Save new tickers
    save_seen_tickers(new_tickers)

    return new_tickers

if __name__ == "__main__":
    tickers = get_new_high_priority_tickers()
    print(tickers)  # Example: ["AKHE", "AIWUK"]
