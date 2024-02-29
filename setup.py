import re
from time import sleep
import sh
import json
import sys


def generate_inventory():
    output = json.loads(sh.terraform("output", "-json"))
    if output:
        text = ""
        for key, val in output.items():
            ip = val.get("value")
            if isinstance(ip, str):
                text += f"[db]\n{ip}"
            elif isinstance(ip, list):
                text += f"\n\n[scrapyd]\n"
                for i in ip:
                    text += f"{i}\n"
        with open("hosts.ini", 'w') as f:
            f.write(text)
        return True
    else:
        return False


def replace_ip_in_file(file_path, old_ip, new_ip):
    with open(file_path, 'r') as file:
        content = file.read()
    new_content = re.sub(old_ip, new_ip, content)
    with open(file_path, 'w') as file:
        file.write(new_content)


def replace_ip_by_regex(file_path, new_ip):
    regex = r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b"  # More accurate IPv4 regex
    replace_ip_in_file(file_path, regex, new_ip)


def update_project(project = "crawler"):
    DB_SERVER = ''
    output = json.loads(sh.terraform("output", "-json"))
    if output:
        text = ""
        for key, val in output.items():
            ip = val.get("value")
            if isinstance(ip, str):
                DB_SERVER = ip
            if isinstance(ip, list):
                text += f"[settings]\ndefault = {project}.settings\n\n"
                for idx, v in enumerate(ip, start=1):
                    text += f"[deploy:scrapy-{idx}]\nurl = http://{v}:6800/\nproject = {project}\n\n"
        with open("project/scrapy.cfg", 'w') as f:
            f.write(text)

    replace_ip_by_regex("project/push.py", DB_SERVER)
    replace_ip_by_regex(f"project/{project}/settings.py", DB_SERVER)


def main():
    args = sys.argv
    if args[-1] == "rm":
        sh.terraform("destroy", "-auto-approve",  _out=sys.stdout, _err=sys.stderr)
    else:
        sh.terraform("apply", "-auto-approve",  _out=sys.stdout, _err=sys.stderr)
        generate_inventory()
        sleep(90)
        sh.ansible_playbook("bootstrap.yml",  _out=sys.stdout, _err=sys.stderr)
        update_project()
        
main()