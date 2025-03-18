import os
import sqlite3
from datetime import datetime

def convert_timestamp(ts):
    try:
        ts_val = float(ts)
        # اگر مقدار ts به نظر برسد که بر حسب میلی‌ثانیه است (مثلاً با اعداد 13 رقمی)، تقسیم بر 1000 کنید
        if ts_val > 10**10:
            ts_val /= 1000
        return datetime.fromtimestamp(ts_val).strftime('%Y-%m-%d %H:%M:%S') if ts_val != 0 else "بدون انقضا"
    except Exception as e:
        return ts

def is_sqlite3_file(file_path):
    try:
        with open(file_path, 'rb') as f:
            header = f.read(100)
        return header.startswith(b'SQLite format 3\x00')
    except Exception:
        return False

def convert_timestamp(ts):
    try:
        return datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S') if ts != 0 else "بدون انقضا"
    except:
        return ts

def format_bytes(size):
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    index = 0
    while size >= 1024 and index < 4:
        size /= 1024
        index += 1
    return f"{size:.2f}{units[index]}"

def format_user_data(row):
    formatted = {
        '📧 Email': row.get('email', 'N/A'),
        '🚨 Enabled': '✅ Yes' if row.get('enable', 0) == 1 else '❌ No',
        '📅 Expire Date': convert_timestamp(row.get('expiry_time', 0)),
        '🔼 Upload': f"↑{format_bytes(row.get('up', 0))}",
        '🔽 Download': f"↓{format_bytes(row.get('down', 0))}",
        '📊 Total': f"↑↓{format_bytes(row.get('total', 0))}",
        '📋🔄 Refreshed On': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    # حذف فیلدهای ناخواسته
    excluded_fields = ['id', 'inbound_id']
    return {k: v for k, v in formatted.items() if k.split()[-1] not in excluded_fields}

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
                    
                    print("\n\033[95m" + "="*40 + "\033[0m")
                    for key, value in formatted_data.items():
                        print(f"{key}: {value}")
                    print("\033[95m" + "="*40 + "\033[0m")
                
                found = True

        conn.close()
        return found

    except Exception as e:
        print(f"\033[91mخطا: {str(e)}\033[0m")
        return False

def main():
    file_path = r"D:\AVIDA\CODE\Tel_To_Pannel\x-ui.db"
    
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