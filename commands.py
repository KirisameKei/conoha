import asyncio
import datetime
import io
import json
import math
import os
import random
import re

import bs4
import discord
import requests
from PIL import Image, ImageDraw, ImageFont
from selenium import webdriver

def role_info(message, role_id):
    """
    実行サーバの役職の情報を取得する関数
    discord.Embedを返す"""

    role = discord.utils.get(message.guild.roles, id=role_id)
    try:
        role_info_embed = discord.Embed(title=role.name, color=role.color)
        if len(role.members) <= 10:
            member = ""
            for mem in role.members:
                member += f"{mem.mention}\n"
            role_info_embed = discord.Embed(title=role.name, description=member, color=role.color)
        else:
            role_info_embed = discord.Embed(title=role.name, description="11人以上いるため省略", color=role.color)
        role_info_embed.add_field(name="人数", value=f"{len(role.members)}", inline=False)
        role_info_embed.add_field(name="色", value=f"{role.color}", inline=False)
        role_made_time = (role.created_at + datetime.timedelta(hours=9)).strftime(r"%Y/%m/%d %H:%M")
        role_info_embed.add_field(name="作成日時", value=f"{role_made_time}　(JST)", inline=False)
        if role.mentionable:
            mention_able = "可"
        else:
            mention_able = "否"
        role_info_embed.add_field(name="メンションの可否", value=mention_able, inline=False)
        role_info_embed.set_footer(text=message.guild.name, icon_url=message.guild.icon_url_as(format="png"))
        return role_info_embed

    except AttributeError:
        error_embed = discord.Embed(title="ERROR", description="ID指定が間違っているかこのサーバにない役職です", color=0xff0000)
        return error_embed


def guild_info(client1, guild_id):
    """
    サーバの情報を取得する関数
    discord.Embedを返す"""
    
    guild = client1.get_guild(guild_id)
    try:
        guild_info_embed = discord.Embed(title=guild.name, color=0xffffff)
        guild_info_embed.set_thumbnail(url=guild.icon_url_as(format="png"))
        guild_info_embed.add_field(name="参加人数", value=f"{len(guild.members)}", inline=True)
        guild_made_time = (guild.created_at + datetime.timedelta(hours=9)).strftime(r"%Y/%m/%d %H:%M")
        guild_info_embed.add_field(name="作成日時", value=f"{guild_made_time}　(JST)", inline=True)
        return guild_info_embed
    except AttributeError:
        error_embed = discord.Embed(title="ERROR", description="ID指定が間違っているか本botの監視下にないサーバです", color=0xff0000)
        return error_embed


async def user_info(client1, user_id):
    """
    ユーザー情報を取得する関数
    discord.Embedを返す"""

    try:
        username = client1.get_user(user_id).name
    except AttributeError:
        bot_know = False
    else:
        bot_know = True

    try:
        user = await client1.fetch_user(user_id)
    except discord.errors.NotFound:
        error_embed = discord.Embed(title="ERROR", description="ID指定が間違っています", color=0xff0000)
        return error_embed

    user_info_embed = discord.Embed(title=user.name, color=0x000000)
    user_info_embed.set_thumbnail(url=user.avatar_url_as(format="png"))
    user_info_embed.add_field(name="botかどうか", value=f"{user.bot}", inline=False)
    user_made_time = (user.created_at + datetime.timedelta(hours=9)).strftime(r"%Y/%m/%d %H:%M")
    user_info_embed.add_field(name="アカウント作成日時", value=f"{user_made_time}　(JST)", inline=False)
    user_info_embed.add_field(name=f"{client1.user.name}の監視下にあるか", value=f"{bot_know}", inline=False)
    return user_info_embed


