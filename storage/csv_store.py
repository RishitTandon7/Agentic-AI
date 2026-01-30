import csv
import os
from typing import List, Dict, Any

PRODUCTS_FILE = 'data/products.csv'
HISTORY_FILE = 'data/negotiation_history.csv'

class CSVStore:
    def __init__(self):
        self._ensure_files()

    def _ensure_files(self):
        if not os.path.exists('data'):
            os.makedirs('data')
        
        if not os.path.exists(PRODUCTS_FILE):
            with open(PRODUCTS_FILE, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['id', 'query', 'name', 'price', 'source', 'url', 'active', 'timestamp'])

        if not os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['timestamp', 'product_id', 'buyer_offer', 'seller_response', 'status', 'round'])

    def save_products(self, products: List[Dict[str, Any]], query: str):
        # Read existing to handle upsert
        existing = {}
        if os.path.exists(PRODUCTS_FILE):
            with open(PRODUCTS_FILE, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    existing[row['url']] = row

        # Mark products from same query as inactive if not in new list?
        # For now, just upsert.
        
        current_urls = set()
        for p in products:
            p_data = {
                'id': p.get('id') or abs(hash(p['url'])),
                'query': query,
                'name': p['name'],
                'price': p['price'],
                'source': p['source'],
                'url': p['url'],
                'active': 'true',
                'timestamp': p.get('timestamp', '')
            }
            existing[p['url']] = p_data
            current_urls.add(p['url'])

        # Write back
        with open(PRODUCTS_FILE, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['id', 'query', 'name', 'price', 'source', 'url', 'active', 'timestamp']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for url, data in existing.items():
                writer.writerow(data)

    def log_negotiation(self, entry: Dict[str, Any]):
        with open(HISTORY_FILE, 'a', newline='', encoding='utf-8') as f:
            fieldnames = ['timestamp', 'product_id', 'buyer_offer', 'seller_response', 'status', 'round']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writerow(entry)
