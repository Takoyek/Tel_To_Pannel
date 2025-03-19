import os
import sqlite3
from datetime import datetime
import jdatetime  # نیاز به نصب: pip install jdatetime

def is_sqlite3_file(file_path):
    try:
        with open(file_path, 'rb') as f:
            header = f.read(100)
        return header.startswith(b'SQLite format 3\x00')
    except Exception:
        return False

def convert_timestamp(ts):
    try:
        if ts == 0:
            return "بدون انقضا"
        dt = datetime.fromtimestamp(ts / 1000)
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except Exception as e:
        print(f"Error converting timestamp {ts}: {e}")
        return ts

def to_shamsi(dt_str):
    try:
        dt = datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
        jd = jdatetime.datetime.fromgregorian(datetime=dt)
        return jd.strftime('%Y/%m/%d %H:%M:%S')
    except:
        return "تبدیل ناموفق"

def calculate_time_remaining(expire_ts, refreshed_on):
    try:
        expire_dt = datetime.fromtimestamp(expire_ts / 1000)
        refreshed_dt = datetime.strptime(refreshed_on, '%Y-%m-%d %H:%M:%S')
        delta = expire_dt - refreshed_dt
        
        days = delta.days
        hours = delta.seconds // 3600
        return f"{days} روز - {hours} ساعت"
    except:
        return "نامعلوم"

def format_bytes(size):
    if size == 0:
        return "نامحدود"
    
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    index = 0
    while size >= 1024 and index < 4:
        size /= 1024
        index += 1
    return f"{size:.2f}{units[index]}"

def format_user_data(row):
    refreshed_on = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    expire_date = convert_timestamp(row.get('expiry_time', 0))
    
    # محاسبات داده
    total_data = row.get('total', 0)
    upload = row.get('up', 0)
    download = row.get('down', 0)
    used_data = upload + download
    remaining_data = total_data - used_data if total_data > 0 else 0
    
    formatted = {
        '🆔 Usaer Name': row.get('email', 'N/A'),
        '🛜 Status': '✅ Enable' if row.get('enable', 0) == 1 else '❌ Disable',
        '📅 Expire Date': expire_date,
        '📅 تاریخ شمسی': to_shamsi(expire_date) if expire_date != "بدون انقضا" else "بدون انقضا",
        '⏰ Remainin Time': calculate_time_remaining(row.get('expiry_time', 0), refreshed_on),
        '🔋 Total Data': format_bytes(total_data),
        '🪫 Used Data': format_bytes(used_data),
        '🔼 Upload': f"↑{format_bytes(upload)}",
        '🔽 Download': f"↓{format_bytes(download)}",
        '⌛️ Remaining Data': format_bytes(remaining_data) if total_data > 0 else "نامحدود",
        '♻️ Refreshed On': refreshed_on
    }
    
    return formatted

def search_in_sqlite(db_path, search_term):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        found = False

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [table[0] for table in cursor.fetchall()]

        for table_name in tables:
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = [col[1] for col in cursor.fetchall()]
            
            if 'email' not in [col.lower() for col in columns]:
                continue

            cursor.execute(
                f'''SELECT * FROM "{table_name}" 
                WHERE LOWER(email) LIKE ?''',
                ('%' + search_term.lower() + '%',)
            )
            results = cursor.fetchall()
            
            if results:
                print(f"\n\033[92m• نتایج در جدول: {table_name}\033[0m")
                print(f"\033[94mتعداد رکوردها: {len(results)}\033[0m")
                
                cursor.execute(f"PRAGMA table_info({table_name})")
                column_names = [col[1] for col in cursor.fetchall()]
                
                for row in results[:3]:
                    raw_data = dict(zip(column_names, row))
                    formatted_data = format_user_data(raw_data)
                    
                    print("\n\033[95m" + "="*55 + "\033[0m")
                    # چیدمان جدید خروجی
                    keys_order = [
                        '🆔 Usaer Name', '🛜 Status',
                        '📅 Expire Date', '📅 تاریخ شمسی',
                        '⏰ Remainin Time', 
                        '🔋 Total Data', '🪫 Used Data',
                        '🔼 Upload', '🔽 Download', 
                        '⌛️ Remaining Data', '♻️ Refreshed On'
                    ]
                    
                    for key in keys_order:
                        if key in formatted_data:
                            print(f"{key}: {formatted_data[key]}")
                    print("\033[95m" + "="*55 + "\033[0m")
                
                found = True

        conn.close()
        return found

    except Exception as e:
        print(f"\033[91mخطا: {str(e)}\033[0m")
        return False

# بقیه کد main() بدون تغییر باقی میماند

    except Exception as e:
        print(f"\033[91mخطا: {str(e)}\033[0m")
        return False

def main():
    file_path = r"D:\AVIDA\CODE\Tel_To_Pannel\db_files\x-ui (9).db"    
    search_term = input("\033[93mلطفاً نام کاربری را وارد کنید: \033[0m").strip()
    if not search_term:
        print("\033[91mخطا: عبارت جستجو نمیتواند خالی باشد.\033[0m")
        return

    if not os.path.exists(file_path):
        print(f"\033[91mخطا: فایل {file_path} یافت نشد\033[0m")
        return

    if not is_sqlite3_file(file_path):
        print("\033[91mخطا: فرمت فایل SQLite معتبر نیست\033[0m")
        return

    found = search_in_sqlite(file_path, search_term)
    
    print("\n\033[1m" + "="*40)
    print("\033[92mنتیجه نهایی: یافت شد" if found else "\033[91mنتیجه نهایی: یافت نشد")
    print("="*40 + "\033[0m")

if __name__ == "__main__":
    main()