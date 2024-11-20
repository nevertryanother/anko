from disnake.ext import commands, tasks
from utils import Database
from utils import get_moscow_time

class ResetTasks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()
        self.weekly_reset.start()

    @tasks.loop(seconds=15)
    async def weekly_reset(self):
        current_time = await get_moscow_time()

        if current_time.weekday() == 0 and current_time.hour == 0 and current_time.minute == 0:
            await self.db.reset_weekly()

    @weekly_reset.before_loop
    async def before_weekly_reset(self):
        await self.bot.wait_until_ready()

def setup(bot):
    bot.add_cog(ResetTasks(bot))