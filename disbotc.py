import datetime
import json
import os
import traceback
#from collections import namedtuple

import aiohttp
import discord
import requests
from discord.ext import tasks

import common
import custom_commands_exe
import emoji_server
import iroha
import kei_server
import muhou
import server_log

intents = discord.Intents.all()
client1 = discord.Client(intents=intents)
os.chdir(os.path.dirname(os.path.abspath(__file__)))

discord_bot_token_1 = os.getenv("discord_bot_token_1")
where_from = os.getenv("where_from")
error_notice_webhook_url = os.getenv("error_notice_webhook")


def unexpected_error(msg=None):
    """
    予期せぬエラーが起きたときの対処
    エラーメッセージ全文と発生時刻を通知"""

    try:
        if msg is not None:
            content = (
                f"{msg.author}\n"
                f"{msg.content}\n"
                f"{msg.channel.name}\n"
            )
        else:
            content = ""
    except:
        unexpected_error()
        return

    now = datetime.datetime.now().strftime("%H:%M") #今何時？
    error_msg = f"```\n{traceback.format_exc()}```" #エラーメッセージ全文
    error_content = {
        "content": "<@523303776120209408>", #けいにメンション
        "avatar_url": "https://cdn.discordapp.com/attachments/644880761081561111/703088291066675261/warning.png",
        "embeds": [ #エラー内容・発生時間まとめ
            {
                "title": "エラーが発生しました",
                "description": content + error_msg,
                "color": 0xff0000,
                "footer": {
                    "text": now
                }
            }
        ]
    }
    requests.post(error_notice_webhook_url, json.dumps(error_content), headers={"Content-Type": "application/json"}) #エラーメッセをウェブフックに投稿


@client1.event
async def on_ready():
    try:
        login_notice_ch = client1.get_channel(595072269483638785)
        with open("./datas/version.txt", mode="r", encoding="utf-8") as f:
            version = f.read()
        await login_notice_ch.send(f"{client1.user.name}がログインしました(from: {where_from})\nversion: {version}")

    except:
        unexpected_error()


@client1.event
async def on_guild_channel_create(channel):
    try:
        guild_name = channel.guild.name

        if type(channel) == discord.CategoryChannel:
            ch_description = f"{guild_name}でカテゴリチャンネル「{channel.name}」が作成されました"
        elif type(channel) == discord.VoiceChannel:
            ch_description = f"{guild_name}でボイスチャンネル「{channel.name}」が作成されました"
        else:
            ch_description = f"{guild_name}でテキストチャンネル「{channel.name}」が作成されました\n{channel.mention}"
        
        now = datetime.datetime.now().strftime(r"%Y/%m/%d　%H:%M")
        ch_embed = discord.Embed(title="チャンネル作成", description=ch_description, color=0xfffffe)
        ch_embed.set_footer(text=now, icon_url=channel.guild.icon_url)
        ch_notice_ch = client1.get_channel(682732694768975884)
        await ch_notice_ch.send(embed=ch_embed)

        #ログ取りのための部分
        if type(channel) == discord.CategoryChannel or type(channel) == discord.VoiceChannel:
            return
        if channel.guild.id == 585998962050203672 or channel.guild.id == 604945424922574848: #けい鯖、いろは鯖なら
            with open("./datas/channels_id.json", mode="r") as f:
                channels_id_dict = json.load(f)
            if channel.guild.id == 585998962050203672: #けい鯖
                log_server = client1.get_guild(707794528848838676)
            if channel.guild.id == 604945424922574848: #いろは鯖
                log_server = client1.get_guild(660445544296218650)

            new_ch = await log_server.create_text_channel(name=channel.name, position=channel.position)
            channels_id_dict[f"{channel.id}"] = new_ch.id

            with open("./datas/channels_id.json", mode="w") as f:
                channels_id_json = json.dumps(channels_id_dict, indent=4)
                f.write(channels_id_json)

    except:
        unexpected_error()


