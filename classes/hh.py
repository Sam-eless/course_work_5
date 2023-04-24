import requests
import time


class HH:
    URL = "https://api.hh.ru/vacancies"

    def __init__(self, employer_id: int):
        self.employer_id = employer_id
        self.params = {'employer_id': f'{self.employer_id}', 'page': 0, 'per_page': 100}

    def get_request(self):
        """Запрос вакансий через API hh.ru"""
        response = requests.get(HH.URL, self.params)
        if response.status_code == 200:
            return response.json()

    @staticmethod
    def get_info(data: dict):
        """Преобразование в кортеж нужного формата"""
        vacancy_id = int(data.get('id'))
        name = data['name']
        employer_id = int(data.get('employer').get('id'))
        city = data.get('area').get('name')
        url = data.get('alternate_url')

        if 'salary' in data.keys():
            if data.get('salary') is not None:
                if 'from' in data.get('salary'):
                    salary = data.get('salary').get('from')
                else:
                    salary = None
            else:
                salary = None
        else:
            salary = None

        vacancy = (vacancy_id, name, employer_id, city, salary, url)
        return vacancy

    def get_vacancies(self) -> list:
        """Получение списка вакансий"""
        vacancies = []
        page = 0
        while True:
            self.params['page'] = page
            data = self.get_request()

            for vacancy in data.get('items'):
                if vacancy.get('salary') is not None and vacancy.get('salary').get('currency') == "RUR":
                    vacancies.append(self.get_info(vacancy))
                elif vacancy.get('salary') is None:
                    vacancies.append(self.get_info(vacancy))

            page += 1
            time.sleep(0.2)

            # на последней странице, заканчиваем сбор данных
            if data.get('pages') == page:
                break

        return vacancies
