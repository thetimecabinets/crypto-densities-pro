import json
from collections import defaultdict
from statistics import mean

INPUT_FILE = "walls.json"
OUTPUT_FILE = "wall-insights.json"

def generate_insights():
    # Load the existing wall data
    with open(INPUT_FILE, "r") as f:
        walls = json.load(f)

    # Prepare a dictionary to collect stats per coin
    summary = defaultdict(lambda: {
        "wall_count": 0,
        "total_value": 0,
        "distances": [],
        "buy_count": 0,
        "sell_count": 0
    })

    # Process each wall
    for wall in walls:
        coin = wall["coin"]
        summary[coin]["wall_count"] += 1
        summary[coin]["total_value"] += wall["value"]
        summary[coin]["distances"].append(abs(float(wall["distance"])))
        if wall["type"] == "buy":
            summary[coin]["buy_count"] += 1
        elif wall["type"] == "sell":
            summary[coin]["sell_count"] += 1

    # Final output
    insights = {}
    for coin, data in summary.items():
        total = data["wall_count"]
        insights[coin] = {
            "wall_count": total,
            "average_value": round(data["total_value"] / total, 2),
            "average_distance": round(mean(data["distances"]), 2),
            "buy_ratio": round(data["buy_count"] / total, 2),
            "sell_ratio": round(data["sell_count"] / total, 2)
        }

    # Write insights to a new file
    with open(OUTPUT_FILE, "w") as f:
        json.dump(insights, f, indent=2)

    print(f"✅ {OUTPUT_FILE} created successfully!")

if __name__ == "__main__":
    generate_insights()
