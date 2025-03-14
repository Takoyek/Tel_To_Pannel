#!/usr/bin/env python3
import sys
from pathlib import Path

# مسیر فایل مورد نظر در سرور VPS
FILE_PATH = Path("/root/DATA/Uploads/7517469464 [avidax1_bot]/config.json")

def search_query_in_file(query):
    # تابع برای جستجو در فایل مشخص شده (config.json)
    matched_files = []
    # بررسی اینکه مسیر به یک فایل اشاره دارد
    if FILE_PATH.is_file():
        try:
            with FILE_PATH.open('r', encoding='utf-8') as f:
                content = f.read()
                # جستجوی عبارت در محتوای فایل
                if query in content:
                    matched_files.append(FILE_PATH)
        except Exception as e:
            # در صورت بروز مشکل هنگام خواندن فایل، هشدار چاپ می‌شود
            print(f"Warning: Unable to read file {FILE_PATH}. Error: {e}")
    else:
        print(f"File {FILE_PATH} does not exist.")
    return matched_files

def main():
    # اگر آرگومان خط فرمان وارد نشده باشد، از کاربر درخواست می‌شود عبارت را وارد کند.
    if len(sys.argv) < 2:
        query = input("لطفاً نام کاربری را وارد کنید: ")
        if not query.strip():
            print("عبارت جستجو نمی‌تواند خالی باشد.")
            sys.exit(1)
    else:
        query = sys.argv[1]

    results = search_query_in_file(query)

    if results:
        print(f"عبارت '{query}' در فایل زیر یافت شد:")
        for file in results:
            print(file)
    else:
        print(f"عبارت '{query}' در {FILE_PATH} یافت نشد.")

if __name__ == "__main__":
    main()
