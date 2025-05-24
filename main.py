from flask import Flask, jsonify
import json

app = Flask(__name__)

@app.route("/api/walls")
def get_filtered_walls():
    try:
        with open("walls.json", "r") as file:
            walls = json.load(file)
        
        # Filter: keep only walls ≥ $100k
        filtered = [w for w in walls if w.get("value", 0) >= 100000]

        # Sort: highest wall value first
        filtered.sort(key=lambda w: w["value"], reverse=True)

        return jsonify(filtered)
    
    except Exception as e:
        return jsonify({"error": "Could not load walls", "details": str(e)}), 500

@app.route("/")
def index():
    return "✅ Backend is running. Visit /api/walls for whale wall data."

# Optional for local testing
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
