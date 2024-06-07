import requests
from bs4 import BeautifulSoup
import json
import time

# URL Python разраб Москва и Санкт-Петербург
SEARCH_URL = 'https://spb.hh.ru/search/vacancy?text=python&area=1&area=2'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/91.0.4472.124 Safari/537.36'
}


def fetch_vacancies(url):
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.text
    return None


def parse_vacancy_details(vacancy_url):
    vacancy_html = fetch_vacancies(vacancy_url)
    if vacancy_html is None:
        return False

    soup = BeautifulSoup(vacancy_html, 'html.parser')
    description = soup.find('div', {'class': 'vacancy-description'})
    if description:
        description_text = description.get_text()
        if 'Django' in description_text and 'Flask' in description_text:
            return True
    return False


def parse_vacancies(html):
    soup = BeautifulSoup(html, 'html.parser')
    vacancies = []
    for item in soup.find_all('div', {'class': 'serp-item serp-item_simple serp-item_link serp-item-redesign'}):
        title = item.find('h2', {'data-qa': 'bloko-header-2'}).get_text()
        link = item.find('a', {'class': 'bloko-link'})['href']
        company = item.find('a', {'data-qa': 'vacancy-serp__vacancy-employer'}).get_text().strip()
        salary = item.find('span', {'class': 'bloko-text'})
        salary = salary.get_text().strip() if salary else 'Не указана'
        city = item.find('span', {'data-qa': 'vacancy-serp__vacancy-address'}).get_text().split(',')[0].strip()

        if parse_vacancy_details(link):
            vacancies.append({
                'title': title,
                'link': link,
                'company': company,
                'salary': salary,
                'city': city
            })
        time.sleep(1)  # задержка между запросами для стабильности парсинга

    return vacancies


def main():
    html = fetch_vacancies(SEARCH_URL)
    if html:
        vacancies = parse_vacancies(html)
        with open('vacancies.json', 'w', encoding='utf-8') as f:
            json.dump(vacancies, f, ensure_ascii=False, indent=4)
        print(f'Найдено и сохранено {len(vacancies)} вакансий')
    else:
        print('Не удалось получить данные с сайта.')


if __name__ == '__main__':
    main()