async def ch_info(client1, ch_id):
    """
    チャンネル情報を取得する関数
    discord.Embedを返す"""

    ch = client1.get_channel(ch_id)
    try:
        ch_name = ch.name
    except AttributeError:
        error_embed = discord.Embed(title="ERROR", description="ID指定が間違っているか本botの監視下にないチャンネルです", color=0xff0000)
        return error_embed

    else:
        ch_info_embed = discord.Embed(title=ch.name, color=0x000000)
        ch_made_time = (ch.created_at + datetime.timedelta(hours=9)).strftime(r"%Y/%m/%d %H:%M")
        ch_info_embed.add_field(name="チャンネル作成日時", value=f"{ch_made_time}　(JST)", inline=False)
        if type(ch) == discord.TextChannel:
            channel_type = "テキストチャンネル"
            if ch.is_nsfw():
                nsfw = "True"
            else:
                nsfw = "False"
            category = ch.category
            if category is None:
                category = "None"
            else:
                category = category.name
            ch_info_embed.add_field(name="NSFW", value=nsfw, inline=False)
            ch_info_embed.add_field(name="所属カテゴリ", value=category, inline=False)
        elif type(ch) == discord.VoiceChannel:
            channel_type = "ボイスチャンネル"
            category = ch.category
            if category is None:
                category = "None"
            else:
                category = category.name
            ch_info_embed.add_field(name="所属カテゴリ", value=category, inline=False)
            ch_info_embed.add_field(name="音声ビットレート", value=f"{ch.bitrate}bit/s", inline=False)
            if ch.user_limit == 0:
                user_limit = "上限なし"
            else:
                user_limit = ch.user_limit
            ch_info_embed.add_field(name="ユーザーリミット", value=ch.user_limit, inline=False)
        elif type(ch) == discord.CategoryChannel:
            channel_type = "カテゴリチャンネル"
            if ch.is_nsfw():
                nsfw = "True"
            else:
                nsfw = "False"
            ch_info_embed.add_field(name="NSFW", value=nsfw, inline=False)
            texts = len(ch.text_channels)
            voices = len(ch.voice_channels)
            ch_info_embed.add_field(name="保有チャンネル数", value=f"テキストチャンネル: {texts}\nボイスチャンネル: {voices}", inline=False)
        else:
            channel_type = "DMチャンネル"
            ch_info_embed.add_field(name="相手", value=ch.recipient.name)
        ch_info_embed.add_field(name="チャンネルタイプ", value=channel_type, inline=False)
        try:
            ch_info_embed.set_footer(text=ch.guild.name, icon_url=ch.guild.icon_url_as(format="png"))
        except AttributeError:
            ch_info_embed.set_footer(text=ch.recipient.name, icon_url=ch.recipient.avatar_url_as(format="png"))
        return ch_info_embed


async def info(client1, message):
    """
    role, guild, user, chの情報を表示する関数"""

    check_list = message.content.split()
    if not len(check_list) == 3:
        await message.channel.send("引数の数が正しくありません\nヒント: `/info␣[role, guild, user, ch]␣ID`")
        return
    check = check_list[1]
    check_id = check_list[2]

    try:
        check_id = int(check_id)
    except ValueError:
        await message.channel.send("IDとして成り立ちません\nヒント: `/info␣[role, guild, user, ch]␣ID`")
        return

    if check == "role":
        info_embed = role_info(message, check_id)
    elif check == "guild":
        info_embed = guild_info(client1, check_id)
    elif check == "user":
        info_embed = await user_info(client1, check_id)
    elif check == "ch":
        info_embed = await ch_info(client1, check_id)
    else:
        await message.channel.send("第二引数の指定が正しくありません\nヒント: `/info␣[role, guild, user, ch]␣ID`")
        return

    await message.channel.send(embed=info_embed)


async def last_login(message):
    """
    第一引数のMCIDが最後に整地鯖にログインした日時を表示する関数"""

    mcid = message.content.split()[1].replace("\\", "")
    p = re.compile(r"^[a-zA-Z0-9_]+$")
    if not p.fullmatch(mcid):
        await message.channel.send("MCIDとして成り立ちません")
        return
    if not (len(mcid) >= 3 and len(mcid) <= 16):
        await message.channel.send("MCIDとして成り立ちません")
        return
    url = f"https://w4.minecraftserver.jp/player/{mcid}"
    try:
        res = requests.get(url)
        res.raise_for_status()
        soup = bs4.BeautifulSoup(res.text, "html.parser")
        if not f"{mcid.lower()}" in f"{soup.td}":
            await message.channel.send("整地鯖にログインしたことがないMCIDです")
            return
        last_login_datetime = str(soup.select("td")[1]).split("\n")[1]
        await message.channel.send(last_login_datetime)
    except requests.exceptions.HTTPError:
        await message.channel.send("現在データ参照元が使用できない状態です。しばらく待ってからもう一度お試しください。")


