from classes.hh import HH
from classes.db_manager import DBManager
from utils.utils import read_json, get_employers
from utils.config import config

EMPLOYERS = 'data/employers.json'


def main():
    params = config()
    db = DBManager('head_hunter', params)

    print('Создается база данных...', end='')
    db.create_database()
    print('[Done]')

    employers = read_json(EMPLOYERS)

    print('Добавляем в базу данных информацию о работодателях...', end='')
    db.insert('employers', get_employers(employers))
    print('[Done]')

    print('Добавляем в базу данных информацию о вакансиях...', end='')
    for i in range(len(employers)):
        hh = HH(employers[i]['id']).get_vacancies()
        db.insert('vacancies', hh)
    print('[Done]')

    while True:
        print(f'Доступные действия:\n\
        1. Получить список всех компаний и количество вакансий у каждой компании\n\
        2. Получить список всех вакансий\n\
        3. Получить среднюю зарплату по вакансиям\n\
        4. Получить список всех вакансий, у которых зарплата выше средней по всем вакансиям\n\
        5. Получить список всех вакансий, в названии которых содержится переданное слово\n\
        Стоп - закончить работу\n')

        user_input = input("Выберите действие:\n")
        if user_input == '1':
            print('Список всех компаний отсортированных по убыванию количества вакансий:')
            count = 1
            for item in db.get_companies_and_vacancies_count():
                print(f'{count}. {item[0]} - {item[1]} вакансий')
                count += 1

        elif user_input == '2':
            all_vacancies = db.get_all_vacancies()
            print(f'Список вакансий, где указана зарплата.\n'
                  'Вакансии отсортированы по зарплате от большей к меньшей')
            count = 1
            for item in all_vacancies:
                print(f'{count}. {item[1]} - {item[0]}({item[3]}), зарплата - {item[2]}')
                count += 1

        elif user_input == '3':
            print(f'Средняя зарплата по всем вакансиям - {db.get_avg_salary()[0][0]} рублей')

        elif user_input == '4':
            all_vacancies = db.get_vacancies_with_higher_salary()
            print(f'Всего вакансий, где зарплата выше средней - {len(all_vacancies)}')
            count = 1
            for item in all_vacancies:
                print(f'{count}. {item[0]} - {item[1]} рублей')
                count += 1

        elif user_input == '5':
            keyword = input('Введите слово для поиска в названии вакансии\n')
            all_vacancies = db.get_vacancies_with_keyword(keyword)
            print(f'Всего вакансий, содержащих "{keyword}" - {len(all_vacancies)}')
            count = 1
            for item in all_vacancies:
                if item[2] is None:
                    print(f'{count}. {item[0]}, {item[1]}')
                else:
                    print(f'{count}. {item[0]}, {item[1]}, зарплата - {int(item[2])}')

                count += 1

        elif user_input.lower() == 'стоп':
            print('Программа завершает работу')
            break

        else:
            print("Неверный ввод, попробуйте еще раз")
            continue

        print('Показать список доступных действий? y/n или enter')
        option = input().lower()
        if option in ('y', ''):
            continue
        else:
            print('Завершение работы.')
            break


if __name__ == '__main__':
    main()