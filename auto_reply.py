import asyncio
import logging
import os
import sqlite3
import subprocess
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from telethon import TelegramClient, events, types

# لاگ
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# تلگرام
api_id = 29646851
api_hash = '70a40f9db30071a7be02eb35fef561b6'
phone_number = '+989155841124'
client = TelegramClient('my_session', api_id, api_hash)

# دیتابیس
engine = create_engine('sqlite:///my_session.db', connect_args={'check_same_thread': False})
Session = sessionmaker(bind=engine)
Base = declarative_base()

class UserState(Base):
    __tablename__ = 'user_state'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, unique=True, nullable=False)
    state = Column(String, nullable=False)

Base.metadata.create_all(engine)

# ---------- افزودن بخش مربوط به دیتابیس inputs.db ----------
DURATION = "30"  # مقدار ثابت

# اتصال به دیتابیس inputs.db
inputs_conn = sqlite3.connect('inputs.db')
inputs_cursor = inputs_conn.cursor()
inputs_cursor.execute('''
    CREATE TABLE IF NOT EXISTS inputs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_name TEXT,
        total_flow TEXT,
        duration TEXT
    )
''')
inputs_conn.commit()

# فایل‌ها
if not os.path.exists('/root/DATA/Uploads'):
    os.makedirs('/root/DATA/Uploads')


allowed_users = [6312958530, 5913828709, 7517469464, 7505307212]
block_format = ['.exe']
block_reply_files = [7517469464, 7505307212]
block_forward = [44444, 55555]
block_reply = [66666, 88888]
block_TMD = [101512739, 1622957174, 133450983, 44444]
allowed_main_menu = [6312958530, 333333]
block_menu = [
    101512739, 1622957174, 133450983, 1499394623,
    736768510, 93983470, 725484841, 58107887, 349942915
]