@client1.event
async def on_guild_channel_update(before, after):
    try:
        guild_name = before.guild.name

        if before.name != after.name:
            if type(before) == discord.CategoryChannel:
                ch_description = f"{guild_name}のカテゴリチャンネル「{before.name}」が「{after.name}」に変更されました"
            elif type(before) == discord.VoiceChannel:
                ch_description = f"{guild_name}のボイスチャンネル「{before.name}」が「{after.name}」に変更されました"
            else:
                ch_description = f"{guild_name}のテキストチャンネル「{before.name}」が「{after.name}」に変更されました\n{after.mention}"
            
            now = datetime.datetime.now().strftime(r"%Y/%m/%d　%H:%M")
            ch_embed = discord.Embed(title="チャンネルアップデート", description=ch_description, color=0x0000ff)
            ch_embed.set_footer(text=now, icon_url=before.guild.icon_url)
            ch_notice_ch = client1.get_channel(682732694768975884)
            await ch_notice_ch.send(embed=ch_embed)

        if before.guild.id == 585998962050203672 or before.guild.id == 604945424922574848: #けい鯖、いろは鯖なら
            if type(before) == discord.CategoryChannel or type(before) == discord.VoiceChannel:
                return

            with open("./datas/channels_id.json", mode="r") as f:
                channels_id_dict = json.load(f)
            try:
                log_channel_id = channels_id_dict[f"{before.id}"]
            except KeyError:
                notice_ch = client1.get_channel(636359382359080961) #python開発やることリスト
                await notice_ch.send(f"<@523303776120209408>\n{guild_name}:{before.name}→{after.name}\n{after.mention}")
            else:
                log_channel = client1.get_channel(log_channel_id)
                await log_channel.edit(name=after.name, position=after.position)

    except:
        unexpected_error()


@client1.event
async def on_guild_channel_delete(channel):
    try:
        guild_name = channel.guild.name

        if type(channel) == discord.CategoryChannel:
            channel_type = "カテゴリチャンネル"
        elif type(channel) == discord.VoiceChannel:
            channel_type = "ボイスチャンネル"
        else:
            channel_type = "テキストチャンネル"

        now = datetime.datetime.now().strftime(r"%Y/%m/%d　%H:%M")
        ch_description = f"{guild_name}で{channel_type}「{channel.name}」が削除されました"
        ch_embed = discord.Embed(title="チャンネル削除", description=ch_description, color=0xff0000)
        ch_embed.set_footer(text=now, icon_url=channel.guild.icon_url)
        ch_notice_ch = client1.get_channel(682732694768975884)
        await ch_notice_ch.send(embed=ch_embed)
        if channel.guild.id == 585998962050203672 or channel.guild.id == 604945424922574848: #けい鯖、いろは鯖なら
            with open("./datas/channels_id.json", mode="r") as f:
                channels_id_dict = json.load(f)
            try:
                del channels_id_dict[f"{channel.id}"]
            except KeyError:
                pass
            else:
                with open("./datas/channels_id.json", mode="w") as f:
                    channels_id_json = json.dumps(channels_id_dict, indent=4)
                    f.write(channels_id_json)

    except:
        unexpected_error()


@client1.event
async def on_guild_join(guild):
    try:
        with open("./datas/ban_server.json", mode="r", encoding="utf-8") as f:
            ban_server_list = json.load(f)

        for ban_server in ban_server_list:
            if guild.id == ban_server[0]:
                await guild.leave()
                return

        title = "よろしくお願いします!!"
        description = f"初めましての方は初めまして、そうでない方はまたお会いしましたね。けい制作の{client1.user.name}です。\n"
        description += f"このbotを{guild.name}に導入していただきありがとうございます。\n"
        description += "皆様にお願いしたいことがあります。このbotに極度に負荷をかけるような行為をしないでください。\n"
        description += "バグ、不具合等問題がありましたら`/bug_report`コマンドで報告ができます\n"
        description += "追加してほしい機能がありましたら`/new_func`コマンドで追加申請ができます(現在管理者持ち以外も実行できてしまいます。いずれ使えなくしておきます)\n"
        description += "問題がなかったらお楽しみください。\n"
        description += "最後に[私のサーバ](https://discord.gg/nrvMKBT)を宣伝・紹介させてください。"
        description += "このbotについてもっと知りたい、このbotを招待したい、けいの活動に興味がある、理由は何でも構いません。ぜひ見ていってください"
        self_introduction_embed = discord.Embed(title=title, description=description, color=0xffff00)
        kei = client1.get_user(523303776120209408)
        self_introduction_embed.set_footer(text="←作った人", icon_url=kei.avatar_url_as(format="png"))

        notice_from_marisa_ch_id = None
        try:
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(send_messages=False),
                guild.me: discord.PermissionOverwrite(send_messages=True)
            }
            ch = await guild.create_text_channel(
                name="魔理沙からのお知らせ",
                overwrites=overwrites,
                position=0,
                topic="魔理沙botに関するお知らせが投稿されます",
                reason="魔理沙botの機能確保のため"
            )
        except discord.errors.Forbidden:
            for ch in guild.text_channels:
                try:
                    await ch.send(embed=self_introduction_embed)
                    notice_from_marisa_ch_id = ch.id
                    break
                except discord.errors.Forbidden:
                    pass
        else:
            await ch.send(embed=self_introduction_embed)
            notice_from_marisa_ch_id = ch.id

        with open("./datas/marisa_notice.json", mode="r", encoding="utf-8") as f:
            marisa_notice_dict = json.load(f)

        marisa_notice_dict[f"{guild.id}"] = notice_from_marisa_ch_id

        with open("./datas/marisa_notice.json", mode="w", encoding="utf-8") as f:
            marisa_notice_json = json.dumps(marisa_notice_dict, indent=4)
            f.write(marisa_notice_json)

        for ch in guild.text_channels:
            try:
                invite_url = await ch.create_invite(reason="けいを招待するため")
                await kei.send(invite_url)
                break
            except discord.errors.Forbidden:
                pass
    except:
        unexpected_error()


