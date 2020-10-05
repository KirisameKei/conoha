import asyncio
import datetime
import re

import discord

async def quote_message(client1, message, url):
    """
    メッセージリンク展開用関数"""

    id_list = url.split("/")
    try:
        guild_id = int(id_list[0])
        channel_id = int(id_list[1])
        message_id = int(id_list[2].split()[0])
    except ValueError:
        await message.channel.send("メッセージリンクを魔改造しないでください")
        return

    channel = client1.get_channel(channel_id)
    if channel is None:
        guild_name = ""
        if id_list[0] == "237758724121427969":
            guild_name = "整地鯖"
        elif id_list[0] == "558125111081697300":
            guild_name = "KGx"

        faild_embed = discord.Embed(title="404", description=guild_name)
        await message.channel.send(embed=faild_embed)
        return

    try:
        msg = await channel.fetch_message(message_id)

        def quote_reaction(msg, embed):
            if msg.reactions:
                reaction_send = ""
                for reaction in msg.reactions:
                    emoji = reaction.emoji
                    count = str(reaction.count)
                    reaction_send = f"{reaction_send}{emoji}{count}"
                embed.add_field(name="reaction", value=reaction_send, inline=False)
            return embed

        if msg.content or msg.embeds or msg.attachments:
            embed = discord.Embed(description=f"{msg.content}\n\n[リンク](https://discordapp.com/channels/{guild_id}/{channel_id}/{message_id})", timestamp=msg.created_at)
            embed.set_author(name=msg.author, icon_url=msg.author.avatar_url_as(format="png"))
            embed.set_footer(text=msg.channel.name, icon_url=msg.guild.icon_url_as(format="png"))
            if msg.attachments:
                embed.set_image(url=msg.attachments[0].url)
            embed = quote_reaction(msg, embed)
            await message.channel.send(embed=embed)

            if len(msg.attachments) >= 2:
                for attachment in msg.attachments[1:]:
                    embed = discord.Embed().set_image(url=attachment.url)
                    await message.channel.send(embed=embed)

            for embed in msg.embeds:
                embed = quote_reaction(msg, embed)
                await message.channel.send(embed=embed)

        else:
            await message.channel.send("メッセージはありますが内容がありません")
    except discord.errors.NotFound:
        await message.channel.send("メッセージが見つかりません")


async def form_link(message):
    """
    各フォームへのリンク"""

    if message.content == "/report":
        await message.channel.send("https://docs.google.com/forms/d/e/1FAIpQLSfK9DQkUCD2qs8zATUuYIC3JuV3MyXRVCYjMb5g4g_hBUusSA/viewform")
    if message.content == "/failure":
        await message.channel.send("https://docs.google.com/forms/d/e/1FAIpQLSdn9fTTs55c-oGLT3c68KVTGvfUjTK-W_cdataU7_XyzqcBRg/viewform")
    if message.content == "/idea":
        await message.channel.send("http://w4.minecraftserver.jp/ideaForm")
    if message.content == "/opinion":
        await message.channel.send("https://docs.google.com/forms/d/e/1FAIpQLSctLrByNvAiQop2lha9Mxn-D5p1OUaOf8JKQJCyAdggGBbzpg/viewform?c=0&w=1")
    if message.content == "/donation":
        await message.channel.send("https://docs.google.com/forms/d/e/1FAIpQLSezwur20tx0JCQ0KMY0JiThYy7oEQDykFRiic96KxK17WOBwA/viewform?c=0&w=1")
    if message.content == "/inquiry":
        await message.channel.send("https://w4.minecraftserver.jp/inquiryForm")
    if message.content == "/formal":
        await message.channel.send("https://www.seichi.network/gigantic")
    if message.content == "/informal":
        await message.channel.send("https://seichi-click-network.sokuhou.wiki/")

    if message.content == "/form":
        embed = discord.Embed(title="各フォームへのリンク一覧",color=0xff0000)
        embed.add_field(name="通報フォーム",value="https://docs.google.com/forms/d/e/1FAIpQLSfK9DQkUCD2qs8zATUuYIC3JuV3MyXRVCYjMb5g4g_hBUusSA/viewform",inline=False)
        embed.add_field(name="不具合フォーム",value="https://docs.google.com/forms/d/e/1FAIpQLSdn9fTTs55c-oGLT3c68KVTGvfUjTK-W_cdataU7_XyzqcBRg/viewform",inline=False)
        embed.add_field(name="アイデアフォーム",value="http://w4.minecraftserver.jp/ideaForm",inline=False)
        embed.add_field(name="意見・感想フォーム",value="https://docs.google.com/forms/d/e/1FAIpQLSctLrByNvAiQop2lha9Mxn-D5p1OUaOf8JKQJCyAdggGBbzpg/viewform?c=0&w=1",inline=False)
        embed.add_field(name="寄付フォーム",value="https://docs.google.com/forms/d/e/1FAIpQLSezwur20tx0JCQ0KMY0JiThYy7oEQDykFRiic96KxK17WOBwA/viewform?c=0&w=1",inline=False)
        embed.add_field(name="お問い合わせフォーム",value="https://w4.minecraftserver.jp/inquiryForm",inline=False)
        await message.channel.send(embed=embed)