# پیام‌های ثابت
MESSAGES = {
    "MAIN_MENU": "1️⃣ جهت تمدید اشتراک فعلی عدد  1  را ارسال کنید.\n"
                 "2️⃣ جهت خرید اشتراک جدید عدد  2  را ارسال کنید.\n"
                 "3️⃣ جهت اطلاع از مانده اشتراک عدد  3  را ارسال کنید.\n"
                 "4️⃣ جهت تغییر نام خود عدد  4  را ارسال کنید.",

    "HELLO": "سلام!\n😊 من یک پاسخگوی آنلاین هستم.",
    "NAME_RQ": "لطفا اسم خودت رو برام ارسال کن:",
    "NEW_NAME": "لطفا اسم جدید خودت رو ارسال کن:",
    "WELLCOM": '✨ سلام {name} عزیز، خوش اومدی🌹',

    "CONFIRM_NAME": '✨ دوست داری اسمت "{text}" ثبت بشه؟\n\n'
                    '✅  اگر اسمت رو صحیح وارد کردی، عدد  1  رو ارسال کن.\n'
                    '🔄  برای تغییر اسمت عدد  2  رو ارسال کن.',

    "TMD_NAME": "✍️ نام اشتراکی که می خواهید تمدید شود چیست؟",
    "NEW_USER_NAME": "✍️ لطفا یک نام کاربری برای اشتراک جدید وارد کنید:",

    "OLD_NAME": "✍️ لطفاً نام اشتراک مورد نظر را ارسال کنید.",
    "OLD_RESID": '⭐️ درخواست شما برای اطلاع از مانده اشتراک "{OLD_username}"\nدر اسرع وقت بررسی شده و به شما اطلاع داده خواهد شد.',

    "GO_BACK": "0️⃣ اگر میخواهید به منوی اصلی برگردید، عدد  0  را ارسال کنید.",

    "50G": "50 گیگ",
    "30G": "30 گیگ",
    "50T": "مبلغ:  110 هزار تومان",
    "30T": "مبلغ:  90 هزار تومان",
    "TMD": "تمدید",
    "NEW": "خرید",


    "NEW_USER_RESID": "⭐️ سفارش شما با مشخصات زیر:\n"
                      " **************************** \n"
                      "نام کاربری: {NEW_username} \n"
                      "حجم: {NEW_hajm} \n"
                      " {NEW_mablagh} \n"
                      "سی روزه\n"
                      " **************************** \n\n"
                      "در اسرع وقت ساخته شده و برای شما ارسال خواهد شد.",

    "TMD_RESID": "⭐️ سفارش شما با مشخصات زیر:\n"
                 " **************************** \n"
                 "نام کاربری: {client_name} \n"
                 "حجم: {total_flow} \n"
                 " {TMD_mablagh} \n"
                 "سی روزه\n"
                 " **************************** \n\n"
                 "در اسرع وقت تمدید شده و به شما اطلاع داده خواهد شد.",                     

    "ORDER": ["⭐️ جهت {order} اشتراک عدد مربوطه را ارسال کنید:\n\n"
              "🔰 برای {order} 50 گیگ - 110 هزار تومان عدد   50   را ارسال کنید.\n"
              "🔰 برای {order} 30 گیگ - 90 هزار تومان عدد   30   را ارسال کنید.\n"],

    "BANK_CARD": ["💳 {mablagh} را واریز کنید به کارت:\n\n"
                  "بر روی شماره کارت انگشت 👇 بزنید، کپی میشود:\n\n"
                  "`5859 8311 9178 6085`\nشکوفه رضایی - بانک تجارت\n\n"
                  "🔵 - ارسال اسکرین شات پرداخت الزامی است.\n"
                  "🟡 - مهلت تست و پرداخت 48 ساعت است.\n"
                  "🔴 - در صورت عدم پرداخت اشتراک شما لغو خواهد شد."],

    "TMD_MESSAGE": "⭐️ اشتراک شما در اسرع وقت تمدید شده و به شما اطلاع داده خواهد شد.",
    
    # پیام‌های فایل
    'file_saved': 'فایل شما با موفقیت دریافت و ذخیره شد.',
    'file_error': 'متأسفانه در دریافت فایل شما مشکلی پیش آمد.',
    'blocklist_format': "متأسفانه فایل‌هایی با پسوند '{ext}' قابل پذیرش نیستند.",
    'no_files': 'شما هیچ فایلی ارسال نکرده‌اید.',
    'file_list_error': 'متأسفانه در لیست کردن فایل‌های شما مشکلی پیش آمد.',
    'file_not_found': 'فایل {file_name} یافت نشد.',
    'files_list': 'لیست فایل‌های شما:\n{file_list}'
}

# لیست‌های کلیدواژه
THANKS = {"ممنون", "مرسی", "دست شما درد نکنه", "سپاس", "تشکر", "لطف کردین", "مچکر", "thank", "mamnoon", "🙏"}
RESID = {"خدمت شما", "تقدیم", "بفرمایید", "بفرمائید"}
TMD_RQ = {"تمدید", "شارژ", "تجدید"}
FIRST_HI = {"سلام", "درود", "salam", "hi"}

user_state = {}

# توابع کمکی
def persian_to_english_number(text):
    return text.translate(str.maketrans('۰۱۲۳۴۵۶۷۸۹', '0123456789'))

async def send_messages(event, messages):
    if isinstance(messages, list):
        for msg in messages:
            await event.respond(msg)
    else:
        await event.respond(messages)

async def get_username(user_id):
    try:
        user = await client.get_entity(user_id)
        return f"{user_id} [{user.username}]" if user.username else str(user_id)
    except Exception as e:
        logger.error(f'خطا در دریافت نام کاربری برای {user_id}: {e}')
        return str(user_id)

async def send_main_menu(event, user_id):
    # تنها در صورتی که user_id در لیست allowed_main_menu باشد، پیام MAIN_MENU ارسال می‌شود
    if user_id in allowed_main_menu:
        await send_messages(event, MESSAGES["MAIN_MENU"])


