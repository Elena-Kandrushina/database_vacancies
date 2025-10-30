import psycopg2
from typing import List, Dict, Any
# from src.config import config
# import pprint


class DBManager:
    """Класс для работы с БД"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.conn = psycopg2.connect(
            host=self.config["host"],
            user=self.config["user"],
            password=self.config["password"],
            port=self.config["port"],
            database=self.config["database"],
        )

    def close(self) -> None:
        """Закрыть соединение."""
        if self.conn:
            self.conn.close()

    def get_companies_and_vacancies_count(self) -> List[Dict[str, Any]]:
        """Возвращает список компаний и количество вакансий у каждой."""
        query = """
            SELECT vacancies.employer_id, name, COUNT(vacancy_id) AS vacancies_count
            FROM employers
            LEFT JOIN vacancies ON employers.employer_id = vacancies.employer_id
            GROUP BY vacancies.employer_id, name
        """
        with self.conn.cursor() as cur:
            cur.execute(query)
            results = cur.fetchall()
        return [{"id компании": r[0], "наименование": r[1], "количество вакансий": r[2]} for r in results]

    def get_all_vacancies(self) -> List[Dict[str, Any]]:
        """Возвращает список всех вакансий с названием компании, названия вакансии и зарплатой."""
        query = """
            SELECT vacancies.vacancy_id, employers.name AS company_name, vacancies.title, vacancies.salary_from,
            vacancies.salary_to, vacancies.currency, vacancies.url
            FROM vacancies
            JOIN employers ON vacancies.employer_id = employers.employer_id
        """
        with self.conn.cursor() as cur:
            cur.execute(query)
            results = cur.fetchall()
        vacancies_list = []
        for r in results:
            vacancy_info = {
                "vacancy_id": r[0],
                "company_name": r[1],
                "title": r[2],
                "salary_from": r[3],
                "salary_to": r[4],
                "currency": r[5],
                "url": r[6],
            }
            vacancies_list.append(vacancy_info)
        return vacancies_list

    def get_avg_salary(self) -> list[dict[str, Any]]:
        """Возвращает среднюю зарплату по всем записям с вакансиями."""
        query = """
                SELECT title, (salary_from + salary_to) / 2.0 AS avg_salary
                FROM vacancies
                WHERE salary_from IS NOT NULL AND salary_to IS NOT NULL
            """
        with self.conn.cursor() as cur:
            cur.execute(query)
            results = cur.fetchall()

        return [{"title": row[0], "avg_salary": row[1]} for row in results]

    def get_avg_salary_all_vacancies(self) -> float:
        """Возвращает среднюю зарплату по всем вакансиям."""
        query = """
            SELECT AVG((salary_from + salary_to)/2.0)
            FROM vacancies
            WHERE salary_from IS NOT NULL AND salary_to IS NOT NULL
        """
        with self.conn.cursor() as cur:
            cur.execute(query)
            result = cur.fetchone()
        return result[0] if result and result[0] is not None else 0

    def get_vacancies_with_higher_salary(self) -> List[Dict[str, Any]]:
        """Возвращает список вакансий с зарплатой выше средней по всем вакансиям."""
        avg_salary = self.get_avg_salary_all_vacancies()
        query = """
            SELECT vacancies.vacancy_id, employers.name AS company_name, vacancies.title, vacancies.salary_from,
            vacancies.salary_to, vacancies.currency, vacancies.url
            FROM vacancies
            JOIN employers ON vacancies.employer_id = employers.employer_id
            WHERE (vacancies.salary_from + vacancies.salary_to)/2.0 > %s
        """
        with self.conn.cursor() as cur:
            cur.execute(query, (avg_salary,))
            results = cur.fetchall()
        vacancies_list = []
        for r in results:
            vacancies_list.append(
                {
                    "vacancy_id": r[0],
                    "company_name": r[1],
                    "title": r[2],
                    "salary_from": r[3],
                    "salary_to": r[4],
                    "currency": r[5],
                    "url": r[6],
                }
            )
        return vacancies_list

    def get_vacancies_with_keyword(self, keyword: str) -> List[Dict[str, Any]]:
        """Возвращает список вакансий, в названии которых есть слово/слова переданные в метод."""

        query = """
            SELECT vacancies.vacancy_id, employers.name AS company_name, vacancies.title, vacancies.salary_from,
            vacancies.salary_to, vacancies.currency, vacancies.url
            FROM vacancies
            JOIN employers ON vacancies.employer_id = employers.employer_id
            WHERE vacancies.title ILIKE %s
        """
        like_pattern = f"%{keyword}%"
        with self.conn.cursor() as cur:
            cur.execute(query, (like_pattern,))
            results = cur.fetchall()
        vacancies_list = []
        for r in results:
            vacancies_list.append(
                {
                    "vacancy_id": r[0],
                    "company_name": r[1],
                    "title": r[2],
                    "salary_from": r[3],
                    "salary_to": r[4],
                    "currency": r[5],
                    "url": r[6],
                }
            )
        return vacancies_list


# для вывода в main:
# params = config()
# db_manager = DBManager(params)
# companies_and_counts = db_manager.get_companies_and_vacancies_count()
#
#
# vacancies = db_manager.get_all_vacancies()
#
# pp = pprint.PrettyPrinter(indent=2)
# pp.pprint(vacancies)
# avg_salary = db_manager.get_avg_salary()
#
# vacancies_higher_avg = db_manager.get_vacancies_with_higher_salary()
# print(vacancies_higher_avg)
# pp.pprint(vacancies_higher_avg)
# keyword_input = input("Введите ключевое слово для поиска вакансий: ")
# vacancies = db_manager.get_vacancies_with_keyword(keyword_input)
#
# print(vacancies)
# pprint.pprint(vacancies)
# db_manager.close()
