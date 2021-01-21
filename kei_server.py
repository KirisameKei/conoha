import asyncio
import datetime
import json
import math
import os
import random
import re
import shutil
import string

import bs4
import discord
import mojimoji
import requests

async def on_member_join(client1, member):
    """
    けい鯖に新規メンバーが来た時用の関数
    以前に入っていたかを検知し入っていなければ初期データを設定する
    新規役職を付与する"""

    with open("./datas/user_data.json", mode="r") as f:
        user_data_dict = json.load(f)

    try:
        user_data = user_data_dict[f"{member.id}"]
    except KeyError:
        user_data_dict[f"{member.id}"] = {"ban": False, "role": [], "mcid": [], "point": 0, "speak": 0}
        with open("./datas/user_data.json", mode="w") as f:
            user_data_json = json.dumps(user_data_dict, indent=4)
            f.write(user_data_json)
    else:
        join_leave_notice_ch = client1.get_channel(709307324170240079)
        if user_data["ban"]:
            await member.guild.kick(member)
            await join_leave_notice_ch.send(f"{member.mention}が{member.guild.name}に参加しようとしましたが失敗しました")
            return

        if not len(user_data["role"]) == 0:
            role_name = ""
            for role_id in user_data["role"]:
                role = discord.utils.get(member.guild.roles, id=role_id)
                await member.add_roles(role)
                role_name += f"{role.name}, "

            await join_leave_notice_ch.send(f"{member.name}さんは過去に以下の役職を保有していたため付与しました```\n{role_name}```")

    new_role = discord.utils.get(member.guild.roles, id=621641465105481738)
    await member.add_roles(new_role)

    infomation_ch = client1.get_channel(588224929300742154)
    info_embed = discord.Embed(title=f"🎉{member.name}さんようこそ{member.guild.name}へ！🎉", color=0xffff00)
    info_embed.add_field(name="はじめに", value="<#586000955053441039>をお読みください\n大体の流れはそこに書いてあります。(botでも誘導します)", inline=False)
    info_embed.add_field(name="MCIDの報告", value="<#640833025822949387>でMCIDを報告してください\n\
複数のMCIDを持っている方はスペース区切り、または改行区切りで同時に登録ができます。\n\
JE版整地鯖にログインしたことのない方は<@523303776120209408>のDMまで、個別に対応します", inline=False)
    info_embed.add_field(name="ルールへの同意", value="「はじめに」にあるルールに同意していただけるなら<#592581835343659030>で\
**/accept**を実行してください。新規役職が外れます", inline=False)
    info_embed.add_field(name="最後に", value="お楽しみください", inline=False)
    await infomation_ch.send(content=f"{member.mention}", embed=info_embed)


async def on_member_remove(client1, member):
    """
    けい鯖で脱退イベントが発生した時用の関数"""

    with open("./datas/user_data.json", mode="r") as f:
        user_data_dict = json.load(f)

    try:
        user_data_dict[f"{member.id}"]["mcid"] = []
        user_data_dict[f"{member.id}"]["point"] = 0
        user_data_dict[f"{member.id}"]["speak"] = 0
    except KeyError:
        user_data_dict[f"{member.id}"] = {"ban": False, "role": [], "mcid": [], "point": 0, "speak": 0}

    with open("./datas/user_data.json", mode="w") as f:
        user_data_json = json.dumps(user_data_dict, indent=4)
        f.write(user_data_json)


async def on_member_update(before, after):
    if before.roles != after.roles:
        leave_role_list = [
            586009049259311105, #実験台
            628175600007512066, #発言禁止
            586000652464029697, #警告2
            586000502635102209, #警告1
            676414213517737995, #警備員
            707570554462273537, #bot停止権
            630778781963124786, #デバッガー
            586418283780112385, #int
            671524901655543858, #狩人
            674093583669788684, #侵入者
            616212704818102275, #ドM
        ]
        with open("./datas/user_data.json", mode="r") as f:
            user_data_dict = json.load(f)
        try:
            role_id_list = user_data_dict[f"{before.id}"]["role"]
        except KeyError:
            user_data_dict[f"{before.id}"] = {"ban": False, "role": [], "mcid": [], "point": 0, "speak": 0}
            role_id_list = user_data_dict[f"{before.id}"]["role"]
        role_id_list.clear()

        for role in after.roles:
            if role.id in leave_role_list:
                role_id_list.append(role.id)

        with open("./datas/user_data.json", mode="w") as f:
            user_data_json = json.dumps(user_data_dict, indent=4)
            f.write(user_data_json)


async def on_message(client1, message):
    """
    けい鯖にメッセージが投稿された時用の関数"""

    if not message.author.bot:
        await count_message(message)

    if message.channel.id == 640833025822949387:
        await mcid(client1, message)

    if message.channel.id == 634602609017225225:
        await login_bonus(message)

    if message.channel.id == 665487669953953804:
        await kikaku(message)

    if message.content.startswith("/pt "):
        await edit_pt(message)

    if message.content.startswith("/ban "):
        await before_ban(client1, message)

    if message.content.startswith("/unban "):
        await unban(client1, message)

    if message.content == "/mypt":
        await mypt(message)

    if message.content.startswith("/mcid"):
        await edit_mcid(message)

    if message.content.startswith("/user_data"):
        await user_data(client1, message)

    if message.content.startswith("/ranking "):
        await ranking(client1, message)

    if message.channel.id == 762546731417731073:
        await story(message)

    if message.channel.id == 762546959138816070:
        await story_secret(message)

    if message.channel.id == 770163289006800927:
        await kazuate(message)

    if message.content == "/marichan_invite":
        await marichan_invite(message)

    if message.content == "/accept":
        await accept(message)

    if message.content == "/version":
        await version(message)

    if message.content == "/datas":
        await send_zip_data(message)

    if message.content == "/ban_list":
        await ban_list(message, client1)

    if message.content == "/gban_list":
        await gban_list(message, client1)

    if message.content.startswith("/leave_guild "):
        await leave_guild(message, client1)

    if message.content.startswith("/global_notice "):
        await global_notice(client1, message)

    #if message.content == "/issue":
    #    await issue_id(message)

    if message.channel.id == 722810355511984185:
        await create_new_func(client1, message)


async def count_message(message):
    """
    投稿されたメッセージ数を数える"""

    with open("./datas/count_message.json", mode="r") as f:
        counter_dict = json.load(f)

    today = datetime.date.today().strftime(r"%Y%m%d")
    try:
        counter_dict[today] += 1
    except KeyError:
        counter_dict[today] = 1

    with open("./datas/count_message.json", mode="w") as f:
        counter_json = json.dumps(counter_dict, indent=4)
        f.write(counter_json)

    if message.channel.id in (586075792950296576, 770163289006800927, 691901316133290035): #スパム許可、数当て、ミニゲームなら
        return

    with open("./datas/user_data.json", mode="r") as f:
        user_data_dict = json.load(f)

    try:
        user_data_dict[f"{message.author.id}"]["speak"] += 1
    except KeyError:
        user_data_dict[f"{message.author.id}"]["speak"] = 1

    regular_member_1_role = discord.utils.get(message.guild.roles, id=641454086310461478)
    regular_member_2_role = discord.utils.get(message.guild.roles, id=726246561100857345)
    regular_member_3_role = discord.utils.get(message.guild.roles, id=726246637185531904)
    now = datetime.datetime.now()
    joined_time = message.author.joined_at + datetime.timedelta(hours=9)

    if regular_member_3_role in message.author.roles:
        pass
    elif regular_member_2_role in message.author.roles:
        if user_data_dict[f"{message.author.id}"]["speak"] >= 3000 and joined_time + datetime.timedelta(days=365) <= now:
            await message.author.add_roles(regular_member_3_role)
            await message.author.remove_roles(regular_member_2_role)
    elif regular_member_1_role in message.author.roles:
        if user_data_dict[f"{message.author.id}"]["speak"] >= 2000 and joined_time + datetime.timedelta(days=182, hours=12) <= now:
            await message.author.add_roles(regular_member_2_role)
            await message.author.remove_roles(regular_member_1_role)
    else:
        if user_data_dict[f"{message.author.id}"]["speak"] >= 1000:
            await message.author.add_roles(regular_member_1_role)

    with open("./datas/user_data.json", mode="w") as f:
        user_data_json = json.dumps(user_data_dict, indent=4)
        f.write(user_data_json)


