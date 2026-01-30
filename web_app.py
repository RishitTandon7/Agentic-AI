from flask import Flask, request, jsonify, send_file, Response
from controller import NegotiationController
from dotenv import load_dotenv
import os
import sys
import traceback
import json

# Force unbuffered output
sys.stdout.reconfigure(line_buffering=True)

app = Flask(__name__)
load_dotenv()

@app.route('/')
def home():
    return send_file('index.html')

@app.route('/search-page')
def search_page():
    """Simplified search interface with product limit control"""
    return send_file('search.html')

@app.route('/simple')
def simple():
    return send_file('simple_index.html')

@app.route('/negotiate', methods=['POST'])
def negotiate():
    # Legacy endpoint wrapper
    return negotiate_chat() 

@app.route('/search', methods=['POST'])
def search_products_endpoint():
    try:
        # Start AI Warmup PARALLEL to scraping
        from model_warmer import ModelWarmer
        warmer = ModelWarmer()
        warmer.start_check_async()
        
        data = request.json
        query = f"{data.get('specs', '')} {data.get('query', '')}".strip()
        budget = float(data.get('budget', 0))
        sources = data.get('sources', ['amazon', 'flipkart'])
        max_results = int(data.get('max_results', 5))  # User can specify limit (default 5)
        
        controller = NegotiationController(query, budget, sources, max_results)
        products = controller.search_products()
        
        return jsonify({"products": products})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/negotiate_chat', methods=['POST'])
def negotiate_chat_endpoint():
    """DEPRECATED - use /negotiate_stream instead"""
    try:
        data = request.json
        products = data.get('products')
        
        # We need a controller instance, but query/budget don't matter as much for this phase
        # if we pass products directly. However, we'll re-instantiate for clean logic.
        query = data.get('query', '')
        budget = float(data.get('budget', 0))
        sources = []
        
        controller = NegotiationController(query, budget, sources)
        
        # Run negotiation ONLY (products passed from frontend or prev step)
        result = controller.run_negotiation(products)
        
        return jsonify(result)
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/negotiate_stream', methods=['POST'])
def negotiate_stream_endpoint():
    """STREAMING VERSION - sends each round immediately"""
    try:
        data = request.json
        products = data.get('products')
        query = data.get('query', '')
        budget = float(data.get('budget', 0))
        
        def generate():
            """Generator that yields each round as it completes"""
            try:
                controller = NegotiationController(query, budget, [])
                
                # Stream each round
                for event in controller.run_negotiation_streaming(products):
                    # Send Server-Sent Event
                    yield f"data: {json.dumps(event)}\n\n"
                    
            except Exception as e:
                error_event = {
                    "type": "error",
                    "message": str(e)
                }
                yield f"data: {json.dumps(error_event)}\n\n"
        
        return Response(
            generate(),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'X-Accel-Buffering': 'no'
            }
        )
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("Starting AURA Negotiation Server...")
    print("Access at: http://localhost:5001")
    app.run(host='0.0.0.0', port=5001, debug=False)
