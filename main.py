from flask import Flask, jsonify
import json
import os

app = Flask(__name__)

@app.route('/')
def index():
    return '✅ Backend is running. Visit /api/walls for live whale wall data.'

@app.route('/api/walls')
def get_walls():
    try:
        with open('walls.json') as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": "Could not load walls", "details": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
