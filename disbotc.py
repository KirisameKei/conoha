import asyncio
import datetime
import io
import json
import os
import subprocess
import traceback
from collections import namedtuple

import aiohttp
import discord
import requests
from discord.ext import tasks

import custom_commands_exe
import iroha
import kei_server
import muhou
import server_log

client1 = discord.Client()
os.chdir(os.path.dirname(os.path.abspath(__file__)))

try:
    import tokens_ConoHa
except ModuleNotFoundError: #けいローカル or heroku
    discord_bot_token_1 = os.getenv("discord_bot_token_1")
    where_from = os.getenv("where_from")
    error_notice_webhook_url = os.getenv("error_notice_webhook")
else: #ConoHa
    discord_bot_token_1 = tokens_ConoHa.discord_bot_token_1
    where_from = tokens_ConoHa.where_from
    error_notice_webhook_url = tokens_ConoHa.error_notice_webhook


def unexpected_error():
    """
    予期せぬエラーが起きたときの対処
    エラーメッセージ全文と発生時刻を通知"""

    now = datetime.datetime.now().strftime("%H:%M") #今何時？
    error_msg = f"```\n{traceback.format_exc()}```" #エラーメッセージ全文
    error_content = {
        "content": "<@523303776120209408>", #けいにメンション
        "avatar_url": "https://cdn.discordapp.com/attachments/644880761081561111/703088291066675261/warning.png",
        "embeds": [ #エラー内容・発生時間まとめ
            {
                "title": "エラーが発生しました",
                "description": error_msg,
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
        with open("version.txt") as f:
            version = f.read()
        await login_notice_ch.send(f"{client1.user.name}がログインしました(from: {where_from})\nversion: {version}")
        try:
            print(f"{client1.user.name}がログインしました")
        except UnicodeEncodeError:
            pass

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
            with open("channels_id.json", mode="r") as f:
                channels_id_dict = json.load(f)
            if channel.guild.id == 585998962050203672: #けい鯖
                log_server = client1.get_guild(707794528848838676)
            if channel.guild.id == 604945424922574848: #いろは鯖
                log_server = client1.get_guild(660445544296218650)

            new_ch = await log_server.create_text_channel(name=channel.name, position=channel.position)
            channels_id_dict[f"{channel.id}"] = new_ch.id

            with open("channels_id.json", mode="w") as f:
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

            with open("channels_id.json", mode="r") as f:
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
            with open("channels_id.json", mode="r") as f:
                channels_id_dict = json.load(f)
            try:
                del channels_id_dict[f"{channel.id}"]
            except KeyError:
                pass
            else:
                with open("channels_id.json", mode="w") as f:
                    channels_id_json = json.dumps(channels_id_dict, indent=4)
                    f.write(channels_id_json)

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

        when_from = (member.created_at + datetime.timedelta(hours=9)).strftime(r"%Y/%m/%d　%H:%M")
        member_embed = discord.Embed(title="╋", description=f"{member.mention}が{member.guild.name}に参加しました\n{when_from}からのdiscordユーザー", color=0xfffffe)
        member_embed.set_author(name=member.name, icon_url=member.avatar_url)
        member_embed.set_footer(text=member.guild.name, icon_url=member.guild.icon_url)
        join_leave_notice_ch = client1.get_channel(588224929300742154)
        await join_leave_notice_ch.send(embed=member_embed)

    except:
        unexpected_error()

@client1.event
async def on_member_remove(member):
    try:
        if member.guild.id == 585998962050203672:
            await kei_server.on_member_remove(client1, member)

        member_embed = discord.Embed(title="━", description=f"{member.mention}が{member.guild.name}から脱退しました", color=0xff0000)
        member_embed.set_author(name=member.name, icon_url=member.avatar_url)
        member_embed.set_footer(text=member.guild.name, icon_url=member.guild.icon_url)
        join_leave_notice_ch = client1.get_channel(588224929300742154)
        await join_leave_notice_ch.send(embed=member_embed)

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
        if message.content == "/ConoHa_stop":
            if not where_from == "ConoHa":
                return
            if not message.author.id == 523303776120209408:
                await message.channel.send("何様のつもり？")
                return
            notice_ch = client1.get_channel(708162800987668541)
            await notice_ch.send("ConoHa起動のbotを終了します")
            await client1.close()
        
        try:
            if message.content.startswith("#") or message.content.startswith("//") or (message.content.startswith(r"/\*") and message.content.endswith(r"\*/")):
                return

            if message.guild is None:
                return

            if message.guild.id == 585998962050203672 or message.guild.id == 604945424922574848: #けい鯖、いろは鯖なら
                await server_log.server_log_on_message(client1, message)

            if message.guild.id == 585998962050203672:
                await kei_server.on_message(client1, message)

            if message.guild.id == 604945424922574848:
                await iroha.on_message(client1, message)

            with open("custom_commands.json", mode="r", encoding="utf-8") as f:
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
        unexpected_error()


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


@tasks.loop(seconds=60)
async def mcid_check():
    try:
        await client1.wait_until_ready()
        now = datetime.datetime.now()
        weekday = datetime.datetime.now().weekday()

        if weekday == 4 and now.hour == 18 and now.minute == 0:
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
add_interest.start()


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
async def kikaku_announcement():
    try:
        await client1.wait_until_ready()
        now = datetime.datetime.now()

        if now.month == 6 and now.day == 30 and now.hour == 20 and now.minute == 10:
            await kei_server.kikaku_announcement(client1)
    except:
        unexpected_error()
kikaku_announcement.start()


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
loop.close()