async def help(message):
    """
    ヘルプ表示用関数"""

    help_embed = discord.Embed(title="魔理沙botのヘルプ", color=0x00aa00)
    
    common_help_key = "**/help**"
    common_help_key += "\n**/new_func**"
    common_help_key += "\n**/bug_report**"
    common_help_key += "\n**/report**"
    common_help_key += "\n**/failure**"
    common_help_key += "\n**/idea**"
    common_help_key += "\n**/opinion**"
    common_help_key += "\n**/donation**"
    common_help_key += "\n**/inquiry**"
    common_help_key += "\n**/formal**"
    common_help_key += "\n**/informal**"
    common_help_key += "\n**/form**"
    common_help_value = "このヘルプを表示します"
    common_help_value += "\n機能追加の申請をします"
    common_help_value += "\n不具合の報告をします"
    common_help_value += "\n通報フォームへのリンクを表示します"
    common_help_value += "\n不具合フォームへのリンクを(ry"
    common_help_value += "\nアイデアフォームへの(ry"
    common_help_value += "\n意見・感想フォーム(ry"
    common_help_value += "\n寄付(ry"
    common_help_value += "\nお問い合わせ(ry"
    common_help_value += "\n公式HPへのリンクを表示します"
    common_help_value += "\n非公式wikiへのリンクを(ry"
    common_help_value += "\n上記のフォームへのリンクをまとめました"
    help_embed.add_field(name="全サーバ共通のコマンド", value=common_help_key, inline=True)
    help_embed.add_field(name="挙動", value=common_help_value, inline=True)

    common_help = "・メッセージリンクを貼ると展開します"
    common_help += "\n・MEE6の発言に:middle_finger:をつけます"
    common_help += "\n・挨拶やお礼に反応します"
    common_help += "\n・「少し放置」と「学校終わって三条」にendリアクションを付けます"
    help_embed.add_field(name="全サーバ共通の機能", value=common_help, inline=False)

    if message.guild.id == 585998962050203672: #けい鯖
        local_help_key = "**/test_member**"
        local_help_key += "\n**/not test_member**"
        local_help_key += "\n**/info␣[role, guild, user, ch]␣ID**\n"
        local_help_key += "\n**/mypt**"
        local_help_key += "\n**/user_data␣ID** or **/user_data**\n"
        local_help_key += "\n**/hide␣me or ID**\n"
        local_help_key += "\n**/find␣me or ID**\n"
        local_help_key += "\n**/last_login␣MCID**"
        local_help_key += "\n**/weather␣[map, 地点名]**"
        local_help_key += "\n**/name␣n**"
        local_help_key += "\n**/break␣MCID**"
        local_help_key += "\n**/mcavatar MCID**"
        local_help_key += "\n**/vote␣args**"
        local_help_key += "\n**/ranking␣[point, speak]**"
        local_help_key += "\n**/random␣[choice, sample, choices, randint]**"
        local_help_value = "実験台役職を付与(危険)"
        local_help_value += "\n実験台役職を剥奪"
        local_help_value += "\n役職, サーバ, ユーザ、チャンネルの情報を表示"
        local_help_value += "\n現在の自分の保有ptを確認"
        local_help_value += "\nユーザーの本鯖での役職、MCID、ポイント、発言数を表示"
        local_help_value += "\nmeで自分に、IDで指定ユーザーにかくれんぼなう役職を付与"
        local_help_value += "\nmeで自分の、IDで指定ユーザーのかくれんぼなう役職を剥奪"
        local_help_value += "\nMCIDの整地鯖最終ログイン日時を表示"
        local_help_value += "\n天気図、地点名の天気予報を表示"
        local_help_value += "\nn文字の名前を生成"
        local_help_value += "\nMCIDの整地量、順位、Lvを表示"
        local_help_value += "\nMCIDのスキンを表示"
        local_help_value += "\n投票用コマンド"
        local_help_value += "\n各種ランキングを表示"
        local_help_value += "\n説明めんどい。python分かる人用"

        local_help = "・<#664286990677573680>のメッセージにリアクションを付けると役職が着脱されます"
        local_help += "\n・発言のログが取られています"
        local_help += "\n・<#634602609017225225>で発言すると確率でポイントが貰えます"
        local_help += "\n・毎週日曜日に保有ptに報じた利子が付与されます(多くのptを保有するほど利率は低くなります)"
        local_help += "\n・毎週日曜日にしりとりチャンネルをリセットします"
        local_help += "\n・しりとりチャンネルで「ん」か「ン」で終わるメッセージを投稿すると続けてくれます"
        local_help += "\n・毎日9:10にJMS notice役職持ちにメンションを飛ばします"
        local_help += "\n・毎日日付変更をお知らせし、本鯖のステータスを表示します"
        local_help += "\n・毎週金曜日にMCIDを変更した人に対し変更申請を促します"

    if message.guild.id == 604945424922574848: #いろは鯖
        local_help_key = "**/info␣[role, guild, user, ch]␣ID**\n"
        local_help_key += "\n**/last_login␣MCID**"
        local_help_key += "\n**/weather␣[map, 地点名]**"
        local_help_key += "\n**/break␣MCID**"
        local_help_key += "\n**/mcavatar MCID**"
        local_help_key += "\n**/vote␣args**"
        local_help_key += "\n**/random␣[choice, sample, choices, randint]**"
        local_help_value = "役職, サーバ, ユーザ、チャンネルの情報を表示"
        local_help_value += "\nMCIDの整地鯖最終ログイン日時を表示"
        local_help_value += "\n天気図、地点名の天気予報を表示"
        local_help_value += "\nMCIDの整地量、順位、Lvを表示"
        local_help_value += "\nMCIDのスキンを表示"
        local_help_value += "\n投票用コマンド"
        local_help_value += "\n説明めんどい。python分かる人用"

        local_help = "・いろは鯖(MC)のログイン情報が記録されています"
        local_help += "\n・発言のログが取られています"
        local_help += "\n・いろは鯖(MC)でのイベントに反応します"

    if message.guild.id == 587909823665012757: #無法地帯
        local_help_key = "**/info␣[role, guild, user, ch]␣ID**\n"
        local_help_key += "\n**/last_login␣MCID**"
        local_help_key += "\n**/weather␣[map, 地点名]**"
        local_help_key += "\n**/break␣MCID**"
        local_help_key += "\n**/mcavatar MCID**"
        local_help_key += "\n**/vote␣args**"
        local_help_key += "\n**/random␣[choice, sample, choices, randint]**"
        local_help_value = "役職, サーバ, ユーザ、チャンネルの情報を表示"
        local_help_value += "\nMCIDの整地鯖最終ログイン日時を表示"
        local_help_value += "\n天気図、地点名の天気予報を表示"
        local_help_value += "\nMCIDの整地量、順位、Lvを表示"
        local_help_value += "\nMCIDのスキンを表示"
        local_help_value += "\n投票用コマンド"
        local_help_value += "\n説明めんどい。python分かる人用"

        local_help = "・MEE6の発言に悪態をつきます"
        local_help += "\n・週に一度サーバアイコンを変更します"

    if message.guild.id == 673838958303641620: #のねむ鯖
        local_help_key = "**/info␣[role, guild, user, ch]␣ID**\n"
        local_help_key += "\n**/last_login␣MCID**"
        local_help_key += "\n**/weather␣[map, 地点名]**"
        local_help_key += "\n**/break␣MCID**"
        local_help_key += "\n**/mcavatar MCID**"
        local_help_key += "\n**/vote␣args**"
        local_help_key += "\n**/random␣[choice, sample, choices, randint]**"
        local_help_value = "役職, サーバ, ユーザ、チャンネルの情報を表示"
        local_help_value += "\nMCIDの整地鯖最終ログイン日時を表示"
        local_help_value += "\n天気図、地点名の天気予報を表示"
        local_help_value += "\nMCIDの整地量、順位、Lvを表示"
        local_help_value += "\nMCIDのスキンを表示"
        local_help_value += "\n投票用コマンド"
        local_help_value += "\n説明めんどい。python分かる人用"

    try:
        help_embed.add_field(name=f"{message.guild.name}でのコマンド", value=local_help_key, inline=True)
        help_embed.add_field(name="挙動", value=local_help_value, inline=True)
    except UnboundLocalError:
        pass

    try:
        help_embed.add_field(name=f"{message.guild.name}での機能", value=local_help, inline=False)
    except UnboundLocalError:
        pass

    await message.channel.send(embed=help_embed)


