import requests
import json
import time

url = "https://api.modrinth.com/v2/search"
offset = 0
limit = 100
HEADERS = {
    "User-Agent": "Linex/ModAgent/1.0 (lynxop33@email.com)",
    "Authorization": "mrp_yourTokenHere"  # only if needed
}
def fetch_data(offset, limit):
    response = requests.get(url, headers=HEADERS, params={"offset": offset, "limit": limit, "facets": '[["project_type:mod"]]'})
    with open("content.json","w") as f:
        json.dump(response.json(),f,indent=4)
        print(f"Fetched {len(response.json())} items at offset {offset}")
        time.sleep(2)  # to avoid hitting rate limits

status = True
while status==False: #for now wont run, but will be used to check if the fetch was successful
    fetch_data(offset, limit)
    offset += limit
    if offset >= 100000:  # stop after fetching 1000 items (adjust as needed)
        print(f"Fetched {offset} items") 
        break

