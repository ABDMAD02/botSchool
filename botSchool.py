from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

from bs4 import BeautifulSoup

def get_grades_selenium(username, password):
    driver = webdriver.Chrome()
    driver.maximize_window()

    try:
        driver.get('https://login1.edupage.org/')

    # Авторизация
        driver.find_element(By.NAME, 'username').send_keys(username)
        driver.find_element(By.NAME, 'password').send_keys(password + Keys.RETURN)
        time.sleep(3)  # Ожидание загрузки страницы
        driver.get('https://skillset-schools.edupage.org/znamky/')
        time.sleep(10)

        with open(r'C:\Users\madi2\OneDrive\Рабочий стол\botSchool\source-page.html', 'w', errors='ignore') as file:
            file.write(driver.page_source)
    except Exception as _ex:
        print(_ex)
    finally:
        driver.close()
        driver.quit()

# def get_classes(file_path):
#     with open(file_path) as file:
#         src = file.read()
#     soup = BeautifulSoup(src, 'lxml')


def main():
    get_grades_selenium()

if __name__ == '__name__':
    main()



username = 'username'
password = 'password'


grades = get_grades_selenium(username, password)
