from typing import Dict

# from src.api_hh import HeadHunterAPI
import psycopg2
from src.config import config
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


def get_db_connection() -> psycopg2.extensions.connection:
    """Функция создает подключение к базе данных, которая создана"""
    params = config()
    return psycopg2.connect(
        host=params["host"],
        user=params["user"],
        password=params["password"],
        port=params["port"],
        database=params["database"],
    )


def create_database() -> None:
    """Создание БД если она не существует"""
    params = config()

    # Подключение к базе "postgres", что бы в ней создать необходимую БД
    try:

        conn = psycopg2.connect(
            host=params["host"],
            user=params["user"],
            password=params["password"],
            port=params["port"],
            database="postgres",
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

        cursor = conn.cursor()

        cursor.execute(
            f"""
                SELECT pg_terminate_backend(pid)
                FROM pg_stat_activity
                WHERE datname = '{params['database']}'
                  AND pid <> pg_backend_pid();
                """
        )

        cursor.execute(f"DROP DATABASE IF EXISTS {params['database']}")
        cursor.execute(f"CREATE DATABASE {params['database']}")
        print(f"База данных {params['database']} успешно создана.")
        cursor.close()
        conn.close()
    except psycopg2.errors.DuplicateDatabase:
        print(f"База данных {params['database']} уже существует.")
    except Exception as e:
        print(f"Ошибка при создании базы данных: {e}")


# create_database()


def create_tables(conn) -> None:
    """Функция создания таблиц employers и vacancies в БД my_db_vacancies"""
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS employers (
                employer_id VARCHAR(20) PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                url VARCHAR(255))
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS vacancies(
                vacancy_id VARCHAR(20) PRIMARY KEY,
                employer_id VARCHAR(20) REFERENCES employers(employer_id),
                title VARCHAR(255) NOT NULL,
                description TEXT,
                salary_from INTEGER,
                salary_to INTEGER,
                currency VARCHAR(20),
                url VARCHAR(255))
                """
            )

            conn.commit()
            print("Таблицы созданы или уже существуют")
    except psycopg2.Error as e:
        conn.rollback()
        print(f"Ошибка при создании таблиц: {e}")
        raise


# try:
#     with get_db_connection() as conn:
#         create_tables(conn)
# except Exception as e:
#     print(f"Ошибка при подключении или создании таблиц: {e}")


def insert_into_table_employer(conn, employer: Dict) -> None:
    """Заполняет таблицу employers данными о компании."""
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO employers (employer_id, name, url)
                VALUES (%s, %s, %s)
                ON CONFLICT (employer_id) DO NOTHING
                """,
                (employer["id"], employer["name"], employer.get("alternate_url")),
            )
        conn.commit()
        print(f"Компания {employer['name']} успешно добавлена.")
    except Exception as e:
        print(f"Ошибка при вставке компании {employer['name']}: {e}")
        conn.rollback()


def insert_into_table_vacancy(conn, vacancy: Dict) -> None:
    """Заполняет таблицу vacancies данными о вакансии."""
    try:
        salary = vacancy.get("salary")
        salary_from = salary.get("from") if salary else None
        salary_to = salary.get("to") if salary else None
        currency = salary.get("currency") if salary else None
        snippet = vacancy.get("snippet", {})
        description = snippet.get("requirement", "")

        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO vacancies (
                    vacancy_id, employer_id, title, description, salary_from, salary_to, currency, url
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (vacancy_id) DO UPDATE SET
                description = EXCLUDED.description,
                salary_from = EXCLUDED.salary_from,
                salary_to = EXCLUDED.salary_to,
                currency = EXCLUDED.currency,
                title = EXCLUDED.title,
                url = EXCLUDED.url
                """,
                (
                    vacancy["id"],
                    vacancy["employer"]["id"],
                    vacancy["name"],
                    description,
                    salary_from,
                    salary_to,
                    currency,
                    vacancy["url"],
                ),
            )
        conn.commit()
        print(f"Вакансия {vacancy['name']} успешно добавлена.")
    except Exception as e:
        print(f"Ошибка при вставке вакансии {vacancy['name']}: {e}")
        conn.rollback()


# Для вывода в main:
# 1. Получение компаний
# company_obj = HeadHunterAPI()
# company_names = [
#     "Ozon", "Яндекс", "wildberries", "Сбер", "Роснефть",
#     "Лукойл", "Альфа-Банк", "ОМК", "Газпром", "Ростех"
# ]
# all_companies = []
#
# for name in company_names:
#     companies = company_obj.get_companies(name)
#     all_companies.extend(companies)
#
# print(f"Общее число компаний: {len(all_companies)}")
#
# # 2. Получение вакансий по id
# vacancy_id_list = [
#     "1527261", "11187865", "3427755", "1388900", "195398",
#     "565840", "1490605", "5845941", "6015750", "11830502",
#     "2159482", "4565267", "2141981", "11125775", "2662767",
#     "19594", "1642211", "5919226", "3141245", "219911"
# ]
# all_vacancies = []
#
# for vacancy_id in vacancy_id_list:
#     vacancies = company_obj.get_vacancies(vacancy_id, 100)
#     all_vacancies.extend(vacancies)
#
# print(f"Общее число вакансий: {len(all_vacancies)}")
#
# # Вставка данных
# try:
#     with get_db_connection() as conn:
#         # вставка компаний
#         for employer in all_companies:
#             insert_into_table_employer(conn, employer)
#
#         # вставка вакансий
#         for vacancy in all_vacancies:
#             insert_into_table_vacancy(conn, vacancy)
#
# except Exception as e:
#     print(f"Ошибка при работе с базой: {e}")
