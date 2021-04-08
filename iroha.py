import datetime
import json

import bs4
import discord
import requests

async def on_member_join(client1, member):
    """
    いろは鯖に新規が来た時用役職
    user_data_dict[f"{member.id}"][ban]がtrueならキックする"""

    with open("./datas/user_data.json", mode="r") as f:
        user_data_dict = json.load(f)

    try:
        if user_data_dict[f"{member.id}"]["ban"]:
            join_leave_notice_ch = client1.get_channel(709307324170240079)
            await member.guild.kick(member)
            await join_leave_notice_ch.send(f"{member.mention}が{member.guild.name}に参加しようとしましたが失敗しました")
    except KeyError:
        pass


async def on_message(client1, message):
    """
    いろは鯖に関する機能"""

    if message.channel.id == 605401823561383937 and message.author.id == 606668660853178399 and message.embeds:
        msg = message.embeds[0].author.name
        if msg.endswith("joined the server"):
            await iroha_server_login(message)

        if msg.endswith("joined the server for the first time"):
            await iroha_server_first_login(message, msg)


async def iroha_server_first_login(message, msg):
    """
    いろは鯖に初ログインしたときの処理"""

    mcid = msg.split()[0].replace("\\", "")
    await message.channel.send(f"{mcid}さんいろは鯖へようこそ！")
    await iroha_server_login(message, mcid)


async def iroha_server_login(message, mcid=None):
    """
    マイクラいろは鯖のログイン記録に関する機能"""

    if mcid is None:
        mcid = message.embeds[0].author.name.split()[0].replace("\\","")

    uuid = mcid_to_uuid(mcid)
    with open("./datas/login_record.json", mode="r") as f:
        data_dict = json.load(f)
    
    today_login_list = data_dict["today"]
    if uuid in today_login_list:
        pass
    else:
        mcid = mcid.replace("\\", "\_")
        await message.channel.send(f"{mcid}さんおはよー")

        today_login_list.append(uuid)
        total_login = data_dict["total"]
        series_login = data_dict["series"]
        try:
            total_login_days = total_login[uuid]
        except KeyError:
            total_login[uuid] = 1
        else:
            total_login[uuid] = total_login_days + 1
            if total_login[uuid] % 50 == 0:
                await message.channel.send(f"合計ログイン日数{total_login[uuid]}日達成！")

        today = datetime.datetime.today().strftime(r"%Y/%m/%d")
        try:
            series_login_days = series_login[uuid][1]
        except KeyError:
            series_login[uuid] = [today, 1]
        else:
            series_login[uuid] = [today, series_login_days + 1]
            if series_login[uuid][1] % 50 == 0:
                await message.channel.send(f"連続ログイン日数{series_login[uuid][1]}日達成！")

        with open("./datas/login_record.json", mode="w") as f:
            data_json = json.dumps(data_dict, indent=4)
            f.write(data_json)


def mcid_to_uuid(mcid):
    """
    MCIDをUUIDに変換する関数
    uuidを返す"""

    url = f"https://api.mojang.com/users/profiles/minecraft/{mcid}"
    try:
        res = requests.get(url)
        res.raise_for_status()
        sorp = bs4.BeautifulSoup(res.text, "html.parser")
        player_data_dict = json.loads(sorp.decode("utf-8"))
        uuid = player_data_dict["id"]
        return uuid
    except requests.exceptions.HTTPError:
        return None


def uuid_to_mcid(uuid):
    """
    UUIDをMCIDに変換する関数
    mcid(\なし)を返す"""

    url = f"https://sessionserver.mojang.com/session/minecraft/profile/{uuid}"
    try:
        res = requests.get(url)
        res.raise_for_status()
        sorp = bs4.BeautifulSoup(res.text, "html.parser")
        player_data_dict = json.loads(sorp.decode("utf-8"))
        mcid = player_data_dict["name"]
        return mcid
    except requests.exceptions.HTTPError:
        return None


async def delete_login_record():
    """
    連続ログイン記録のための関数
    日付変更時に動き、昨日ログインしてない人のデータを消す"""

    today = datetime.date.today()
    before_yesterday = today - datetime.timedelta(days=2)

    with open("./datas/login_record.json", mode="r") as f:
        data_dict = json.load(f)

    data_dict["today"].clear()

    series_login_dict = data_dict["series"]
    delete_uuid_list = []
    for uuid in series_login_dict:
        last_login = series_login_dict[uuid][0]
        if last_login == before_yesterday.strftime(r"%Y/%m/%d"):
            delete_uuid_list.append(uuid)

    for uuid in delete_uuid_list:
        del data_dict["series"][uuid]

    with open("./datas/login_record.json", mode="w") as f:
        data_json = json.dumps(data_dict, indent=4)
        f.write(data_json)


async def change_login_record(client1):
    send_ch = client1.get_channel(690032563028230150)
    await send_ch.purge()

    with open("./datas/login_record.json", mode="r") as f:
        data_dict = json.load(f)

    total_login_dict = data_dict["total"]
    description = ""
    for key, value in sorted(total_login_dict.items(), key=lambda x: -x[1]):
        mcid = uuid_to_mcid(key)
        for i in range(16-len(mcid)):
            mcid += " "
        description += f"{mcid}: {value}\n"
    description = f"```\n{description}```"
    total_login_embed = discord.Embed(titel="連続ログイン", description=description, color=0x005500)

    series_login_dict = data_dict["series"]
    description = ""
    for key, value in sorted(series_login_dict.items(), key=lambda x: -x[1][1]):
        mcid = uuid_to_mcid(key)
        for i in range(16-len(mcid)):
            mcid += " "
        description += f"{mcid}: {value[1]}\n"
    description = f"```\n{description}```"
    series_login_embed = discord.Embed(tite="通算ログイン", description=description, color=0x005500)

    await send_ch.send(embed=total_login_embed)
    await send_ch.send(embed=series_login_embed)