async def weather(message):
    """
    weatherコマンド対応用関数"""

    if message.content.split()[1] == "map":
        url_date = datetime.date.today().strftime(r"%y%m%d")
        now = datetime.datetime.now().hour
        if now >= 0 and now < 6:
            await message.channel.send("この時間は機能を停止しております(実装がめんどくさいんです許してください)")
            return
        elif now >= 6 and now < 9:
            url_time = "03"
        elif now >= 9 and now < 12:
            url_time = "06"
        elif now >= 12 and now < 15 :
            url_time = "09"
        elif now >= 15 and now < 18:
            url_time = "12"
        elif now >= 18 and now < 21:
            url_time = "15"
        elif now >= 21 and now < 24:
            url_time = "18"

        url = f"https://www.jma.go.jp/jp/g3/images/jp_c/{url_date}{url_time}.png"
        weather_embed = discord.Embed()
        weather_embed.set_image(url=url)
        await message.channel.send(embed=weather_embed)

    else:
        with open("citycodes.json", mode="r", encoding="utf-8") as f:
            citycode = json.load(f)

        try:
            lon_lat_list = citycode[message.content.split()[1]]
        except KeyError:
            cities = ""
            for city in citycode.keys():
                cities += f"{city}、"
            await message.channel.send(f"その地点は登録されていません\n現在登録されている地点:```\n{cities}```")
            return
        key = os.getenv("weather_API_key")

        lon = lon_lat_list[0]
        lat = lon_lat_list[1]

        api = f"http://api.openweathermap.org/data/2.5/onecall?units=metric&lat={lat}&lon={lon}&exclude=minutely,hourly&lang=ja&units=metric&APPID={key}"

        try:
            res = requests.get(api)
            res.raise_for_status()
            sorp = bs4.BeautifulSoup(res.text, "html.parser")
            weather_data_dict = json.loads(sorp.decode("utf-8"))
        except requests.exceptions.HTTPError:
            await message.channel.send("現在データ参照元が使用できない状態です。しばらく待ってからもう一度お試しください。")
            return
        else:
            now = (datetime.datetime.fromtimestamp(weather_data_dict["current"]["dt"])).strftime(r"%Y/%m/%d-%H:%M")
            #────現在の天気によってembedの色を決める────
            if weather_data_dict["current"]["weather"][0]["main"] == "Thunderstorm":
                color = 0xffff00
            elif weather_data_dict["current"]["weather"][0]["main"] == "Drizzle" or weather_data_dict["current"]["weather"][0]["main"] == "Rain":
                color = 0x0000ff
            elif weather_data_dict["current"]["weather"][0]["main"] == "Snow":
                color = 0xfffffe
            elif weather_data_dict["current"]["weather"][0]["main"] == "Clear":
                color = 0xff7700
            elif weather_data_dict["current"]["weather"][0]["main"] == "Atmosphere" or weather_data_dict["current"]["weather"][0]["main"] == "Clouds":
                color = 0x888888
            #────ここまで色決め────
            weather_embed = discord.Embed(title=f"{message.content.split()[1]}の天気概況&予報", description=f"{now}発表", color=color)
            icon = weather_data_dict["current"]["weather"][0]["icon"]
            weather_embed.set_thumbnail(url=f"http://openweathermap.org/img/wn/{icon}@2x.png")
            weather = weather_data_dict["current"]["weather"][0]["description"]
            temp = weather_data_dict["current"]["temp"]
            pressure = weather_data_dict["current"]["pressure"]
            wind_speed = weather_data_dict["current"]["wind_speed"]
            humidity = weather_data_dict["current"]["humidity"]
            text = f"現在の{message.content.split()[1]}の天気は{weather}。\n気温は{temp}℃で気圧は{pressure}hPa、風速は{wind_speed}m/sで湿度は{humidity}%です。"
            try:
                rain = weather_data_dict["current"]["rain"]["1h"]
            except KeyError:
                pass
            else:
                if rain >= 80:
                    strong = "猛烈な"
                elif rain >= 50:
                    strong = "非常に激しい"
                elif rain >= 30:
                    strong = "激しい"
                elif rain >= 20:
                    strong = "強い"
                elif rain >= 10:
                    strong = "やや強い"
                else:
                    strong = ""
                text += f"\n1時間に振った雨の量は{rain}mmで{strong}雨になっています。"
            try:
                snow = weather_data_dict["current"]["snow"]["1h"]
            except KeyError:
                pass
            else:
                text += f"\n積雪量は{snow*10}cmです。"

            sunrise = (datetime.datetime.fromtimestamp(weather_data_dict["current"]["sunrise"])).strftime(r"%H:%M")
            sunset = (datetime.datetime.fromtimestamp(weather_data_dict["current"]["sunset"])).strftime(r"%H:%M")
            text += f"\n\n本日の日の出時刻は{sunrise}、日の入り時刻は{sunset}となっています。"
            weather_embed.add_field(name="現在の天気概況", value=text, inline=False)

            when_list = ["明日", "明後日", "明々後日"]
            for i in range(4):
                if i == 0:
                    pass
                else:
                    weather = ""
                    for wt in weather_data_dict["daily"][i]["weather"]:
                        weather += wt["description"] + ", "
                    max_temp = weather_data_dict["daily"][i]["temp"]["max"]
                    min_temp = weather_data_dict["daily"][i]["temp"]["min"]
                    pressure = weather_data_dict["daily"][i]["pressure"]
                    wind_speed = weather_data_dict["daily"][i]["wind_speed"]
                    humidity = weather_data_dict["daily"][i]["humidity"]
                    pop = math.floor(weather_data_dict["daily"][i]["pop"] * 100)

                    date = (datetime.datetime.fromtimestamp(weather_data_dict["daily"][i]["dt"])).strftime(r"%Y/%m/%d-%H:%M")
                    text = (
                        f"{date}\n"
                        f"天気　　　　: {weather}\n予想最高気温: {max_temp}℃\n予想最低気温: {min_temp}℃\n"
                        f"予想気圧　　: {pressure}hPa\n予想風速　　: {wind_speed}m/s\n予想湿度　　: {humidity}%\n降水確率　　: {pop}%"
                    )
                    try:
                        rain = weather_data_dict["daily"][i]["rain"]
                    except KeyError:
                        pass
                    else:
                        text += f"\n予想降雨量　: {rain}mm"

                    try:
                        snow = weather_data_dict["daily"][i]["snow"]
                    except KeyError:
                        pass
                    else:
                        text += f"\n予想降雪量　: {snow*10}cm"

                    sunrise = (datetime.datetime.fromtimestamp(weather_data_dict["daily"][i]["sunrise"])).strftime(r"%d日%H:%M")
                    sunset = (datetime.datetime.fromtimestamp(weather_data_dict["daily"][i]["sunset"])).strftime(r"%d日%H:%M")
                    text += f"\n\n{when_list[i-1]}の日の出時刻は{sunrise}、日の入り時刻は{sunset}です"

                    weather_embed.add_field(name=f"{when_list[i-1]}の天気予報", value=text, inline=False)
            await message.channel.send(embed=weather_embed)


