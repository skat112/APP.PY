from flask import Flask, render_template, request
import pymysql
import requests
from bs4 import BeautifulSoup
from config import host, user, password, db_name

app = Flask(__name__)

def clean_text(text):
    return text.strip().lower() if text else ''

def load_vacancies_into_database():
    connection = pymysql.connect(
        host=host,
        user=user,
        password=password,
        database=db_name,
    )

    try:
        with connection.cursor() as cursor:
            create_table_query = """
            CREATE TABLE IF NOT EXISTS job_vacancies (
                id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(255),
                company VARCHAR(255),
                location VARCHAR(255),
                requirements TEXT,
                salary VARCHAR(100),
                link VARCHAR(255)
            )"""
            cursor.execute(create_table_query)

            clear_table_query = "TRUNCATE TABLE job_vacancies"
            cursor.execute(clear_table_query)

            base_url = 'https://career.habr.com/vacancies?type=all&page='
            page = 1

            while True:
                url = base_url + str(page)
                response = requests.get(url)

                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    vacancies = soup.find_all('div', class_='vacancy-card__inner')

                    if not vacancies:
                        break

                    for vacancy in vacancies:
                        vacancy_data = {
                            'title': clean_text(vacancy.find('a', class_='vacancy-card__title-link').text),
                            'company': clean_text(vacancy.find('div', class_='vacancy-card__company-title').text),
                            'location': clean_text(vacancy.find('div', class_='vacancy-card__meta').text),
                            'requirements': clean_text(vacancy.find('div', class_='vacancy-card__skills').text) if vacancy.find('div', class_='vacancy-card__skills') else '',
                            'salary': clean_text(vacancy.find('div', class_='vacancy-card__salary').text),
                            'link': 'https://career.habr.com' + vacancy.find('a', class_='vacancy-card__title-link')['href']
                        }

                        insert_query = """
                        INSERT INTO job_vacancies (title, company, location, requirements, salary, link)
                        VALUES (%s, %s, %s, %s, %s, %s)"""
                        cursor.execute(insert_query, (vacancy_data['title'], vacancy_data['company'], vacancy_data['location'], vacancy_data['requirements'], vacancy_data['salary'], vacancy_data['link']))

                    connection.commit()
                    page += 1
                else:
                    print('Failed to retrieve data from the website')
                    break

        print("Data successfully saved to the database.")

    except pymysql.MySQLError as e:
        print("Error working with the database:", e)

    finally:
        connection.close()

@app.route('/', methods=['GET', 'POST'])
def search_vacancies():
    if request.method == 'POST':
        load_vacancies_into_database()
        position = request.form.get('position').lower()
        city = request.form.get('city').lower()
        skills = request.form.get('skills').lower()
        company = request.form.get('company').lower()
        
        search_query_display = f'Search Query: Position - {position}, City - {city}, Skills - {skills}, Company - {company}'

        connection = pymysql.connect(
            host=host,
            user=user,
            password=password,
            database=db_name,
        )
        try:
            with connection.cursor() as cursor:
                search_query = """
                SELECT title, company, location, requirements, salary, link
                FROM job_vacancies
                WHERE (%s = '' OR title LIKE %s)
                AND (%s = '' OR location LIKE %s)
                AND (%s = '' OR requirements REGEXP %s)
                AND (%s = '' OR company LIKE %s)"""
                cursor.execute(search_query, (position, f'%{position}%', city, f'%{city}%', skills, skills.replace(',', '|'), company, f'%{company}%'))
                results = cursor.fetchall()

                count_query = "SELECT COUNT(*) FROM job_vacancies"
                cursor.execute(count_query)
                total_vacancies = cursor.fetchone()[0]

        except pymysql.MySQLError as e:
            print("Error working with the database:", e)

        finally:
            connection.close()

        return render_template('index.html', results=results, total_vacancies=total_vacancies, search_query_display=search_query_display)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
