import disnake
from disnake.ext import commands
from utils import Database

db = Database()

class PersonalRole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database

    @commands.slash_command(name="role")
    async def personal_role(self, interaction):
        pass

    @personal_role.sub_command(name="manage", description="управление персональной ролью")
    async def manage(self, interaction, role: disnake.Role = commands.Param(name="роль", description="хойня")):
        pass

def setup(bot):
    bot.add_cog(PersonalRole(bot))