async def login_bonus(message):
    """
    ログボ"""

    if message.author.bot:
        return

    msg = mojimoji.han_to_zen(mojimoji.zen_to_han(message.content, kana=False), ascii=False) #全角英字を半角に、半角カタカナを全角に
    msg = msg.lower()
    msg = msg.replace("　", "").replace(" ", "").replace("\n", "").replace("゛", "").replace("っ", "").replace("ッ", "").replace("-", "").replace("ー", "")
    msg = msg.replace("ma", "ま").replace("ri", "り").replace("sa", "さ")
    msg = msg.replace("マ", "ま").replace("リ", "り").replace("サ", "さ")
    msg = msg.replace("chan", "ちゃん").replace("tyan", "ちゃん").replace("tan", "たん")
    msg = msg.replace("チ", "ち").replace("ャ", "ゃ").replace("タ", "た").replace("ン", "ん")
    NG_word_list = [
        "魔理",
        "まりさ",
        "まりちゃん",
        "まりたん",
    ]
    for NG_word in NG_word_list:
        if NG_word in msg:
            await message.channel.send("強制はずれ")
            return

    with open("./datas/word.json", mode="r", encoding="utf-8") as f:
        word_dict = json.load(f)

    flag = False
    for key in word_dict.keys():
        if key in message.content:
            get_pt = word_dict[key]
            touraku = f"指定ワードを引きました！: {key}"
            flag = True
            break

    if flag:
        del word_dict[key]
        with open("./datas/word.json", mode="w", encoding="utf-8") as f:
            word_json = json.dumps(word_dict, indent=4, ensure_ascii=False)
            f.write(word_json)

    else:
        kouho_list = ["おめでとう！", "はずれ", "はずれ"]
        touraku = random.choice(kouho_list)
        if touraku == "はずれ":
            await message.channel.send(touraku)
            return

        get_pt = random.randint(1,32)

    with open("./datas/user_data.json", mode="r") as f:
        user_data_dict = json.load(f)
    
    try:
        had_pt = user_data_dict[f"{message.author.id}"]["point"]
    except KeyError:
        user_data_dict[f"{message.author.id}"] = {"ban": False, "role": [], "mcid": [], "point": 0, "speak": 0}
        had_pt = user_data_dict[f"{message.author.id}"]["point"]

    after_pt = had_pt + get_pt
    if after_pt < 0:
        after_pt = 0

    user_data_dict[f"{message.author.id}"]["point"] = after_pt
    with open("./datas/user_data.json", mode="w") as f:
        user_data_json = json.dumps(user_data_dict, indent=4)
        f.write(user_data_json)

    await message.channel.send(f"{touraku}\n{get_pt}ptゲット！\n{message.author.name}の保有pt: {had_pt}→{after_pt}")


async def add_pt(message, user_id, pt):
    """
    user_idにpt付与"""

    member = message.guild.get_member(user_id)
    try:
        user_name = member.name
    except AttributeError:
        await message.channel.send("そんな人この鯖にいません")
        return

    with open("./datas/user_data.json", mode="r") as f:
        user_data_dict = json.load(f)

    try:
        had_pt = user_data_dict[f"{member.id}"]["point"]
    except KeyError:
        user_data_dict[f"{member.id}"] = {"ban": False, "role": [], "mcid": [], "point": 0, "speak": 0}
        had_pt = user_data_dict[f"{member.id}"]["point"]

    user_data_dict[f"{member.id}"]["point"] = had_pt + pt
    with open("./datas/user_data.json", mode="w") as f:
        user_data_json = json.dumps(user_data_dict, indent=4)
        f.write(user_data_json)

    await message.channel.send(f"{member.name}の保有pt: {had_pt}→{had_pt+pt}")


async def use_pt(message, user_id, pt):
    """
    user_idからpt剥奪"""

    member = message.guild.get_member(user_id)
    try:
        user_name = member.name
    except AttributeError:
        await message.channel.send("そんな人この鯖にいません")
        return

    with open("./datas/user_data.json", mode="r") as f:
        user_data_dict = json.load(f)

    try:
        had_pt = user_data_dict[f"{member.id}"]["point"]
    except KeyError:
        user_data_dict[f"{member.id}"] = {"ban": False, "role": [], "mcid": [], "point": 0, "speak": 0}
        had_pt = user_data_dict[f"{message.author.id}"]["point"]

    if (had_pt-pt) < 0:
        await message.channel.send(f"ptが足りません\n{member.name}の保有pt: {had_pt}")
        return

    user_data_dict[f"{member.id}"]["point"] = had_pt - pt
    with open("./datas/user_data.json", mode="w") as f:
        user_data_json = json.dumps(user_data_dict, indent=4)
        f.write(user_data_json)

    await message.channel.send(f"{member.name}の保有pt: {had_pt}→{had_pt-pt}")


async def set_pt(message, user_id, pt):
    """
    第一引数のユーザーのptを第二引数ptにする"""

    member = message.guild.get_member(user_id)
    try:
        user_name = member.name
    except AttributeError:
        await message.channel.send("そんな人この鯖にいません")
        return

    with open("./datas/user_data.json", mode="r") as f:
        user_data_dict = json.load(f)

    try:
        had_pt = user_data_dict[f"{member.id}"]["point"]
    except KeyError:
        user_data_dict[f"{member.id}"] = {"ban": False, "role": [], "mcid": [], "point": 0, "speak": 0}
        had_pt = user_data_dict[f"{member.id}"]["point"]

    user_data_dict[f"{member.id}"]["point"] = pt
    with open("./datas/user_data.json", mode="w") as f:
        user_data_json = json.dumps(user_data_dict, indent=4)
        f.write(user_data_json)

    await message.channel.send(f"{member.name}の保有pt: {had_pt}→{pt}")


async def crd_pt(message, user_id):
    """
    第一引数のユーザーに通常と同じ確率・範囲でptを付与"""

    if not message.author.id == 523303776120209408:
        await message.channel.send("何様のつもり？")
        return

    member = message.guild.get_member(user_id)
    try:
        user_name = member.name
    except AttributeError:
        await message.channel.send("そんな人この鯖にいません")
        return

    kouho_list = ["おめでとう！", "はずれ", "はずれ"]
    touraku = random.choice(kouho_list)
    if touraku == "はずれ":
        await message.channel.send(f"{user_name}への補填結果: {touraku}")
        return

    get_pt = random.randint(1,32)
    
    with open("./datas/user_data.json", mode="r") as f:
        user_data_dict = json.load(f)
    
    try:
        had_pt = user_data_dict[f"{member.id}"]["point"]
    except KeyError:
        user_data_dict[f"{member.id}"] = {"ban": False, "role": [], "mcid": [], "point": 0, "speak": 0}
        had_pt = user_data_dict[f"{member.id}"]["point"]

    user_data_dict[f"{member.id}"]["point"] = had_pt + get_pt
    with open("./datas/user_data.json", mode="w") as f:
        user_data_json = json.dumps(user_data_dict, indent=4)
        f.write(user_data_json)
    
    await message.channel.send(f"{user_name}への補填結果: {touraku}{get_pt}ptゲット！\n{user_name}の保有pt: {had_pt}→{had_pt+get_pt}")


async def sum_pt(message):
    """
    現在のptの合計を求める関数"""

    with open("./datas/user_data.json", mode="r") as f:
        user_data_dict = json.load(f)

    pt = 0
    for user_data in user_data_dict.values():
        pt += user_data["point"]

    lc, amari = divmod(pt, 3456)
    st, ko = divmod(amari, 64)

    await message.channel.send(f"合計{pt}pt({lc}LC+{st}st+{ko})")


async def edit_pt(message):
    """
    第一引数：操作(付与、剥奪、セット、補償、合計算出)
    第二引数：対象のID(sumでは不要)
    第三引数(crd、sumでは不要)：pt"""

    if not message.author.id == 523303776120209408:
        await message.channel.send("何様のつもり？")
        return

    operation = message.content.split()[1]
    if operation == "sum":
        await sum_pt(message)
        return

    try:
        user_id = int(message.content.split()[2])
    except IndexError:
        await message.channel.send("引数が足りません\nヒント：/pt␣[add, use, set, crd, sum]␣ID␣(n(n≧0))")
        return
    except ValueError:
        await message.channel.send("ユーザーIDは半角数字です")
        return

    if operation == "crd":
        await crd_pt(message, user_id)
        return

    try:
        pt = int(message.content.split()[3])
    except IndexError:
        await message.channel.send("引数が足りません\nヒント：/pt␣[add, use, set, crd, sum]␣ID␣(n(n≧0))")
        return
    except ValueError:
        await message.channel.send("引数が不正です\nヒント：/pt␣[add, use, set, crd, sum]␣ID␣(n(n≧0))")
        return

    if operation == "add":
        await add_pt(message, user_id ,pt)
    elif operation == "use":
        await use_pt(message, user_id, pt)
    elif operation == "set":
        await set_pt(message, user_id, pt)
    else:
        await message.channel.send("引数が不正です\nヒント：`/pt␣[add, use, set, crd, sum]␣ID␣(n(n≧0))`")
        return


