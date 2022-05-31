import argparse
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from numpy import polyfit, poly1d
from modules.utils import get_data
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.linear_model import LinearRegression, Lasso, Ridge, ElasticNet

cars = get_data('autoru_learn_full.csv', 'raw')
separator = '======================================================================================'


def build_cat_feature_plot(x, grid_place):
    plt.subplot(6, 2, grid_place)
    plt.title(x)
    sns.countplot(data=cars, x=x)
    plt.subplot(6, 2, grid_place + 1)
    plt.title(f'{x} vs Price')
    sns.boxplot(x=cars[x], y=cars.Price)


def build_num_feature_plot(x, grid_place):
    plt.subplot(4, 2, grid_place)
    z = polyfit(cars[x], cars.Price, 1)
    p = poly1d(z)
    plt.scatter(x=cars[x], y=cars.Price)
    plt.plot(cars[x], p(cars[x]), "r--")
    plt.title(f'{x} vs Price')
    plt.ylabel('Price')
    plt.xlabel(x)


def build_compare_plot(prediction, y, model):
    plt.figure(figsize=(7, 7))
    plt.title(model)
    plt.scatter(y, prediction)
    plt.plot([0, max(y)], [0, max(prediction)])
    plt.xlabel('Real Price')
    plt.ylabel('Predicted Price')
    plt.show()


def build_compare_metrics(prediction, y):
    mse = mean_squared_error(y, prediction)
    rmse = mean_squared_error(y, prediction, squared=False)
    r2 = r2_score(y, prediction)
    return [mse, rmse, r2]


def run(verbose=False):
    global cars
    cars.dropna(inplace=True)
    cars['Owners'] = cars['Owners'].astype(str)
    # cars = cars[cars['PriceSegment'] == 'ECONOMY']
    cars = cars[['Mark', 'City', 'Owners', 'Year', 'Mileage', 'Horsepower', 'Price', 'Model']]
    # cars = cars[['Mark', 'City', 'Owners', 'Pts', 'Transmission', 'FuelType', 'GearType', 'Year', 'Mileage', 'Horsepower', 'Price', 'Model']]
    # cars = cars[['Mark', 'City', 'Owners', 'Pts', 'Transmission', 'FuelType', 'GearType', 'Year', 'Mileage', 'Horsepower', 'Price', 'Model', 'Tax', 'Trunk', 'EngineVolume', 'Acceleration', 'Clearance']]

    if not verbose:
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
        exclude_cat_features = ['City', 'Mark', 'Model', 'PriceSegment']
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
    # cars['GearType'] = cars['GearType'].apply(lambda x: '4wd' if x == 'ALL_WHEEL_DRIVE' else '2wd')
    # cars['Transmission'] = cars['Transmission'].apply(lambda x: 'mt' if x == 'MECHANICAL' else 'at')
    # cars = cars[cars['FuelType'].isin(['GASOLINE', 'DIESEL'])]
    # cars = pd.get_dummies(cars, columns=['Transmission', 'FuelType', 'GearType', 'Pts'])
    cars['Owners'] = cars['Owners'].astype('int64')
    mark_avg_prices = cars.groupby('Mark', as_index=False)['Price'].mean()  # dict of Marks
    cars = cars.merge(mark_avg_prices, how='left', on='Mark', suffixes=('', 'Mean')).drop(columns=['Mark']).rename(columns={'PriceMean': 'Mark'})
    model_avg_prices = cars.groupby('Model', as_index=False)['Price'].mean()  # dict of Models
    cars = cars.merge(model_avg_prices, how='left', on='Model', suffixes=('', 'Mean')).drop(columns=['Model']).rename(columns={'PriceMean': 'Model'})
    cars['CityID'] = cars['City'].astype('category')
    cars['CityID'] = cars['CityID'].cat.codes
    cities_id = cars[['City', 'CityID']].drop_duplicates()  # dict of cities
    cars['City'] = cars['CityID']
    cars.drop(columns=['CityID'], inplace=True)
    cars.info()
    print(cars.head())

    print(separator)
    print('CORRELATION PLOT')
    cars = cars[['Price', 'Mark', 'City', 'Owners', 'Year', 'Mileage', 'Horsepower', 'Model']]
    # cars = cars[['Price', 'Mark', 'City', 'Owners', 'Pts', 'Transmission', 'FuelType', 'GearType', 'Year', 'Mileage', 'Horsepower', 'Model']]
    # cars = cars[['Price', 'Mark', 'City', 'Owners', 'Pts', 'Transmission', 'FuelType', 'GearType', 'Year', 'Mileage', 'Horsepower', 'Model', 'Tax', 'Trunk', 'EngineVolume', 'Acceleration', 'Clearance']]
    plt.figure(figsize=(30, 25))
    sns.set(font_scale=4)
    sns.heatmap(cars.corr(method='spearman'), annot=True)
    plt.show()

    print(separator)
    print('MODELS COMPARE PLOTS')
    x = cars.drop('Price', axis=1)
    y = cars['Price']
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.3, random_state=369)
    lr_model = LinearRegression()
    lasso_model = Lasso()
    ridge_model = Ridge()
    en_model = ElasticNet()
    rf_model = RandomForestRegressor(random_state=369)
    lr_model.fit(x_train, y_train)
    lasso_model.fit(x_train, y_train)
    ridge_model.fit(x_train, y_train)
    en_model.fit(x_train, y_train)
    rf_model.fit(x_train, y_train)
    lr_pred = lr_model.predict(x_test)
    lasso_pred = lasso_model.predict(x_test)
    ridge_pred = ridge_model.predict(x_test)
    en_pred = en_model.predict(x_test)
    rf_pred = rf_model.predict(x_test)
    sns.set(font_scale=1)
    build_compare_plot(lr_pred, y_test, 'LinearRegression')
    build_compare_plot(lasso_pred, y_test, 'Lasso')
    build_compare_plot(ridge_pred, y_test, 'Ridge')
    build_compare_plot(en_pred, y_test, 'ElasticNet')
    build_compare_plot(rf_pred, y_test, 'RandomForest')

    print(separator)
    print('MODELS COMPARE METRICS (best - first, worst - last)')
    lr_metrics = build_compare_metrics(lr_pred, y_test)
    lasso_metrics = build_compare_metrics(lasso_pred, y_test)
    ridge_metrics = build_compare_metrics(ridge_pred, y_test)
    en_metrics = build_compare_metrics(en_pred, y_test)
    rf_metrics = build_compare_metrics(rf_pred, y_test)
    metrics_df = pd.DataFrame({
        'LinearRegression': lr_metrics,
        'Lasso': lasso_metrics,
        'Ridge': ridge_metrics,
        'ElasticNet': en_metrics,
        'RandomForest': rf_metrics,
    }, index=['MSE', 'RMSE', 'R2']).T.sort_values(by='R2', ascending=False)
    print(metrics_df)

    print(separator)
    print('FEATURE IMPORTANCE RANDOM FOREST')
    feature_importance = dict(zip(rf_model.feature_names_in_, rf_model.feature_importances_))
    for feature, value in feature_importance.items():
        print(f'{feature} -> {round(value, 2)}')
    print(separator)


if __name__ == '__main__':
    args_parser = argparse.ArgumentParser()
    args_parser.add_argument("-v", dest="verbose", action=argparse.BooleanOptionalAction)
    args = args_parser.parse_args()
    raise SystemExit(run(args.verbose))
