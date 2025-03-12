import os
import shutil
import math
import time
import subprocess
from PIL import Image
from io import BytesIO
from selenium import webdriver
from colorama import Fore, Style
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
import sqlite3

# دریافت مقادیر از پایگاه داده
conn = sqlite3.connect("inputs.db")
cursor = conn.cursor()
cursor.execute("SELECT client_name, total_flow, duration FROM inputs ORDER BY id DESC LIMIT 1")
row = cursor.fetchone()
if row:
    CLIENT_NAME, TOTAL_FLOW, DURATION = row
    print("مقادیر خوانده شده از پایگاه داده:")
    print("CLIENT_NAME =", CLIENT_NAME)
    print("TOTAL_FLOW  =", TOTAL_FLOW)
    print("DURATION    =", DURATION)
else:
    CLIENT_NAME = "Nadia-New"
    TOTAL_FLOW  = "666"
    DURATION    = "777"
    print("هیچ داده‌ای در پایگاه داده یافت نشد؛ استفاده از مقادیر پیش‌فرض.")
conn.close()

WAIT_TIME   = 1
BASE_URL    = "http://tmd.taino.top:2095/"



def take_full_page_screenshot(browser, save_path):
    browser.set_window_size(1920, 1080)
    screenshot_png = browser.get_screenshot_as_png()
    original_image = Image.open(BytesIO(screenshot_png))
    pixel_ratio = browser.execute_script("return window.devicePixelRatio") or 1
    width, height = original_image.size
    new_width = int(width * pixel_ratio)
    new_height = int(height * pixel_ratio)
    final_image = original_image.resize((new_width, new_height), Image.LANCZOS)
    final_image.save(save_path, quality=95, optimize=True)


def login_to_panel(username, password):
    try:
        browser.get(BASE_URL)       
        WebDriverWait(browser, 5).until(
            EC.presence_of_element_located((By.NAME, "username"))
        )        
        username_field = browser.find_element(By.NAME, 'username')
        password_field = browser.find_element(By.NAME, 'password')        
        username_field.clear()
        password_field.clear()
        username_field.send_keys(username)
        password_field.send_keys(password)
        password_field.send_keys(Keys.RETURN)
        
        WebDriverWait(browser, 5).until(lambda driver: "panel" in driver.current_url.lower())
        
        if "login" in browser.current_url.lower():
            raise Exception("ورود با خطا مواجه شد.")  
        print(Fore.GREEN + "ورود به پنل انجام شد.\n\n" + Style.RESET_ALL + " آدرس فعلی: \n" + Fore.YELLOW 
            + str(browser.current_url) + Style.RESET_ALL)

    except Exception as e:
        print("خطا در ورود به پنل:", e)
        error_screenshot = os.path.join("/root/Screen/", "login_error.png")
        take_full_page_screenshot(browser, error_screenshot)


def click_inbounds():
    try:
        inbound_button = WebDriverWait(browser, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//b[text()='Inbounds']/.."))
        )
        browser.execute_script("arguments[0].scrollIntoView(true);", inbound_button)
        inbound_button.click()
    except Exception as e:
        print("خطا در یافتن یا کلیک روی دکمه 'Inbounds':", e)
    time.sleep(WAIT_TIME)
    print("کلیک روی دکمه '" + Fore.BLUE + "Inbounds" + Style.RESET_ALL + "' انجام شد.\n")
    print("آدرس فعلی: \n" + Fore.YELLOW + str(browser.current_url) + Style.RESET_ALL)


def search_client_and_capture(CLIENT_NAME):
    try:
        search_input = WebDriverWait(browser, 5).until(
            EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Search']"))
        )
    except Exception as e:
        print("خطا در یافتن فیلد جستجو:", e)
        return

    browser.execute_script("arguments[0].scrollIntoView(true);", search_input)
    
    search_input.clear()
    search_input.send_keys(CLIENT_NAME)
    search_input.send_keys(Keys.RETURN)
    print(f"\n در حال جستجو کلاینت: '" + Fore.YELLOW + f"{CLIENT_NAME}" + Style.RESET_ALL + "' \n")
    
    time.sleep(WAIT_TIME)
    # full_search_screenshot = os.path.join("/root/Screen/", "search_result_full.png")
    # take_full_page_screenshot(browser, full_search_screenshot)


def expand_all_inbound_rows():
    try:
        expand_buttons = WebDriverWait(browser, 5).until(
            EC.presence_of_all_elements_located((
                By.XPATH, 
                "//div[@role='button' and @aria-label='Expand row' and contains(@class, 'ant-table-row-collapsed')]"
            ))
        )
        print(Fore.YELLOW + f"{len(expand_buttons)}" + Style.RESET_ALL + " دکمه برای باز کردن زیر مجموعه‌ ها پیدا شدند.\n")
        
        for btn in expand_buttons:
            try:
                browser.execute_script("arguments[0].scrollIntoView(true);", btn)
                time.sleep(0.5)
                btn.click()
            except Exception as ex:
                print("خطا در کلیک روی دکمه Expand:", ex)
            time.sleep(1)
    except Exception as e:
        print("خطا در باز کردن زیرمجموعه‌های اینباند:", e)

    full_screenshot_path = os.path.join("/root/Screen/", "01_inbounds.png")
    take_full_page_screenshot(browser, full_screenshot_path)