async def random_name(message):
    """
    nameコマンド対応用関数"""

    try:
        name_length = int(message.content.split()[1])
    except ValueError:
        await message.channel.send("不正な引数です")
        return

    if not (name_length >= 1 and name_length <= 10):
        await message.channel.send("引数の値は1～10の範囲にしてください")
        return

    name_kouho = [
        "あ", "い", "う", "え", "お", "か", "き", "く", "け", "こ", "さ", "し", "す", "せ", "そ",
        "た", "ち", "つ", "て", "と", "な", "に", "ぬ", "ね", "の", "は", "ひ", "ふ", "へ", "ほ",
        "ま", "み", "む", "め", "も", "や", "ゆ", "よ", "ら", "り", "る", "れ", "ろ", "わ", "ゐ", "ゑ", "を", "ん",
        "が", "ぎ", "ぐ", "げ", "ご", "ざ", "じ", "ず", "ぜ", "ぞ", "だ", "ぢ", "づ", "で", "ど",
        "ば", "び", "ぶ", "べ", "ぼ", "ぱ", "ぴ", "ぷ", "ぺ", "ぽ", "ぱ", "ぴ", "ぷ", "ぺ", "ぽ"
    ]

    name = ""
    for i in range(name_length):
        name += random.choice(name_kouho)
    await message.channel.send(name)


