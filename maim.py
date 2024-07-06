import requests
from bs4 import BeautifulSoup

# Базовый URL страницы с вакансиями
base_url = 'https://career.habr.com/vacancies?type=all&page='

# Начинаем с первой страницы
page = 1

# Запрашиваем у пользователя строки для поиска в различных критериях
position = input("Введите ключевое слово для поиска в названии вакансии: ").lower()
city = input("Введите ключевое слово для поиска в городе: ").lower()

experience_level = input("Введите ключевое слово для поиска в уровне опыта: ").lower()
skills = input("Введите навыки через запятую для поиска: ").lower()
company = input("Введите ключевое слово для поиска в названии компании: ").lower()

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

             }

            if (
                (not position or position in vacancy_data['title']) and
                (not city or city in vacancy_data['location']) and
                (not salary or salary in vacancy_data['salary_text']) and
                (not experience_level or experience_level in vacancy_data['requirements']) and
                (not skills or all(skill.strip() in vacancy_data['requirements'] for skill in skills.split(','))) and
                (not company or company in vacancy_data['name_company'])
            ):
                link = 'https://career.habr.com' + vacancy.find('a', class_='vacancy-card__title-link')['href']

                print(f'Название вакансии: {vacancy_data["title"]}')
                print(f'Компания: {vacancy_data["name_company"]}')
                print(f'Местоположение: {vacancy_data["location"]}')
                print(f'Навыки: {vacancy_data["requirements"]}')
                print(f'Зарплата: {vacancy_data["salary"]}')
                print(f'Ссылка: {link}')
                print('---')

        # Переходим к следующей странице
        page += 1
    else:
        print('Не удалось получить данные с сайта')
        break
