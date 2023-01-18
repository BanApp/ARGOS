import subprocess
import time

cnt = 1
print("Network flows collecting..")

while True:
    #네트워크 플로우 수집
    command_flow = "timeout 9s hubble observe flows --output=jsonpb | mongoimport --db logs --collection network_flows"

    #네트워크 엔드포인트 수집
    #command_endpoint = "timeout 9s hubble observe endpoints --output=jsonpb | mongoimport --db logs --collection network_endpoints"

    subprocess.run(command_flow, shell=True)
    time.sleep(10)

    cnt = cnt+1

    if cnt % 200 == 0:
        print("cycle: " + str(cnt) + " done!")

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