async def seichi_break(message):
    """
    breakコマンド対応用関数"""

    mcid = message.content.split()[1].replace("\\", "")
    p = re.compile(r"^[a-zA-Z0-9_]+$")
    if not p.fullmatch(mcid):
        await message.channel.send("MCIDに使用できない文字が含まれています。")
        return
    url = f"https://api.mojang.com/users/profiles/minecraft/{mcid}"
    try:
        res = requests.get(url)
        res.raise_for_status()
        sorp = bs4.BeautifulSoup(res.text, "html.parser")
        try:
            player_data_dict = json.loads(sorp.decode("utf-8"))
        except json.decoder.JSONDecodeError:
            mcid = mcid.replace("_", "\_")
            await message.channel.send(f"{mcid}は存在しません")
            return
        uuid = player_data_dict["id"]
    except requests.exceptions.HTTPError:
        await message.channel.send("現在データ参照元が使用できない状態です。しばらく待ってからもう一度お試しください。")
        return

    uuid_1 = uuid[:8]
    uuid_2 = uuid[8:12]
    uuid_3 = uuid[12:16]
    uuid_4 = uuid[16:20]
    uuid_5 = uuid[20:]
    uuid = f"{uuid_1}-{uuid_2}-{uuid_3}-{uuid_4}-{uuid_5}"
    url = f"https://w4.minecraftserver.jp/api/ranking/player/{uuid}?types=break"

    try:
        res = requests.get(url)
        res.raise_for_status()
        sorp = bs4.BeautifulSoup(res.text, "html.parser")
        player_data_dict = json.loads(sorp.decode("utf-8"))
    except requests.exceptions.HTTPError:
        await message.channel.send("現在データ参照元が使用できない状態です。しばらく待ってからもう一度お試しください。")
        return

    broke = int(player_data_dict[0]["data"]["raw_data"])
    rank = player_data_dict[0]["rank"]
    mc_avatar_url = f"http://avatar.minecraft.jp/{mcid}/minecraft/m.png"
    mc_avatar_url = f"https://minotar.net/armor/body/{mcid}/130.png"

    #────────────ここからコピペ禁止────────────
    if broke < 15:
        level = 1
    elif broke < 49:
        level = 2
    elif broke < 106:
        level = 3
    elif broke < 198:
        level = 4
    elif broke < 333:
        level = 5
    elif broke < 705:
        level = 6
    elif broke < 1265:
        level = 7
    elif broke < 2105:
        level = 8
    elif broke < 9557:#2105～9556までがこのelfi文内に入る
        level = 9
        n = 2015
        while True:
            n += 1242
            if broke < n:
                break
            else:
                level += 1
    elif broke < 11047:
        level = 15
    elif broke < 12835:
        level = 16
    elif broke < 14980:
        level = 17
    elif broke < 17554:
        level = 18
    elif broke < 20642:
        level = 19
    elif broke < 24347:
        level = 20
    elif broke < 28793:
        level = 21
    elif broke < 34128:
        level = 22
    elif broke < 40530:
        level = 23
    elif broke < 48212:
        level = 24
    elif broke < 57430:
        level = 25
    elif broke < 68491:
        level = 26
    elif broke < 81764:
        level = 27
    elif broke < 97691:
        level = 28
    elif broke < 212363:
        level = 29
        n = 97691
        while True:
            n += 19112
            if broke < n:
                break
            else:
                level += 1
    elif broke < 235297:
        level = 35
    elif broke < 262817:
        level = 36
    elif broke < 295891:
        level = 37
    elif broke < 335469:
        level = 38
    elif broke < 383022:
        level = 39
    elif broke < 434379:
        level = 40
    elif broke < 489844:
        level = 41
    elif broke < 549746:
        level = 42
    elif broke < 614440:
        level = 43
    elif broke < 684309:
        level = 44
    elif broke < 759767:
        level = 45
    elif broke < 841261:
        level = 46
    elif broke < 929274:
        level = 47
    elif broke < 1024328:
        level = 48
    elif broke < 1126986:
        level = 49
    elif broke < 1250000:
        level = 50
    elif broke < 2375000:
        level = 51
        n = 1250000
        while True:
            n += 125000
            if broke < n:
                break
            else:
                level += 1
    elif broke < 4125000:
        level = 60
        n = 2375000
        while True:
            n += 175000
            if broke < n:
                break
            else:
                level += 1
    elif broke < 6325000:
        level = 70
        n = 4215000
        while True:
            n += 220000
            if broke < n:
                break
            else:
                level += 1
    elif broke < 9215000:
        level = 80
        n = 6325000
        while True:
            n += 280000
            if broke < n:
                break
            else:
                level += 1
    elif broke < 13165000:
        level = 90
        n = 9215000
        while True:
            n += 360000
            if broke < n:
                break
            else:
                level += 1
    elif broke < 13615000:
        level = 100
    elif broke < 17665000:
        level = 101
        n = 13615000
        while True:
            n += 450000
            if broke < n:
                break
            else:
                level += 1
    elif broke < 22565000:
        level = 110
        n = 13615000
        while True:
            n += 490000
            if broke < n:
                break
            else:
                level += 1
    elif broke < 27965000:
        level = 120
        n = 22565000
        while True:
            n += 540000
            if broke < n:
                break
            else:
                level += 1
    elif broke < 33865000:
        level = 130
        n = 27965000
        while True:
            n += 590000
            if broke <n:
                break
            else:
                level += 1
    elif broke < 40465000:
        level = 140
        n = 33865000
        while True:
            n += 660000
            if broke < n:
                break
            else:
                level += 1
    elif broke < 47865000:
        level = 150
        n = 40465000
        while True:
            n += 740000
            if broke < n:
                break
            else:
                level += 1
    elif broke < 56065000:
        level = 160
        n = 47865000
        while True:
            n += 820000
            if broke < n:
                break
            else:
                level += 1
    elif broke < 65265000:
        level = 170
        n = 56065000
        while True:
            n += 920000
            if broke < n:
                break
            else:
                level += 1
    elif broke < 75265000:
        level = 180
        n = 65265000
        while True:
            n += 1000000
            if broke < n:
                break
            else:
                level += 1
    elif broke < 85615000:
        level = 190
        n = 75265000
        while True:
            n += 1150000
            if broke < n:
                break
            else:
                level += 1
    elif broke < 87115000:
        level = 199
    else:
        level = 200
        star_level,amari = divmod(broke,87115000)
    #────────────ここまでコピペ禁止────────────

    broke = "{:,}".format(broke)
    try:
        embed = discord.Embed(title=f"{mcid}",description=f"整地量：{broke}\n順位：{rank}\nレベル：{level}☆{star_level}")
    except UnboundLocalError:
        embed = discord.Embed(title=f"{mcid}",description=f"整地量：{broke}\n順位：{rank}\nレベル：{level}")

    embed.set_thumbnail(url=mc_avatar_url)
    await message.channel.send(embed=embed)


