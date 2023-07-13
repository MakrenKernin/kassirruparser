from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import time
import json

def create_data(name, theatre, duration, description, dates, prices, first_img_link, last_date_link):
    data = {
        'name': name,
        'theatre': theatre,
        'duration': duration,
        'description': description,
        'dates': dates,
        'prices': prices,
        'first_img_link': first_img_link,
        'last_date_link': last_date_link,
    }
    return data

def parse_show(url):
    driver = webdriver.Chrome()  # Инициализация веб-драйвера (Chrome)
    driver.get(url)  # Открытие веб-страницы
    # Создание объекта BeautifulSoup для парсинга содержимого страницы
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    # Ждем, пока элемент с названием загрузится на странице
    wait = WebDriverWait(driver, 10)
    name_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'h1[data-ajaxupdateable="title"]')))
    # Извлечение названия спектакля
    name = name_element.text.replace('\n', "")

    # Извлечение театра
    try:
        theatre = soup.find("div", {"class": "place-name"}).text.replace('\n', "")
    except:
        theatre = None

    # Извлечение описания
    try:
        div_element = soup.find("div", {"class": "full"})
        p_tags = div_element.find_all("p")
        description = [tag.text for tag in p_tags]
    except:
        description = None

    # Извлечение продолжительности
    try:
        div_element = soup.find("div", {"class": "full"})
        p_tags = div_element.find_all("p")
        duration = None

        for tag in p_tags:
            if "Продолжительность:" in tag.text:
                duration = tag.text.split("Продолжительность:", 1)[-1].strip()
                break
    except:
        duration = None

    # Извлечение дат
    try:
        # Проверяем наличие выпадающего списка
        element = driver.find_element(By.CLASS_NAME, "date-dropdown")
        element.click()

        # Ждем, пока появится выпадающий список
        dropdown = WebDriverWait(driver, 1).until(
            EC.presence_of_element_located((By.CLASS_NAME, "jq-selectbox__dropdown"))
        )

        # Извлекаем текст из элемента dropdown и преобразуем его в список
        dropdown_text = dropdown.text.split('\n')
        dates = [item for item in dropdown_text if item.strip() != '']

        # Находим все элементы <li> в выпадающем списке
        dropdown_items = dropdown.find_elements(By.CSS_SELECTOR, "li")

        # Выполняем клик по последнему элементу в списке
        last_item = dropdown_items[-1]
        last_item.click()

    except:
        # Если выпадающий список отсутствует, извлекаем дату из элемента с классом "date"
        try:
            date_element = driver.find_element(By.CLASS_NAME, "date")
            date = date_element.text.strip()
            dates = [date]
        except:
            dates = None

    # Парсинг цен
    prices = set()
    buttons = driver.find_elements(By.XPATH, "//table[contains(@class, 'table table-price')]//a[contains(text(), 'Выбрать места')]")
    for button in buttons:
        driver.execute_script("arguments[0].click();", button)
        time.sleep(5)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.item:not([class*=' '])")))
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        items = soup.select("div.item:not([class*=' '])")
        for item in items:
            price = int(item.text.split()[0].replace(" Р.", ""))
            prices.add(price)
        driver.find_element(By.CSS_SELECTOR, "body").send_keys(Keys.ESCAPE)
        time.sleep(2)
    prices = sorted(prices)

    # Извлечение ссылки на фото
    try:
        first_img_link = soup.find("div", {"class": "image"}).find("img")["src"]
    except:
        first_img_link = None

    # Извлечение последней даты
    try:
        last_date_link = dates[-1]
    except:
        last_date_link = None

    driver.quit()  # Закрытие веб-драйвера

    result = create_data(name, theatre, duration, description, dates, prices, first_img_link, last_date_link)
    result_json = json.dumps(result, indent=4, ensure_ascii=False)
    return result_json

if __name__ == "__main__":
    url_list = [
        'https://msk.kassir.ru/teatr/nichego-ne-boysya-ya-s-toboy#1589112'
    ]

    parsed_data_list = []

    for url in url_list:
        parsed_data = parse_show(url)
        parsed_data_list.append(parsed_data)

    #url = input("Введите или вставьте URL на спектакль: ")
    #url = 'https://msk.kassir.ru/teatr/nichego-ne-boysya-ya-s-toboy#1589112'
    #parsed_data = parse_show(url)
    print(parsed_data)
