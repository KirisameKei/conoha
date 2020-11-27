import os
import time
import traceback
import subprocess

import requests

os.chdir(os.path.dirname(os.path.abspath(__file__)))

try:
    wh_url = "https://discord.com/api/webhooks/723682595799564378/inZ8Ga6YnkKrPYZCrxtv5OeCZtZGShq8e6HagAnt0Je2vGuN4Wta2Y9GAGY4lGTemYhM"
    content = {
        "username": "Auto Reboot Bot",
        "avatar_url": "https://cdn.discordapp.com/attachments/644880761081561111/723696069388796034/humomari.jpg",
        "content": "10秒後に魔理沙botを再起動してdisbotc.pyの最新版を適用するよ！"
    }
    requests.post(wh_url, content)

    with open("./datas/version.txt", mode="r") as f:
        version = f.read()

    version_list = version.split(".")
    revision_version = int(version_list[2]) + 1
    new_version = f"{version_list[0]}.{version_list[1]}.{revision_version}"

    with open("./datas/version.txt", mode="w") as f:
        f.write(new_version)

    time.sleep(10)

    subprocess.run("sudo systemctl restart disbotc", shell=True)

except:
    wh_url = "https://discord.com/api/webhooks/723682595799564378/inZ8Ga6YnkKrPYZCrxtv5OeCZtZGShq8e6HagAnt0Je2vGuN4Wta2Y9GAGY4lGTemYhM"
    content = {
        "username": "ERROR",
        "avatar_url": "https://cdn.discordapp.com/attachments/644880761081561111/703088291066675261/warning.png",
        "content": traceback.format_exc()
    }
    requests.post(wh_url, content)
