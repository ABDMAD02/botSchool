import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import time
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

def get_html_selenium(username, password):
    chrome_options = Options()
    chrome_options.add_argument("--user-data-dir=C:/Users/madi2/OneDrive/Рабочий стол/chrome")
    driver = webdriver.Chrome(options=chrome_options)
    driver.maximize_window()

    try:
        driver.get('https://login1.edupage.org/')

        driver.find_element(By.NAME, 'username').send_keys(username)
        driver.find_element(By.NAME, 'password').send_keys(password + Keys.RETURN)
        time.sleep(3)
        driver.get('https://skillset-schools.edupage.org/znamky/')
        time.sleep(3)

        with open(r'C:\Users\madi2\OneDrive\Рабочий стол\botSchool\source-page.html', 'w', errors='ignore') as file:
            file.write(driver.page_source)

    except Exception as _ex:
        print(_ex)
    finally:
        driver.close()
        driver.quit()

def get_items_class_from_html(file_path):
    with open(file_path) as file:
        src = file.read()
    soup = BeautifulSoup(src, 'html.parser')

    classrooms = []
    items_divs = soup.find_all('div', class_='ecourse-standards-subject-title')
    for item in items_divs:
        item_class = item.find('div', class_='className')
        classrooms.append(item_class.text)

    with open(r'C:\Users\madi2\OneDrive\Рабочий стол\botSchool\class.txt', 'w', errors='ignore') as file:
        for classroom in classrooms:
            file.write(f'{classroom}\n')
    return '[INFO] classrooms have been added successfully!'

def read_classes_from_txt(file_path):
    classes = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            class_name = line.strip()
            if class_name:
                classes.append(class_name)
    return classes

def get_grades_selenium(username, password, class_name):
    chrome_options = Options()
    chrome_options.add_argument("--user-data-dir=C:/Users/madi2/OneDrive/Рабочий стол/chrome")
    driver = webdriver.Chrome(options=chrome_options)
    driver.maximize_window()

    try:
        driver.get('https://login1.edupage.org/login/edubarLogin.php')

        driver.find_element(By.NAME, 'username').send_keys(username)
        driver.find_element(By.NAME, 'password').send_keys(password + Keys.RETURN)

        driver.get('https://skillset-schools.edupage.org/znamky/')

        class_select_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'ecourse-standards-subject-item'))
        )


        option_xpath = f"//div[contains(text(), '{class_name}')]"
        option = driver.find_element(By.XPATH, option_xpath)
        option.click()

        time.sleep(10)

        grades = []
        grade_elements = driver.find_elements(By.CLASS_NAME, 'znZnamka')
        for grade_element in grade_elements:
            grades.append(grade_element.text)

        return grades

    finally:
        driver.quit()

username = 'username'
password = 'password'

get_html_selenium(username, password)

print(get_items_class_from_html(file_path=r'C:\Users\madi2\OneDrive\Рабочий стол\botSchool\source-page.html'))

classes = read_classes_from_txt(file_path=r'C:\Users\madi2\OneDrive\Рабочий стол\botSchool\class.txt')

print("Доступные классы:")
for i, class_name in enumerate(classes):
    print(f"{i + 1}: {class_name}")

selected_class_number = input("Введите номер класса: ").strip()

try:
    selected_class_index = int(selected_class_number) - 1
    selected_class_name = classes[selected_class_index]

    if selected_class_name:
        grades = get_grades_selenium(username, password, selected_class_name)
        print(f"Оценки для {selected_class_name}:")
        for grade in grades:
            print(grade)

        os.remove(r'C:\Users\madi2\OneDrive\Рабочий стол\botSchool\class.txt')
        os.remove(r'C:\Users\madi2\OneDrive\Рабочий стол\botSchool\source-page.html')
        print("Файл class.txt был успешно удален.")
    else:
        print(f"Класс с номером {selected_class_number} не найден.")
        os.remove(r'C:\Users\madi2\OneDrive\Рабочий стол\botSchool\class.txt')
        os.remove(r'C:\Users\madi2\OneDrive\Рабочий стол\botSchool\source-page.html')

except (ValueError, IndexError):
    print(f"Класс с номером {selected_class_number} не найден.")
    os.remove(r'C:\Users\madi2\OneDrive\Рабочий стол\botSchool\class.txt')
    os.remove(r'C:\Users\madi2\OneDrive\Рабочий стол\botSchool\source-page.html')





