from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import time

def clean_price(p):
    p = p.replace("₹", "").replace(",", "").strip()
    if ".." in p:
        p = p.replace("..", ".")
    return "₹" + p

def main():
    start_time = time.time()

    print("=== Amazon Top 5 Product Finder (Fast) ===\n")

    target = input("Target Acquisition: ").strip()
    specs = input("Specifications: ").strip()
    budget = input("Capital Allocation ₹: ").strip()

    query = f"{target} {specs}"
    search_url = f"https://www.amazon.in/s?k={query.replace(' ', '+')}"

    print(f"\n🔍 Searching Amazon for: {query}\n")

    results = []
    seen = set()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(search_url, timeout=60000)
        page.wait_for_timeout(5000)

        # Scroll to load more items
        page.mouse.wheel(0, 4000)
        page.wait_for_timeout(3000)

        soup = BeautifulSoup(page.content(), "html.parser")

        cards = soup.select("div.s-main-slot div[data-component-type='s-search-result']")

        print(f"Found {len(cards)} search result cards.\n")

        # First pass: get prices from search cards
        fallback_links = []

        for card in cards:
            if len(results) >= 5:
                break

            a = card.select_one("a.a-link-normal.s-no-outline")
            if not a:
                continue

            link = "https://www.amazon.in" + a.get("href").split("?")[0]
            if link in seen:
                continue
            seen.add(link)

            whole = card.select_one("span.a-price-whole")
            frac = card.select_one("span.a-price-fraction")

            if whole:
                price = whole.get_text(strip=True)
                if frac:
                    price += "." + frac.get_text(strip=True)
                results.append((link, clean_price(price)))
            else:
                fallback_links.append(link)

        # Fallback: open product pages only if needed
        for link in fallback_links:
            if len(results) >= 5:
                break
            try:
                page.goto(link, timeout=60000)
                page.wait_for_timeout(2500)
                psoup = BeautifulSoup(page.content(), "html.parser")

                whole = psoup.select_one("span.a-price-whole")
                frac = psoup.select_one("span.a-price-fraction")

                if whole:
                    price = whole.get_text(strip=True)
                    if frac:
                        price += "." + frac.get_text(strip=True)
                    results.append((link, clean_price(price)))
            except Exception:
                continue

        browser.close()

    for i, (link, price) in enumerate(results, 1):
        print(f"{i}. {link}")
        print(f"   👉 Price: {price}\n")

    end_time = time.time()
    print(f"⏱️ Total time taken: {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
    main()