async def before_ban(client1, message):
    """
    第一引数のIDを持つユーザーを事前BANする関数"""

    if not message.author.id == 523303776120209408:
        await message.channel.send("何様のつもり？")
        return

    try:
        user_id = int(message.content.split()[1])
    except ValueError:
        await message.channel.send("不正な引数です")
        return

    try:
        baned_user = await client1.fetch_user(user_id)
    except discord.errors.NotFound:
        await message.channel.send("IDが間違っています")
        return

    with open("./datas/user_data.json", mode="r") as f:
        user_data_dict = json.load(f)

    try:
        user_data = user_data_dict[f"{user_id}"]
        if user_data["ban"]:
            await message.channel.send(f"{baned_user.name}は既にBANされています")
            return
    except KeyError:
        pass

    user_info_embed = discord.Embed(title="以下のユーザーを事前BANしますか？", description="はい(BANする): 👍\nいいえ(ミス): 👎", color=0x000000)
    user_info_embed.set_thumbnail(url=baned_user.avatar_url)
    user_info_embed.add_field(name=".", value=baned_user.name)
    msg = await message.channel.send(embed=user_info_embed)
    await msg.add_reaction("👍")
    await msg.add_reaction("👎")
    def check(reaction, user):
        return user == message.author and (str(reaction.emoji) == "👍" or str(reaction.emoji) == "👎")
    try:
        reaction, user = await client1.wait_for("reaction_add", check=check, timeout=60)
    except asyncio.TimeoutError:
        await message.channel.send("タイムアウトしました。最初からやり直してください")
        return

    else:
        if str(reaction.emoji) == "👎":
            await message.channel.send("キャンセルしました")
            return

        try:
            user_data = user_data_dict[f"{user_id}"]
        except KeyError:
            user_data_dict[f"{user_id}"] = {"ban": False, "role": [], "mcid": [], "point": 0, "speak": 0}
            user_data = user_data_dict[f"{user_id}"]

        user_data["ban"] = True

        with open("./datas/user_data.json", mode="w") as f:
            user_data_json = json.dumps(user_data_dict, indent=4)
            f.write(user_data_json)

        await message.channel.send(f"{baned_user.name}を事前BANしました")


async def unban(client1, message):
    """
    第一引数のIDを持つユーザーの事前BANを解除する関数"""

    if not message.author.id == 523303776120209408:
        await message.channel.send("何様のつもり？")
        return

    try:
        user_id = int(message.content.split()[1])
    except ValueError:
        await message.channel.send("不正な引数です")
        return

    try:
        baned_user = await client1.fetch_user(user_id)
    except discord.errors.NotFound:
        await message.channel.send("IDが間違っています")
        return

    with open("./datas/user_data.json", mode="r") as f:
        user_data_dict = json.load(f)

    try:
        user_data = user_data_dict[f"{user_id}"]
        if not user_data["ban"]:
            await message.channel.send(f"{baned_user.name}は事前BANされていません")
            return
    except KeyError:
        await message.channel.send("そのユーザーIDは登録されていません")
        return

    user_info_embed = discord.Embed(title="以下のユーザーの事前BANを解除しますか？", description="はい(解除): 👍\nいいえ(ミス): 👎", color=0x000000)
    user_info_embed.set_thumbnail(url=baned_user.avatar_url)
    user_info_embed.add_field(name=".", value=baned_user.name)
    msg = await message.channel.send(embed=user_info_embed)
    await msg.add_reaction("👍")
    await msg.add_reaction("👎")
    def check(reaction, user):
        return user == message.author and (str(reaction.emoji) == "👍" or str(reaction.emoji) == "👎")
    try:
        reaction, user = await client1.wait_for("reaction_add", check=check, timeout=60)
    except asyncio.TimeoutError:
        await message.channel.send("タイムアウトしました。最初からやり直してください")
        return

    else:
        if str(reaction.emoji) == "👎":
            await message.channel.send("キャンセルしました")
            return

        user_data_dict[f"{user_id}"]["ban"] = False
        with open("./datas/user_data.json", mode="w") as f:
            user_data_json = json.dumps(user_data_dict, indent=4)
            f.write(user_data_json)

        await message.channel.send(f"{baned_user.name}の事前BANを解除しました")


async def mypt(message):
    """
    自分のpt保有量を確認する関数"""

    with open("./datas/user_data.json", mode="r") as f:
        user_data_dict = json.load(f)

    try:
        had_pt = user_data_dict[f"{message.author.id}"]["point"]
    except KeyError:
        user_data_dict[f"{message.author.id}"] = {"ban": False, "role": [], "mcid": [], "point": 0, "speak": 0}
        had_pt = user_data_dict[f"{message.author.id}"]["point"]

    await message.channel.send(f"{message.author.name}さんは{had_pt}pt保有しています。")


async def user_data(client1, message):
    """
    けい鯖のユーザーのデータを表示する関数"""

    try:
        user_id = int(message.content.split()[1])
    except ValueError:
        await message.channel.send("不正な引数です")
        return
    except IndexError:
        user_id = message.author.id

    member = message.guild.get_member(user_id)
    try:
        user_name = member.name
    except AttributeError:
        await message.channel.send("そんな人この鯖にいません")
        return

    with open("./datas/user_data.json", mode="r") as f:
        user_data_dict = json.load(f)

    user_data = user_data_dict[f"{member.id}"]

    user_data_embed = discord.Embed(color=0xfffffe)
    user_data_embed.set_author(name=f"{member.name}", icon_url=member.avatar_url)

    roles = ""
    for role in reversed(member.roles):
        roles += f"{role.mention}\n"
    user_data_embed.add_field(name="roles", value=roles, inline=True)

    mcids = ""
    for mcid in user_data["mcid"]:
        mcid = mcid.replace("_", "\\_")
        mcids += f"{mcid}\n"
    counter = len(user_data["mcid"])
    mcids += f"以上{counter}アカ"
    user_data_embed.add_field(name="MCID", value=mcids, inline=True)

    point = user_data["point"]
    user_data_embed.add_field(name="point", value=f"{point}", inline=True)

    speak = user_data["speak"]
    user_data_embed.add_field(name="speak", value=f"{speak}", inline=True)

    joined_time = (member.joined_at + datetime.timedelta(hours=9)).strftime(r"%Y/%m/%d-%H:%M")
    user_data_embed.add_field(name="joined", value=joined_time, inline=True)

    await message.channel.send(embed=user_data_embed)


async def mcid(client1, message):
    """
    MCID報告システム"""

    if message.author.bot:
        return

    message_content = message.content.replace("\\", "")
    p = re.compile(r"^[a-zA-Z0-9_\\\n →]+$")
    if not p.fullmatch(message_content):
        await message.channel.send("MCID(報告/変更報告)に使えない文字が含まれています")
        return

    if len(message_content.split("→")) == 1:
        await new_mcid(client1, message, message_content)

    elif len(message_content.split("→")) == 2:
        await change_mcid(message, message_content)

    else:
        await message.channel.send("MCIDの変更申請は1アカウントずつ行ってください。")


def check_mcid_length(mcid):
    """
    申請されたMCIDがMCIDとして成り立つかチェックする
    boolを返す"""

    if len(mcid) >= 3 and len(mcid) <= 16:
        return True
    else:
        return False


def check_mcid_yet(mcid):
    """
    申請されたMCIDが未登録MCIDかチェックする
    boolを返す"""

    with open("./datas/user_data.json", mode="r") as f:
        user_data_dict = json.load(f)

    for user_id in user_data_dict:
        for mcid_registered in user_data_dict[user_id]["mcid"]:
            if mcid.lower() == mcid_registered.lower():
                return False
    return True


def check_mcid_logined(mcid):
    """
    整地鯖にログインしたことがあるかをチェックする
    boolまたはNoneTypeを返す"""

    url = f"https://ranking-gigantic.seichi.click/player/{mcid.lower()}"
    try:
        res = requests.get(url)
        res.raise_for_status()
        soup = bs4.BeautifulSoup(res.text, "html.parser")
        td = soup.td
        if f"{mcid.lower()}" in f"{td}":
            return True
        else:
            return False
    except requests.exceptions.HTTPError:
        return None


