from agents.judge_agent import JudgeAgent
import json

def test_judge():
    product = {
        "name": "Dell XPS 15",
        "price": 120000,
        "rating": 4.5,
        "reviews": 120,
        "source": "amazon",
        "url": "https://amazon.in/dp/B0D12345"
    }
    
    judge = JudgeAgent()
    print("Testing JudgeAgent.evaluate...")
    try:
        result = judge.evaluate(product, user_query="dell xps 15 laptop i7", user_budget=150000)
        print("Result:")
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_judge()
