import aiosqlite
from dataclasses import dataclass
from config import DATABASE_NAME
import time
from datetime import datetime, timedelta
import pytz

moscow_plus3_tz = pytz.timezone('Europe/Moscow')

@dataclass
class Database:
    name: str = DATABASE_NAME

    async def connect(self):
        self.connection = await aiosqlite.connect(self.name)
        self.cursor = await self.connection.cursor()

    async def close(self):
        await self.connection.close()

    async def execute(self, query, *args):
        await self.connect()
        await self.cursor.execute(query, args)
        await self.connection.commit()

    async def fetchall(self, query, *args):
        await self.connect()
        await self.cursor.execute(query, args)
        return await self.cursor.fetchall()

    async def fetchone(self, query, *args):
        await self.connect()
        await self.cursor.execute(query, args)
        return await self.cursor.fetchone()

    async def create_tables(self):
        await self.connect()
        try:
            await self.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    balance INTEGER DEFAULT 0,
                    total_voice_time REAL DEFAULT 0,
                    today_voice_time REAL DEFAULT 0,
                    week_voice_time REAL DEFAULT 0,
                    total_messages INTEGER DEFAULT 0,
                    today_messages INTEGER DEFAULT 0,
                    week_messages INTEGER DEFAULT 0,
                    last_activity INTEGER DEFAULT 0,
                    last_daily_reset INTEGER DEFAULT 0,
                    last_weekly_reset INTEGER DEFAULT 0
                );
                """
            )
        except Exception as e:
            print(f"Ошибка при создании таблицы: {e}")
        finally:
            await self.close()

    def get_moscow_time(self):
        return datetime.now(moscow_plus3_tz)
    
    async def reset_weekly(self):
        current_time = self.get_moscow_time()
        current_week_start = current_time - timedelta(days=current_time.weekday())
        current_week_start = current_week_start.date()
        users = await self.fetchall("SELECT id, last_weekly_reset FROM users")
        
        for user in users:
            user_id, last_reset = user

            if last_reset:
                last_reset_time = datetime.fromtimestamp(last_reset, moscow_plus3_tz).date()
            else:
                last_reset_time = None

            if last_reset_time != current_week_start:
                await self.execute(
                    "UPDATE users SET week_voice_time = ?, week_messages = ?, last_weekly_reset = ? WHERE id = ?",
                    0, 0, int(current_time.timestamp()), user_id
                )

        await self.close()

    async def reset_daily(self):
        current_time = self.get_moscow_time()
        current_date = current_time.date()

        users = await self.fetchall("SELECT id, last_daily_reset FROM users")
        
        for user in users:
            user_id, last_reset = user

            if last_reset:
                last_reset_time = datetime.fromtimestamp(last_reset, moscow_plus3_tz).date()
            else:
                last_reset_time = None

            if last_reset_time != current_date:
                await self.execute(
                    "UPDATE users SET today_voice_time = ?, today_messages = ?, last_daily_reset = ? WHERE id = ?",
                    0, 0, int(current_time.timestamp()), user_id
                )

        await self.close()

    async def record_voice_time(self, user_id, duration):
        await self.connect()

        timestamp = int(time.time())

        user_data = await self.fetchone(
            "SELECT total_voice_time, today_voice_time, week_voice_time, last_activity FROM users WHERE id = ?",
            user_id
        )

        if user_data:
            total_voice_time, today_voice_time, week_voice_time, last_activity = user_data

            new_total_voice_time = total_voice_time + duration
            new_today_voice_time = today_voice_time + duration
            new_week_voice_time = week_voice_time + duration

            await self.execute(
                """
                UPDATE users
                SET total_voice_time = ?, today_voice_time = ?, week_voice_time = ?, last_activity = ?
                WHERE id = ?
                """,
                new_total_voice_time, new_today_voice_time, new_week_voice_time, timestamp, user_id
            )
        else:
            await self.execute(
                """
                INSERT INTO users (id, total_voice_time, today_voice_time, week_voice_time, last_activity)
                VALUES (?, ?, ?, ?, ?)
                """,
                user_id, duration, duration, duration, timestamp
            )

        await self.close()

    async def get_voice_time(self, user_id):
        await self.connect()

        result = await self.fetchone(
            "SELECT total_voice_time FROM users WHERE id = ?",
            user_id
        )

        return result[0] if result else 0

    async def get_today_voice_time(self, user_id):
        await self.connect()

        result = await self.fetchone(
            "SELECT today_voice_time FROM users WHERE id = ?",
            user_id
        )

        return result[0] if result else 0

    async def get_week_voice_time(self, user_id):
        await self.connect()

        result = await self.fetchone(
            "SELECT week_voice_time FROM users WHERE id = ?",
            user_id
        )

        return result[0] if result else 0

    async def get_balance(self, user_id):
        await self.connect()
        balance = await self.fetchone("SELECT balance FROM users WHERE id = ?", user_id)

        if balance is None:
            await self.execute(
                "INSERT INTO users (id, balance) VALUES (?, ?)",
                user_id, 0
            )
            return 0
        
        return balance[0]

    async def set_balance(self, user_id, new_balance):
        await self.get_balance(user_id)
        await self.connect()
        await self.execute(
            "UPDATE users SET balance = ? WHERE id = ?",
            new_balance, user_id
        )

    async def increment_balance(self, user_id, amount):
        await self.get_balance(user_id)
        await self.connect()
        await self.execute(
            "UPDATE users SET balance = balance + ? WHERE id = ?",
            amount, user_id
        )

    async def decrement_balance(self, user_id, amount):
        await self.get_balance(user_id)
        await self.connect()
        await self.execute(
            "UPDATE users SET balance = balance - ? WHERE id = ?",
            amount, user_id
        )

    async def record_message_count(self, user_id):
        await self.connect()

        timestamp = int(time.time())

        user_data = await self.fetchone(
            "SELECT total_messages, today_messages, week_messages, last_activity FROM users WHERE id = ?",
            user_id
        )

        if user_data:
            total_messages, today_messages, week_messages, last_activity = user_data

            new_total_messages = total_messages + 1
            new_today_messages = today_messages + 1
            new_week_messages = week_messages + 1

            await self.execute(
                """
                UPDATE users
                SET total_messages = ?, today_messages = ?, week_messages = ?, last_activity = ?
                WHERE id = ?
                """,
                new_total_messages, new_today_messages, new_week_messages, timestamp, user_id
            )
        else:
            await self.execute(
                """
                INSERT INTO users (id, total_messages, today_messages, week_messages, last_activity)
                VALUES (?, ?, ?, ?, ?)
                """,
                user_id, 1, 1, 1, timestamp
            )

        await self.close()

    async def get_total_messages(self, user_id):
        await self.connect()

        result = await self.fetchone(
            "SELECT total_messages FROM users WHERE id = ?",
            user_id
        )

        return result[0] if result else 0

    async def get_today_messages(self, user_id):
        await self.connect()

        result = await self.fetchone(
            "SELECT today_messages FROM users WHERE id = ?",
            user_id
        )

        return result[0] if result else 0

    async def get_week_messages(self, user_id):
        await self.connect()

        result = await self.fetchone(
            "SELECT week_messages FROM users WHERE id = ?",
            user_id
        )

        return result[0] if result else 0