async def new_mcid(client1, message, message_content):
    """
    新規MCID報告
    初期設定と追加に対応"""

    right_mcid_length_list = []
    for mcid in list(set(message_content.split())):
        right_mcid = check_mcid_length(mcid)
        if not right_mcid:
            mcid = mcid.replace("_", "\\_")
            await message.channel.send(f"{mcid}はMCIDとして成り立ちません")
        else:
            right_mcid_length_list.append(mcid)

    right_mcid_not_yet_list = []
    for mcid in right_mcid_length_list:
        right_mcid = check_mcid_yet(mcid)
        if not right_mcid:
            mcid = mcid.replace("_", "\\_")
            await message.channel.send(f"**{mcid}**は既に登録されています")
        else:
            right_mcid_not_yet_list.append(mcid)

    right_mcid_logined_list = []
    for mcid in right_mcid_not_yet_list:
        right_mcid = check_mcid_logined(mcid)
        if right_mcid is None:
            await message.channel.send("現在データ参照元が使用できない状態です。しばらくたってからもう一度お試しください。")
            return
        if not right_mcid:
            mcid = mcid.replace("_", "\\_")
            await message.channel.send(f"**{mcid}**は```\n・実在しない\n・整地鯖にログインしたことがない\n\
・MCIDを変更した\n・整地鯖ログイン後まだプレイヤーデータ保存がされていない\n・MCID変更後整地鯖にログインしてプレイヤーデータ保存がされていない```\n\
可能性があります。\nこの機能は整地鯖ウェブページへの負荷となります。__**意図的に間違った入力を繰り返していると判断した場合処罰の対象になります。\
**__もしこれがバグならけいにお知らせください。")
        else:
            right_mcid_logined_list.append(mcid)

    if len(right_mcid_logined_list) == 0:
        return

    with open("./datas/user_data.json", mode="r") as f:
        user_data_dict = json.load(f)

    try:
        user_data = user_data_dict[f"{message.author.id}"]
    except KeyError:
        user_data_dict[f"{message.author.id}"] = {"ban": False, "role": [], "mcid": [], "point": 0, "speak": 0}
        user_data = user_data_dict[f"{message.author.id}"]

    mcid_list = user_data["mcid"]
    if len(mcid_list) == 0:
        user_data["mcid"] = right_mcid_logined_list
    else:
        msg = await message.channel.send("既に登録されているMCIDがあります。変更の間違いではありませんか？追加で宜しいですか？\n\
変更->「🇨」\n追加->「🇦」\nをリアクションしてください")
        await msg.add_reaction("🇨")
        await msg.add_reaction("🇦")
        def check(reaction, user):
            return user == message.author and (str(reaction.emoji) == "🇦" or str(reaction.emoji) == "🇨")
        try:
            reaction, user = await client1.wait_for("reaction_add", check=check, timeout=60)
        except asyncio.TimeoutError:
            await message.channel.send("タイムアウトしました。最初からやり直してください")
            return
        else:
            if str(reaction.emoji) == "🇨":
                await message.channel.send("変更申請の形式は旧MCID→新MCIDです。最初からやり直してください。")
                return
            if str(reaction.emoji) == "🇦":
                user_data["mcid"] = mcid_list + right_mcid_logined_list

    with open("./datas/user_data.json", mode="w") as f:
        user_data_json = json.dumps(user_data_dict, indent=4)
        f.write(user_data_json)

    mcid_list_str = str(right_mcid_logined_list).replace("_", "\\_")
    await message.channel.send(f"MCIDの登録が完了しました。登録されたMCID: {mcid_list_str}")

    new_role = discord.utils.get(message.guild.roles, id=621641465105481738)
    accept_able_role = discord.utils.get(message.guild.roles, id=626062897633689620)
    if new_role in message.author.roles:
        await message.author.add_roles(accept_able_role)
        await message.channel.send("MCIDの報告ありがとうございます。ルールに同意していただけるなら<#592581835343659030>で**/accept**をお願いします。")


async def change_mcid(message, message_content):
    """
    既存のMCIDの変更に対応"""

    before_mcid = message_content.split("→")[0]
    after_mcid = message_content.split("→")[1]
    if before_mcid.lower() == after_mcid.lower():
        await message.channel.send("大文字小文字のみの変更ですか？それなら報告は必要ありません。")
        return

    right_mcid = check_mcid_length(after_mcid)
    if not right_mcid:
        mcid = after_mcid.replace("_", "\\_")
        await message.channel.send(f"{mcid}はMCIDとして成り立ちません")
        return

    right_mcid = check_mcid_yet(after_mcid)
    if not right_mcid:
        mcid = after_mcid.replace("_", "\\_")
        await message.channel.send(f"**{mcid}**は既に登録されています")
        return

    right_mcid = check_mcid_logined(after_mcid)
    if right_mcid is None:
        await message.channel.send("現在データ参照元が使用できない状態です。しばらくたってからもう一度お試しください。")
        return
    if not right_mcid:
        mcid = after_mcid.replace("_", "\\_")
        await message.channel.send(f"**{mcid}**は```\n・実在しない\n・整地鯖にログインしたことがない\n\
・MCIDを変更した\n・整地鯖ログイン後まだプレイヤーデータ保存がされていない\n・MCID変更後整地鯖にログインしてプレイヤーデータ保存がされていない```\n\
可能性があります。\nこの機能は整地鯖ウェブページへの負荷となります。__**意図的に間違った入力を繰り返していると判断した場合処罰の対象になります。\
**__もしこれがバグならけいにお知らせください。")
        return

    with open("./datas/user_data.json", mode="r") as f:
        user_data_dict = json.load(f)

    try:
        user_data = user_data_dict[f"{message.author.id}"]
    except KeyError:
        user_data_dict[f"{message.author.id}"] = {"ban": False, "role": [], "mcid": [], "point": 0, "speak": 0}
        user_data = user_data_dict[f"{message.author.id}"]

    mcid_list = user_data["mcid"]
    flag = False
    for mcid in mcid_list:
        if before_mcid.lower() == mcid.lower():
            index = mcid_list.index(mcid)
            mcid_list[index] = after_mcid
            flag = True
            break

    if not flag:
        str(mcid_list).replace("_", "\\_")
        await message.channel.send(f"**{before_mcid}**は登録されていません。現在あなたが登録しているMCID:\n{mcid_list}")
        return

    with open("./datas/user_data.json", mode="w") as f:
        user_data_json = json.dumps(user_data_dict, indent=4)
        f.write(user_data_json)

    before_mcid = before_mcid.replace("_", "\\_")
    after_mcid = after_mcid.replace("_", "\\_")
    await message.channel.send(f"MCIDの変更が登録されました\n**{before_mcid}**→**{after_mcid}**")


async def edit_mcid(message):
    """
    登録されているMCIDを編集(追加/削除)する関数"""

    admin_role = discord.utils.get(message.guild.roles, id=585999549055631408)
    if not (admin_role in message.author.roles):
        await message.channel.send("何様のつもり？")
        doM_role = discord.utils.get(message.guild.roles, id= 616212704818102275)
        await message.author.add_roles(doM_role)
        return

    try:
        operation = message.content.split()[1]
        user_id = int(message.content.split()[2])
        mcid = message.content.split()[3].replace("\\", "")
    except ValueError:
        await message.channel.send("IDとして成り立ちません")
        return
    except IndexError:
        await message.channel.send("引数が足りません\nヒント: `/mcid␣[set, del]␣userid␣MCID`")
        return

    if operation == "set":
        await set_mcid(message, user_id, mcid)
    elif operation == "del":
        await del_mcid(message, user_id, mcid)
    else:
        await message.channel.send("第一引数が不正です\nヒント: `/mcid␣[set, del]␣userid␣MCID`")


async def set_mcid(message, user_id , mcid):
    """
    指定ユーザーの登録されているMCIDに第4引数のMCIDを追加する関数"""

    if not check_mcid_length(mcid):
        await message.channel.send(f"{mcid}はMCIDとして成り立ちません")
        return
    if not check_mcid_yet(mcid):
        await message.channel.send(f"{mcid}は既に登録されています")
        return
    right_mcid = check_mcid_logined(mcid)
    if right_mcid is None:
        await message.channel.send("現在データ参照元が使用できない状態です。しばらくたってからもう一度お試しください。")
        return
    if not right_mcid:
        await message.channel.send("整地鯖で認識されていないMCIDです")
        return

    with open("./datas/user_data.json", mode="r") as f:
        user_data_dict = json.load(f)

    try:
        user_data = user_data_dict[f"{user_id}"]
    except KeyError:
        user_data_dict[f"{user_id}"] = {"ban": False, "role": [], "mcid": [], "point": 0, "speak": 0}
        user_data = user_data_dict[f"{user_id}"]
    mcid_list = user_data["mcid"]

    mcid_list.append(mcid)

    with open("./datas/user_data.json", mode="w") as f:
        user_data_json = json.dumps(user_data_dict, indent=4)
        f.write(user_data_json)

    member_name = message.guild.get_member(user_id).name
    mcid = mcid.replace("_", "\\_")
    await message.channel.send(f"{member_name}のMCIDに{mcid}を追加しました")