async def new_function(client1, message):
    """
    機能追加申請用関数"""

    start_msg = "```\n機能追加の申請をします。\n各項目は全て1回の送信で書いてください。\n\
各項目は10分でタイムアウトします。\n備考などがない場合はなしと入力してください。\n\
複雑な場合はけいに直接言っていただいても構いません。```"
    msg_list = [
        "この依頼内容を公開してよろしいですか？\n良い場合はyes、悪い場合はnoと入力してください\n\
__**特殊な理由がない限りyesにしてください。**__(noの場合けいのDMに送られるためログが埋もれて忘れ去られる可能性があります。)",
        "何をしたら？\n例：/seichiと入力したら、16時になったら等",
        "何をする？\n例：整地鯖役職を付与する、チャンネルにあるメッセージをすべて消去する等",
        "チャンネル、役職の指定は？\n例：Hypixl役職持ちが実行すると怒られる、<#665937884662202434>を消す等",
        "その他備考は？\n他に要求がある場合ここに書いてください。",
    ]
    reply_list = []
    send_msg_list = []

    def check1(m):#公開設定
        return m.author == message.author and m.channel == message.channel and m.content == "yes" or m.content == "no"
    def check2(m):#何をしたら？
        return m.author == message.author and m.channel == message.channel
    def check3(m):#何をする？
        return m.author == message.author and m.channel == message.channel
    def check4(m):#チャンネルや役職の指定は？
        return m.author == message.author and m.channel == message.channel
    def check5(m):#備考は？
        return m.author == message.author and m.channel == message.channel
    def check6(m):#これでいいですか？
        return m.author == message.author and m.channel == message.channel and m.content == "yes" or m.content == "no"

    check_list = [
        check1,
        check2,
        check3,
        check4,
        check5,
    ]

    flag = False
    start = await message.channel.send(start_msg)
    msg = await message.channel.send(msg_list[0])
    send_msg_list.append(msg)
    for i in range(len(msg_list)):
        try:
            reply = await client1.wait_for("message", check=check_list[i], timeout=600)
            reply_list.append(reply)
        except asyncio.TimeoutError:
            timeout_msg = await message.channel.send("タイムアウトしました。最初からやり直してください。")
            try:
                await message.channel.purge(after=message, before=timeout_msg)
            except discord.errors.NotFound:
                pass
        else:
            try:
                send_msg = await message.channel.send(msg_list[i+1])
                send_msg_list.append(send_msg)
            except IndexError:
                flag = True
            
    if flag:
        embed = discord.Embed(title="これで申請してよろしいですか？", description="良ければyes、やり直すならnoと入力してください", color=0xfffffe)
        embed.add_field(name="やりたいこと", value=f"{reply_list[1].content}{reply_list[2].content}", inline=False)
        embed.add_field(name="条件の指定", value=reply_list[3].content)
        embed.add_field(name="備考", value=reply_list[4].content)
        if reply_list[0].content == "yes":
            koukai_hikoukai = "公開"
        else:
            koukai_hikoukai = "非公開"
        embed.add_field(name="公開設定", value=koukai_hikoukai, inline=False)
        try:
            await message.channel.purge(after=message)
        except discord.errors.NotFound:
            pass

        kakunin = await message.channel.send(embed=embed)
        try:
            reply = await client1.wait_for("message", check=check6, timeout=600)
        except asyncio.TimeoutError:
            await message.channel.send("タイムアウトしました。最初からやり直してください。")
            await kakunin.delete()
        else:
            if reply.content == "yes":
                embed = discord.Embed(title="依頼が届きました", color=0x00ff00)
                embed.add_field(name="やりたいこと", value=f"{reply_list[1].content}{reply_list[2].content}", inline=False)
                embed.add_field(name="条件の指定", value=reply_list[3].content)
                embed.add_field(name="備考", value=reply_list[4].content)
                embed.set_author(name=message.author.name, icon_url=message.author.avatar_url_as(format="png"))
                embed.set_footer(text=message.guild.name, icon_url=message.guild.icon_url_as(format="png"))
                if reply_list[0].content == "no":#非公開なら
                    await reply.delete()
                    kei = client1.get_user(523303776120209408)
                    await kei.send(embed=embed)
                    await message.channel.send("依頼内容をけいのDMに送信しました。回答をお待ちください。\n疑問点がある、情報が不十分等の理由でDMを送らせていただく場合があります。")
                else:
                    guild_name = message.guild.name
                    await reply.delete()
                    notice_ch = client1.get_channel(636359382359080961)
                    await notice_ch.send(content="<@523303776120209408>", embed=embed)
                    await message.channel.send("依頼内容をけいの実験サーバ「python開発やることリスト」に送信しました。回答をお待ちください。\n\
疑問点がある、情報が不十分等の理由でメンションやDMをさせていただく場合があります。")

            else:
                await message.channel.send("最初からやり直してください。")
                await kakunin.delete()
                await reply.delete()