# هندلر اصلی
@client.on(events.NewMessage(incoming=True))

async def handler(event):
    # اگر رویداد خصوصی نباشد یا شناسه فرستنده در لیست block_reply قرار داشته باشد
    if not event.is_private or event.sender_id in block_reply:
    # فقط به پیام‌های خصوصی از کاربرانی که در لیست allowed_users هستند پاسخ داده می‌شود
#    if not event.is_private or event.sender_id not in allowed_users:
        return


    sender = await event.get_sender()
    if sender and sender.bot:
        return

    user_id = event.sender_id
    user_state.setdefault(user_id, "register")
    current_state = user_state[user_id]
    raw_text = event.raw_text.strip()
    text = persian_to_english_number(raw_text)
    text_lower = text.lower()

    logger.info(f"Received message from {user_id}: {raw_text}")


    # پردازش کلیدواژه‌ها
    if any(kw in text_lower for kw in FIRST_HI):
        with Session() as session:
            user = session.query(UserState).filter_by(user_id=user_id).first()
            if user:
                await send_messages(event, MESSAGES["WELLCOM"].format(name=user.state))
                await send_main_menu(event, user_id)
                user_state[user_id] = "MAIN_MENU"
            else:
                await send_messages(event, MESSAGES["HELLO"])
                await send_messages(event, MESSAGES["NAME_RQ"])
                user_state[user_id] = "awaiting_name"
        return

    if any(kw in text_lower for kw in THANKS):
        await event.respond("خواهش میکنم 🌺")
        return

    if any(kw in text_lower for kw in RESID):
        await event.respond("ممنون 🙏")
        return

    if any(kw in text_lower for kw in TMD_RQ) and user_id not in block_TMD:
        await event.respond(MESSAGES["TMD_MESSAGE"])
        return

    # دستورات مدیریت کاربر
    if text_lower == "clear:me":
        with Session() as session:
            user = session.query(UserState).filter_by(user_id=user_id).first()
            if user:
                session.delete(user)
                session.commit()
                await event.respond("نام شما با موفقیت از دیتابیس حذف شد.")
            else:
                await event.respond("نام شما در دیتابیس یافت نشد.")
        return

    if text_lower.startswith("clear:"):
        target_user_id = text.split(":", 1)[1].strip()
        with Session() as session:
            user = session.query(UserState).filter_by(user_id=target_user_id).first()
            if user:
                session.delete(user)
                session.commit()
                await event.respond(f"نام کاربری با آی‌دی {target_user_id} حذف شد.")
            else:
                await event.respond(f"کاربری با آی‌دی {target_user_id} یافت نشد.")
        return

    # مدیریت stateها
    if current_state == "awaiting_name":
        user_state[user_id] = "confirm_name"
        user_state[f"{user_id}_name"] = text
        await send_messages(event, MESSAGES["CONFIRM_NAME"].format(text=text))

    elif current_state == "confirm_name":
        if text == "1":
            name = user_state.pop(f"{user_id}_name")
            with Session() as session:
                user = session.query(UserState).filter_by(user_id=user_id).first()
                if user:
                    user.state = name
                else:
                    session.add(UserState(user_id=user_id, state=name))
                session.commit()
            user_state[user_id] = "MAIN_MENU"
            await send_messages(event, MESSAGES["WELLCOM"].format(name=name))
            await send_main_menu(event, user_id)
        elif text == "2":
            user_state[user_id] = "awaiting_name"
            await send_messages(event, MESSAGES["NEW_NAME"])

    elif current_state == "MAIN_MENU":
        if text == "1":
            user_state[user_id] = "awaiting_TMD_SUB"
            user_state[f"{user_id}_order"] = MESSAGES["TMD"]  # ذخیره مقدار سفارش، مثلاً "تمدید"
            order_message = [msg.format(order=MESSAGES["TMD"]) for msg in MESSAGES["ORDER"]]
            await send_messages(event, order_message)
            await send_messages(event, MESSAGES["GO_BACK"])

        elif text == "2":
            user_state[user_id] = "awaiting_NEW_USER"
            user_state[f"{user_id}_order"] = MESSAGES["NEW"]  # ذخیره مقدار سفارش، مثلاً "خرید"
            order_message = [msg.format(order=MESSAGES["NEW"]) for msg in MESSAGES["ORDER"]]
            await send_messages(event, order_message)
            await send_messages(event, MESSAGES["GO_BACK"])

        elif text == "3":
            user_state[user_id] = "awaiting_OLD_USER"
            await send_messages(event, MESSAGES["OLD_NAME"])

        elif text == "4":
            user_state[user_id] = "awaiting_name"
            await send_messages(event, MESSAGES["NEW_NAME"])

