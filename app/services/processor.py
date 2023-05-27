import time
import requests



async def process_data(data):
    # Your code to process the data goes here
    print(data)

async def call_api():
    # Your code to call the API goes here
    response = requests.get("https://example.com/api/data")
    if response.status_code == 200:
        data = response.json()
        await process_data(data)
    else:
        print("Error calling API")

async def sync_roles():
    print("Syncing roles")
    time.sleep(5)
    print("Roles synced")