async def vote(message):
    """
    投票機能"""

    if message.author.bot:
        return

    vote_list = message.content.split()
    if len(vote_list) == 1:
        await message.channel.send("/vote␣投票の題名\nor\n/vote␣投票の題名␣候補1␣候補2␣・・・␣候補n(n≦20)")
        return

    if len(vote_list) > 22:
        await message.channel.send("候補が多すぎます。20個以下にしてください。")
        return

    if len(vote_list) == 2:
        vote_embed = discord.Embed(title=vote_list[1], color=0xfffffe)
        vote_msg = await message.channel.send(embed=vote_embed)
        await vote_msg.add_reaction("⭕")
        await vote_msg.add_reaction("❌")

    else:
        reaction_list = [
            "🇦", "🇧", "🇨", "🇩", "🇪",
            "🇫", "🇬", "🇭", "🇮", "🇯",
            "🇰", "🇱", "🇲", "🇳", "🇴",
            "🇵", "🇶", "🇷", "🇸", "🇹"
        ]

        vote_content = ""
        i = 0
        for msg in vote_list[2:]:
            vote_content += f"{reaction_list[i]}:{msg}\n"
            i += 1
        vote_embed = discord.Embed(title=vote_list[1], description=vote_content, color=0xfffffe)
        vote_msg = await message.channel.send(embed=vote_embed)

        for j in range(i):
            await vote_msg.add_reaction(reaction_list[j])