async def bug_report(client1, message):
    """
    不具合報告用関数"""

    start_msg = "```\n不具合の報告をします。\n各項目は全て1回の送信で書いてください。\n虚偽の報告はけいが不快になります。\n\
各項目は10分でタイムアウトします。\n複雑な場合はけいに直接言っていただいても構いません。```"

    start = await message.channel.send(start_msg)
    instrunction = await message.channel.send("いつ、どこで、誰が、何をしたら、どうなったかを詳しく書いてください。")

    def check1(m):
        return m.author == message.author and m.channel == message.channel

    flag = False
    try:
        reply = await client1.wait_for("message", check=check1, timeout=600)
    except asyncio.TimeoutError:
        await message.channel.send("タイムアウトしました。最初からやり直してください。")
        await start.delete()
        await instrunction.delete()
    else:
        flag = True
        await start.delete()
        await instrunction.delete()
        await reply.delete()

    if flag:
        confirmation_embed = discord.Embed(title="この内容で報告してよろしいですか？", description="良ければyes、やり直すならnoと入力してください", color=0xfffffe)
        confirmation_embed.add_field(name="不具合の内容", value=reply.content)
        confirmation = await message.channel.send(embed=confirmation_embed)
        
        def check2(m):
            return m.author == message.author and m.channel == message.channel and (m.content == "yes" or m.content == "no")

        try:
            y_or_n = await client1.wait_for("message", check=check2, timeout=600)
        except asyncio.TimeoutError:
            await message.channel.send("タイムアウトしました。最初からやり直してください。")
            await confirmation.delete()
        else:
            if y_or_n.content == "yes":
                notice_ch = client1.get_channel(636359382359080961)
                now = datetime.datetime.now().strftime(r"%Y/%m/%d　%H:%M")
                notice_embed = discord.Embed(title="バグです！", description=reply.content, color=0xff0000)
                notice_embed.set_author(name=message.author.name, icon_url=message.author.avatar_url_as(format="png"))
                notice_embed.set_footer(text=f"{message.guild.name}　{now}", icon_url=message.guild.icon_url_as(format="png"))
                await notice_ch.send(content="<@523303776120209408>", embed=notice_embed)
                await message.channel.send("不具合の報告ありがとうございます。内容をけいの実験サーバ「python開発やることリスト」に送信しました。\n\
疑問点がある、情報が不十分等の理由でメンションやDMをさせていただく場合があります。")
            else:
                await message.channel.send("最初からやり直してください。")

            await y_or_n.delete()


