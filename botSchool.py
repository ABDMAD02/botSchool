import os
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

def init_webdriver():
    options = webdriver.ChromeOptions()
    options.add_argument("--user-data-dir=C:/Users/yerkanat_a/Desktop/chrome")
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    return driver

def clear_browser_cache(driver):
    driver.execute_script("window.localStorage.clear();")
    driver.execute_script("window.sessionStorage.clear();")
    driver.delete_all_cookies()

def login_to_edupage(driver, username, password):
    driver.get('https://login1.edupage.org/')
    clear_browser_cache(driver)
    driver.find_element(By.NAME, 'username').send_keys(username)
    driver.find_element(By.NAME, 'password').send_keys(password + Keys.RETURN)
    time.sleep(3)

def save_page_source(driver, url, file_path):
    driver.get(url)
    time.sleep(3)
    with open(file_path, 'w', errors='ignore') as file:
        file.write(driver.page_source)
        
# OPTION №1 \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

def get_html_selenium(username, password):
    driver = init_webdriver()
    try:
        login_to_edupage(driver, username, password)
        save_page_source(driver, 'https://skillset-schools.edupage.org/znamky/', r'C:\Users\yerkanat_a\Desktop\botSchool-main\source-page.html')
    except Exception as _ex:
        print(_ex)
    finally:
        driver.quit()

def get_items_class_from_html(file_path):
    with open(file_path) as file:
        src = file.read()
    soup = BeautifulSoup(src, 'html.parser')
    classrooms = [item.find('div', class_='className').text for item in soup.find_all('div', class_='ecourse-standards-subject-title')]
    with open(r'C:\Users\yerkanat_a\Desktop\botSchool-main\class.txt', 'w', errors='ignore') as file:
        for classroom in classrooms:
            file.write(f'{classroom}\n')
    return '[INFO] classrooms have been added successfully!'

def read_classes_from_txt(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        classes = [line.strip() for line in file if line.strip()]
    return classes

def get_grades_selenium(username, password, class_name):
    driver = init_webdriver()
    clear_browser_cache(driver)
    try:
        login_to_edupage(driver, username, password)
        fetch_students_grades(driver, class_name)
        df = extract_grades(driver)
        return df
    finally:
        driver.quit()
        
def fetch_students_grades(driver, class_name):
    driver.get('https://skillset-schools.edupage.org/znamky/')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'ecourse-standards-subject-item')))
    option_xpath = f"//div[contains(text(), '{class_name}')]"
    option = driver.find_element(By.XPATH, option_xpath)
    option.click()
    time.sleep(2)  
    

def extract_grades(driver):
    student_data = []
    rows = driver.find_elements(By.XPATH, "//tr[contains(@class, 'row1') or contains(@class, 'row2')]")
    for row in rows:
        student_name = row.find_element(By.CLASS_NAME, 'edubarSmartLink').text
        grades = [grade.text for grade in row.find_elements(By.CLASS_NAME, 'znZnamka')]
        student_data.append([student_name, grades])
    return pd.DataFrame(student_data, columns=['Student Name', 'Grades'])
    
# OPTION №2 \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

def fetch_student_data(username, password):
    
    driver = init_webdriver()
    clear_browser_cache(driver)
    login_to_edupage(driver, username, password)

    driver.get('https://skillset-schools.edupage.org/dashboard/eb.php?mode=attendance')
    clicable_div = driver.find_element(By.XPATH, '//div[@title="Классы"]')
    clicable_div.click()
    content_div = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, 'dropDown')))
    ul_element = content_div.find_element(By.TAG_NAME, 'ul')
    li_elements = ul_element.find_elements(By.TAG_NAME, 'li')
    
    classes = []
    for li in li_elements:
        classes.append(li.text)
    
    return classes 

def fetch_attendance_data(username, password):
    driver = init_webdriver()
    clear_browser_cache(driver)
    try:
        login_to_edupage(driver, username, password)
        driver.get('https://skillset-schools.edupage.org/dashboard/eb.php?mode=attendance')
        click_div = driver.find_element(By.CLASS_NAME, 'asc-ribbon-button')
        click_div.click()
    
        content_div = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'tmp-selected')))

        ul_element = content_div.find_element(By.TAG_NAME, 'ul')
        li_element = ul_element.find_elements(By.TAG_NAME, 'li')
    
        classrooms = []
        for li in li_element:
            classrooms.append(li)
        return classrooms
        
    finally: 
        driver.quit()
        
    
