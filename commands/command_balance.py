import disnake
from disnake.ext import commands
from utils import Database

class Balance(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()

    @commands.slash_command(name="balance", description="просмотреть баланс.")
    async def balance(self, interaction, user: disnake.User = commands.Param(name="участник", description="целевой участник", default=None)):
        if user is None:
            user = interaction.user

        coins = await self.db.get_balance(user.id)

        embed = disnake.Embed(
            title=f"Баланс — {user.name}",
            description=f"",
            color=0x2b2d31
        )
        embed.add_field(name="> Монеты:", value=f"```{coins}```", inline=True)
        embed.add_field(name="> Анкоины:", value="```0```", inline=True)
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.set_image(url="https://i.imgur.com/kdtdTSE.png")

        await interaction.response.send_message(embed=embed)

def setup(bot):
    bot.add_cog(Balance(bot))
    