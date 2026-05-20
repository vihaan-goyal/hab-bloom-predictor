from dotenv import load_dotenv
load_dotenv()

import earthaccess
import os
from datetime import date, timedelta

os.makedirs("data/raw", exist_ok=True)

earthaccess.login(strategy="environment")

def already_downloaded(date_str):
    date_compact = date_str.replace("-", "")
    for f in os.listdir("data/raw"):
        if date_compact in f and f.endswith(".nc"):
            return True
    return False

def download_range(start_date, end_date, reverse=False):
    current = end_date if reverse else start_date
    step = timedelta(days=-1) if reverse else timedelta(days=1)
    
    while (current >= start_date) if reverse else (current <= end_date):
        date_str = current.strftime("%Y-%m-%d")
        
        if already_downloaded(date_str):
            print(f"Skipping {date_str}")
            current += step
            continue
        
        print(f"Searching {date_str}...")
        results = earthaccess.search_data(
            short_name="MODISA_L3m_CHL",
            temporal=(date_str, date_str),
        )
        filtered = [r for r in results if "DAY" in str(r['umm']) and "4km" in str(r['umm'])]
        
        if filtered:
            earthaccess.download(filtered, "data/raw")
            print(f"Downloaded {date_str}")
        else:
            print(f"No data for {date_str}")
        
        current += step
download_range(date(2003, 1, 1), date(2025, 12, 31))