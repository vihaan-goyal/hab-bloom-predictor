import earthaccess
from dotenv import load_dotenv
import os
load_dotenv()

import earthaccess
earthaccess.login(strategy="environment")

os.makedirs("data/raw", exist_ok=True)

results = earthaccess.search_data(
    short_name="MODISA_L3m_CHL",
    temporal=("2020-07-15", "2020-07-15"),
)

filtered = [r for r in results if "DAY" in str(r['umm']) and "4km" in str(r['umm'])]

print(f"Found {len(filtered)} daily 4km files")

files = earthaccess.download(filtered, "data/raw")
print(f"Downloaded: {files}")