async def mcavatar(client1, message):
    """
    第一引数のMCIDのマイクラスキンを取得"""

    mcid = message.content.split()[1]
    mcid = mcid.replace("\\_", "_")
    url = f"https://api.mojang.com/users/profiles/minecraft/{mcid}"
    try:
        res = requests.get(url)
        res.raise_for_status()
        sorp = bs4.BeautifulSoup(res.text, "html.parser")
        try:
            mcid_dict = json.loads(sorp.decode("utf-8"))
        except json.decoder.JSONDecodeError:
            await message.channel.send("そのMCIDは存在しません")
            return
    except requests.exceptions.HTTPError:
        await message.channel.send("現在データ参照元が使用できない状態です。しばらく待ってからもう一度お試しください。")
        return

    url = f"https://minotar.net/armor/body/{mcid}/130.png"
    res = requests.get(url)
    image = io.BytesIO(res.content)
    image.seek(0)
    skin = Image.open(image)
    skin.save("skin.png")
    skin = discord.File("skin.png")
    await message.channel.send(file=skin)


async def random_(message):
    """
    pythonのランダムをdis上で再現する"""

    arg = message.content.split()[1]

    if arg == "choice":
        try:
            args = message.content.split()[2:]
        except IndexError:
            await message.channel.send("候補がありません")
            return
        await message.channel.send(random.choice(args))

    elif arg == "sample":
        try:
            sample = int(message.content.split()[2])
        except IndexError:
            await message.channel.send("引数が足りません。ヒント:/random␣sample␣n(n≧1)␣候補")
            return
        except ValueError:
            await message.channel.send("数の指定は正の整数です")
            return
        try:
            args = message.content.split()[3:]
        except IndexError:
            await message.channel.send("候補がありません")
            return
        if len(args) < sample:
            await message.channel.send("候補数よりサンプル数のほうが多いです")
            return
        await message.channel.send(random.sample(args, sample))

    elif arg == "choices":
        try:
            sample = int(message.content.split()[2])
        except IndexError:
            await message.channel.send("引数が足りません。ヒント:/random␣choices␣n(n≧1)␣候補")
            return
        except ValueError:
            await message.channel.send("数の指定は正の整数です")
            return
        try:
            args = message.content.split()[3:]
        except IndexError:
            await message.channel.send("候補がありません")
            return
        if sample <= 0:
            await message.channel.send("サンプル数は正の整数です")
            return
        await message.channel.send(random.choices(args, k=sample))

    elif arg == "randint":
        try:
            start = int(message.content.split()[2])
            end = int(message.content.split()[3])
        except IndexError:
            await message.channel.send("引数が足りません。ヒント:/random␣randint␣min␣max")
            return
        except ValueError:
            await message.channel.send("max, minは整数です")
            return
        if start >= end:
            await message.channel.send("minがmaxと同じか大きいです")
            return
        await message.channel.send(f"{random.randint(start, end)}")

    else:
        await message.channel.send("そんな引数ありません")
