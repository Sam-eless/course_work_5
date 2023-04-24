import psycopg2
from psycopg2 import errors


class DBManager:
    """Класс для работы с базой данных.
     Для работы нужно ввести название БД и передать распарсенный конфиг."""
    def __init__(self, dbname: str, params: dict):
        self.dbname = dbname
        self.params = params

    def create_database(self):
        """Создает БД и таблицы"""
        # Подключение к postgres
        conn = psycopg2.connect(dbname='postgres', **self.params)
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute(f"DROP DATABASE IF EXISTS {self.dbname}")
            cur.execute(f"CREATE DATABASE {self.dbname}")

        # Создаем таблицы в созданной БД
        with psycopg2.connect(dbname=self.dbname, **self.params) as conn:
            with conn.cursor() as cur:
                cur.execute('CREATE TABLE IF NOT EXISTS employers'
                            '('
                            'employer_id int PRIMARY KEY,'
                            'employer_name varchar(255) UNIQUE NOT NULL)')

                cur.execute('CREATE TABLE IF NOT EXISTS vacancies('
                            'vacancy_id int PRIMARY KEY, '
                            'vacancy_name varchar(255) NOT NULL, '
                            'employer_id int REFERENCES employers(employer_id) NOT NULL, '
                            'city varchar(255), '
                            'url text, '
                            'salary real)')

    def insert(self, table_title: str, data: list) -> None:
        """Добавление данных в базу данных в зависимости от таблицы"""
        with psycopg2.connect(dbname=self.dbname, **self.params) as conn:
            with conn.cursor() as cur:
                if table_title == 'employers':
                    cur.executemany('INSERT INTO employers(employer_id, employer_name) '
                                    'VALUES(%s, %s)', data)
                elif table_title == 'vacancies':
                    cur.executemany('INSERT INTO vacancies (vacancy_id, vacancy_name, employer_id, '
                                    'city, salary, url) '
                                    'VALUES(%s, %s, %s, %s, %s, %s)'
                                    'ON CONFLICT (vacancy_id) DO NOTHING', data)

    def execute_query(self, query) -> list:
        """Возвращает результат запроса"""
        with psycopg2.connect(dbname=self.dbname, **self.params) as conn:
            with conn.cursor() as cur:
                cur.execute(query)
                result = cur.fetchall()
        return result

    def get_companies_and_vacancies_count(self) -> list:
        """Получает список всех компаний и количество вакансий у каждой компании"""
        companies_and_vac_count = self.execute_query("SELECT employer_name, COUNT(*) as quantity_vacancies "
                                     "FROM vacancies "
                                     "LEFT JOIN employers USING(employer_id)"
                                     "GROUP BY employer_name "
                                     "ORDER BY quantity_vacancies DESC, employer_name")
        return companies_and_vac_count

    def get_all_vacancies(self) -> list:
        """ Получает список всех вакансий с указанием названия компании,
        названия вакансии и зарплаты и ссылки на вакансию"""
        all_vacancies = self.execute_query("SELECT employers.employer_name, vacancy_name, salary, url "
                                     "FROM vacancies "
                                     "JOIN employers USING(employer_id)"
                                     "WHERE salary IS NOT NULL "
                                     "ORDER BY salary DESC, vacancy_name")
        return all_vacancies

    def get_avg_salary(self) -> list:
        """ Получает среднюю зарплату по вакансиям"""
        # avg_salary = self.execute_query("SELECT ROUND(AVG(salary)) as average_salary FROM vacancies")
        with psycopg2.connect(dbname=self.dbname, **self.params) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT ROUND(AVG(salary)) as average_salary FROM vacancies")
                avg_salary = cur.fetchall()
        return avg_salary

    def get_vacancies_with_higher_salary(self) -> list:
        """ Получает список всех вакансий, у которых зарплата выше средней по всем вакансиям"""
        vac_higher_salary = self.execute_query("SELECT vacancy_name, salary "
                                     "FROM vacancies "
                                     "WHERE salary > (SELECT AVG(salary) FROM vacancies) "
                                     "ORDER BY salary DESC, vacancy_name")
        return vac_higher_salary

    def get_vacancies_with_keyword(self, keyword: str) -> list:
        """Получает список всех вакансий, в названии которых содержатся переданные в метод слова, например “python”"""
        vac_with_keyword = self.execute_query("SELECT vacancy_name, url, salary "
                                     "FROM vacancies "
                                     f"WHERE vacancy_name ~~* '%{keyword}%'"
                                              "ORDER BY vacancy_name")
        return vac_with_keyword
