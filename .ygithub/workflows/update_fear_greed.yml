name: Update Fear & Greed Index

on:
  schedule:
    - cron: '*/5 * * * *'  # Every 5 minutes
  workflow_dispatch:       # Allows manual trigger from GitHub UI

jobs:
  update:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout Repo
      uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install Dependencies
      run: pip install requests

    - name: Run Update Script
      run: python update_fear_greed.py

    - name: Commit and Push
      run: |
        git config user.name "github-actions"
        git config user.email "github-actions@github.com"
        git add historical-fear-greed.json
        git commit -m "Update Fear & Greed history"
        git push
