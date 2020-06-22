import discord

def check_channel(message, allow_ch_list=None, disallow_ch_list=None):
    """
    使用許可リストに入っているか、または使用不許可リストに入っていないか確かめる関数
    使用可能時Trueを、不可能時Falseを返す
    channel ver"""

    try:
        if message.channel.id in allow_ch_list:
            return True
        else:
            return False
    except TypeError:
        if message.channel.id in disallow_ch_list:
            return False
        else:
            return True


def check_role(message, allow_role_list=None, disallow_role_list=None):
    """
    使用許可リストに入っているか、または使用不許可リストに入っていないか確かめる関数
    使用可能時Trueを、不可能時Falseを返す
    role ver"""

    flag = "allow"
    for role in message.author.roles:
        try:
            if role.id in allow_role_list: #ここでリストに入っている
                return True

        except TypeError:
            flag = "disallow"
            if role.id in disallow_role_list: #またはここでリストに入っていないときTrueを返す
                return False

    if flag == "allow":
        return False
    else:
        return True


async def on_message(client1, message, custom_commands):
    if not (message.content in custom_commands.keys()):
        return

    #登録されているメッセージのみが残る
    command_content = custom_commands[message.content]
    try:
        allow_ch_list = command_content["able_c"]
        check = check_channel(message, allow_ch_list=allow_ch_list)
    except KeyError:
        disallow_ch_list = command_content["disable_c"]
        check = check_channel(message, disallow_ch_list=disallow_ch_list)

    if not check: #チャンネル上使用不可
        await message.channel.send("このコマンドはこのチャンネルでは使用できません")
        return

    #チャンネル権限はパスしている場合
    try:
        allow_role_list = command_content["able_r"]
        check = check_role(message, allow_role_list=allow_role_list)
    except KeyError:
        disallow_role_list = command_content["disable_r"]
        check = check_role(message, disallow_role_list=disallow_role_list)

    if not check: #役職上使用不可
        await message.channel.send("あなたはこのコマンドの使用は許可されていません")
        return

    for msg in command_content["message"]:
        await message.channel.send(msg)
    for role_id in command_content["add_role"]:
        role = discord.utils.get(message.guild.roles, id=role_id)
        try:
            await message.author.add_roles(role)
        except AttributeError:
            await message.channel.send("そのIDを持つ役職はありません")
    for role_id in command_content["remove_role"]:
        role = discord.utils.get(message.guild.roles, id=role_id)
        try:
            await message.author.remove_roles(role)
        except AttributeError:
            await message.channel.send("そのIDを持つ役職はありません")
