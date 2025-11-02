# Backup the original file
import shutil
import os

src = r'c:\Users\lenovo\Desktop\AI sentiment web scraping\backend\scraper.py'
dst = r'c:\Users\lenovo\Desktop\AI sentiment web scraping\backend\scraper.bak.py'

try:
    shutil.copy2(src, dst)
    print(f"Backup created: {dst}")
except Exception as e:
    print(f"Error creating backup: {e}")