async def del_mcid(message, user_id, mcid):
    """
    指定ユーザーの登録されているMCIDから第4引数のMCIDを削除する関数"""

    with open("./datas/user_data.json", mode="r") as f:
        user_data_dict = json.load(f)

    try:
        user_data = user_data_dict[f"{user_id}"]
    except KeyError:
        user_data_dict[f"{user_id}"] = {"ban": False, "role": [], "mcid": [], "point": 0, "speak": 0}
        user_data = user_data_dict[f"{user_id}"]
    mcid_list = user_data["mcid"]

    try:
        mcid_list.remove(mcid)
    except ValueError:
        member_name = message.guild.get_member(user_id).name
        mcid = mcid.replace("_", "\\_")
        await message.channel.send(f"{member_name}は{mcid}というMCIDを登録していません")
        return

    with open("./datas/user_data.json", mode="w") as f:
        user_data_json = json.dumps(user_data_dict, indent=4)
        f.write(user_data_json)

    member_name = message.guild.get_member(user_id).name
    mcid = mcid.replace("_", "\\_")
    await message.channel.send(f"{member_name}のMCID、{mcid}を削除しました")


async def check_mcid_exist_now(client1):
    """
    現在登録されているMCIDが存在するかをチェックする関数
    存在しない場合そのMCIDを登録している人にメンションを飛ばす"""

    with open("./datas/user_data.json", mode="r") as f:
        user_data_dict = json.load(f)

    alart_msg = ""
    not_exist_mcid_list = []
    for user_id in user_data_dict:
        for mcid in user_data_dict[user_id]["mcid"]:
            url = f"https://api.mojang.com/users/profiles/minecraft/{mcid}"
            try:
                res = requests.get(url)
                res.raise_for_status()
                sorp = bs4.BeautifulSoup(res.text, "html.parser")
                try:
                    mcid_dict = json.loads(sorp.decode("utf-8"))
                except json.decoder.JSONDecodeError:
                    alart_msg += f"<@{user_id}> "
                    not_exist_mcid_list.append(mcid)
            except requests.exceptions.HTTPError:
                return

    if len(not_exist_mcid_list) == 0:
        return

    alart_msg = f"{alart_msg}\nMCIDを変更しましたか？以下のMCIDは現在無効です。<#640833025822949387>で過去のMCID→現在のMCIDを入力してください\n{not_exist_mcid_list}"
    alart_ch = client1.get_channel(585999375952642067)
    await alart_ch.send(alart_msg)


async def kazuate(message):
    """
    数当て"""

    if message.author.bot:
        return

    try:
        int(message.content)
    except ValueError:
        return

    if not len(message.content) == 3:
        return

    with open("./datas/kazuate.txt", mode="r", encoding="utf-8") as f:
        data = f.read()

    try:
        seikai = int(data.split()[0])
    except ValueError:
        await message.channel.send("既にあたりが出ています")
        return
    kazu = int(data.split()[1])

    if int(message.content) == seikai:
        with open("./datas/user_data.json", mode="r", encoding="utf-8") as f:
            user_data_dict = json.load(f)

        before_pt = user_data_dict[f"{message.author.id}"]["point"]
        after_pt = user_data_dict[f"{message.author.id}"]["point"] + (500 - kazu)
        if after_pt < 0:
            after_pt = 0

        user_data_dict[f"{message.author.id}"]["point"] = after_pt

        with open("./datas/user_data.json", mode="w", encoding="utf-8") as f:
            user_data_json = json.dumps(user_data_dict, indent=4)
            f.write(user_data_json)
        await message.channel.send(f"{message.author.name}さん正解！{500-kazu}ptゲット！\n{before_pt}pt->{after_pt}pt")

        with open("./datas/kazuate.txt", mode="w", encoding="utf-8") as f:
            f.write("None 0")

        await message.channel.edit(topic="既にあたりが出ています")
    else:
        with open("./datas/kazuate.txt", mode="w", encoding="utf-8") as f:
            f.write(f"{seikai} {kazu+1}")
        await message.channel.send(f"{message.content}ははずれ！")


async def marichan_invite(message):
    """
    魔理沙bot招待コマンドが実行されたとき用の関数"""

    await message.delete()
    await message.channel.send("コマンド漏洩防止のためコマンドを削除しました", delete_after=5)
    marichan_inviter_role = discord.utils.get(message.guild.roles, id=663542711290429446)
    await message.author.add_roles(marichan_inviter_role)

    invite_url = os.getenv("marichan_invite_url")
    try:
        await message.author.send(invite_url)
    except discord.errors.Forbidden:
        await message.channel.send("権限エラー。DMを解放してください。")
        return

    with open("/var/www/html/discord/login_data.json", mode="r") as f:
        login_data_dict = json.load(f)

    try:
        login_data = login_data_dict[f"{message.author.id}"]
    except KeyError:
        dat = f"{string.digits}{string.ascii_lowercase}{string.ascii_uppercase}"
        passwd = "".join([random.choice(dat) for i in range(8)])

        avatar_url = message.author.avatar_url

        while True:
            dat = f"{string.digits}{string.ascii_lowercase}{string.ascii_uppercase}"
            file_name = "".join([random.choice(dat) for i in range(10)])
            if not os.path.exists(f"/var/www/html/discord/user_guild/{file_name}.html"):
                with open(f"/var/www/html/discord/user_guild/{file_name}.html", mode="w", encoding="utf-8") as f:
                    default = '\
<meta http-equiv="content-type" charset="utf-8">\n\
\n\
<html>\n\
<title>\n\
    けいのうぇぶさいと\n\
</title>\n\
<head>\n\
    <style>\n\
    a{\n\
        color:#00a0ff;\n\
    }\n\
    </style>\n\
    <h2>\n\
    <a href="../../index.html"><img src="http://avatar.minecraft.jp/kei_3104/minecraft/m.png" width="72" height="72"></a>\n\
    <a href="../../discord.html">discord</a>\n\
    <a href="../../travel.html">旅記とか</a>\n\
    <a href="../../form.html">意見・感想</a>\n'+f'<img src="{message.author.avatar_url}" width="72" height="72">'+'\
    </h2>\n\
    <style>\n\
    body{\n\
        background:#36393f;\n\
        color:#ffffff;\n\
    }\n\
    </style>\n\
</head>\n\
</html>'
                    f.write(default)
                    break
            else:
                pass

        login_data_dict[f"{message.author.id}"] = [passwd, file_name]
        with open("/var/www/html/discord/login_data.json", mode="w") as f:
            login_data_json = json.dumps(login_data_dict, indent=4)
            f.write(login_data_json)
        await message.author.send(passwd)

    embed = discord.Embed(title="DMに招待urlとパスワードを送信しました", description="urlで管理者を持っているサーバに入れられます。\nパスワードは[けいのウェブサイト](http://www.kei-3104.com) で使用できます")
    await message.channel.send(embed=embed)
    #await message.channel.send("DMに招待urlを送信しました。管理者権限を持っているサーバに入れられます。")


async def accept(message):
    """
    新規役職剥奪用関数"""

    new_role = discord.utils.get(message.guild.roles, id=621641465105481738)
    accept_able_role = discord.utils.get(message.guild.roles, id=626062897633689620)
    crafter_role = discord.utils.get(message.guild.roles, id=586123363513008139)

    if not new_role in message.author.roles:
        await message.channel.send("もう新規役職付いてないよ^^")
        return

    if not accept_able_role in message.author.roles:
        await message.channel.send("まず<#640833025822949387>をお願いします")
        return

    if not message.channel.id == 592581835343659030:
        await message.channel.send("説明読みました？チャンネル違いますよ？")
        return

    await message.author.remove_roles(new_role)
    await message.author.remove_roles(accept_able_role)
    await message.author.add_roles(crafter_role)
    await message.channel.send(f"改めまして{message.author.name}さんようこそ{message.guild.name}へ！\n\
<#664286990677573680>に自分がほしい役職があったらぜひ付けてみてください！\n\
もしよろしければ<#586571234276540449>もしていただけると嬉しいです！")


