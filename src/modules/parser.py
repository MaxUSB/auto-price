import os
import json
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
                    cars = response.json()['offers']
                    try:
                        for car in cars:
                            car_dict = {
                                'ID': car['id'],
                                'Color': car['color_hex'],
                                'Owners': car['documents']['owners_number'],
                                'IsOriginalPts': car['documents']['pts_original'],
                                'Year': car['documents']['year'],
                                'YearTax': car['owner_expenses']['transport_tax']['tax_by_year'],
                                'Price': car['price_info']['price'],
                                'City': car['seller']['location']['region_info']['name'],
                                'Mileage': car['state']['mileage'],
                                'IsNotBeaten': car['state']['state_not_beaten'],
                                'Mark': car['vehicle_info']['mark_info']['name'],
                                'IsLeftHand': car['vehicle_info']['steering_wheel'] == 'LEFT',
                                'HP': car['vehicle_info']['tech_param']['power'],
                                'Capacity': car['vehicle_info']['tech_param']['displacement'],
                                'Transmission': car['vehicle_info']['tech_param']['transmission'],
                                'FuelType': car['vehicle_info']['tech_param']['engine_type'],
                                'GearType': car['vehicle_info']['tech_param']['gear_type'],
                                'BodyType': car['vehicle_info']['configuration']['body_type'],
                            }
                            parsed_cars.append(car_dict)
                    except KeyError as error:
                        print(f'\nerror: on page {page} {error}')
                else:
                    print(f'\nerror: {response.status_code} status for page {page}')

            print('done.\nremoving duplicates...', end=' ')
            parsed_cars_df = pd.DataFrame(parsed_cars)
            parsed_cars_df.drop_duplicates(['ID'], inplace=True)

            print('done.\nsaving data...', end=' ')
            self.__save_to_csv(parsed_cars_df, 'autoru_learn.csv')
            print('done.')

        if parsed_cars_df.empty:
            print('error: no car was parsed')
            return 1

        return 0
