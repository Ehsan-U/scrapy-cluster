import json
import sys
import sh
from scrapyd_client import ScrapydClient
import os

project = "crawler"
spider = "truepeoplesearch"

if len(sys.argv) == 1:
    os.chdir("project")
    sh.scrapyd_deploy("-a",  _out=sys.stdout, _err=sys.stderr)
    os.chdir("../")

def get_scrapyd_servers():
    ips = []
    output = json.loads(sh.terraform("output", "-json"))
    if output:
        text = ""
        for key, val in output.items():
            ip = val.get("value")
            if isinstance(ip, list):
                for v in ip:
                    ips.append(v)
    return ips

scale = int(sys.argv[-1]) if len(sys.argv) > 1 else 4

servers = get_scrapyd_servers()
for i in range(scale, start=1):
    for server in servers:
        url = f"http://{server}:6800"
        client = ScrapydClient(url=url)
        client.schedule(project, spider)
    print(f"\r [+] Spider instances deployed: {i}",end='')
print("\n", [f"http://{server}:6800/" for server in servers])