import disnake
from disnake.ext import commands
import time
from utils import Database

class VoiceActivity(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_users = {}
        self.db = Database()

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: disnake.Member, before: disnake.VoiceState, after: disnake.VoiceState):
        if before.channel is None and after.channel is not None:
            self.active_users[member.id] = time.time()

        elif before.channel is not None and after.channel is None:
            if member.id in self.active_users:
                enter_time = self.active_users.pop(member.id)
                duration = time.time() - enter_time
                await self.db.record_voice_time(member.id, duration)

        elif before.channel != after.channel:
            if member.id in self.active_users:
                enter_time = self.active_users.pop(member.id)
                duration = time.time() - enter_time
                await self.db.record_voice_time(member.id, duration)

            self.active_users[member.id] = time.time()

def setup(bot):
    bot.add_cog(VoiceActivity(bot))