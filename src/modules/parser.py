import os
import json
import requests
import pandas as pd


class Parser:
    def __init__(self, start_price, end_price):
        self.url = ''
        self.project_path = os.getenv('project_path')
        self.start_price = start_price
        self.end_price = end_price

    def __save_to_csv(self, data, file_name):
        file_path = f'{self.project_path}/data/{file_name}'
        data.to_csv(file_path, index=False)

    def get_autoru_cars(self):
        self.url = 'https://auto.ru/-/ajax/desktop/listing/'

        print('loaded config...', end=' ')
        with open(f'{self.project_path}/src/configs/autoru_headers.json', 'r') as file:
            header = json.load(file)

        print('done.\ngetting page number...', end=' ')
        request_parameter = {
            "category": "cars",
            "section": "all",
            "price_to": self.start_price,
            "price_from": self.end_price,
            "page": 1,
            "geo_id": [225],
        }
        response = requests.post(url=self.url, json=request_parameter, headers=header).json()
        total_pages = response['pagination']['total_page_count']

        print('done.\nparsing running...')
        parsed_cars = []
        for page in range(1, total_pages + 1):
            print(f'\rparsing {page} of {total_pages} pages...', end=' ')
            request_parameter['page'] = page
            response = requests.post(url=self.url, json=request_parameter, headers=header)
            if response.status_code == 200:
                cars = response.json()['offers']
                try:
                    for car in cars:
                        car_dict = {}
                        car_dict.update(car['price_info'])
                        car_dict.update(car['documents'])
                        car_dict['ID'] = car['id']
                        car_dict['Condition'] = car.get('section', None)
                        car_dict['Color'] = car.get('color_hex', None)
                        car_dict['About'] = car.get('lk_summary', None)
                        car_dict['Description'] = car.get('description', None)
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
                        parsed_cars.append(car_dict)
                except KeyError as error:
                    print(f'\nerror: on page {page} {error}')
            else:
                print(f'\nerror: {response.status_code} status for page {page}')

        print('done.\ndone.\nremoving duplicates...', end=' ')
        parsed_cars_df = pd.DataFrame(parsed_cars)
        parsed_cars_df.drop_duplicates(['ID'], inplace=True)
        print('done.')

        if parsed_cars_df.empty:
            print('error: no car was parsed')
            return 1
        else:
            print('saving data...', end=' ')
            self.__save_to_csv(parsed_cars_df, 'autoru_learn.csv')
            print('done.')
            return 0
