from typing import Dict, List, Any
import requests


class HeadHunterAPI:
    """Класс для работы с API hh.ru"""

    def __init__(self) -> None:
        self.base_url = "https://api.hh.ru"
        self.params = {"text": "", "page": 0, "per_page": 100}
        self.vacancies: List[Dict[str, Any]] = []

    def get_companies(self, name: str, per_page: int = 20) -> List[Dict[str, Any]]:
        """Метод получения списка компаний по имени с учетом выполнения условия,
        что у организации существуют открытые вакансии, но не более 10 вакансий"""

        url = "https://api.hh.ru/employers"
        params: Dict[str, Any] = {"text": name, "per_page": per_page}
        response = requests.get(url, params=params)
        if response.status_code == 200:
            companies = response.json().get("items", [])
            return [company for company in companies if 10 > company.get("open_vacancies", 0) > 0]
        else:
            print(f"Ошибка получения компаний: статус {response.status_code}")
            return []

    def get_vacancies(self, employer_id: str, per_page: int = 100) -> List[Dict[str, Any]]:
        """Метод получения вакансий по id компаний"""
        # url = "https://api.hh.ru/vacancies"
        params: Dict[str, Any] = {"employer_id": employer_id, "per_page": per_page}
        response = requests.get(f"{self.base_url}/vacancies", params=params)
        if response.status_code == 200:
            vacancies: List[Dict[str, Any]] = response.json().get("items", [])
            return vacancies
        else:
            print(f"Ошибка получения вакансий: статус {response.status_code}")
            return []


# Я потом это затащу в utils
# company_obj = HeadHunterAPI()
# company_names = [
#     "Ozon",
#     "Яндекс",
#     "wildberries",
#     "Сбер",
#     "Роснефть",
#     "Лукойл",
#     "Альфа-Банк",
#     "ОМК",
#     "Газпром",
#     "Ростех",
# ]
# all_companies = []
#
# for name in company_names:
#     companies = company_obj.get_companies(name)
#     all_companies.extend(companies)
#
# print(f"Все компании: {all_companies}")
# print(len(all_companies))
#
# # Получаем вакансии по id
# vacancy_id_list = [
#     "1527261",
#     "11187865",
#     "3427755",
#     "1388900",
#     "195398",
#     "565840",
#     "1490605",
#     "5845941",
#     "6015750",
#     "11830502",
#     "2159482",
#     "4565267",
#     "2141981",
#     "11125775",
#     "2662767",
#     "19594",
#     "1642211",
#     "5919226",
#     "3141245",
#     "219911",
# ]
# all_vacancies = []
# for vacancy_id in vacancy_id_list:
#     vacancies = company_obj.get_vacancies(vacancy_id, 100)
#     all_vacancies.extend(vacancies)
#
# print(f"Вакансии: {all_vacancies}")
# print(len(all_vacancies))


# Если захочу отсеять поля с отсутствием ЗП
# return [vacancy for vacancy in vacancies
#         if vacancy.get('salary')
#         and vacancy['salary'].get('from') is not None
#         and vacancy['salary'].get('to') is not None]
