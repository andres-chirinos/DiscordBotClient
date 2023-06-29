from discord_webhook import DiscordWebhook
from __init__ import guild_id, Cache

import discord
from discord import app_commands
from discord.ext import commands


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
            if len(result)>0:
                renuncio = True
            else:
                result = list(set(after.roles) - set(before.roles))

            if str(result[0].id) in Cache.lrange('ranks', 0, -1):
                if renuncio:
                    result = f'<@!{before.id}> Renunció a <@&{result[0].id}>'
                else:
                    result = f'<@!{before.id}> Asumió a <@&{result[0].id}>'

                webhook = DiscordWebhook(
                    url=Cache.hget("webhooks", "rank-log"),
                    rate_limit_retry=True,
                    content = result,
                )
                await webhook.execute()

async def setup(bot: commands.Bot):
    await bot.add_cog(Listeners(bot), guild=discord.Object(id=guild_id))
