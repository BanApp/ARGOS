import requests
import datetime

url = "http://localhost:19999/api/v1/data?chart=ipv4.udppackets&points=4&after=-4&options=seconds"
response = requests.get(url)
data = response.json()["data"]

received_data = [d[1] for d in data]
print(received_data)
