import discord
from discord import app_commands
from discord.ext import commands
from __init__ import guild_id

class Webhook(commands.GroupCog, name = 'webhook'):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

        super().__init__()

    ##Webhook Handling
    #Create webhook
    @app_commands.command(name = 'create', description = 'Crear una webhook')
    @app_commands.describe(name = 'Nombre')
    async def create(self, interaction: discord.Interaction, name: str):
        webhook = await interaction.channel.create_webhook(name = name, avatar = None, reason = None)
        await interaction.response.send_message(content = f'🟢 `{webhook.url}`', ephemeral = True)

    #List webhooks
    async def webhook_autocomplete(self, interaction: discord.Interaction, current: str):
        webhooks = await interaction.channel.webhooks()
        return [app_commands.Choice(name = webhook.name, value = str(webhook.id)) for webhook in webhooks]

    #See webhook info
    @app_commands.command(name = 'info', description = 'Información de una webhook')
    @app_commands.describe(webhookname = 'Nombre')
    @app_commands.autocomplete(webhookname = webhook_autocomplete)
    async def info(self, interaction: discord.Interaction, webhookname: str):
        webhooks = await interaction.channel.webhooks()
        for webhook in webhooks:
            if webhook.id == int(webhookname):
                await interaction.response.send_message(content = f'🟢 `{webhook.url}`', ephemeral = True)

    #Delete webhook 
    @app_commands.command(name = 'delete', description = 'Eliminar una webhook')
    @app_commands.describe(webhookname = 'Nombre')
    @app_commands.autocomplete(webhookname = webhook_autocomplete)
    async def delete(self, interaction: discord.Interaction, webhookname: str):
        webhooks = await interaction.channel.webhooks()
        for webhook in webhooks:
            if webhook.id == int(webhookname):
                await webhook.delete()
                await interaction.response.send_message(content = '🟢', ephemeral = True)

    #Purge webhooks
    @app_commands.command(name = 'purge', description = 'Limpiar webhooks')
    async def purge(self, interaction: discord.Interaction):
        webhooks = await interaction.channel.webhooks()
        for webhook in webhooks:
            await webhook.delete()
            await interaction.response.send_message(content = '🟢', ephemeral = True)

async def setup(bot: commands.Bot):   
    await bot.add_cog(Webhook(bot), guild = discord.Object(id = guild_id))        