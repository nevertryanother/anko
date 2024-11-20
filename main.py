from utils import Bot, Database
from config import TOKEN as token

db = Database()
bot = Bot()

@bot.event
async def on_ready():
    await db.connect()
    await db.create_tables()
    print("запущен... ;)")

try:
    bot.load_extensions("commands")
except Exception as e:
    print(e)
    
# не забудь вставить токен в конфиг
bot.run(token)