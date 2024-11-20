import disnake
from disnake.ext import commands

bot = commands.InteractionBot(intents=disnake.Intents.all())

class Bot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=disnake.Intents.all())

    async def on_ready(self):
        print(f"Запустился")

        await self.change_presence(status=disnake.Status.online, activity=disnake.Activity(type=disnake.ActivityType.watching, name="баббабы"))