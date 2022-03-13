import requests
import pandas as pd
import os
import json


class Parser:
    def __init__(self, url, out_dir, start_price, stop_price):
        self.url = url
        self.out_dir = out_dir
        self.start_price = start_price
        self.stop_price = stop_price

    def get_cars(self):
        # Проверяем есть ли папка 'data'. Если нет, то создаем
        if not os.path.exists(self.out_dir):
            dir_path = os.path.join(self.out_dir)
            os.mkdir(dir_path)

        # Импортируем заголовки запроса из json
        with open('data/header.json', 'r') as file:
            header = json.load(file)

        # Подготовительный запрос для определения количества страниц
        request_parameter = {
            "category": "cars",
            "section": "all",
            "price_to": self.start_price,
            "price_from": self.stop_price,
            "page": 1,
            "geo_id": [225]
        }
        response = requests.post(url=self.url, json=request_parameter, headers=header)
        dump = response.json()

        # Вытаскиваем количество страниц результата поиска и количество найденных машин из ответа
        total_pages = dump['pagination']['total_page_count']
        cars = dump['pagination']['total_offers_count']

        print('\nВ ценовом диапазоне {}-{} рублей найдено {} объявлений на {} страницах' \
              .format(self.start_price, self.stop_price, cars, total_pages))

        page = 1
        all_cars = []

        while page < total_pages + 1:
            # Запрос по всем машинам во всей стране (category: cars, section: all, geo_id: 255)
            request_parameter = {
                "category": "cars",
                "section": "all",
                "price_to": self.start_price,
                "price_from": self.stop_price,
                "page": page,
                "geo_id": [225]
            }
            try:
                response = requests.post(url=self.url, json=request_parameter, headers=header)
                if response.status_code == 200:
                    print('Парсинг страницы {} из {}'.format(page, total_pages))
                    dump = response.json()
                    for car in dump['offers']:
                        car_dict = {}
                        car_dict.update(car['price_info'])
                        car_dict.update(car['documents'])
                        car_dict['ID'] = car['id']
                        car_dict['Condition'] = car.get('section', 'None')
                        car_dict['Color'] = car.get('color_hex', 'None')
                        car_dict['About'] = car.get('lk_summary', 'None')
                        car_dict['Description'] = car.get('description', 'None')
                        car_dict['Seller'] = car['seller_type']
                        car_dict['Mark'] = car['vehicle_info']['mark_info']['name']
                        car_dict['Model'] = car['vehicle_info']['model_info']['name']
                        car_dict['Engine'] = car['vehicle_info']['tech_param']['engine_type']
                        car_dict['Power_hp'] = car['vehicle_info']['tech_param']['power']
                        car_dict['Gear'] = car['vehicle_info']['tech_param']['gear_type']
                        car_dict['Transmission'] = car['vehicle_info']['tech_param']['transmission']
                        car_dict['Mileage'] = car['state']['mileage']
                        car_dict['Location'] = car['seller']['location']['region_info']['name']
                        car_dict['Days_on_sale'] = car['additional_info']['days_on_sale']
                        all_cars.append(car_dict)
                else:
                    print('Ошибка {} на странице: {} Повтор запроса...'.format(response.status_code, page))
                    response.close()
                    continue
            except KeyError:
                print('Ошибка получения данных на странице: ', page)

            # Закрываем соединение, переходим к следующей страницы
            response.close()
            page += 1

        # Формируем датафрейм
        data = pd.DataFrame(all_cars)
        data.drop_duplicates(subset=['ID'], inplace=True)

        # Сохраняем все в .csv файл
        file_name = 'data_auto_ru.csv'
        save_data_to_csv(data, file_name, self.out_dir)

        print('Парсинг данных успешно завершен!')


def save_data_to_csv(data, file_name, out_dir):
    file_path = os.path.join(out_dir, file_name)
    data.to_csv(file_path, index=False)
