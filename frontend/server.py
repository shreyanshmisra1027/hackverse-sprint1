"""
Simple Flask server to connect frontend to backend pipeline
Run: python server.py (from frontend/ directory)
Then open: http://localhost:5000
"""
import sys
sys.path.insert(0, '../backend')

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import sys
sys.path.insert(0, '../backend')
from pipeline import run_pipeline

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze():
    data = request.json
    stock = data.get('stock', 'NVIDIA')
    profile = data.get('profile', 'Priya')
    sentiment_available = data.get('sentiment_available', True)

    try:
        result = run_pipeline(stock, profile, sentiment_available)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Starting server at http://localhost:5000")
    app.run(debug=True, port=5000)