def extract_attendance(driver, class_name, student_name):
    driver.get('https://skillset-schools.edupage.org/dashboard/eb.php?mode=attendance')
    click_div = driver.find_element(By.XPATH, '//div[@title="Классы"]')
    click_div.click()
        
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'dropDown')))
    option_xpath = f"//li/a[contains(text(), '{class_name.strip()}')]"
    option = driver.find_element(By.XPATH, option_xpath)
    option.click()
    time.sleep(2)
    
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'dash_lessonDlg')))
    option_xpath = f"//div[contains(text(), '{student_name}')]"
    option = driver.find_element(By.XPATH, option_xpath)
    option.click()
    content = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, 'dash_dochadzka')))
    attendance_data = []
    rows = content.find_elements(By.XPATH, "//tr[not(@class)]")
    for row in rows:
        attendance_data.append(row.text)
    return pd.DataFrame(attendance_data, columns=['Date'])


def get_attendance_selenium(username, password, class_name, student_name):
    driver = init_webdriver()
    clear_browser_cache(driver)
    try:
        login_to_edupage(driver, username, password)
        df = extract_attendance(driver, class_name, student_name)
        return df
    finally:
        driver.quit()

def extract_students(driver, class_name):
    try:
        driver.get('https://skillset-schools.edupage.org/dashboard/eb.php?mode=attendance')
        click_div = driver.find_element(By.XPATH, '//div[@title="Классы"]')
        click_div.click()
        
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'dropDown')))
        option_xpath = f"//li/a[contains(text(), '{class_name.strip()}')]"
        option = driver.find_element(By.XPATH, option_xpath)
        option.click()
        time.sleep(2)  
    
        student = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'dash_lessonDlg')))
        students = []
        rows = student.find_elements(By.XPATH, ".//div")
        for row in rows:
            students.append(row.text)
        return students
    finally:
        driver.quit()
        
def ensure_directory_exists(file_path):
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)
    
def main():
    username = 'irineaim@gmail.com'
    password = 'Idioma01@Idioma01@'

    print("Выберите опцию:")
    print("1: Оценки класса")
    print("2: Посещаемость ученика")
    option = input("Введите номер опции: ").strip()

    if option == '1':
        get_html_selenium(username, password)
        print(get_items_class_from_html(file_path=r'C:\Users\yerkanat_a\Desktop\botSchool-main\source-page.html'))
        classes = read_classes_from_txt(file_path=r'C:\Users\yerkanat_a\Desktop\botSchool-main\class.txt')
        print("Доступные классы:")
        for i, class_name in enumerate(classes):
            print(f"{i + 1}: {class_name}")
        selected_class_number = input("Введите номер класса: ").strip()

        try:
            selected_class_index = int(selected_class_number) - 1
            selected_class_name = classes[selected_class_index]
            if selected_class_name:
                df = get_grades_selenium(username, password, selected_class_name)
                print(f"Оценки для {selected_class_name}:")
                print(df)
                df.to_csv(r'C:\Users\yerkanat_a\Desktop\botSchool-main\grades.csv', index=False)
                os.remove(r'C:\Users\yerkanat_a\Desktop\botSchool-main\class.txt')
                print("Файл class.txt был успешно удален.")
            else:
                print(f"Класс с номером {selected_class_number} не найден.")
        except (ValueError, IndexError):
            print(f"Класс с номером {selected_class_number} не найден.")
            
    elif option == '2':
        classes = fetch_student_data(username, password)
        print("Доступные классы:")
        for i, class_name in enumerate(classes):
            print(f"{i + 1}: {class_name}")
        selected_class_number = input("Введите номер класса: ").strip()

        try:
            selected_class_index = int(selected_class_number) - 1
            selected_class_name = classes[selected_class_index]
            if selected_class_name:
                driver = init_webdriver()
                try:
                    login_to_edupage(driver, username, password)
                    students = extract_students(driver, selected_class_name)
                    print(f"Доступные ученики в классе {selected_class_name}:")
                    for i, student_name in enumerate(students):
                        print(f"{i + 1}: {student_name}")
                    selected_student_number = input("Введите номер ученика: ").strip()
                    selected_student_index = int(selected_student_number) - 1
                    selected_student_name = students[selected_student_index]
                    if selected_student_name:
                        df = get_attendance_selenium(username, password, selected_class_name, selected_student_name)
                        print(f"Посещаемость для {selected_student_name}:")
                        print(df)
                        sanitized_student_name = "".join(c for c in selected_student_name if c.isalnum() or c in "._- ").rstrip()
                        attendance_file_path = os.path.join(
                        r'C:\Users\madi2\OneDrive\Рабочий стол\botSchool',
                        f'{sanitized_student_name}_attendance.csv')
                        ensure_directory_exists(attendance_file_path)
                        df.to_csv(attendance_file_path, index=False)
                    else:
                        print(f"Ученик с номером {selected_student_number} не найден.")
                finally:
                    driver.quit()
            else:
                print(f"Класс с номером {selected_class_number} не найден.")
        except (ValueError, IndexError):
            print(f"Класс с номером {selected_class_number} не найден.")
    else:
        print("Неверный номер опции. Пожалуйста, выберите 1 или 2.")

if __name__ == '__main__':
    main()



