from telethon import TelegramClient, events
import sqlite3
import asyncio
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

async def wait_for_confirmation(from_id):
    confirmation_future = asyncio.Future()

    async def confirmation_handler(event):
        confirmation_future.set_result(event.raw_text.strip())
        client.remove_event_handler(confirmation_handler)  # حذف handler پس از دریافت پیام

    client.add_event_handler(confirmation_handler, events.NewMessage(incoming=True, from_users=from_id))
    result = await confirmation_future
    return result

@client.on(events.NewMessage(incoming=True))
async def handler(event):
    # فقط پیام‌های خصوصی از آیدی 6312958530 پاسخ داده می‌شود
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
            cursor.execute("INSERT INTO inputs (client_name, total_flow, duration) VALUES (?, ?, ?)",
                           (client_name_input, total_flow_input, duration_input))
            conn.commit()
            await event.reply("اطلاعات دریافت و ذخیره شد.\nلطفاً تایید کنید: آیا اطلاعات صحیح هستند؟ (بله/خیر)")
            confirmation = await wait_for_confirmation(event.sender_id)
            if confirmation.lower() in ["بله", "yes"]:
                await event.reply("تایید شد. در حال اجرای فایل extend_subscription.py")
                subprocess.call("/root/myenv/bin/python3 extend_subscription.py", shell=True)
            else:
                await event.reply("اطلاعات تایید نشد. لطفاً دوباره ارسال کنید.")
            await client.disconnect()
        else:
            await event.reply("فرمت پیام نادرست است. لطفاً به صورت: client_name/ total_flow/ duration ارسال کنید.")
    except Exception as e:
        await event.reply("خطا در پردازش پیام: " + str(e))

client.start(phone=phone_number)
client.run_until_disconnected()
conn.close()
