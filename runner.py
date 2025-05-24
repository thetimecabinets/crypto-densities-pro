import time
import subprocess

while True:
    print("⏳ Running fetcher.py...")
    try:
        subprocess.run(["python", "fetcher.py"], check=True)
    except Exception as e:
        print(f"⚠️ Error running fetcher: {e}")

    print("✅ Sleeping for 5 minutes...")
    time.sleep(300)  # 300 seconds = 5 minutes
