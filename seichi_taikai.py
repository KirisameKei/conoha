import datetime
import math
import json

import discord


async def seichi_result(client1):
    with open("./datas/kikaku.json", mode="r", encoding="utf-8") as f:
        kikaku_data_dict = json.load(f)

    yesterday = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y%m%d")
    with open(f"../graph_v3/player_data_break_{yesterday}.json", mode="r", encoding="utf-8") as f:
        player_data_dict = json.load(f)

    rank = 1
    for player_data in sorted(player_data_dict.values(), key=lambda x: -x["all"]):
        if rank == 20:
            daily_20th_score = player_data["all"]
            break
        else:
            rank += 1

    if daily_20th_score >= 10000000:
        ninzuu_housyu = 16
    else:
        ninzuu_housyu = 0

    for uuid in kikaku_data_dict.keys():
        kikaku_data = kikaku_data_dict[uuid]
        try:
            kikaku_data["score"] = player_data_dict[uuid]["all"]
        except KeyError:
            kikaku_data["score"] = 0

    sankasya_data_dict = {}
    for uuid, value in sorted(kikaku_data_dict.items(), key=lambda x: -x[1]["score"]):
        sankasya_data_dict[uuid] = value

    rank = 0
    loop = 0
    page = math.ceil(len(sankasya_data_dict) / 10)
    for value in sankasya_data_dict.values():
        if (rank % 10) == 0:
            loop += 1
            description = ""

        user_id = value["user_id"]
        mcid = value["mcid"]
        score = value["score"]
        if rank == 0:
            jyunni_housyu = 192
        elif rank == 1:
            jyunni_housyu = 128
        elif rank == 2:
            jyunni_housyu = 64
        else:
            jyunni_housyu = 0

        if score >= 31040000:
            tairyo_saikutsu_housyu = 64
        else:
            tairyo_saikutsu_housyu = 0

        if score % 3104 == 0:
            tyousei_housyu = math.floor((score * 0.01) / 3104)
        else:
            tyousei_housyu = 0

        for i in range(16-len(mcid)):
            mcid += " "
        mcid = mcid.replace("_", "\_")

        score = "{:,}".format(score)

        description += (
            f"<@{user_id}>\n"
            f"{mcid}: {rank+1}位: {score}\n"
            f"    順位報酬　　: {int(jyunni_housyu/64)}st\n"
            f"    大量採掘報酬: {int(tairyo_saikutsu_housyu/64)}st\n"
        )
        st, ko = divmod(tyousei_housyu, 64)
        description += (
            f"    調整報酬　　: {st}st + {ko}個\n"
            f"    人数報酬　　: {ninzuu_housyu}個\n"
        )
        st, ko = divmod(jyunni_housyu+tairyo_saikutsu_housyu+tyousei_housyu+ninzuu_housyu, 64)
        description += f"    　**合計　: {st}st + {ko}個**\n"

        if (rank % 10) == 9:
            embed = discord.Embed(
                title=f"結果発表({loop}/{page})",
                description=description,
                color=0xffff00
            )
            #notice_ch = client1.get_channel(586420858512343050) #企画についてのお知らせ(本番用)
            notice_ch = client1.get_channel(595072269483638785) #1組
            if loop == 1:
                mention = "＠企画参加者" #"<@&668021019700756490>"
            else:
                mention=""
            await notice_ch.send(content=mention, embed=embed)

        rank += 1

    if len(sankasya_data_dict) % 10 != 0:
        embed = discord.Embed(
            title=f"結果発表({loop}/{page})",
            description=description,
            color=0xffff00
        )
        #notice_ch = client1.get_channel(586420858512343050) #企画についてのお知らせ(本番用)
        notice_ch = client1.get_channel(595072269483638785) #1組
        if loop == 1:
            #mention = "<@&668021019700756490>"
            mention = "＠企画参加者"
        else:
            mention=""
        await notice_ch.send(content=mention, embed=embed)
