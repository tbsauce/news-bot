import threading
from trading import *
from webscraper import * 


def web_scraper_loop():
    while True:
        symbols = scrape_symbols()
        update_symbol_queue(symbols)
        time.sleep(30)

def symbol_manager_loop():
    while True:
        new_symbols = check_new_symbols()
        for symbol in new_symbols:
            threading.Thread(target=run_symbol_worker, args=(symbol,), daemon=True).start()
        time.sleep(5)

threading.Thread(target=web_scraper_loop, daemon=True).start()
threading.Thread(target=symbol_manager_loop, daemon=True).start()

# Main thread keeps alive
while True:
    time.sleep(60)
