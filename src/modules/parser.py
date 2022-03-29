import os
import json
import time
import requests
import pandas as pd


class Parser:
    def __init__(self, start_price, end_price):
        self.url = ''
        self.project_path = os.getenv('project_path')
        self.start_price = [start_price, end_price / 2 + 1]
        self.end_price = [end_price / 2, end_price]

    def __save_to_csv(self, data, file_name):
        file_path = f'{self.project_path}/data/{file_name}'
        data.to_csv(file_path, index=False)

    def get_autoru_cars(self):
        self.url = 'https://auto.ru/-/ajax/desktop/listing/'

        print('loaded config...', end=' ')
        with open(f'{self.project_path}/src/configs/autoru_headers.json', 'r') as file:
            header = json.load(file)
        print('done.')

        parsed_cars_df = pd.DataFrame()
        for i in range(len(self.start_price)):
            print(f'for price interval {self.start_price[i]}...{self.end_price[i]}:')
            print('getting page number...', end=' ')
            request_parameter = {
                "category": "cars",
                "section": "used",
                "price_to": self.start_price[i],
                "price_from": self.end_price[i],
                "page": 1,
                "geo_id": [225],
            }
            response = requests.post(url=self.url, json=request_parameter, headers=header).json()
            total_pages = response['pagination']['total_page_count']

            print('done.\nparsing running:')
            parsed_cars = []
            for page in range(1, total_pages + 1):
                print(f'\r\t{page} of {total_pages} pages...', end=' ')
                request_parameter['page'] = page
                response = requests.post(url=self.url, json=request_parameter, headers=header)
                if response.status_code == 200:
                    cars = response.json().get('offers')
                    if cars is None:
                        time.sleep(15)
                        continue
                    for car in cars:
                        car_dict = {}
                        try: car_dict['ID'] = car['id']
                        except: car_dict['ID'] = None
                        try: car_dict['Color'] = car['color_hex']
                        except: car_dict['Color'] = None
                        try: car_dict['Owners'] = car['documents']['owners_number']
                        except: car_dict['Owners'] = None
                        try: car_dict['Pts'] = car['documents']['pts']
                        except: car_dict['Pts'] = None
                        try: car_dict['Year'] = car['documents']['year']
                        except: car_dict['Year'] = None
                        try: car_dict['YearTax'] = car['owner_expenses']['transport_tax']['tax_by_year']
                        except: car_dict['YearTax'] = None
                        try: car_dict['Price'] = car['price_info']['price']
                        except: car_dict['Price'] = None
                        try: car_dict['City'] = car['seller']['location']['region_info']['name']
                        except: car_dict['City'] = None
                        try: car_dict['Mileage'] = car['state']['mileage']
                        except: car_dict['Mileage'] = None
                        try: car_dict['Mark'] = car['vehicle_info']['mark_info']['name']
                        except: car_dict['Mark'] = None
                        try: car_dict['IsLeftHand'] = car['vehicle_info']['steering_wheel'] == 'LEFT'
                        except: car_dict['IsLeftHand'] = None
                        try: car_dict['HP'] = car['vehicle_info']['tech_param']['power']
                        except: car_dict['HP'] = None
                        try: car_dict['Capacity'] = car['vehicle_info']['tech_param']['displacement']
                        except: car_dict['Capacity'] = None
                        try: car_dict['Transmission'] = car['vehicle_info']['tech_param']['transmission']
                        except: car_dict['Transmission'] = None
                        try: car_dict['FuelType'] = car['vehicle_info']['tech_param']['engine_type']
                        except: car_dict['FuelType'] = None
                        try: car_dict['GearType'] = car['vehicle_info']['tech_param']['gear_type']
                        except: car_dict['GearType'] = None
                        parsed_cars.append(car_dict)
                else:
                    print(f'\nerror: {response.status_code} status for page {page}')

            print('done.\nsaving data...', end=' ')
            parsed_cars_df = parsed_cars_df.append(parsed_cars)
            parsed_cars_df.drop_duplicates(['ID', 'Mark'], inplace=True)
            parsed_cars_df.drop(columns=['ID'], inplace=True)
            self.__save_to_csv(parsed_cars_df, 'autoru_learn.csv')
            print('done.')

        if parsed_cars_df.empty:
            print('error: no car was parsed')
            return 1

        return 0
