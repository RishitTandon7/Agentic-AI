import argparse
from controller import NegotiationController
from dotenv import load_dotenv

def main():
    load_dotenv()
    
    parser = argparse.ArgumentParser(description="Dual-Agent Negotiation System")
    parser.add_argument("query", type=str, help="Product to search for (e.g. 'smartphone')")
    parser.add_argument("budget", type=float, help="Buyer's max budget")
    parser.add_argument("--sources", nargs="+", default=["amazon", "flipkart"], help="Sources to scrape (default: amazon flipkart)")
    
    args = parser.parse_args()
    
    controller = NegotiationController(args.query, args.budget, args.sources)
    controller.run()

if __name__ == "__main__":
    main()
