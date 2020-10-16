import datetime
import json

import discord

async def server_log_on_message(client1, message):
    """
    けい鯖、HJK、いろは鯖でメッセージが投稿されたときの関数"""

    with open("./datas/channels_id.json", mode="r") as f:
        channels_id_dict = json.load(f)
    try:
        log_channel_id = channels_id_dict[f"{message.channel.id}"]
    except KeyError:
        notice_ch = client1.get_channel(636359382359080961) #python開発やることリスト
        await notice_ch.send(f"<@523303776120209408>\n{message.channel.mention}の辞書登録あく！")
    else:
        log_channel = client1.get_channel(log_channel_id)
        if message.attachments or message.content or message.embeds:
            now = datetime.datetime.now().strftime("%H:%M")
            message_embed = discord.Embed(description=message.content, color=0xfffffe)
            message_embed.set_author(name=message.author.name,icon_url=message.author.avatar_url)
            message_embed.set_footer(text=now)
            if message.attachments:
                message_embed.set_image(url=message.attachments[0].url)
            if message.content or message.attachments:
                await log_channel.send(embed=message_embed)
            if len(message.attachments) >= 2:
                for attachment in message.attachments[1:]:
                    message_embed = discord.Embed().set_image(url=attachment.url)
                    await log_channel.send(embed=message_embed)
            for embed in message.embeds:
                await log_channel.send(embed=embed)


async def server_log_on_message_update(client1, before, after):
    """
    けい鯖、HJK、いろは鯖でメッセージが編集されたときの関数"""

    with open("./datas/channels_id.json", mode="r") as f:
        channels_id_dict = json.load(f)
    try:
        log_channel_id = channels_id_dict[f"{before.channel.id}"]
    except KeyError:
        notice_ch = client1.get_channel(636359382359080961) #python開発やることリスト
        await notice_ch.send(f"<@523303776120209408>\n{before.channel.mention}の辞書登録あく！")
    else:
        log_channel = client1.get_channel(log_channel_id)
        if before.attachments or before.content or before.embeds:
            now = datetime.datetime.now().strftime("%H:%M")
            message_embed = discord.Embed(description=f"**編集前**\n{before.content}", color=0x0000ff)
            message_embed.set_author(name=before.author.name, icon_url=before.author.avatar_url)
            message_embed.set_footer(text=now)
            if before.attachments:
                message_embed.set_image(url=before.attachments[0].url)
            if before.content or before.attachments:
                await log_channel.send(embed=message_embed)
            if len(before.attachments) >= 2:
                for attachment in before.attachments[1:]:
                    message_embed = discord.Embed().set_image(url=attachment.url)
                    await log_channel.send(embed=message_embed)
            for embed in before.embeds:
                await log_channel.send(content="編集前のembed", embed=embed)

        if after.attachments or after.content or after.embeds:
            message_embed = discord.Embed(description=f"**編集後**\n{after.content}", color=0x0000ff)
            message_embed.set_author(name=after.author.name, icon_url=after.author.avatar_url)
            message_embed.set_footer(text=now)
            if after.attachments:
                message_embed.set_image(url=after.attachments[0].url)
            if after.content or after.attachments:
                await log_channel.send(embed=message_embed)
            if len(after.attachments) >= 2:
                for attachment in after.attachments[1:]:
                    message_embed = discord.Embed().set_image(url=attachment.url)
                    await log_channel.send(embed=message_embed)
            for embed in after.embeds:
                await log_channel.send(content="編集後のembed", embed=embed)


async def server_log_on_message_delete(client1, message):
    """
    けい鯖、HJK、いろは鯖でメッセージが削除されたときの関数"""

    with open("./datas/channels_id.json", mode="r") as f:
        channels_id_dict = json.load(f)
    try:
        log_channel_id = channels_id_dict[f"{message.channel.id}"]
    except KeyError:
        pass
    else:
        log_channel = client1.get_channel(log_channel_id)
        if message.attachments or message.embeds or message.content:
            now = datetime.datetime.now().strftime("%H:%M")
            message_embed = discord.Embed(description=message.content, color=0xff0000)
            message_embed.set_author(name=message.author.name,icon_url=message.author.avatar_url)
            message_embed.set_footer(text=now)
            if message.attachments:
                message_embed.set_image(url=message.attachments[0].url)
            if message.content or message.attachments:
                await log_channel.send(embed=message_embed)
            if len(message.attachments) >= 2:
                for attachment in message.attachments[1:]:
                    message_embed = discord.Embed().set_image(url=attachment.url)
                    await log_channel.send(embed=message_embed)
            for embed in message.embeds:
                await log_channel.send(embed=embed, content="削除されたembed")