# -------------------------------------------------------------------
    if current_state == "awaiting_TMD_SUB":
        if text in ("50", "30"):
            user_state[user_id] = "awaiting_TMD_SUB_client_name"
            user_state[f"{user_id}_SUB_type"] = text
            await send_messages(event, MESSAGES["TMD_NAME"])
        elif text in ("9", "0"):
            user_state[user_id] = "MAIN_MENU"
            await send_main_menu(event, user_id)
            
    elif current_state == "awaiting_TMD_SUB_client_name":
        sub_type = user_state.pop(f"{user_id}_SUB_type", None)    
        if sub_type:
            volume = MESSAGES["50G"] if sub_type == "50" else MESSAGES["30G"]
            toman = MESSAGES["50T"] if sub_type == "50" else MESSAGES["30T"]
            message = MESSAGES["TMD_RESID"].format(client_name=text, total_flow=volume, TMD_mablagh=toman)
            await send_messages(event, message)
            formatted_bank_message = MESSAGES["BANK_CARD"][0].format(mablagh=toman)
            await send_messages(event, [formatted_bank_message])
            await send_messages(event, MESSAGES["GO_BACK"])
            user_state[user_id] = "TMD_MENU"

            # ذخیره client_name و total_flow در دیتابیس + اجرای اسکریپت
            client_name_input = text.strip()
            total_flow_input = sub_type  # "50" یا "30"
            inputs_cursor.execute(
                "INSERT INTO inputs (client_name, total_flow, duration) VALUES (?, ?, ?)",
                (client_name_input, total_flow_input, DURATION)
            )
            inputs_conn.commit()
            subprocess.call("/root/myenv/bin/python3 extend_subscription.py", shell=True)

    elif current_state == "TMD_MENU":
        if text == "9":
            user_state[user_id] = "awaiting_TMD_SUB"
            await send_messages(event, MESSAGES["TMD_MENU"])
            await send_messages(event, MESSAGES["GO_BACK"])

        elif text == "0":
            user_state[user_id] = "MAIN_MENU"
            await send_main_menu(event, user_id)
