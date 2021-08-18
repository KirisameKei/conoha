import datetime
import json

import bs4
import discord
import requests

async def on_member_join(client1, member):
    """
    いろは鯖に新規が来た時用役職
    user_data_dict[f"{member.id}"][ban]がtrueならキックする"""

    return

    """
    with open("./datas/user_data.json", mode="r") as f:
        user_data_dict = json.load(f)

    try:
        if user_data_dict[f"{member.id}"]["ban"]:
            join_leave_notice_ch = client1.get_channel(709307324170240079)
            await member.guild.kick(member)
            await join_leave_notice_ch.send(f"{member.mention}が{member.guild.name}に参加しようとしましたが失敗しました")
    except KeyError:
        pass"""


async def on_message(client1, message):
    pass