import asyncio
from aiogram import Bot
from datetime import datetime
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC



# все данные
chat_id = YOUR_TG_ID # можно поставить свой id (кому бот присылает дз)
phone_number = "PHONE_NUMBER" 
password = "PASSWORD_GOSUSLUGI"
token = "TOKEN"


url = None
url0 = "https://school.yarcloud.ru/journal-app/u.543/week.0" 
url1 = "https://school.yarcloud.ru/journal-app/u.543/week.-1"

# Создаем объекты бота и диспетчера
bot = Bot(token)

# получаем день недели и выбираем ссылку
week_day = datetime.now().isoweekday() - 1
if week_day < 5:
    url = url0
    week_day += 1
else:
    url = url1
    week_day = 0

# настройки открытия браузера
service = Service()
options = webdriver.ChromeOptions()
options.add_argument('--no-sandbox')
# # options.add_argument('headless') # можно убрать, но тогда при запуске программы будет открываться браузер

# функция по отправке сообщения
async def send_message(chat_id, msg):
    if msg == f"":
        sent_message = await bot.send_message(chat_id, f"Дз на следующий день не записанно")
        await bot.pin_chat_message(chat_id=chat_id, message_id=sent_message.message_id)
        # sent_message = asyncio.run(bot.send_message(chat_id, f"Дз на следующий день не записанно"))  # вставить тг айди группы или свой
        # asyncio.run(bot.pin_chat_message(chat_id=chat_id, message_id=sent_message.message_id))
        # sent_message = asyncio.get_event_loop().run_until_complete(bot.send_message(chat_id, f"Дз на следующий день не записанно"))
        # asyncio.get_event_loop().run_until_complete(bot.pin_chat_message(chat_id=chat_id, message_id=sent_message.message_id))
    else:
        sent_message = await bot.send_message(chat_id, msg)
        await bot.pin_chat_message(chat_id=chat_id, message_id=sent_message.message_id)


def main():
    try:
        # открытие сайта
        driver = webdriver.Chrome(service=service, options=options)
        driver.get('https://school.yarcloud.ru/journal-app/')
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//a[contains(@class,'esia-login-page__button')]"))
        )

        # поиск кнопки и нажатие на неё
        reg_button = driver.find_element(By.XPATH, "//a[contains(@class,'esia-login-page__button')]")
        reg_button.click()
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "login"))
        )

        # ввод логина и пароля для перехода в дневник
        login = driver.find_element(By.ID, "login")
        login.send_keys(phone_number)
        password_gosuslugi = driver.find_element(By.ID, "password")
        password_gosuslugi.send_keys(password)
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Войти')]"))
        )

        # нажатие кнопки для перехода в дневник
        driver.find_element(By.XPATH, "//button[contains(text(), 'Войти')]").click()
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "dnevnikDays"))
        )

        # перерегистрация домена
        driver.get(url)
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "dnevnikDays"))
        )

        # ищем див dnevnikDays в котором лежат дни недели с дз
        el = driver.find_element(By.ID, "dnevnikDays")
        html = el.get_attribute('outerHTML')

        # закрываем сайт и сохраняем дни дневника
        driver.close()
        soup = BeautifulSoup(html, "html.parser")
        all_days = soup.find_all('div', class_='dnevnik-day')

        # определяем с каким днём недели надо работать
        hw_day = all_days[week_day]
        lessons = hw_day.find_all('div', class_='dnevnik-lesson')
        msg = f""
        for lesson in lessons:
            try:
                name_lesson = lesson.select_one('.js-rt_licey-dnevnik-subject').text
                task_lesson = lesson.select_one('.dnevnik-lesson__task').text
                # lesson.select_one(".dnevnik-lesson__attach").get("href")
                msg += f"{name_lesson.strip()}: {task_lesson.strip()}"
                msg += "\n"
            except:
                pass
        asyncio.get_event_loop().run_until_complete(
            send_message(chat_id, msg)
        )
    except:
        asyncio.get_event_loop().run_until_complete(
            send_message(your_id, f"Что-то пошло не так")
        )

if __name__ == "__main__":
    main()
