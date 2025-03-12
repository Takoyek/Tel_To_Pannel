from telethon import TelegramClient, events
import sqlite3
import subprocess

# تنظیمات تلگرام
api_id = 29646851
api_hash = '70a40f9db30071a7be02eb35fef561b6'
phone_number = '+989155841124'
client = TelegramClient('session_name', api_id, api_hash)

# اتصال به پایگاه داده SQLite و ایجاد جدول در صورت عدم وجود
conn = sqlite3.connect("inputs.db")
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS inputs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_name TEXT,
        total_flow TEXT,
        duration TEXT
    )
""")
conn.commit()

@client.on(events.NewMessage(incoming=True))
async def handler(event):
    # فقط پیام‌های خصوصی از آیدی 6312958530 پردازش می‌شود
    if not event.is_private or event.sender_id != 6312958530:
        return

    sender = await event.get_sender()
    if sender and sender.bot:
        return

    try:
        text = event.raw_text.strip()
        # انتظار داریم پیام به فرمت: client_name/ total_flow/ duration باشد.
        parts = text.split('/')
        if len(parts) == 3:
            client_name_input = parts[0].strip()
            total_flow_input = parts[1].strip()
            duration_input = parts[2].strip()
            cursor.execute(
                "INSERT INTO inputs (client_name, total_flow, duration) VALUES (?, ?, ?)",
                (client_name_input, total_flow_input, duration_input)
            )
            conn.commit()
            subprocess.call("/root/myenv/bin/python3 extend_subscription.py", shell=True)
            await client.disconnect()
    except Exception:
        # در صورت بروز خطا، هیچ پیامی ارسال نمی‌شود.
        pass

client.start(phone=phone_number)
client.run_until_disconnected()
conn.close()
