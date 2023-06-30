import discord, json
from discord import app_commands
from discord.ext import commands
from __init__ import guild_id

class Message(commands.GroupCog, name = 'message'):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        super().__init__()
    
    def getmessagefromlink(self, messagelink:str):
        link = messagelink.split('/')
        channel = self.bot.get_channel(int(link[-2]))
        return channel.fetch_message(int(link[-1]))

    def getjsonmessage(self, json_content:str):
        data = json.loads(json_content)
        embeds = []
        if data['embeds'] != None: embeds = [discord.Embed().from_dict(embed_json) for embed_json in data['embeds']]
        data['embeds'] = embeds
        return data
    ##Message
    #Send
    @app_commands.command(name = 'send', description = 'Enviar un mensaje')
    @app_commands.describe(json_content = 'Contenido en json')
    async def send(self, interaction: discord.Interaction, json_content:str):
        message = self.getjsonmessage(json_content)
        await interaction.channel.send(content = message['content'], embeds = message['embeds'])
        return await interaction.response.send_message(content = '🟢',ephemeral = True)

    #Edit
    @app_commands.command(name = 'edit', description = 'Editar un mensaje')
    @app_commands.describe(messagelink = 'Enlace al mensaje', json_content = 'Contenido en json')
    async def edit(self, interaction: discord.Interaction, messagelink:str, json_content:str):
        toeditmessage = await self.getmessagefromlink(messagelink)
        message = self.getjsonmessage(json_content)
        await toeditmessage.edit(content = message['content'], embeds = message['embeds'])   
        return await interaction.response.send_message(content = '🟢',ephemeral = True)

    #Delete
    @app_commands.command(name = 'delete', description = 'Eliminar un mensaje')
    @app_commands.describe(messagelink = 'Enlace al mensaje', delay = 'Tiempo de espera antes de eliminar el mensaje')
    async def delete(self, interaction: discord.Interaction, messagelink:str, delay:float = None):
        message = await self.getmessagefromlink(messagelink)
        await message.delete(delay = delay)
        return await interaction.response.send_message(content = '🟢',ephemeral = True)

    #Purge
    @app_commands.command(name = 'purge', description = 'Eliminar mensajes')
    @app_commands.describe(limit = 'Numero de mensajes')
    async def purge(self, interaction: discord.Interaction, limit: int = None):
        await interaction.channel.purge(limit=limit)
        return await interaction.response.send_message(content = f'🟢',ephemeral = True)
    
    #Purge
    @app_commands.command(name = 'reaction', description = 'Añadir una reacción')
    @app_commands.describe(messagelink = 'Enlace al mensaje')
    async def reaction(self, interaction: discord.Interaction, messagelink: str, emoji: str):
        message = await self.getmessagefromlink(messagelink)
        await message.add_reaction(emoji)
        return await interaction.response.send_message(content = f'🟢',ephemeral = True)

async def setup(bot: commands.Bot):       
    await bot.add_cog(Message(bot), guild = discord.Object(id = guild_id))       