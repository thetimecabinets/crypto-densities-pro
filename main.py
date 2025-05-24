from flask import Flask, jsonify
import json

app = Flask(__name__)

@app.route('/')
def index():
    return '✅ Backend is running. Visit /api/orders for whale wall data.'

@app.route('/api/orders')
def get_orders():
    with open('data.json') as f:
        data = json.load(f)
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
