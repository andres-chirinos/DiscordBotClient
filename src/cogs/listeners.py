from discord_webhook import DiscordWebhook
from __init__ import Cache, Memoria, role_connection

import discord, datetime, random
from discord import app_commands
from discord.ext import commands
from discord.utils import get

class Open_modal(discord.ui.Modal):
    def __init__(self, bot: commands.Bot, user_id: int = None, *args, **kwargs):
        self.bot = bot
        self.user_id = user_id
        self.horas = discord.ui.TextInput(label="Número de horas", min_length=1)

        super().__init__(title="Calculadora de impuestos", *args, **kwargs)
        self.add_item(self.horas)

    async def on_submit(self, interaction: discord.Interaction):
        return await interaction.response.send_message(
            content=f"Tendria que pagar {round(int(self.horas.value) * float(Cache.get('tax')))}",
            ephemeral=True,
        )

class Set_view(discord.ui.View):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Calcular Impuestos",
        style=discord.ButtonStyle.red,
        custom_id="tax_button",
    )
    async def open(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(Open_modal(self.bot, interaction.user.id))


class Listeners(commands.GroupCog, name="listeners"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

        super().__init__()

    @commands.Cog.listener()
    async def on_thread_create(self, thread):
        if thread.parent_id == int(Cache.hget("channels", "parlamentforum_id")):
            await thread.send(content=f"🟢 <@&{int(Cache.hget('roles', 'deputy_id'))}>")
        elif thread.parent_id == int(Cache.hget("channels", "marketforum_id")):
            await thread.send(content=f"🟢 <@&{int(Cache.hget('roles', 'trader_id'))}>")

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if len(before.roles) != len(after.roles):
            result = list(set(before.roles) - set(after.roles))
            renuncio = False
            if len(result) > 0:
                renuncio = True
            else:
                result = list(set(after.roles) - set(before.roles))

            if str(result[0].id) in Cache.lrange("ranks", 0, -1):
                if renuncio:
                    result = f"<@!{before.id}> Renunció a <@&{result[0].id}>"
                else:
                    result = f"<@!{before.id}> Asumió a <@&{result[0].id}>"

                webhook = DiscordWebhook(
                    url=Cache.hget("webhooks", "rank-log"),
                    rate_limit_retry=True,
                    content=result,
                )
                await webhook.execute()

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: discord.Reaction, user):
        if str(reaction.message.id) in Cache.lrange("votes", 0, -1) and (
            not str(user.id) in Cache.lrange("ranks", 0, -1) or user in reaction.users()
        ):
            await reaction.remove(user)

    # Set tax
    @app_commands.command(name="settax", description="Boton para calcular impuestos")
    async def settax(self, interaction: discord.Interaction, message: str = None):
        await interaction.channel.send(content=message, view=Set_view(self.bot))
        return await interaction.response.send_message(
            content="🟢", ephemeral=True, delete_after=10
        )

    @app_commands.command(name="paytax", description="Pagar impuestos")
    async def paytax(
        self, interaction: discord.Interaction, user: discord.User, horas: int
    ):
        if horas != 0:
            role_data = await role_connection.get_role_data(user.id)
            metadata = role_data["metadata"]
            metadata["hours"] = horas + metadata["hours"]
            metadata["update"] = datetime.datetime.now().isoformat()

            Memoria.get_database("master").get_collection("users").update_one(
                {"_id": user.id}, {"$set": {"metadata": metadata}}
            )
            DiscordWebhook(
                url=Cache.hget("webhooks", "tax-log"),
                rate_limit_retry=True,
                content=f"<@{user.id}> pagó {horas} por valor {round(horas * float(Cache.get('tax')))}$",
            ).execute()
        await role_connection.reflesh_role_connection(user.id)
        return await interaction.response.send_message(
            content="🟢", ephemeral=True, delete_after=10
        )

    @app_commands.command(description="Elegir jurados")
    async def choosejurors(
        self,
        interaction: discord.Interaction,
        nojurados: str = "0",
        numjurados: int = 3,
    ):
        nojurados = [int(user_id[2:-1]) for user_id in nojurados.split(" ")]

        for role_id in Cache.lrange("ranks", 0, -1):
            jurados = [
                f"<@!{member.id}>"
                for member in get(interaction.guild.roles, id=int(role_id)).members
                if not member.id in nojurados
            ]

        return await interaction.response.send_message(
            content=f"{' '.join(random.choices(jurados, k = numjurados))} son jurados",
            delete_after=10,
        )


async def setup(bot: commands.Bot):
    bot.add_view(Set_view(bot))
    await bot.add_cog(Listeners(bot), guild=bot.guild)