async def ranking(client1, message):
    """
    第一引数にpointかspeakを"""

    operation = message.content.split()[1]
    if operation == "point":
        with open("./datas/user_data.json", mode="r") as f:
            user_data_dict = json.load(f)

        description = ""
        i = 0
        for key, value in sorted(user_data_dict.items(), key=lambda x: -x[1]["point"]):
            if i >= 20:
                break
            user = client1.get_user(int(key))
            point = value["point"]
            if user is None:
                description += f"{i+1}位: None: {point}\n"
            else:
                description += f"{i+1}位: {user.name}: {point}\n"
            i += 1

        embed = discord.Embed(title="ポイントランキング", description=f"```\n{description}```", color=0x005500)

    elif operation == "speak":

        with open("./datas/user_data.json", mode="r") as f:
            user_data_dict = json.load(f)

        description = ""
        i = 0
        for key, value in sorted(user_data_dict.items(), key=lambda x: -x[1]["speak"]):
            if i >= 20:
                break
            user = client1.get_user(int(key))
            speak = value["speak"]
            if user is None:
                description += f"{i+1}位: None: {speak}\n"
            else:
                description += f"{i+1}位: {user.name}: {speak}\n"
            i += 1
        
        embed = discord.Embed(title="発言数ランキング", description=f"```\n{description}```", color=0x005500)

    else:
        await message.channel.send("引数が不正です。\nヒント: `/ranking␣[point, speak]`")
        return
    await message.channel.send(embed=embed)


async def story(message):
    """
    物語作ろうぜ"""

    if message.author.bot:
        return

    if not message.content:
        await message.delete()
        return

    if message.content.startswith("/"):
        return

    with open("./datas/story.txt", mode="a", encoding="utf-8") as f:
        f.write(f"{message.content}\n")


async def story_secret(message):
    """
    物語作ろうぜ
    でも前々文は見えないぜ"""

    if message.author.bot:
        return

    if not message.content:
        await message.delete()
        return

    if message.content.startswith("/"):
        return

    with open("./datas/story_secret.txt", mode="a", encoding="utf-8") as f:
        f.write(f"{message.content}\n")

    embed = discord.Embed(description=message.content)
    embed.set_author(name=message.author.name, icon_url=message.author.avatar_url_as(format="png"))
    await message.channel.purge()
    await message.channel.send(embed=embed)


async def record_story(client1):
    """
    毎週月曜日の朝3:30に物語を記録"""

    record_ch = client1.get_channel(762553442040021032)

    with open("./datas/story.txt", mode="r", encoding="utf-8") as f:
        story = f.read()

    while True:
        if len(story) > 2000:
            embed = discord.Embed(description=story[:2000], color=0x00ffff)
            await record_ch.send(embed=embed)
            story = story[2000:]
        else:
            embed = discord.Embed(description=story, color=0x00ffff)
            await record_ch.send(embed=embed)
            break

    with open("./datas/story_secret.txt", mode="r", encoding="utf-8") as f:
        story = f.read()

    while True:
        if len(story) > 2000:
            embed = discord.Embed(description=story[:2000], color=0xaa00aa)
            await record_ch.send(embed=embed)
            story = story[2000:]
        else:
            embed = discord.Embed(description=story, color=0xaa00aa)
            await record_ch.send(embed=embed)
            break

    with open("./datas/story.txt", mode="w", encoding="utf-8") as f:
        f.write("")

    with open("./datas/story_secret.txt", mode="w", encoding="utf-8") as f:
        f.write("")

    ch = client1.get_channel(762546731417731073)
    await ch.send("----キリトリ----")
    ch = client1.get_channel(762546959138816070)
    await ch.send("----キリトリ----")


async def create_new_func(client1, message):
    """
    PHPから送られてくるwebhookデータを解析し条件に合致するようならJSONに書き込む
    条件に合致しなければリクエスト者に対してDMを送る"""

    if not message.author.id == 722810440362491995:
        return

    request_list = message.content.split("\n")
    user_id = int(request_list[0])
    user = client1.get_user(user_id)
    try:
        guild_id = int(request_list[1])
    except ValueError:
        await user.send(f"サーバID:{request_list[1]} は不正です。リクエストは却下されました。")
        return
    guild = client1.get_guild(guild_id)
    if guild is None:
        await user.send(f"サーバID:{guild_id} を持つサーバは存在しないか本botの監視下にありません。リクエストは却下されました。")
        return
    member = guild.get_member(user_id)
    if member is None:
        await user.send(f"あなたはサーバ:{guild.name} に入っていません。リクエストは却下されました。")
        return
    if not member.guild_permissions.administrator:
        await user.send(f"あなたはサーバ:{guild.name} の管理者権限を持っていません。リクエストは却下されました。")
        return
    about_ch = request_list[3].split()
    if about_ch[0] == "all_ok":
        ch_permmission = {"disable_c": []}
    elif about_ch[0] == "able":
        ch_permmission = {"able_c": []}
        for ch in about_ch[1:]:
            try:
                ch_id = int(ch)
            except ValueError:
                await user.send(f"チャンネルID:{ch} は不正です。リクエストは却下されました。")
                return
            channel = guild.get_channel(ch_id)
            if channel is None:
                await user.send(f"チャンネルID:{ch_id} を持つチャンネルは{guild.name}に存在しません。リクエストは却下されました。")
                return
            ch_permmission["able_c"].append(ch_id)
    else:
        ch_permmission = {"disable_c": []}
        for ch in about_ch[1:]:
            try:
                ch_id = int(ch)
            except ValueError:
                await user.send(f"チャンネルID:{ch} は不正です。リクエストは却下されました。")
                return
            channel = guild.get_channel(ch_id)
            if channel is None:
                await user.send(f"チャンネルID:{ch_id} を持つチャンネルは{guild.name}に存在しません。リクエストは却下されました。")
                return
            ch_permmission["disable_c"].append(ch_id)

    about_role = request_list[4].split()
    if about_role == "all_ok":
        role_permission = {"disable_r": []}
    elif about_role == "able":
        role_permission = {"able_r": []}
        for role_ in about_role[1:]:
            try:
                role_id = int(role_)
            except ValueError:
                await user.send(f"役職ID:{role_} は不正です。リクエストは却下されました。")
                return
            role = guild.get_role(role_id)
            if role is None:
                await user.send(f"役職ID:{role_id} を持つ役職は{guild.name}に存在しません。リクエストは却下されました。")
                return
            role_permission["able_r"].append(role_id)
    else:
        role_permission = {"disable_r": []}
        for role_ in about_role[1:]:
            try:
                role_id = int(role_)
            except ValueError:
                await user.send(f"役職ID:{role_} は不正です。リクエストは却下されました。")
                return
            role = guild.get_role(role_id)
            if role is None:
                await user.send(f"役職ID:{role_id} を持つ役職は{guild.name}に存在しません。リクエストは却下されました。")
                return
            role_permission["disable_r"].append(role_id)

    send_message = request_list[5].split()
    if send_message[0] == "None":
        msg_dict = {"message": []}
    else:
        msg_dict = {"message": []}
        for msg in send_message:
            msg_dict["message"].append(msg)
    add_role = request_list[6].split()
    if add_role[0] == "None":
        add_role_dict = {"add_role": []}
    else:
        add_role_dict = {"add_role": []}
        for role_ in add_role:
            try:
                role_id = int(role_)
            except ValueError:
                await user.send(f"役職ID:{role_} は不正です。リクエストは却下されました。")
                return
            role = guild.get_role(role_id)
            if role is None:
                await user.send(f"役職ID:{role_id} を持つ役職は{guild.name}に存在しません。リクエストは却下されました。")
                return
            add_role_dict["add_role"].append(role_id)
    remove_role = request_list[7].split()
    if remove_role[0] == "None":
        remove_role_dict = {"remove_role": []}
    else:
        remove_role_dict = {"remove_role": []}
        for role_ in remove_role:
            try:
                role_id = int(role_)
            except ValueError:
                await user.send(f"役職ID:{role_} は不正です。リクエストは却下されました。")
                return
            role = guild.get_role(role_id)
            if role is None:
                await user.send(f"役職ID:{role_id} を持つ役職は{guild.name}に存在しません。リクエストは却下されました。")
                return
            remove_role_dict["remove_role"].append(role_id)

    with open("./datas/custom_commands.json", mode="r", encoding="utf-8") as f:
        custom_commands_dict = json.load(f)

    try:
        custom_commands = custom_commands_dict[f"{guild_id}"]
    except KeyError:
        custom_commands_dict[f"{guild_id}"] = {}
        custom_commands = custom_commands_dict[f"{guild_id}"]

    command = {}
    command.update(ch_permmission)
    command.update(role_permission)
    command.update(msg_dict)
    command.update(add_role_dict)
    command.update(remove_role_dict)

    trigger = request_list[2]

    custom_commands[trigger] = command

    with open("./datas/custom_commands.json", mode="w", encoding="utf-8") as f:
        custom_commands_json = json.dumps(custom_commands_dict, indent=4, ensure_ascii=False)
        f.write(custom_commands_json)

    await user.send(f"新規コマンド:{trigger}を登録しました。")


