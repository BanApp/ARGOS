import json
import time
import subprocess
from datetime import datetime
from pymongo import MongoClient
client = MongoClient('mongodb://localhost:27017/')
db = client.logs
collection = db.network_flows

def extract_data(data, new_data, prefix):
    if isinstance(data, list):
        for index, item in enumerate(data):
            extract_data(item, new_data, prefix + str(index) + "_")
    elif isinstance(data, dict):
        for key, value in data.items():
            if key in ["source_port", "destination_port"]:
                new_key = key + ' '
            else:
                new_key = prefix + key.replace("'", '"') + "_"
            extract_data(value, new_data, new_key)
    else:
        new_key = prefix[:-1].replace("'", '"')
        new_data[new_key] = data


cnt = 1

while 1:
    command_flow = "hubble observe flows --output=json"
    result = subprocess.run(command_flow, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    ans = result.stdout.decode()
    ans = ans.split("\n")

    for i in ans:
        new_data = {}
        try:
            json_data = json.loads(i)
            extract_data(json_data, new_data, "")
            collection.insert_one(new_data)
        except:
            pass
    print(datetime.now())

    cnt = cnt + 1

    if cnt % 10000 == 0:
        print("cycle is done!")
        cnt = 1
        rm_command = "cp /dev/null nohup.out"
        subprocess.run(rm_command, shell=True)

        try:
            command2 = "hubble status"
            command3 = "cilium hubble port-forward&"
            command4 = "lsof -i :4245"
            output = subprocess.run(command4, shell=True, capture_output=True)
            if 'COMMAND' in str(output.stdout):
                print('port 4245 is already in use')
            else:
                subprocess.run(command2, shell=True)
                subprocess.run(command3, shell=True)
        except:
            break
    time.sleep(8)