@client1.event
async def on_member_join(member):
    try:
        if member.guild.id == 585998962050203672:
            await kei_server.on_member_join(client1, member)

        if member.guild.id == 604945424922574848:
            await iroha.on_member_join(client1, member)

        if member.guild.id == 587909823665012757:
            await muhou.on_member_join(client1, member)

    except:
        unexpected_error()

@client1.event
async def on_member_remove(member):
    try:
        if member.guild.id == 585998962050203672:
            await kei_server.on_member_remove(client1, member)

    except:
        unexpected_error()


@client1.event
async def on_message(message):
    if message.content == "/bot_stop":
        kei_ex_guild = client1.get_guild(585998962050203672)
        bot_stop_right_role = discord.utils.get(kei_ex_guild.roles, id=707570554462273537)
        if not bot_stop_right_role in message.author.roles:
            await message.channel.send("何様のつもり？")
            return

        now = datetime.datetime.now().strftime(r"%Y年%m月%d日　%H:%M")
        stop_msg = f"{message.author.mention}により{client1.user.name}が停止させられました"
        main_content = {
            "username": "BOT STOP",
            "avatar_url": "https://cdn.discordapp.com/attachments/644880761081561111/703088291066675261/warning.png",
            "content": "<@523303776120209408>",
            "embeds": [
                {
                    "title": "botが停止させられました",
                    "description": stop_msg,
                    "color": 0xff0000,
                    "footer": {
                        "text": now
                    }
                }
            ]
        }
        requests.post(error_notice_webhook_url, json.dumps(main_content), headers={"Content-Type": "application/json"}) #エラーメッセをウェブフックに投稿

        await client1.close()

    try:
        try:
            if message.content.startswith("#") or message.content.startswith("//") or (message.content.startswith(r"/\*") and message.content.endswith(r"\*/")):
                return

            if message.guild is None:
                return

            if client1.user in message.mentions:
                if not message.author.bot:
                    await message.channel.send(where_from)

            if message.guild.id == 585998962050203672 or message.guild.id == 604945424922574848: #けい鯖、いろは鯖なら
                await server_log.server_log_on_message(client1, message)

            if message.guild.id == 585998962050203672:
                await kei_server.on_message(client1, message)

            if message.guild.id == 604945424922574848:
                await iroha.on_message(client1, message)

            if message.content.startswith("/set_notice_ch"):
                await common.set_notice_ch(message)

            if message.content == "/check_notice_ch":
                await common.check_notice_ch(message)

            with open("./datas/custom_commands.json", mode="r", encoding="utf-8") as f:
                custom_commands_dict = json.load(f)

            if f"{message.guild.id}" in custom_commands_dict.keys():
                if message.author.bot:
                    return
                custom_commands = custom_commands_dict[f"{message.guild.id}"]
                await custom_commands_exe.on_message(client1, message, custom_commands)

        except (RuntimeError, aiohttp.client_exceptions.ServerDisconnectedError):
            pass
        except discord.errors.Forbidden:
            await message.channel.send("権限がありません")
    except:
        unexpected_error(msg=message)