async def version(message):
    """
    バージョンを表示"""

    with open("./datas/version.txt", mode="r") as f:
        version = f.read()
    await message.channel.send(f"現在のConoHa起動のbotのバージョンは{version}です") 


async def send_zip_data(message):
    """
    データ類を全部引っ張ってくる関数"""

    if not message.author.id == 523303776120209408:
        await message.channel.send("何様のつもり？")
        doM_role = discord.utils.get(message.guild.roles, id= 616212704818102275)
        await message.author.add_roles(doM_role)
        return

    shutil.make_archive("datas", format="zip", base_dir="./datas")
    f = discord.File("datas.zip")
    await message.author.send(file=f)


async def ban_list(message, client1):
    """
    事前BANしている人のリスト"""

    if not message.author.id == 523303776120209408:
        await message.channel.send("このコマンドは使用できません")
        return

    await message.channel.send("時間かかりますよ")

    with open("./datas/user_data.json", mode="r", encoding="utf-8") as f:
        user_data_dict = json.load(f)

    banned_user = ""
    i = 0
    for user_id in user_data_dict:
        if user_data_dict[user_id]["ban"]:
            user = await client1.fetch_user(int(user_id))
            banned_user += f"{user} <@{user_id}>\n"
            i +=1
    banned_user += f"\n以上{i}アカ"
    await message.channel.send(embed=discord.Embed(title="事前BAN", description=banned_user))


async def gban_list(message, client1):
    """
    魔理沙はこのサーバには入りません"""

    if not message.author.id == 523303776120209408:
        await message.channel.send("このコマンドは使用できません")
        return

    with open("./datas/ban_server.json", mode="r", encoding="utf-8") as f:
        ban_server_list = json.load(f)

    text = ""
    for ban_server in ban_server_list:
        text += f"ServerID: {ban_server[0]}\nServerName: {ban_server[1]}\nOwnerID: {ban_server[2]}\n\n"

    await message.channel.send(text)


async def leave_guild(message, client1):
    """
    サーバから抜ける"""

    if not message.author.id == 523303776120209408:
        await message.channel.send("このコマンドは使用できません")
        return

    try:
        guild_id = int(message.content.split()[1])
        reason = message.content.split()[2]
    except ValueError:
        await message.channel.send("intキャストできる形で入力してください")
        return
    except IndexError:
        await message.channel.send("サーバから抜ける理由を書いてください")
        return

    guild = client1.get_guild(guild_id)
    embed = discord.Embed(
        title="以下のサーバから抜け、サーバをブラックリスト登録しますか？",
        description="はい(離脱&ブラックリスト登録): 👍\nいいえ(ミス): 👎",
        color=0xff0000
    )
    embed.set_author(name=guild.name, icon_url=guild.icon_url_as(format="png"))
    embed.set_footer(text=guild.owner.name, icon_url=guild.owner.avatar_url_as(format="png"))
    msg = await message.channel.send(embed=embed)
    await msg.add_reaction("👍")
    await msg.add_reaction("👎")
    def check(reaction, user):
        return user == message.author and (str(reaction.emoji) == "👍" or str(reaction.emoji) == "👎")
    try:
        reaction, user = await client1.wait_for("reaction_add", check=check, timeout=60)
    except asyncio.TimeoutError:
        await message.channel.send("タイムアウトしました。最初からやり直してください")
        return

    else:
        if str(reaction.emoji) == "👎":
            await message.channel.send("キャンセルしました")
            return

        if guild.owner.id == 523303776120209408:
            await message.channel.send("あんた正気か？")
            return

        for ch in guild.text_channels:
            try:
                await ch.send(f"{client1.user.name}はこのサーバを抜けます\nReason: {reason}")
            except discord.errors.Forbidden:
                pass
            else:
                break

        with open("./datas/ban_server.json", mode="r", encoding="utf-8") as f:
            ban_server_list = json.load(f)

        ban_server_list.append(
            [
                guild.id,
                guild.name,
                guild.owner.id
            ]
        )

        with open("./datas/ban_server.json", mode="w", encoding="utf-8") as f:
            ban_server_list_json = json.dumps(ban_server_list, indent=4, ensure_ascii=False)
            f.write(ban_server_list_json)

        await guild.leave()


async def global_notice(client1, message):
    """
    導入サーバすべてのお知らせチャンネルにお知らせを送信"""

    if not message.author.id == 523303776120209408:
        await message.channel.send("このコマンドは使用できません")
        return

    msg = message.content.replace("/global_notice ", "")

    with open("./datas/marisa_notice.json", mode="r", encoding="utf-8") as f:
        marisa_notice_dict = json.load(f)

    for guild in client1.guilds:
        try:
            notice_ch = guild.get_channel(marisa_notice_dict[f"{guild.id}"])
        except KeyError:
            marisa_notice_dict[f"{guild.id}"] = None
            notice_ch = None

        if notice_ch is None:
            flag = False
            for ch in guild.text_channels:
                try:
                    await ch.send(msg)
                    marisa_notice_dict[f"{guild.id}"] = ch.id
                    flag = True
                    break
                except discord.errors.Forbidden:
                    pass
            if not flag:
                try:
                    await guild.owner.send(f"{guild.name}に{client1.user.name}が発言できるチャンネルがありません。以下の内容をサーバメンバーに周知してください\n\n{msg}")
                except discord.errors.Forbidden:
                    pass
        elif notice_ch == "rejected":
            pass
        else:
            try:
                await notice_ch.send(msg)
            except discord.errors.Forbidden:
                flag = False
                for ch in guild.text_channels:
                    try:
                        await ch.send(msg)
                        marisa_notice_dict[f"{guild.id}"] = ch.id
                        flag = True
                        break
                    except discord.errors.Forbidden:
                        pass
                if not flag:
                    try:
                        await guild.owner.send(f"{guild.name}に{client1.user.name}が発言できるチャンネルがありません。以下の内容をサーバメンバーに周知してください\n\n{msg}")
                    except discord.errors.Forbidden:
                        pass

    with open("./datas/marisa_notice.json", mode="w", encoding="utf-8") as f:
        marisa_notice_json = json.dumps(marisa_notice_dict, indent=4)
        f.write(marisa_notice_json)

    await message.channel.send("全サーバに通知完了")


'''
async def issue_id(message):
    """
    メッセージ送信者にDMでパスワードを発行して
    /var/www/html/discord/login_data.jsonに記録する"""

    with open("/var/www/html/discord/login_data.json", mode="r") as f:
        login_data_dict = json.load(f)

    try:
        login_data = login_data_dict[f"{message.author.id}"]
    except KeyError:
        dat = f"{string.digits}{string.ascii_lowercase}{string.ascii_uppercase}"
        passwd = "".join([random.choice(dat) for i in range(8)])

        avatar_url = message.author.avatar_url

        while True:
            dat = f"{string.digits}{string.ascii_lowercase}{string.ascii_uppercase}"
            file_name = "".join([random.choice(dat) for i in range(10)])
            if not os.path.exists(f"/var/www/html/discord/user_guild/{file_name}.html"):
                with open(f"/var/www/html/discord/user_guild/{file_name}.html", mode="w", encoding="utf-8") as f:
                    default = '\
<meta http-equiv="content-type" charset="utf-8">\n\
\n\
<html>\n\
<title>\n\
    けいのうぇぶさいと\n\
</title>\n\
<head>\n\
    <style>\n\
    a{\n\
        color:#00a0ff;\n\
    }\n\
    </style>\n\
    <h2>\n\
    <a href="../../index.html"><img src="http://avatar.minecraft.jp/kei_3104/minecraft/m.png" width="72" height="72"></a>\n\
    <a href="../../discord.html">discord</a>\n\
    <a href="../../travel.html">旅記とか</a>\n\
    <a href="../../form.html">意見・感想</a>\n'+f'<img src="{message.author.avatar_url}" width="72" height="72">'+'\
    </h2>\n\
    <style>\n\
    body{\n\
        background:#36393f;\n\
        color:#ffffff;\n\
    }\n\
    </style>\n\
</head>\n\
</html>'
                    f.write(default)
                    break
            else:
                pass

        login_data_dict[f"{message.author.id}"] = [passwd, file_name]
        with open("/var/www/html/discord/login_data.json", mode="w") as f:
            login_data_json = json.dumps(login_data_dict, indent=4)
            f.write(login_data_json)
        await message.author.send(passwd)
        embed = discord.Embed(title="DMにパスワードを送信しました", description="パスワードは[けいのウェブサイト](http://www.kei-3104.com) で使用できます")
        await message.channel.send(embed=embed)
    else:
        await message.channel.send("既にIDを持っています")'''


