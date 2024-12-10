import cloudscraper
import time
import random
import json
from bs4 import BeautifulSoup

# Настройки
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'

# Создаем экземпляр cloudscraper для обхода защиты
scraper = cloudscraper.create_scraper()  # Используется для обхода Cloudflare
scraper.headers.update({'User-Agent': user_agent})  # Устанавливаем заголовок User-Agent

# Список для сохранения извлеченных данных
clinics_link_list = []

def get_source_html(url):
    try:
        count = 1  # Начинаем с первой страницы
        print(f"Получена начальная страница: {url}")

        # Начальный запрос
        response = scraper.get(url)
        if response.status_code != 200:
            print(f"Ошибка: Код состояния {response.status_code} для страницы {url}")
            return

        # Парсинг первой страницы
        process_page(response.content, count)

        # Переход на следующие страницы
        for _ in range(9):  # Обход 9 страниц
            count += 1  # Увеличиваем номер страницы
            next_url = f'https://zoon.ru/spb/medical/type/detskaya_poliklinika/page-{count}/'
            print(f"Переход на страницу: {next_url}")

            # Делаем запрос на следующую страницу
            response = scraper.get(next_url)
            if response.status_code != 200:
                print(f"Ошибка: Код состояния {response.status_code} для страницы {next_url}")
                break

            # Обработка страницы
            process_page(response.content, count)

            # Задержка для имитации пользователя
            time.sleep(random.uniform(2, 5))
    except Exception as ex:
        print("Ошибка:", ex)

def process_page(html, page_number):
    """
    Обработка содержимого страницы.
    """
    global clinics_link_list  # Указываем, что работаем с глобальным списком
    soup = BeautifulSoup(html, 'lxml')
    print(f"Обрабатывается страница номер: {page_number}")

    titles = soup.find_all('div', class_='minicard-item__title')
    for title in titles:
        href_link = title.find('a').get('href')
        if href_link and 'javascript:void()' not in href_link:
            clinics_link_list.append(f'{href_link}')  # Сохраняем данные в список

def open_list():
    with open('clinics_link_list.txt') as file:
        lines = [line.rstrip() for line in file.readlines()]

    data_dict = []
    count = 0

    for line in lines:
        r = scraper.get(line)
        result = r.content

        soup = BeautifulSoup(result, 'lxml')
        title = soup.find(class_='service-page-header--text')
        title_text = title.find('span').text if title else "Не указано"

        rating = soup.find('div', class_='z-text--default')
        rating_text = rating.text if rating else "Не указано"

        social_network = soup.find_all('a', class_='service-description-social-btn')

        social_network_url = []
        for item in social_network:
            social_network_url.append(item.get('href'))

        data = {
            'Clinic_name': title_text,
            'Rating': rating_text,
            'Social_network': social_network_url,
        }
        count += 1
        print(f'#{count}: {line} выполнено !')
        data_dict.append(data)

    with open('data_list.json', 'w', encoding='utf-8') as json_file:
        json.dump(data_dict, json_file, indent=4,ensure_ascii=False)
    print("Данные успешно сохранены в файл.")

def main():
    # url = 'https://zoon.ru/spb/medical/?search_query_form=1&m%5B5200e522a0f302f066000055%5D=1&center%5B%5D=58.88582657466453&center%5B%5D=30.438743843686385&zoom=7'
    # get_source_html(url)
    #
    # with open('clinics_link_list.txt', 'w', encoding='utf-8') as file:
    #     for link in clinics_link_list:
    #         file.write(f'{link} \n')
    # print("Данные успешно сохранены в файл.")

    open_list()

if __name__ == '__main__':
    main()