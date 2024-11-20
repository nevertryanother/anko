import disnake
from disnake.ext import commands
from utils import Database

db = Database()

class MessageActivity(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = db

    @commands.Cog.listener()
    async def on_message(self, message: disnake.Message):
        await db.record_message_count(message.author.id)

def setup(bot):
    bot.add_cog(MessageActivity(bot))