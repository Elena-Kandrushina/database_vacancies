from src.api_hh import HeadHunterAPI
from src.config import config
from src.db_manager import DBManager
from src.utils import (
    create_database,
    create_tables,
    get_db_connection,
    insert_into_table_employer,
    insert_into_table_vacancy,
)


def interaction_with_user() -> None:
    print("Добро пожаловать в сервис подбора вакансий")
    print("Мы подобрали для Вас вакансии топовых компаний")

    company_names = [
        "Ozon",
        "Яндекс",
        "wildberries",
        "Сбер",
        "Роснефть",
        "Лукойл",
        "Альфа-Банк",
        "ОМК",
        "Газпром",
        "Ростех",
    ]
    print(f"Топ компаний: {company_names}")
    user_answer = input("Нажмите 1, чтобы создать базу данных: ")
    if user_answer == "1":
        create_database()
    else:
        print("К сожалению, сервис прекратил работу по причине неверного ввода")
        exit()

    user_answer_1 = input("Нажмите 1, чтобы создать таблицы в БД и пополнить их данными: ")
    if user_answer_1 == "1":
        company_obj = HeadHunterAPI()
        try:
            with get_db_connection() as conn:
                create_tables(conn)
        except Exception as e:
            print(f"Ошибка при подключении или создании таблиц: {e}")
        company_names = [
            "Ozon",
            "Яндекс",
            "wildberries",
            "Сбер",
            "Роснефть",
            "Лукойл",
            "Альфа-Банк",
            "ОМК",
            "Газпром",
            "Ростех",
        ]
        all_companies = []

        for name in company_names:
            companies = company_obj.get_companies(name)
            all_companies.extend(companies)

        print(f"Общее число компаний: {len(all_companies)}")

        # Получение вакансий по id
        vacancy_id_list = [
            "1527261",
            "11187865",
            "3427755",
            "1388900",
            "195398",
            "565840",
            "1490605",
            "5845941",
            "6015750",
            "11830502",
            "2159482",
            "4565267",
            "2141981",
            "11125775",
            "2662767",
            "19594",
            "1642211",
            "5919226",
            "3141245",
            "219911",
        ]
        all_vacancies = []

        for vacancy_id in vacancy_id_list:
            vacancies = company_obj.get_vacancies(vacancy_id, 100)
            all_vacancies.extend(vacancies)

        print(f"Общее число вакансий: {len(all_vacancies)}")

        # Вставка данных
        try:
            with get_db_connection() as conn:
                # вставка компаний
                for employer in all_companies:
                    insert_into_table_employer(conn, employer)

                # вставка вакансий
                for vacancy in all_vacancies:
                    insert_into_table_vacancy(conn, vacancy)

        except Exception as e:
            print(f"Ошибка при работе с базой: {e}")
    else:
        print("К сожалению, сервис прекратил работу по причине неверного ввода")
        exit()


def user_interaction_db_manager(db_manager: DBManager):
    user_answer = input("Нажмите 1, чтобы получить список компаний и количество вакансий: ")
    if user_answer == "1":
        result = db_manager.get_companies_and_vacancies_count()
        print("\nКомпания — Количество вакансий:")
        for item in result:
            print(f"{item['наименование']}: {item['количество вакансий']}")
    else:
        print("К сожалению, сервис прекратил работу по причине неверного ввода")
        exit()

    user_answer_1 = input("Нажмите 1, чтобы получить все вакансии: ")
    if user_answer_1 == "1":
        vacancies = db_manager.get_all_vacancies()
        print("\nВсе вакансии:")
        for v in vacancies:
            print(
                f"{v['title']} ({v['company_name']}): {v['salary_from']} - {v['salary_to']} {v['currency']}"
                f" \nПодробнее по ссылке: {v['url']}\n"
            )
    else:
        print("К сожалению, сервис прекратил работу по причине неверного ввода")
        exit()

    user_answer_2 = input("Нажмите 1, чтобы получить среднюю зарплату по вакансиям: ")
    if user_answer_2 == "1":
        avg_salary_data = db_manager.get_avg_salary()
        print("Средняя зарплата по вакансиям:")
        for item in avg_salary_data:
            print(f"Вакансия {item['title']}: {item['avg_salary']:.2f}")
    else:
        print("К сожалению, сервис прекратил работу по причине неверного ввода")
        exit()

    user_answer_3 = input("Нажмите 1, чтобы получить вакансии с зарплатой выше средней: ")
    if user_answer_3 == "1":
        vacancies_higher = db_manager.get_vacancies_with_higher_salary()
        print("\nВакансии с зарплатой выше средней:")
        for v in vacancies_higher:
            print(
                f"{v['title']} ({v['company_name']}): {v['salary_from']} - {v['salary_to']} {v['currency']}"
                f" \nПодробнее: {v['url']}\n"
            )
    else:
        print("К сожалению, сервис прекратил работу по причине неверного ввода")
        exit()

    user_answer_4 = input("Нажмите 1, чтобы выполнить поииск вакансий по ключевому слову: ")
    if user_answer_4 == "1":
        keyword = input("Введите ключевое слово: ").strip()
        results = db_manager.get_vacancies_with_keyword(keyword)
        if results:
            print(f"\nВакансии с ключевым словом '{keyword}':")
            for v in results:
                print(
                    f"{v['title']} ({v['company_name']}): {v['salary_from']} - {v['salary_to']} {v['currency']}"
                    f" \nПодробнее: {v['url']}\n"
                )
        else:
            print("По вашему запросу ничего не найдено.")
    else:
        print("К сожалению, сервис прекратил работу по причине неверного ввода")
        exit()


if __name__ == "__main__":
    interaction_with_user()

    params = config()
    db_manager = DBManager(params)
    try:
        user_interaction_db_manager(db_manager)
    finally:
        db_manager.close()
