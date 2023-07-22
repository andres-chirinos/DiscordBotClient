import discord
from discord import app_commands
from discord.ext import commands
from __init__ import Cache

class Open_modal(discord.ui.Modal):
    def __init__(self, bot: commands.Bot):
        self.bot = bot        
        self.reason = discord.ui.TextInput(label = 'Nombre del hilo', min_length = 3, max_length = 20, required = False)

        super().__init__(title = 'Abrir un hilo privado')
        self.add_item(self.reason)

    async def on_submit(self, interaction: discord.Interaction):
        if self.reason is None:
            if interaction.user.nick is None: self.reason = interaction.user.name
            else: self.reason = interaction.user.nick
        thread = await interaction.channel.create_thread(name = f'{self.reason}', type = discord.ChannelType.private_thread, invitable = False)
        await thread.add_user(interaction.user)
        return await interaction.response.send_message(content = '🟢', ephemeral = True, delete_after = 10)

class Set_view(discord.ui.View):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        super().__init__(timeout = None)
    
    @discord.ui.button(label = "Abrir un hilo privado", style = discord.ButtonStyle.red, custom_id = 'thread_button')
    async def open(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(Open_modal(self.bot))

class Ticket_view(discord.ui.View):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        super().__init__(timeout = None)
    
    @discord.ui.button(label = "Abrir ticket", style = discord.ButtonStyle.red, custom_id = 'ticket_button')
    async def open(self, interaction: discord.Interaction, button: discord.ui.Button):
        num = int(Cache.hget("appdata", "ticket_num"))+1
        Cache.hset("appdata", "ticket_num", num)
        thread = await interaction.channel.create_thread(name = f'{interaction.user.name}-{num}', type = discord.ChannelType.private_thread, invitable = False)
        await thread.add_user(interaction.user)
        return await interaction.response.send_message(content = '🟢', ephemeral = True, delete_after = 10)

class Thread(commands.GroupCog, name = 'thread'):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        
        super().__init__()

    ##Thread handling
    #Create thread
    @app_commands.command(name = 'create', description = 'Crear un hilo')
    @app_commands.describe(name = 'Nombre', private = '¿Es privado?')
    async def create(self, interaction: discord.Interaction, name: str, private: bool = False):
        if private is True: private = discord.ChannelType.private_thread
        else: private = discord.ChannelType.public_thread
        thread = await interaction.channel.create_thread(name = name, type = private, invitable = False)
        return await interaction.response.send_message(content = f'🟢 <#{thread.id}>',ephemeral = True)

    #Delete thread
    @app_commands.command(name = 'delete', description = 'Eliminar un hilo')
    async def delete(self, interaction: discord.Interaction):
        await interaction.channel.delete()
        return await interaction.response.send_message(content = '🟢',ephemeral = True)

    #Purge threads
    @app_commands.command(name = 'purge', description = 'Limpiar hilos')
    async def purge(self, interaction: discord.Interaction):
        for thread in interaction.channel.threads:
            thread.delete()
        return await interaction.response.send_message(content = '🟢',ephemeral = True)

    ##User handling
    #add user thread
    @app_commands.command(name = 'add', description = 'Añadir un usuario')
    @app_commands.describe(user = 'Elija al usuario')
    async def add(self, interaction: discord.Interaction, user: discord.Member):
        await interaction.channel.add_user(user)
        return await interaction.response.send_message(content = f'🟢 {user.mention}',ephemeral = True)
    
    #remove user thread
    @app_commands.command(name = 'remove', description = 'Quitar un usuario')
    @app_commands.describe(user = 'Elija al usuario')
    async def remove(self, interaction: discord.Interaction, user: discord.Member):
        await interaction.channel.remove_user(user)
        return await interaction.response.send_message(content = f'🟢 {user.mention}',ephemeral = True)

    ##Thread views
    #Set a thread open button
    @app_commands.command(name = 'set', description = 'Boton para crear hilos')
    async def set(self, interaction: discord.Interaction, message: str = None): 
        await interaction.channel.send(content = message, view = Set_view(self.bot))
        return await interaction.response.send_message(content = '🟢', ephemeral = True, delete_after = 10)
    
    #Set a ticket open button
    @app_commands.command(name = 'ticket', description = 'Boton para crear hilos')
    async def ticket(self, interaction: discord.Interaction, message: str = None): 
        await interaction.channel.send(content = message, view = Ticket_view(self.bot))
        return await interaction.response.send_message(content = '🟢', ephemeral = True, delete_after = 10)

async def setup(bot: commands.Bot): 
    bot.add_view(Set_view(bot))
    await bot.add_cog(Thread(bot), guild = bot.guild)        