# -------------------------------------------------------------------

    elif current_state == "awaiting_NEW_USER":
        if text in ("50", "30"):
            user_state[user_id] = "awaiting_NEW_USER_NEW_username"
            user_state[f"{user_id}_SUB_type"] = text
            await send_messages(event, MESSAGES["NEW_USER_NAME"])
        elif text in ("9", "0"):
            user_state[user_id] = "MAIN_MENU"
            await send_main_menu(event, user_id)

    elif current_state == "awaiting_NEW_USER_NEW_username":
        sub_type = user_state.pop(f"{user_id}_SUB_type", None)
        if sub_type:
            volume = MESSAGES["50G"] if sub_type == "50" else MESSAGES["30G"]
            toman = MESSAGES["50T"] if sub_type == "50" else MESSAGES["30T"]
            message = MESSAGES["NEW_USER_RESID"].format(NEW_username=text, NEW_hajm=volume, NEW_mablagh=toman)
            await send_messages(event, message)
            formatted_bank_message = MESSAGES["BANK_CARD"][0].format(mablagh=toman)
            await send_messages(event, [formatted_bank_message])
            await send_messages(event, MESSAGES["GO_BACK"])
            user_state[user_id] = "NEW_USER"

    elif current_state == "NEW_USER":
        if text == "9":
            user_state[user_id] = "awaiting_NEW_USER"
            await send_messages(event, MESSAGES["NEW_USER"])
            await send_messages(event, MESSAGES["GO_BACK"])

        elif text == "0":
            user_state[user_id] = "MAIN_MENU"
            await send_main_menu(event, user_id)

    elif current_state == "awaiting_OLD_USER":
        if text in ("9", "0"):
            user_state[user_id] = "MAIN_MENU"
            await send_main_menu(event, user_id)
        else:
            await send_messages(event, MESSAGES["OLD_RESID"].format(OLD_username=text))
            await send_messages(event, MESSAGES["GO_BACK"])

    logger.info(f"Sent messages to {user_id}")

# هندلر فایل‌ها
@client.on(events.NewMessage(func=lambda e: e.media or e.raw_text in ("my:files",) or e.raw_text.startswith("sendme:")))
async def file_handler(event):
    is_outgoing = event.out
    user_id = event.chat_id if is_outgoing else event.sender_id
    
    if user_id in allowed_users:
        user_folder_name = await get_username(user_id)
        user_folder = os.path.join('/root/DATA/Uploads', user_folder_name)
        
        if not os.path.exists(user_folder):
            os.makedirs(user_folder)

        if event.media:
            try:
                filename = None
                if isinstance(event.media, types.MessageMediaDocument):
                    for attr in event.media.document.attributes:
                        if isinstance(attr, types.DocumentAttributeFilename):
                            filename = attr.file_name
                            break
                elif isinstance(event.media, types.MessageMediaPhoto):
                    filename = 'photo.jpg'

                if filename and not is_outgoing:
                    _, ext = os.path.splitext(filename)
                    if ext.lower() in block_format:
                        if user_id not in block_reply_files:
                            await event.reply(MESSAGES['blocklist_format'].format(ext=ext))
                        logger.warning(f'فایل با پسوند {ext} از کاربر {user_id} بلاک شد.')
                        return

                await event.download_media(file=user_folder + '/')
                logger.info(f'فایل {"ارسالی به" if is_outgoing else "دریافتی از"} کاربر {user_id} ذخیره شد.')
                
                if not is_outgoing and user_id not in block_reply_files:
                    await event.reply(MESSAGES['file_saved'])

            except Exception as e:
                logger.error(f'خطا در ذخیره فایل برای کاربر {user_id}: {e}')
                if not is_outgoing and user_id not in block_reply_files:
                    await event.reply(MESSAGES['file_error'])

        elif event.raw_text == "my:files":
            try:
                files = os.listdir(user_folder)
                if files:
                    file_list = "\n".join(files)
                    await event.reply(MESSAGES['files_list'].format(file_list=file_list))
                else:
                    await event.reply(MESSAGES['no_files'])
            except Exception as e:
                logger.error(f'خطا در لیست فایل‌ها برای کاربر {user_id}: {e}')
                await event.reply(MESSAGES['file_list_error'])

        elif event.raw_text.startswith("sendme:"):
            file_name = event.raw_text.split("sendme:", 1)[1].strip()
            file_path = os.path.join(user_folder, file_name)
            if os.path.exists(file_path):
                await event.reply(file=file_path)
                logger.info(f'فایل {file_name} برای کاربر {user_id} ارسال شد.')
            else:
                await event.reply(MESSAGES['file_not_found'].format(file_name=file_name))

# راه‌اندازی سرویس
client.start()
logger.info("Connected to Telegram." if client.is_connected() else "Connection failed.")
client.run_until_disconnected()