def click_exact_edit_client():
    try:        
        rows = WebDriverWait(browser, 5).until(
            EC.presence_of_all_elements_located((By.XPATH, "//tr[contains(@class, 'ant-table-row')]"))
        )
        
        for row in rows:
            try:
                cell = row.find_element(By.XPATH, ".//td[normalize-space(text())='{}']".format(CLIENT_NAME))
                if cell:
                    edit_btn = row.find_element(
                        By.XPATH, ".//i[contains(@class, 'normal-icon') and contains(@class, 'anticon-edit')]"
                    )
                    browser.execute_script("arguments[0].scrollIntoView(true);", edit_btn)
                    browser.execute_script("arguments[0].click();", edit_btn)
                    print("دکمه '" + Fore.BLUE + "Edit Client" + Style.RESET_ALL 
                        + "' مربوط به رکورد '" + Fore.YELLOW + "{}".format(CLIENT_NAME) + Style.RESET_ALL + "' کلیک شد.\n")


                    return
            except Exception as inner_e:
                continue
        print("ردیف دقیق '{}' پیدا نشد!".format(CLIENT_NAME))
    except Exception as e:
        print("خطا در انتخاب دقیق '{}' و کلیک روی Edit Client:".format(CLIENT_NAME), e)


def edit_total_flow_value(new_value):
    try:
        total_flow_input = WebDriverWait(browser, 5).until(
            EC.presence_of_element_located((
                By.XPATH,
                "//div[contains(@class, 'ant-form-item') and .//*[contains(text(), 'Total Flow')]]//input"
            ))
        )
        total_flow_input.clear()
        time.sleep(0.5)
        browser.execute_script(
            "arguments[0].value=''; arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", 
            total_flow_input
        )
        time.sleep(0.5)
        total_flow_input.send_keys(new_value)
        print(f"مقدار فیلد {Fore.BLUE}'Total Flow'{Style.RESET_ALL} "
        f"به {Fore.YELLOW}{new_value}{Style.RESET_ALL} تغییر یافت.\n")

    except Exception as e:
        print("خطا در تغییر مقدار 'Total Flow':", e)


def click_reset_traffic():
    try:
        reset_button = WebDriverWait(browser, 5).until(
            EC.presence_of_element_located((
                By.XPATH,
                "//div[contains(@class, 'ant-form-item') and .//*[contains(text(), 'Usage')]]//i"
            ))
        )
        browser.execute_script("arguments[0].click();", reset_button)
        print("کلیک روی دکمه '" + Fore.MAGENTA + "Reset Traffic" + Style.RESET_ALL + "' انجام شد.\n")
        #time.sleep(WAIT_TIME)
        #reset_screenshot_path = os.path.join("/root/Screen/", "reset_traffic_result.png")
        #take_full_page_screenshot(browser, reset_screenshot_path)
    except Exception as e:
        time.sleep(WAIT_TIME)
        print("خطا در عملیات کلیک روی دکمه 'Reset Traffic':", e)
        error_screenshot = os.path.join("/root/Screen/", "reset_traffic_error.png")
        take_full_page_screenshot(browser, error_screenshot)


def click_reset_confirmation_and_capture():
    try:
        confirmation = WebDriverWait(browser, 5).until(
            EC.presence_of_element_located(
                (By.XPATH, "//div[contains(text(), 'Are you sure you want to reset traffic?')]")
            )
        )
        print("پنجره تایید '" + Fore.MAGENTA + "Reset Traffic" + Style.RESET_ALL + "' ظاهر شد.\n")
        ActionChains(browser).send_keys(Keys.ENTER).perform()
        print("کلید '" + Fore.MAGENTA + "ENTER" + Style.RESET_ALL + "' ارسال شد.\n")

#        time.sleep(WAIT_TIME)
#        confirm_screenshot_path = os.path.join("/root/Screen/", "reset_confirm_result.png")
#        take_full_page_screenshot(browser, confirm_screenshot_path)
    except Exception as e:
        print("خطا در عملیات تایید Reset Traffic:", e)


# ------------------  پارت دوم  ------------------

