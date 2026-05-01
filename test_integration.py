import json
from controller import NegotiationController

def test_full_pipeline():
    print("Testing Full Negotiation Pipeline Integration...")
    
    # Sample product
    products = [
        {
            "name": "Dell XPS 13 Laptop - Intel Core i7, 16GB RAM, 512GB SSD",
            "price": 85000,
            "rating": 4.5,
            "reviews": 120,
            "source": "amazon",
            "url": "https://amazon.in/dp/example"
        }
    ]
    
    # Initialize controller
    controller = NegotiationController(
        query="i7 laptop",
        budget=90000,
        sources=["amazon"],
        max_results=1
    )
    
    print("\n[1] Testing Streaming Negotiation...")
    for event in controller.run_negotiation_streaming(products):
        if event['type'] == 'complete':
            print("✅ STREAMING COMPLETE")
            print(f"Final Choice: {event['final_choice']['name']}")
            print(f"Judge Verdict: {event['judge_analysis'].get('verdict')}")
            print(f"Judge Score: {event['judge_analysis'].get('score')}")
            
            # CRITICAL CHECK: Frontend compatibility
            assert 'verdict' in event['judge_analysis']
            assert 'score' in event['judge_analysis']
            assert 'summary' in event['judge_analysis']
            print("✅ FRONTEND KEYS PRESENT")

    print("\n[2] Testing Standard Negotiation...")
    result = controller.run_negotiation(products)
    if result and result['final_choice']:
        analysis = result['final_choice'].get('judge_analysis')
        print(f"✅ STANDARD COMPLETE")
        print(f"Judge Verdict: {analysis.get('verdict')}")
        assert 'verdict' in analysis
        print("✅ FRONTEND KEYS PRESENT")

if __name__ == "__main__":
    test_full_pipeline()
