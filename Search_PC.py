import json

# مسیر فایل JSON
file_path = r"D:\AVIDA\CODE\Tel_To_Pannel\js2.json"

# دریافت نام کاربری از کاربر
username = input("لطفاً نام کاربری را وارد کنید: ")

# خواندن فایل JSON
with open(file_path, 'r', encoding='utf-8') as file:
    data = json.load(file)

# جستجو در مسیر inbounds/.../settings/clients
found = False
for inbound in data.get("inbounds", []):  # بررسی همه inbounds
    clients = inbound.get("settings", {}).get("clients", [])
    for client in clients:
        if client.get("email") == username:
            found = True
            break  # متوقف کردن جستجو در اولین مورد پیدا شده
    if found:
        break  # خروج از حلقه اصلی

# نمایش نتیجه
if found:
    print(f"✅ نام کاربری '{username}' پیدا شد!")
else:
    print(f"❌ نام کاربری '{username}' پیدا نشد.")