async def count_members(client1):
    """
    サーバにいる人数を数えて記録する関数"""

    with open("./datas/count_members.json", mode="r") as f:
        members_dict = json.load(f)
    today = datetime.date.today().strftime(r"%Y%m%d")
    guild = client1.get_guild(585998962050203672)
    members_dict[today] = len(guild.members)
    with open("./datas/count_members.json", mode="w") as f:
        members_json = json.dumps(members_dict, indent=4)
        f.write(members_json)


async def change_date(client1):
    """
    日付変更お知らせ用関数"""

    notice_ch = client1.get_channel(710021903879897098)
    today = datetime.date.today()

    today_str = today.strftime(r"%Y/%m/%d")
    finished_percentage = round((datetime.date.today().timetuple()[7] - 1) / 365 * 100, 2) #正直動きがわからないのとうるう年はバグる
    if datetime.date.today() >= datetime.date(today.year, 6, 29):
        year_seichi = today.year + 1
    else:
        year_seichi = today.year
    seichisaba_birthday = datetime.date(year_seichi, 6, 29)
    how_many_days = str(seichisaba_birthday - today)
    how_many_days = how_many_days.replace(how_many_days[-13:], "")
    text = (
        f"本日の日付: {today_str}\n"
        f"{today.year}年の{finished_percentage}%が終了しました\n"
        f"整地鯖{year_seichi-2016}周年まであと{how_many_days}日です"
    )

    daily_embed = discord.Embed(title=f"日付変更をお知らせします", description=text, color=0xfffffe)

    yesterday_str = (today - datetime.timedelta(days=1)).strftime(r"%Y%m%d")
    before_yesterday_str = (today - datetime.timedelta(days=2)).strftime(r"%Y%m%d")
    with open("./datas/count_message.json", mode="r") as f:
        message_dict = json.load(f)
    yesterday_messages = message_dict[yesterday_str]
    before_yesterday_messages = message_dict[before_yesterday_str]
    plus_minus = yesterday_messages - before_yesterday_messages
    if plus_minus > 0:
        plus_minus = f"+{plus_minus}"
    else:
        plus_minus = f"{plus_minus}"
    daily_embed.add_field(name="messages", value=f"昨日の発言数: {yesterday_messages}\n前日比: {plus_minus}", inline=True)

    with open("./datas/count_members.json", mode="r") as f:
        members_dict = json.load(f)
    today_members = members_dict[datetime.date.today().strftime(r"%Y%m%d")]
    yesterday_members = members_dict[yesterday_str]
    plus_minus = today_members - yesterday_members
    if plus_minus > 0:
        plus_minus = f"+{plus_minus}"
    else:
        plus_minus = f"{plus_minus}"
    daily_embed.add_field(name="members", value=f"今の人数: {today_members}\n前日比: {plus_minus}", inline=True)

    await notice_ch.send(embed=daily_embed)


async def add_interest(client1):
    """
    保有ptに応じた利子を付与する関数"""

    with open("./datas/user_data.json", mode="r") as f:
        user_data_dict = json.load(f)

    notice_ch = client1.get_channel(585999375952642067)
    for user_id in user_data_dict:
        point = user_data_dict[user_id]["point"]
        if point <= 128:
            rishi = 1.2
        elif point <= 576:
            rishi = 1.1
        elif point <= 1728:
            rishi = 1.05
        elif point <= 3456:
            rishi = 1.01
        else:
            rishi = 1
        after_pt = math.floor(point*rishi)
        user_data_dict[user_id]["point"] = after_pt

    with open("./datas/user_data.json", mode="w") as f:
        user_data_json = json.dumps(user_data_dict, indent=4)
        f.write(user_data_json)

    await notice_ch.send("利子を付与しました")


async def setting_kazuate(client1):
    """
    数当てをセットする"""

    with open("./datas/kazuate.txt", mode="r", encoding="utf-8") as f:
        seikai = f.read().split()[0]

    with open("./datas/kazuate.txt", mode="w", encoding="utf-8") as f:
        f.write(f"{random.randint(1, 999)} 0")

    ch = client1.get_channel(770163289006800927)
    await ch.edit(topic="")
    if seikai == "None":
        await ch.send("セッティング完了")
    else:
        await ch.send(f"正解は{seikai}でした")
        await ch.send("セッティング完了")


async def hint_kazuate(client1, weekday):
    """
    数当てのヒントを出す"""

    hint_range = [
        None,
        100,
        None,
        None,
        500,
        None,
        300
    ]

    ch = client1.get_channel(770163289006800927)
    with open("./datas/kazuate.txt", mode="r", encoding="utf-8") as f:
        kazuate_list = f.read().split()

    try:
        seikai = int(kazuate_list[0])
    except ValueError:
        await ch.edit(topic="既にあたりが出ています")
        return
    kazu = int(kazuate_list[1])

    low = random.randint(0, hint_range[weekday])
    high = random.randint(0, hint_range[weekday])
    low = seikai - low
    high = seikai + high
    if low <= 0:
        low = 1
    if high >= 1000:
        high = 999
    text = f"{low} ~ {high}"
    await ch.edit(topic=text)

    with open("./datas/kazuate.txt", mode="w", encoding="utf-8") as f:
        f.write(f"{seikai} {kazu+100}")


async def kikaku(message):
    """
    企画用"""

    if message.author.bot:
        return

    kikaku_role = discord.utils.get(message.guild.roles, id=668021019700756490)
    if message.content == "/cancel":
        if kikaku_role in message.author.roles:
            await message.author.remove_roles(kikaku_role)
            await message.channel.send(f"{message.author.name}さんがキャンセルしました")
        else:
            await message.channel.send(f"{message.author.name}さんはまだ企画に参加していません")
        return

    now = datetime.datetime.now()
    finish_time = datetime.datetime(2021, 1, 1, 0, 0)
    if now >= finish_time:
        await message.channel.send("現在企画は行われていません")
        return

    if kikaku_role in message.author.roles:
        await message.channel.send(f"{message.author.name}さんは既に参加しています")
        return

    mcid = message.content.replace("\_", "_")
    with open("./datas/user_data.json", mode="r") as f:
        user_data_dict = json.load(f)

    mcid_list = user_data_dict[f"{message.author.id}"]["mcid"]
    flag = False
    for mcid_applicationed in mcid_list:
        if mcid.lower() == mcid_applicationed.lower():
            flag = True
            break

    if not flag:
        mcid_list = str(mcid_list).replace("_", "\_")
        await message.channel.send(f"そのMCIDは登録されていません。\n現在登録されているMCID{mcid_list}")
        return

    await message.author.add_roles(kikaku_role)
    await message.channel.send(f"{message.author.name}さんが参加しました")


async def kikaku_announcement(client1):
    """
    当選発表"""

    guild = client1.get_guild(585998962050203672)
    kikaku_role = discord.utils.get(guild.roles, id=668021019700756490)
    tousen = random.sample(kikaku_role.members, k=3)

    tousen_role = discord.utils.get(guild.roles, id=669720120314167307)
    tousen[0].add_roles(tousen_role)
    tousen[1].add_roles(tousen_role)
    tousen[2].add_roles(tousen_role)

    embed = discord.Embed(title=":tada:おめでとう:tada:", description=f"1等: {tousen[0].mention}\n2等: {tousen[1].mention}, {tousen[2].mention}", color=0xffff00)
    ch = client1.get_channel(586420858512343050)
    await ch.send(content="<@&668021019700756490>", embed=embed)
    await ch.send("**受け取り期日は2021/1/15までとします。**ただし、事情により期限内に受け取れない場合期限内に言っていただければ対応します。")