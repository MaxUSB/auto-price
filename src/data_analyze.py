import os
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn import linear_model

cars = pd.read_csv(f"{os.getenv('project_path')}/data/autoru_learn.csv")
separator = '======================================================================================\n' \
            '====================================================================================== '


def build_cat_feature_plot(x, grid_place):
    plt.subplot(7, 2, grid_place)
    plt.title(x)
    sns.countplot(data=cars, x=x)
    plt.subplot(7, 2, grid_place + 1)
    plt.title(f'{x} vs Price')
    sns.boxplot(x=cars[x], y=cars.Price)


def build_num_feature_plot(x, grid_place):
    plt.subplot(3, 2, grid_place)
    plt.scatter(x=cars[x], y=cars.Price)
    plt.title(f'{x} vs Price')
    plt.ylabel('Price')
    plt.xlabel(x)


def run():
    global cars

    print(separator)
    print('DATAFRAME INFO')
    cars.info()
    cars.dropna(inplace=True)
    cars['YearTax'] = cars['YearTax'].astype(int)
    cars['Owners'] = cars['Owners'].astype(str)

    print(separator)
    print(f'MARKS (count={len(cars.Mark.unique())})\n', cars.Mark.unique())

    print(separator)
    print('PRICE PLOTS')
    plt.figure(figsize=(20, 8))
    plt.subplot(1, 2, 1)
    plt.title('Price Distribution')
    sns.histplot(data=cars.Price, kde=True)
    plt.subplot(1, 2, 2)
    plt.title('Price Spread')
    sns.boxplot(y=cars.Price)
    plt.show()

    print(separator)
    print('MARKS COUNT PLOT')
    plt.figure(figsize=(25, 8))
    plt.subplot(1, 1, 1)
    sub_plt = cars.Mark.value_counts().plot(kind='bar')
    plt.title('Marks')
    sub_plt.set(xlabel='Marks', ylabel='Frequency')
    plt.show()

    print(separator)
    print('CAT FEATURES VS PRICE PLOTS')
    grid_place = 1
    plt.figure(figsize=(30, 40))
    exclude_cat_features = ['Mark', 'City']
    cat_features = [x for x in list(cars.select_dtypes(include=['object', 'bool']).columns) if x not in exclude_cat_features]
    for cat_feature in cat_features:
        build_cat_feature_plot(cat_feature, grid_place)
        grid_place += 2
    plt.tight_layout()
    plt.show()

    print(separator)
    print('NUM FEATURES VS PRICE PLOTS')
    grid_place = 1
    plt.figure(figsize=(20, 20))
    exclude_num_features = ['Price']
    num_features = [x for x in list(cars.select_dtypes(include=['int64', 'float64']).columns) if x not in exclude_num_features]
    for num_feature in num_features:
        build_num_feature_plot(num_feature, grid_place)
        grid_place += 1
    plt.tight_layout()
    plt.show()

    print(separator)
    print('ENCODED FEATURE')
    cars = cars[['Mark', 'City', 'Owners', 'Pts', 'Transmission', 'FuelType', 'GearType', 'Year', 'Mileage', 'HP', 'Price']]
    cars['GearType'] = cars['GearType'].apply(lambda x: '4wd' if x == 'ALL_WHEEL_DRIVE' else '2wd')
    cars['Transmission'] = cars['Transmission'].apply(lambda x: 'mt' if x == 'MECHANICAL' else 'at')
    cars = cars[cars['FuelType'].isin(['GASOLINE', 'DIESEL'])]
    cars['Owners'] = cars['Owners'].astype('int64')
    mark_avg_prices = cars.groupby('Mark', as_index=False)['Price'].mean()  # dict of Marks
    cars = cars.merge(mark_avg_prices, how='left', on='Mark', suffixes=('', 'Mean')).drop(columns=['Mark']).rename(columns={'PriceMean': 'Mark'})
    cars['CityID'] = cars['City'].astype('category')
    cars['CityID'] = cars['CityID'].cat.codes
    cities_id = cars[['City', 'CityID']].drop_duplicates()  # dict of cities
    cars['City'] = cars['CityID']
    cars.drop(columns=['CityID'], inplace=True)
    cars['Pts'] = np.where(cars['Pts'].str.contains('ORIGINAL'), 1, 0)
    cars = pd.get_dummies(cars, columns=['Transmission', 'FuelType', 'GearType'], prefix=["transmission", "fuel", 'gear'])
    print(cars.head())

    print(separator)
    print('CORRELATION PLOT')
    plt.figure(figsize=(30, 25))
    sns.heatmap(cars.corr(method='spearman'), annot=True)
    plt.show()

    print(separator)
    lr_model = linear_model.LinearRegression()
    lasso_model = linear_model.Lasso()
    ridge_model = linear_model.Ridge()
    en_model = linear_model.ElasticNet()


if __name__ == '__main__':
    run()
