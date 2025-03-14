import os
import sqlite3

def is_sqlite3_file(file_path):
    try:
        with open(file_path, 'rb') as f:
            header = f.read(100)
        return header.startswith(b'SQLite format 3\x00')
    except Exception:
        return False

def search_in_sqlite(db_path, search_term):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        found = False

        # جستجو در تمام جداول برای ستون email
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        for table in tables:
            table_name = table[0]
            # بررسی وجود ستون email در جدول
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            # بررسی وجود ستون email
            email_column = any(col[1].lower() == 'email' for col in columns)
            if not email_column:
                continue

            # اجرای جستجو در ستون email
            cursor.execute(
                f'SELECT * FROM "{table_name}" WHERE "email" LIKE ?',
                ('%' + search_term + '%',)
            )
            results = cursor.fetchall()
            
            if results:
                print(f"\nیافت شد در جدول: {table_name}")
                print(f"تعداد نتایج: {len(results)}")
                print("نمونه رکوردها:")
                for row in results[:3]:
                    print(row)
                found = True

        conn.close()
        return found

    except Exception as e:
        print(f"خطا در جستجو: {str(e)}")
        return False

def main():
    file_path = r"D:\AVIDA\CODE\Tel_To_Pannel\x-ui.db"
    
    # دریافت عبارت جستجو از کاربر
    search_term = input("لطفاً نام کاربری را وارد کنید: ").strip()
    
    if not search_term:
        print("عبارت جستجو نمیتواند خالی باشد.")
        return

    if not os.path.exists(file_path):
        print(f"فایل پیدا نشد: {file_path}")
        return

    if is_sqlite3_file(file_path):
        found = search_in_sqlite(file_path, search_term)
    else:
        print("این فایل از نوع SQLite نیست.")
        found = False

    print("\nنتیجه نهایی:")
    print("یافت شد" if found else "یافت نشد")

if __name__ == "__main__":
    main()