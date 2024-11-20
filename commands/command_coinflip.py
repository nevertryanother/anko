import asyncio
import disnake
import random
from disnake.ext import commands
from disnake import ui
from utils import Database
from time import time

db = Database()

class View(ui.View):
    def __init__(self, bid, author_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bid = bid
        self.author_id = author_id

    @ui.button(label="Орел", style=disnake.ButtonStyle.secondary)
    async def head(self, button, interaction: disnake.MessageInteraction):
        if interaction.user.id != self.author_id:
            embed = disnake.Embed(title="Ошибка", description="Вы не автор команды.", color=0x2b2d31)
            embed.set_thumbnail(url=interaction.user.display_avatar.url)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        result = random.randint(0, 1)

        if result == 0:
            await db.decrement_balance(interaction.user.id, self.bid)

            embed = disnake.Embed(color=0x2b2d31)
            embed.set_image("https://i.imgur.com/ZGrjQZw.gif")

            end_embed = disnake.Embed(
                title="Вы выиграли",
                description=f"Выпала орел и вы выиграли {self.bid * 0.9:.0f}",
                color=0x2b2d31
            )
            end_embed.set_thumbnail(url=interaction.user.display_avatar.url)

        else:
            await db.increment_balance(interaction.user.id, self.bid * 0.9)

            embed = disnake.Embed(color=0x2b2d31)
            embed.set_image("https://i.imgur.com/eZbhjUw.gif")

            end_embed = disnake.Embed(
                title="Вы проиграли",
                description=f"Выпала решка и вы проиграли {self.bid}",
                color=0x2b2d31
            )
            end_embed.set_thumbnail(url=interaction.user.display_avatar.url)

        end_embed.set_thumbnail(url=interaction.user.display_avatar.url)
        end_embed.set_image(url="https://i.imgur.com/kdtdTSE.png")

        await interaction.message.edit(embed=embed, view=None)

        await asyncio.sleep(10)

        await interaction.message.edit(embed=end_embed, view=None)
        
    @ui.button(label="Решка", style=disnake.ButtonStyle.secondary)
    async def tail(self, button, interaction: disnake.MessageInteraction):
        if interaction.user.id != self.author_id:
            embed = disnake.Embed(title="Ошибка", description="Вы не автор команды.", color=0x2b2d31)
            embed.set_thumbnail(url=interaction.user.display_avatar.url)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        result = random.randint(0, 1)

        if result == 0:
            await db.decrement_balance(interaction.user.id, self.bid)

            embed = disnake.Embed(color=0x2b2d31)
            embed.set_image("https://i.imgur.com/ZGrjQZw.gif")

            end_embed = disnake.Embed(
                title="Вы проиграли",
                description=f"Выпала орел и вы проиграли {self.bid}",
                color=0x2b2d31
            )
            end_embed.set_thumbnail(url=interaction.user.display_avatar.url)

        else:
            await db.increment_balance(interaction.user.id, self.bid * 0.9)

            embed = disnake.Embed(color=0x2b2d31)
            embed.set_image("https://i.imgur.com/eZbhjUw.gif")

            end_embed = disnake.Embed(
                title="Вы выиграли",
                description=f"Выпала решка и вы выиграли {self.bid * 0.9:.0f}",
                color=0x2b2d31
            )
            end_embed.set_thumbnail(url=interaction.user.display_avatar.url)

        end_embed.set_thumbnail(url=interaction.user.display_avatar.url)
        end_embed.set_image(url="https://i.imgur.com/kdtdTSE.png")

        await interaction.message.edit(embed=embed, view=None)

        await asyncio.sleep(10)

        await interaction.message.edit(embed=end_embed, view=None)

class Coinflip(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()

    @commands.slash_command(name="coinflip", description="подбросить монетку")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def coinflip(self, interaction, 
        bid: int = commands.Param(name="сумма", description="сумма для ставки")
    ):
        balance = await self.db.get_balance(interaction.user.id)

        if bid > await self.db.get_balance(interaction.user.id):
            embed = disnake.Embed(
                title="Ошибка",
                description=f"Недостаточно средств, ваш баланс {balance}",
                color=0x2b2d31
            )
            embed.set_thumbnail(url=interaction.user.display_avatar.url)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        if bid < 50:
            embed = disnake.Embed(
                title="Ошибка",
                description="Минимальная ставка 50",
                color=0x2b2d31
            )
            embed.set_thumbnail(url=interaction.user.display_avatar.url)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if bid > 10000:
            embed = disnake.Embed(
                title="Ошибка",
                description="Максимальная ставка 10000",
                color=0x2b2d31
            )
            embed.set_thumbnail(url=interaction.user.display_avatar.url)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        

        embed = disnake.Embed(
            title="Орел или решка",
            description=f"Выберите сторону, на которую хотите поставить {bid}",
            color=0x2b2d31
        )
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        view = View(bid, interaction.user.id, timeout=None)
        await interaction.response.send_message(embed=embed, view=view) 

    @coinflip.error
    async def mycommand_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            remaining_time = round(error.retry_after, 2)

            current_time = time()

            available_at = current_time + remaining_time

            timestamp = int(available_at)

            embed = disnake.Embed(
                title="Ошибка",
                description=f"Подбросить снова монетку можно <t:{timestamp}:R>",
                color=0x2b2d31
            )
            embed.set_thumbnail(url=ctx.author.display_avatar.url)
            await ctx.send(embed=embed, delete_after=remaining_time-1)

def setup(bot):
    bot.add_cog(Coinflip(bot))