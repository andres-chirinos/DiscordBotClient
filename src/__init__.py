from dotenv import load_dotenv
from discord.ext import commands
from lib.role_connection import RoleConnection
import os, redis, discord, pymongo

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
load_dotenv(dotenv_path=".env")

# Memoria y cache interno
Cache = redis.from_url(
    url=os.getenv(
        "REDIS_URL",
        "redis://default:ouBdBv91Z7t60rEfd0VL@containers-us-west-192.railway.app:7660",
    ),
    decode_responses=True
)
Memoria = pymongo.MongoClient(os.getenv("MONGO_URL"))

role_connection = RoleConnection(Memoria=Memoria, client_id=int(os.environ.get("DISCORD_CLIENT_ID")), bot_token=os.environ.get("DISCORD_BOT_TOKEN"), client_secret = os.environ.get("DISCORD_CLIENT_SECRET"),metadata_set = Cache.get("registermetadata"))

# Aplicacion Discord
class MyBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
        self.guild = discord.Object(id=int(os.environ.get("DISCORD_GUILD_ID")))
        self.initial_extensions = [
            "cogs.thread",
            "cogs.message",
            "cogs.listeners",
        ]

    async def setup_hook(self):
        for ext in self.initial_extensions:
            await self.load_extension(ext)

        await self.tree.sync(guild=self.guild)

    async def on_ready(self):
        await self.change_presence(
            status=discord.Status.online,
            activity=discord.Game(
                f"""[{str(Cache.hget('appdata', 'prefix'))}] {str(Cache.hget('appdata', 'desc'))}"""
            ),
        )

bot = MyBot(
    command_prefix=commands.when_mentioned_or(str(Cache.hget("appdata", "prefix"))),
    help_command=None,
    case_insensitive=True,
    description=str(Cache.hget("appdata", "desc")),
    intents=discord.Intents.all(),
    aplicaction_id=int(os.environ.get("DISCORD_CLIENT_ID")),
)

if __name__ == "__main__":
    bot.run(os.environ.get("DISCORD_BOT_TOKEN"))
