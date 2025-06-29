from bs4 import BeautifulSoup
import requests
import heapq

# Get both pages
clinic_trials_page = requests.get('https://www.stocktitan.net/news/clinical-trials.html')
clinic_trials_soup = BeautifulSoup(clinic_trials_page.content, 'html.parser')

fda_approvals_page = requests.get('https://www.stocktitan.net/news/fda-approvals.html')
fda_approvals_soup = BeautifulSoup(fda_approvals_page.content, 'html.parser')

def extract_ticker_info(soup):
    results = []
    news_items = soup.find_all('div', class_='news-feed-content small lh-sm col')

    for item in news_items:
        # Find the ticker symbol
        ticker_link = item.find('a', class_='symbol-link notranslate')
        if not ticker_link:
            continue
        ticker = ticker_link.text.strip()

        # Find tags (low float / penny stock)
        tags_div = item.find('div', class_='news-list-tags')
        tag_texts = [span.text.strip().lower() for span in tags_div.find_all('span', class_='badge tag-special')] if tags_div else []

        # Determine presence of tags
        has_penny = 'penny stock' in tag_texts
        has_lowfloat = 'low float' in tag_texts

        # Assign numerical value
        value = 0
        if has_penny and has_lowfloat:
            value = 3
        elif has_lowfloat:
            value = 2
        elif has_penny:
            value = 1

        results.append((ticker, value))

    return results

# Get ticker data from both pages
fda_ticker_info = extract_ticker_info(fda_approvals_soup)
trials_ticker_info = extract_ticker_info(clinic_trials_soup)

'''
# Print results
print("FDA Approvals:")
for ticker, value in fda_ticker_info:
    print(f"{ticker}: {value}")

print("\nClinical Trials:")
for ticker, value in trials_ticker_info:
    print(f"{ticker}: {value}")
'''

# Combine both lists
all_ticker_info = fda_ticker_info + trials_ticker_info

# Priority queue (max-heap): negate score so highest score comes first
priority_queue = [(-score, ticker) for ticker, score in all_ticker_info]
heapq.heapify(priority_queue)

# Process in priority order
print("Sending tickers by priority:")
while priority_queue:
    neg_score, ticker = heapq.heappop(priority_queue)
    score = -neg_score  # Convert back to positive
    print(f"{ticker} (Score: {score})")