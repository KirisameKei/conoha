import json

import discord

async def set_notice_ch(message):
    """
    導入サーバすべてのお知らせチャンネルにお知らせを送信"""

    if not message.author.guild_permissions.administrator:
        await message.channel.send("このコマンドは管理者のみが使用できます")
        return

    with open("./datas/marisa_notice.json", mode="r", encoding="utf-8") as f:
        notice_ch_dict = json.load(f)

    if message.content == "/set_notice_ch":
        notice_ch_dict[f"{message.guild.id}"] = message.channel.id
        try:
            await message.channel.send("このチャンネルに全体通知を送信します")
        except discord.errors.Forbidden:
            await message.author.send("このチャンネルで魔理沙が喋ることはできません")

    elif message.content.startswith("/set_notice_ch "):
        if message.content.split()[1].lower() == "none":
            notice_ch_dict[f"{message.guild.id}"] = "rejected"
            await message.channel.send("全体通知受信を拒否しました")
        else:
            await message.channel.send("`/set_notice_ch`で実行チャンネルを通知チャンネルに、`/set_notice_ch None`で通知拒否")
    else:
        await message.channel.send("`/set_notice_ch`で実行チャンネルを通知チャンネルに、`/set_notice_ch None`で通知拒否")

    with open("./datas/marisa_notice.json", mode="w", encoding="utf-8") as f:
        notice_ch_json = json.dumps(notice_ch_dict, indent=4)
        f.write(notice_ch_json)


async def check_notice_ch(message):
    """
    全体通知チャンネルを確認する"""

    with open("./datas/marisa_notice.json", mode="r", encoding="utf-8") as f:
        notice_ch_dict = json.load(f)

    try:
        notice_ch_id = notice_ch_dict[f"{message.guild.id}"]
    except KeyError:
        notice_ch_dict[f"{message.guild.id}"] = "rejectd"
        notice_ch_id = notice_ch_dict[f"{message.guild.id}"]

    if notice_ch_id == "rejected":
        await message.channel.send("通知を拒否しています。`/set_notice_ch`を実行すると実行チャンネルで本botに関する通知を受け取れます")
        with open("./datas/marisa_notice.json", mode="w", encoding="utf-8") as f:
            notice_ch_json = json.dumps(notice_ch_dict, indent=4)
            f.write(notice_ch_json)
    else:
        await message.channel.send(f"<#{notice_ch_id}>")