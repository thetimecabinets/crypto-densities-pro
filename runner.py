import threading
import time
import subprocess
from main import app  # This imports the Flask app for Zeabur

def run_fetcher():
    while True:
        print("⏳ Running fetcher.py...")
        try:
            subprocess.run(["python", "fetcher.py"], check=True)
        except Exception as e:
            print(f"⚠️ Error running fetcher: {e}")
        print("💤 Sleeping for 5 minutes...")
        time.sleep(300)

# Start background fetch loop
fetcher_thread = threading.Thread(target=run_fetcher)
fetcher_thread.daemon = True
fetcher_thread.start()

# Start Flask API (this keeps the service alive)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
