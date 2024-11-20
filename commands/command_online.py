import disnake
from disnake.ext import commands
from utils import Database
from utils import format_voice_time

class Online(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()

    @commands.slash_command(name="online", description="посмотреть статистику участника")
    async def online(self, interaction, user: disnake.User = commands.Param(name="участник", description="целевой участник", default=None)):
        if user is None:
            user = interaction.user

        total_online_seconds = await self.db.get_voice_time(user.id)
        today_online_seconds = await self.db.get_today_voice_time(user.id)
        week_online_seconds = await self.db.get_week_voice_time(user.id)

        total_online = format_voice_time(total_online_seconds)
        today_online = format_voice_time(today_online_seconds)
        week_online = format_voice_time(week_online_seconds)

        total_messages = await self.db.get_total_messages(user.id)
        today_messages = await self.db.get_today_messages(user.id)
        week_messages = await self.db.get_week_messages(user.id)

        voice_embed = disnake.Embed(
            title="Голосовой актив",
            color=0x2b2d31)
        
        voice_embed.add_field(name="За день", value=f"```{today_online}```", inline=True)
        voice_embed.add_field(name="За неделю", value=f"```{week_online}```", inline=True)
        voice_embed.add_field(name="Всего", value=f"```{total_online}```", inline=True)
        voice_embed.set_image(url="https://i.imgur.com/kdtdTSE.png")
        voice_embed.set_thumbnail(url=user.display_avatar.url)

        text_embed = disnake.Embed(
            title="Сообщения",
            color=0x2b2d31)
        
        text_embed.add_field(name="За день", value=f"```{today_messages}```", inline=True)
        text_embed.add_field(name="За неделю", value=f"```{week_messages}```", inline=True)
        text_embed.add_field(name="Всего", value=f"```{total_messages}```", inline=True)
        text_embed.set_image(url="https://i.imgur.com/kdtdTSE.png")
        text_embed.set_thumbnail(url="https://i.imgur.com/kdtdTSE.png")
        voice_embed.set_author(name=f"{user.name} - онлайн")

        await interaction.response.send_message(embeds=[voice_embed, text_embed])

def setup(bot):
    bot.add_cog(Online(bot))
        