@client1.event
async def on_message_edit(before, after):
    try:
        try:
            if before.guild is None:
                return

            if before.guild.id == 585998962050203672 or before.guild.id == 604945424922574848: #けい鯖、いろは鯖なら
                await server_log.server_log_on_message_update(client1, before, after)

        except (RuntimeError, aiohttp.client_exceptions.ServerDisconnectedError):
            pass
    except:
        unexpected_error()


@client1.event
async def on_message_delete(message):
    try:
        try:
            if message.guild is None:
                return

            if message.channel.guild.id == 585998962050203672 or message.channel.guild.id == 604945424922574848: #けい鯖、いろは鯖なら
                await server_log.server_log_on_message_delete(client1, message)

        except (RuntimeError, aiohttp.client_exceptions.ServerDisconnectedError):
            pass
    except:
        unexpected_error()


@client1.event
async def on_member_update(before, after):
    try:
        if before.guild.id == 585998962050203672:
            await kei_server.on_member_update(before, after)
    except:
        unexpected_error()


@client1.event
async def on_guild_emojis_update(guild, before, after):
    try:
        if guild.id == 735632039050477649:
            await emoji_server.emoji_update(client1, guild, before, after)

    except:
        unexpected_error()


@tasks.loop(seconds=60)
async def mcid_check():
    try:
        await client1.wait_until_ready()
        now = datetime.datetime.now()
        weekday = datetime.datetime.now().weekday()

        if weekday == 2 and now.hour == 20 and now.minute == 0:
            await kei_server.check_mcid_exist_now(client1)

    except:
        unexpected_error()
mcid_check.start()


@tasks.loop(seconds=60)
async def change_date():
    try:
        await client1.wait_until_ready()
        now = datetime.datetime.now()

        if now.hour == 0 and now.minute == 0:
            await kei_server.count_members(client1)
            await kei_server.change_date(client1)

    except:
        unexpected_error()
change_date.start()


@tasks.loop(seconds=60)
async def add_interest():
    try:
        await client1.wait_until_ready()
        now = datetime.datetime.now()
        weekday = now.weekday()

        if weekday == 6 and now.hour == 2 and now.minute == 0:
            await kei_server.add_interest(client1)

    except:
        unexpected_error()
#add_interest.start()


@tasks.loop(seconds=60)
async def delete_login_record():
    try:
        await client1.wait_until_ready()
        now = datetime.datetime.now()

        if now.hour == 0 and now.minute == 0:
            await iroha.delete_login_record()

    except:
        unexpected_error()
delete_login_record.start()


@tasks.loop(seconds=60)
async def change_login_record():
    try:
        await client1.wait_until_ready()
        now = datetime.datetime.now()

        if now.minute == 30:
            await iroha.change_login_record(client1)

    except:
        unexpected_error()
change_login_record.start()

@tasks.loop(seconds=60)
async def record_story():
    try:
        await client1.wait_until_ready()
        now = datetime.datetime.now()

        if now.weekday() == 0 and now.hour == 3 and now.minute == 15:
            await kei_server.record_story(client1)

    except:
        unexpected_error()
record_story.start()


@tasks.loop(seconds=60)
async def kikaku_announcement():
    try:
        await client1.wait_until_ready()
        now = datetime.datetime.now()

        if now.month == 3 and now.day == 28 and now.hour == 12 and now.minute == 0:
            await kei_server.kikaku_announcement(client1)
    except:
        unexpected_error()
#kikaku_announcement.start()


client1.run(os.getenv("discord_bot_token_1"))


"""
Entry = namedtuple("Entry", "client event token")
entries = [
    Entry(client=client1,event=asyncio.Event(),token=discord_bot_token_1),
    #Entry(client=client2,event=asyncio.Event(),token=discord_bot_token_2),
    #Entry(client=client4,event=asyncio.Event(),token=discord_bot_token_4)
]  

async def login():
    for e in entries:
        await e.client.login(e.token)

async def wrapped_connect(entry):
    try:
        await entry.client.connect()
    except Exception as e:
        await entry.client.close()
        print("We got an exception: ", e.__class__.__name__, e)
        entry.event.set()

async def check_close():
    futures = [e.event.wait() for e in entries]
    await asyncio.wait(futures)

loop = asyncio.get_event_loop()
loop.run_until_complete(login())
for entry in entries:
    loop.create_task(wrapped_connect(entry))
loop.run_until_complete(check_close())
loop.close()"""
