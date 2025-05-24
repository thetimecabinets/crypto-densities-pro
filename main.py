from flask import Flask, jsonify
import json
import os

# ✅ Import fetcher if needed
import fetcher

app = Flask(__name__)

@app.route('/')
def index():
    return '✅ Backend is running. Visit /api/orders for whale wall data.'

@app.route('/api/orders')
def get_orders():
    with open('data.json') as f:
        data = json.load(f)
    return jsonify(data)

# ✅ Run fetcher once if data.json is empty
def run_fetcher_once():
    if not os.path.exists('data.json'):
        print("🔁 data.json not found. Running fetcher...")
        fetcher.main()
    else:
        with open('data.json') as f:
            try:
                data = json.load(f)
                if len(data) == 0:
                    print("🔁 data.json is empty. Running fetcher...")
                    fetcher.main()
                else:
                    print("✅ data.json has data.")
            except json.JSONDecodeError:
                print("⚠️ data.json is broken. Running fetcher...")
                fetcher.main()

# ✅ Run everything
if __name__ == '__main__':
    run_fetcher_once()
    app.run(debug=True)
