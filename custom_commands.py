import discord

async def on_message(client1, message, custom_commands_dict):
    guild = client1.get_guild(message.guild.id)
    channel = client1.get_channel(message.channel.id)