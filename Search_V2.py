#!/usr/bin/env python3
import os
import sqlite3
from datetime import datetime
import jdatetime

def find_latest_file(directory):
    try:
        files = [
            os.path.join(directory, f)
            for f in os.listdir(directory)
            if os.path.isfile(os.path.join(directory, f))
        ]
        return max(files, key=os.path.getctime) if files else None
    except Exception:
        return None

def is_sqlite3_file(file_path):
    try:
        with open(file_path, 'rb') as f:
            return f.read(100).startswith(b'SQLite format 3\x00')
    except Exception:
        return False

def convert_timestamp(ts):
    try:
        return datetime.fromtimestamp(ts / 1000).strftime('%Y-%b-%d') if ts != 0 else ""
    except Exception:
        return ""

def to_shamsi(dt_str):
    try:
        if not dt_str:
            return ""
        dt = datetime.strptime(dt_str, '%Y-%b-%d')
        return jdatetime.datetime.fromgregorian(datetime=dt).strftime('%Y/%m/%d')
    except Exception:
        return ""

def format_bytes(size):
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    index = 0
    while size >= 1024 and index < 4:
        size /= 1024
        index += 1
    return f"{size:.2f} {units[index]}"

def calculate_time_remaining(expire_ts, refreshed_on):
    try:
        expire_dt = datetime.fromtimestamp(expire_ts / 1000)
        refreshed_dt = datetime.strptime(refreshed_on, '%Y-%m-%d %H:%M')
        delta = expire_dt - refreshed_dt
        return f"{delta.days} روز و {delta.seconds // 3600} ساعت"
    except Exception:
        return ""

def format_user_data(row):
    refreshed_time = datetime.now().strftime('%Y-%m-%d %H:%M')
    expire_date = convert_timestamp(row.get('expiry_time', 0))
    shamsi_expire = to_shamsi(expire_date) if expire_date else "N/A"
    
    try:
        j_date = jdatetime.datetime.fromgregorian(datetime=datetime.strptime(refreshed_time, '%Y-%m-%d %H:%M'))
        refreshed_jdate = j_date.strftime('%Y/%m/%d - %H:%M')
    except Exception:
        refreshed_jdate = ""

    total_data = row.get('total', 0)
    used_data = row.get('up', 0) + row.get('down', 0)
    
    return {
        '📝 نام کاربری': row.get('email', ''),
        '⚙️ وضعیت': '✅ فعال' if row.get('enable', 0) == 1 else '❌ غیرفعال',
        '📅 تاریخ پایان اشتراک': f"\n{shamsi_expire}  --------  {expire_date}" if expire_date else "N/A",
        '⏰ زمان باقیمانده': calculate_time_remaining(row.get('expiry_time', 0), refreshed_time),
        '🔋 حجم کل': format_bytes(total_data),
        '📤 حجم مصرف شده': format_bytes(used_data),
        '📥 حجم باقیمانده': format_bytes(total_data - used_data),
        '♻️ آخرین بروزرسانی': refreshed_jdate
    }

def search_in_sqlite(db_path, search_term):
    try:
        if not is_sqlite3_file(db_path):
            return False

        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            found = False
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [table[0] for table in cursor.fetchall()]

            for table_name in tables:
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = [col[1].lower() for col in cursor.fetchall()]
                
                if 'email' not in columns:
                    continue

                cursor.execute(f'SELECT * FROM "{table_name}" WHERE email = ? COLLATE NOCASE', (search_term,))
                results = cursor.fetchall()
                
                if results:
                    column_names = [col[1] for col in cursor.execute(f"PRAGMA table_info({table_name})").fetchall()]
                    for row in results:
                        formatted_data = format_user_data(dict(zip(column_names, row)))
                        print("\n\033[95m" + "_"*20 + "\033[0m")
                        for key in [
                            '📝 نام کاربری', '⚙️ وضعیت', '📅 تاریخ پایان اشتراک',
                            '⏰ زمان باقیمانده', '🔋 حجم کل', '📤 حجم مصرف شده',
                            '📥 حجم باقیمانده', '♻️ آخرین بروزرسانی'
                        ]:
                            if formatted_data.get(key):
                                print(f"{key}: {formatted_data[key]}")
                        print("\033[95m" + "_"*20 + "\033[0m")
                    found = True
            return found
    except Exception:
        return False






def main():
    directory = r"/root/DATA/Uploads/7517469464 [avidax1_bot]/"
    if not os.path.exists(directory):
        return
    
    latest_file = find_latest_file(directory)
    if not latest_file or not is_sqlite3_file(latest_file):
        return
    
    search_term = input("\033[93m✍️ نام اشتراکی که می خواهید تمدید شود چیست؟ \033[0m").strip()
    if not search_in_sqlite(latest_file, search_term):
        print(f"\n\033[91mاشتراک با نام '{search_term}' وجود ندارد یا اشتباه است.\033[0m")

if __name__ == "__main__":
    main()