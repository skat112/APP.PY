from config import host, user, password, db_name
import requests
from bs4 import BeautifulSoup

def clean_text(text):
    return text.strip().lower() if text else ''

# Базовый URL страницы с вакансиями
base_url = 'https://career.habr.com/vacancies?type=all&page='

# Начинаем с первой страницы
page = 1

# Запрашиваем у пользователя строки для поиска в различных критериях
position = input("Введите название вакансии: ").lower()
city = input("Введите город: ").lower()
skills = input("Введите навыки через запятую для поиска: ").lower()
company = input("Введите название компании: ").lower()

while True:
    # Формируем URL текущей страницы
    url = base_url + str(page)

    # Отправляем GET-запрос на сервер
    response = requests.get(url)

    # Проверяем, успешно ли был выполнен запрос
    if response.status_code == 200:
        # Создаем объект BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Находим все элементы, содержащие информацию о вакансиях
        vacancies = soup.find_all('div', class_='vacancy-card__inner')

        # Если на странице нет вакансий, прерываем цикл
        if not vacancies:
            break

        # Перебираем все найденные вакансии и извлекаем информацию
        for vacancy in vacancies:
            vacancy_data = {
                'title': vacancy.find('a', class_='vacancy-card__title-link').text.strip().lower(),
                'name_company': vacancy.find('div', class_='vacancy-card__company-title').text.strip().lower(),
                'location': vacancy.find('div', class_='vacancy-card__meta').text.strip().lower(),
                'requirements': vacancy.find('div', class_='vacancy-card__skills').text.strip().lower() if vacancy.find('div', class_='vacancy-card__skills') else '',
                'salary': vacancy.find('div', class_='vacancy-card__salary').text.strip().lower()
            }

            if (
                (not position or position in vacancy_data['title']) and
                (not city or city in vacancy_data['location']) and
                (not skills or all(skill.strip() in vacancy_data['requirements'] for skill in skills.split(','))) and
                (not company or company in vacancy_data['name_company'])
            ):
                link = 'https://career.habr.com' + vacancy.find('a', class_='vacancy-card__title-link')['href']

                print(f'Название вакансии: {vacancy_data["title"]}')
                print(f'Компания: {vacancy_data["name_company"]}')
                print(f'Город: {vacancy_data["location"]}')
                print(f'Навыки: {vacancy_data["requirements"]}')
                print(f'Зарплата: {vacancy_data["salary"]}')
                print(f'Ссылка на вакансию: {link}')
                print('---')

        # Переходим к следующей странице
        page += 1
    else:
        print('Не удалось получить данные с сайта')
        break

import pymysql

# Establish connection to the database
connection = pymysql.connect(
    host='localhost',
    user='root',
    password='yphau110',
    database='pr',
)

try:
    with connection.cursor() as cursor:
        # Create job_vacancies table
        create_table_query = """
        CREATE TABLE IF NOT EXISTS job_vacancies (
            id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(255),
            company VARCHAR(255),
            location VARCHAR(255),
            requirements TEXT,
            salary VARCHAR(100),
            link VARCHAR(255)
        )
        """
        cursor.execute(create_table_query)

        print("Table 'job_vacancies' created successfully.")
        truncate_query = "TRUNCATE TABLE job_vacancies"
        cursor.execute(truncate_query)
        print("Таблица 'job_vacancies' успешно очищена.")


        for vacancy in vacancies:
            vacancy_data = {
                'title': vacancy.find('a', class_='vacancy-card__title-link').text.strip().lower(),
                'company': vacancy.find('div', class_='vacancy-card__company-title').text.strip().lower()
            }

            # Проверяем, есть ли вакансия с таким названием и компанией в базе данных
            select_query = """
            SELECT * FROM job_vacancies
            WHERE title = %s AND company = %s
            """
            cursor.execute(select_query, (vacancy_data['title'], vacancy_data['company']))
            existing_vacancy = cursor.fetchone()

            if not existing_vacancy:
                # Если нет совпадений, добавляем данные в базу данных
                insert_query = """
                INSERT INTO job_vacancies (title, company, location, requirements, salary, link)
                VALUES (%s, %s, %s, %s, %s, %s)
                """

                # Предположим, что остальные данные для вставки в vacancy_data
                # также присутствуют и должны быть добавлены в execute в нужном порядке
                # Этот код представляет эту идею
                cursor.execute(insert_query, (vacancy_data['title'], vacancy_data['company'], '', '', '', ''))

        connection.commit()
        print(f"Данные со страницы {page} успешно сохранены в базу данных.")
        page += 1

except pymysql.MySQLError as e:
    print("Ошибка при работе с базой данных:", e)

finally:
    connection.close()
