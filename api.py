# api.py
from flask import Flask, jsonify
import json
import os

CACHE_FILE = os.getenv('CACHE_FILE')

app = Flask(__name__)

@app.route('/api/travel-info', methods=['GET'])
def get_travel_info():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r') as f:
            data = json.load(f)
        return jsonify(data)
    else:
        return jsonify({'error': 'No cached data available'}), 404

if __name__ == '__main__':
    print(os.getenv('PORT'))
    app.run(debug=True, port=os.getenv('PORT'))