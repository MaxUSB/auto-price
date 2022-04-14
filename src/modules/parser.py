import sys
import time
import requests
import pandas as pd
from .utils import get_config, save_data


class Parser:
    def __init__(self):
        self.url = ''
        self.config = get_config('parser')

    def get_autoru_cars(self, start_price, end_price, increment):
        self.url = 'https://auto.ru/-/ajax/desktop/listing/'

        parsed_cars_df = pd.DataFrame()
        while start_price < end_price:
            print(f'for price interval {start_price}...{start_price + increment}:')
            print('getting page number...', end=' ')
            request_parameter = {
                "category": "cars",
                "section": "used",
                "price_from": start_price,
                "price_to": start_price + increment,
                "page": 1,
                "geo_id": [225],
            }
            response = requests.post(url=self.url, json=request_parameter, headers=self.config['autoru_headers']).json()
            total_pages = response['pagination']['total_page_count']

            print('done.\nparsing running:')
            parsed_cars = []
            for page in range(1, total_pages + 1):
                print(f'\r\t{page} of {total_pages} pages...', end=' ')
                request_parameter['page'] = page
                response = requests.post(url=self.url, json=request_parameter, headers=self.config['autoru_headers'])
                if response.status_code == 200:
                    cars = response.json().get('offers')
                    if cars is None:
                        time.sleep(15)
                        continue
                    for car in cars:
                        car_dict = {}
                        try:
                            car_dict['ID'] = car['id']
                        except:
                            car_dict['ID'] = None
                        try:
                            car_dict['Owners'] = car['documents']['owners_number']
                        except:
                            car_dict['Owners'] = None
                        try:
                            car_dict['Pts'] = car['documents']['pts']
                        except:
                            car_dict['Pts'] = None
                        try:
                            car_dict['Year'] = car['documents']['year']
                        except:
                            car_dict['Year'] = None
                        try:
                            car_dict['Price'] = car['price_info']['price']
                        except:
                            car_dict['Price'] = None
                        try:
                            car_dict['City'] = car['seller']['location']['region_info']['name']
                        except:
                            car_dict['City'] = None
                        try:
                            car_dict['Mileage'] = car['state']['mileage']
                        except:
                            car_dict['Mileage'] = None
                        try:
                            car_dict['Mark'] = car['vehicle_info']['mark_info']['name']
                        except:
                            car_dict['Mark'] = None
                        try:
                            car_dict['Model'] = car['vehicle_info']['model_info']['name']
                        except:
                            car_dict['Model'] = None
                        try:
                            car_dict['Horsepower'] = car['vehicle_info']['tech_param']['power']
                        except:
                            car_dict['Horsepower'] = None
                        try:
                            car_dict['Capacity'] = car['vehicle_info']['tech_param']['displacement']
                        except:
                            car_dict['Capacity'] = None
                        try:
                            car_dict['Transmission'] = car['vehicle_info']['tech_param']['transmission']
                        except:
                            car_dict['Transmission'] = None
                        try:
                            car_dict['FuelType'] = car['vehicle_info']['tech_param']['engine_type']
                        except:
                            car_dict['FuelType'] = None
                        try:
                            car_dict['GearType'] = car['vehicle_info']['tech_param']['gear_type']
                        except:
                            car_dict['GearType'] = None
                        try:
                            car_dict['PriceSegment'] = car['vehicle_info']['super_gen']['price_segment']
                        except:
                            car_dict['PriceSegment'] = None
                        parsed_cars.append(car_dict)
                else:
                    print(f'\nerror: {response.status_code} status for page {page}', file=sys.stderr)

            print('done.\nsaving data...', end=' ')
            parsed_cars_df = parsed_cars_df.append(parsed_cars)
            parsed_cars_df.drop(columns=['ID'], inplace=True)
            parsed_cars_df['Mark'] = parsed_cars_df['Mark'].apply(lambda x: 'LADA' if x == 'LADA (ВАЗ)' else x)
            success = save_data(parsed_cars_df, 'autoru_learn.csv', 'raw')
            if not success:
                return 1
            print('done.')
            start_price += increment

        if parsed_cars_df.empty:
            print('error: no car was parsed', file=sys.stderr)
            return 1

        return 0
