import schedule
import time
import requests

def process_data(data):
    # Your code to process the data goes here
    print(data)

def call_api():
    # Your code to call the API goes here
    response = requests.get("https://example.com/api/data")
    if response.status_code == 200:
        data = response.json()
        process_data(data)
    else:
        print("Error calling API")

# Schedule the task to run every 15 minutes
schedule.every(15).minutes.do(call_api)

# Run the scheduled task indefinitely
while True:
    schedule.run_pending()
    time.sleep(1)