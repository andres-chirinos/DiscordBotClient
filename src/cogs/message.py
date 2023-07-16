import discord, json
from discord import app_commands
from discord.ext import commands
from __init__ import Cache
import discord_emoji
from n2w import convert

class Vote_form(discord.ui.Modal):
    def __init__(self, bot: commands.Bot, message: discord.Message):
        self.bot = bot
        self.message = message
        self.options = discord.ui.TextInput(label = "Numero de opciones", placeholder="2", required = True, max_length=1)

        super().__init__(title = 'Vote form', timeout=60000)

        self.add_item(self.options)

    async def on_submit(self, interaction: discord.Interaction):
        await self.message.clear_reactions()
        await self.message.pin(reason='Vote')
        Cache.linsert(name='votes', where='AFTER', refvalue=self.message.id, value=self.message.id)
        for i in range(1, int(self.options.value)+1):
            await self.message.add_reaction(discord_emoji.to_unicode(f':{convert(i)}:'))
        return await interaction.response.send_message(content = '🟢',ephemeral = True)
    
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

    #Reactions
    @app_commands.command(name = 'reaction', description = 'Añadir una reacción')
    @app_commands.describe(messagelink = 'Enlace al mensaje')
    async def reaction(self, interaction: discord.Interaction, messagelink: str, emoji: str):
        message = await self.getmessagefromlink(messagelink)
        await message.add_reaction(emoji)
        return await interaction.response.send_message(content = f'🟢',ephemeral = True)

async def setup(bot: commands.Bot):

    @bot.tree.context_menu(name = 'Create vote', guild = bot.guild)
    async def create_vote(interaction: discord.Interaction, message: discord.Message):
        await interaction.response.send_modal(Vote_form(bot, message))

    await bot.add_cog(Message(bot), guild = bot.guild)       