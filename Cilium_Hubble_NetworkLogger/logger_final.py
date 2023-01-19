import json
import time
import subprocess
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
            extract_data(value, new_data, prefix + key.replace("'", '"') + "_")
    else:
        new_key = prefix[:-1].replace("'", '"')
        new_data[new_key] = data

cnt = 1

while 1:
    command_flow = "timeout 2s hubble observe flows --output=json > flows.json"
    command_flow_rm = "rm flows.json"
    subprocess.run(command_flow, shell=True)
    with open('flows.json', 'r') as json_file:
        for line in json_file:
            new_data = {}
            json_data = json.loads(line)
            extract_data(json_data, new_data, "")
            #final_data = json.dumps(new_data, ensure_ascii=False)
            collection.insert_one(new_data)
    subprocess.run(command_flow_rm, shell=True)

    cnt = cnt + 1

    if cnt % 300 == 0:
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
    print("Everything is OK!")
    time.sleep(30)