def edit_client_window_and_capture():
    try:
        WebDriverWait(browser, WAIT_TIME).until(
            EC.visibility_of_element_located((By.ID, "client-modal"))
        )
        time.sleep(1)
        
        before_path = os.path.join("/root/Screen/", "02_edit_client_before.png")
        take_full_page_screenshot(browser, before_path)
        
        edit_total_flow_value(TOTAL_FLOW)
        
        WebDriverWait(browser, WAIT_TIME).until(
            lambda driver: driver.execute_script("return document.readyState") == "complete"
        )
        
        click_reset_traffic()
        click_reset_confirmation_and_capture()
        
        # after_path = os.path.join("/root/Screen/", "edit_client_after.png")
        # take_full_page_screenshot(browser, after_path)
    except Exception as e:
        print("خطا در عملیات ویرایش پنجره 'Edit Client':", e)


def toggle_start_after_first_use_and_capture():
    try:
        btn = WebDriverWait(browser, 5).until(
            EC.presence_of_element_located((
                By.XPATH,
                "//div[contains(@class, 'ant-form-item') and .//*[contains(text(), 'Start After First Use')]]//button"
            ))
        )
        browser.execute_script("arguments[0].scrollIntoView(true);", btn)
        state = btn.get_attribute("aria-pressed")
        if state is None:
            classes = btn.get_attribute("class")
            if classes and "ant-switch-checked" in classes:
                state = "true"
            else:
                state = "false"
        print("وضعیت اولیه دکمه 'Start After First Use' برابر است با:", state)
        if state.lower() != "true":
            btn.click()
            #time.sleep(WAIT_TIME)
        else:
            print("\nدکمه نیاز به تغییر ندارد.\n")
#        screenshot_path = os.path.join("/root/Screen/", "start_after_updated.png")
#        take_full_page_screenshot(browser, screenshot_path)
    except Exception as e:
        print("خطا در عملیات تغییر وضعیت دکمه 'Start After First Use':", e)


def update_duration_field_by_selector(new_value=None):
    if new_value is None:
        new_value = DURATION
    try:
        duration_input = WebDriverWait(browser, 5).until(
            EC.presence_of_element_located((
                By.XPATH,
                "//div[contains(@class, 'ant-form-item') and .//*[contains(text(), 'Duration')]]//input"
            ))
        )
        duration_input.clear()
        time.sleep(0.5)
        browser.execute_script("arguments[0].value=''; arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", duration_input)
        time.sleep(0.5)
        duration_input.send_keys(new_value)
        print(f"\n فیلد '" + Fore.MAGENTA + "Duration" + Style.RESET_ALL 
            + "' به " + Fore.YELLOW + f"{new_value}" + Style.RESET_ALL + " تغییر یافت.\n")
        
        screenshot_path = os.path.join("/root/Screen/", "03_duration.png")
        take_full_page_screenshot(browser, screenshot_path)
    except Exception as e:
        print("خطا در به‌روز کردن فیلد 'Duration':", e)


def save_changes_and_capture():
    try:
        save_button = WebDriverWait(browser, 5).until(
            EC.presence_of_element_located((
                By.CSS_SELECTOR,
                "#client-modal > div.ant-modal-wrap > div > div.ant-modal-content > div.ant-modal-footer > div > button.ant-btn.ant-btn-primary"
            ))
        )
        browser.execute_script("arguments[0].scrollIntoView(true);", save_button)
        browser.execute_script("arguments[0].click();", save_button)
        print("کلیک روی دکمه '" + Fore.MAGENTA + "Save Changes" + Style.RESET_ALL + "' انجام شد.\n")
        time.sleep(WAIT_TIME + 1)
        final_save_path = os.path.join("/root/Screen/", "04_save_changes.png")
        take_full_page_screenshot(browser, final_save_path)
    except Exception as e:
        print("خطا در عملیات کلیک روی دکمه 'Save Changes' یا گرفتن اسکرین‌شات:", e)


# ------------------ Main Program ------------------

start_time = time.time()
screen_dir = "/root/Screen/"
if os.path.exists(screen_dir):
    shutil.rmtree(screen_dir)
os.makedirs(screen_dir)
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
service = Service(ChromeDriverManager().install())
browser = webdriver.Chrome(service=service, options=options)
print(Fore.GREEN + "\nمرورگر راه‌اندازی شد." + Style.RESET_ALL + "\n")
login_to_panel('msi', 'msi')
click_inbounds()
time.sleep(WAIT_TIME)
search_client_and_capture(CLIENT_NAME)
expand_all_inbound_rows()
click_exact_edit_client()
edit_client_window_and_capture()
toggle_start_after_first_use_and_capture()
update_duration_field_by_selector(DURATION)
save_changes_and_capture()
print(Fore.GREEN + "عملیات تمدید اشتراک کاربر با موفقیت انجام شد." + Style.RESET_ALL)
browser.quit()
subprocess.call("pkill -f chrome", shell=True)
print(Fore.LIGHTRED_EX + "\nمرورگر بسته شد." + Style.RESET_ALL)
end_time = time.time()
elapsed = end_time - start_time
print(Fore.YELLOW + "\nزمان اجرای کل برنامه: {:.2f} ثانیه".format(elapsed) + Style.RESET_ALL)
print(".\n")