async def greeting(message):
    """
    おはよう、こんにちは、こんばんは、おやすみ、ありがとう
    が入ったメッセが送られたとき用の関数"""

    if message.author.bot:
        return

    now = datetime.datetime.now()
    now_h = now.hour
    if "おはよう" in message.content:
        if now_h >= 5 and now_h <= 9:
            await message.channel.send(f"おはようございます、{message.author.name}さん！")
        else:
            await message.channel.send("今おはよう！？")
    if "こんにちは" in message.content:
        if now_h >= 9 and now_h <= 17:
            await message.channel.send(f"こんにちは、{message.author.name}さん！")
        else:
            await message.channel.send("今こんにちは！？")
    if "こんばんは" in message.content:
        if (now_h >= 17 and now_h <= 23) or (now_h >= 0 and now_h <= 5):
            await message.channel.send(f"こんばんは、{message.author.name}さん！")
        else:
            await message.channel.send("今こんばんは！？")
    if "おやすみ" in message.content:
        if now_h >= 18 and now_h <= 20:
            await message.channel.send(f"{message.author.name}さんは早寝だね～。おやすみなさ～い")
        elif (now_h >= 21 and now_h <= 23) or now_h == 0:
            await message.channel.send(f"おやすみなさい、{message.author.name}さん:zzz:")
        elif now_h >= 1 and now_h <= 3:
            await message.channel.send(f"夜更かしのしすぎには気を付けてね？おやすみなさい、{message.author.name}さん")
        elif now_h >= 4 and now_h <= 5:
            await message.channel.send("・・・")
        elif now_h >= 6 and now_h <= 10:
            await message.channel.send("二度寝っていいよね:+1:")
        else:
            await message.channel.send("お昼寝？おやすみ～")
    if "ありがとう" in message.content:
        await message.add_reaction("🍆")
        await message.channel.send(":eggplant:")


async def end_reaction(message):
    """
    「少し放置」にendを付ける"""

    try:
        await message.add_reaction("🔚")
    except discord.errors.Forbidden:
        pass


async def mention(message, where_from):
    """
    どこで起動しているかを表示"""

    await message.channel.send(where_from)