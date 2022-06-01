import argparse
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from modules.utils import get_data
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.linear_model import LinearRegression, Lasso, Ridge, ElasticNet

separator = '======================================================================================'

features = ['Price', 'Mark', 'City', 'Owners', 'Year', 'Mileage', 'Horsepower', 'Model']
# features = ['Price', 'Mark', 'City', 'Owners', 'Year', 'Mileage', 'Horsepower', 'Model', 'Pts', 'Transmission', 'FuelType', 'GearType']
# features = ['Price', 'Mark', 'City', 'Owners', 'Year', 'Mileage', 'Horsepower', 'Model', 'Pts', 'Transmission', 'FuelType', 'GearType', 'Tax', 'Trunk', 'EngineVolume', 'Acceleration', 'Clearance']

cars = get_data('autoru_learn_full.csv', 'raw').dropna()
cars['Owners'] = cars['Owners'].astype(str)
cars = cars[features]


def build_cat_feature_plot(x, grid_place, rows_count):
    plt.subplot(rows_count, 1, grid_place)
    sns.countplot(data=cars, x=x)
    plt.title(x)


def build_num_feature_plot(x, grid_place, rows_count):
    plt.subplot(rows_count, 1, grid_place)
    plt.boxplot(cars[x], vert=False)
    plt.title(x)


def build_predicts_plot(prediction, y, model):
    plt.figure(figsize=(7, 7))
    plt.scatter(y, prediction)
    plt.title(model)
    plt.plot([0, max(y)], [0, max(prediction)])
    plt.xlabel('Real Price')
    plt.ylabel('Predicted Price')
    plt.show()


def get_metrics(prediction, y):
    rmse = mean_squared_error(y, prediction, squared=False)
    r2 = r2_score(y, prediction)
    return [rmse, r2]


def run(verbose=False):
    global cars
    # cars = cars[cars['PriceSegment'] == 'ECONOMY']

    if verbose:
        print(separator)
        print('CAT FEATURES ANALYZE')
        grid_place = 1
        plt.figure(figsize=(10, 20))
        exclude_cat_features = ['City', 'Mark', 'Model', 'PriceSegment']
        cat_features = [x for x in list(cars.select_dtypes(include=['object', 'bool']).columns) if x not in exclude_cat_features]
        for cat_feature in cat_features:
            build_cat_feature_plot(cat_feature, grid_place, len(cat_features))
            grid_place += 1
        plt.tight_layout()
        plt.show()

        print(separator)
        print('NUM FEATURES ANALYZE')
        grid_place = 1
        plt.figure(figsize=(10, 20))
        exclude_num_features = ['Price']
        num_features = [x for x in list(cars.select_dtypes(include=['int64', 'float64']).columns) if x not in exclude_num_features]
        for num_feature in num_features:
            build_num_feature_plot(num_feature, grid_place, len(num_features))
            grid_place += 1
        plt.tight_layout()
        plt.show()

    # CLEAR BAD VALUES
    for x in ['Mileage']:
        q75, q25 = np.percentile(cars.loc[:, x], [75, 25])
        qr = q75 - q25
        min_val = q25 - (1.5 * qr)
        max_val = q75 + (1.5 * qr)
        cars.loc[cars[x] < min_val, x] = np.nan
        cars.loc[cars[x] > max_val, x] = np.nan
    cars = cars.dropna()

    print(separator)
    print('FEATURE ENCODING')
    # cars = cars[cars['FuelType'].isin(['GASOLINE', 'DIESEL'])]
    # cars['GearType'] = cars['GearType'].apply(lambda x: 1 if x == 'ALL_WHEEL_DRIVE' else 0)
    # cars['Transmission'] = cars['Transmission'].apply(lambda x: 1 if x == 'MECHANICAL' else 0)
    # cars['Pts'] = cars['Pts'].apply(lambda x: 1 if x == 'ORIGINAL' else 0)
    # cars['FuelType'] = cars['FuelType'].apply(lambda x: 1 if x == 'GASOLINE' else 0)

    cars['Owners'] = cars['Owners'].astype('int64')

    mark_avg_prices = cars.groupby('Mark', as_index=False)['Price'].mean()  # dict of Marks for predictor
    cars = cars.merge(mark_avg_prices, how='left', on='Mark', suffixes=('', 'Mean')).drop(columns=['Mark']).rename(columns={'PriceMean': 'Mark'})

    model_avg_prices = cars.groupby('Model', as_index=False)['Price'].mean()  # dict of Models for predictor
    cars = cars.merge(model_avg_prices, how='left', on='Model', suffixes=('', 'Mean')).drop(columns=['Model']).rename(columns={'PriceMean': 'Model'})

    cars['CityID'] = cars['City'].astype('category').cat.codes
    cities_id = cars[['City', 'CityID']].drop_duplicates()  # dict of Cities for predictor
    cars['City'] = cars['CityID']
    cars.drop(columns=['CityID'], inplace=True)

    print(cars.head())

    # print(separator)
    # print('CORRELATION PLOT')
    # cars = cars[features]
    # plt.figure(figsize=(30, 25))
    # sns.set(font_scale=4)
    # sns.heatmap(cars.corr(method='spearman'), annot=True)
    # plt.show()

    print(separator)
    print('FIT MODELS AND PREDICT')
    x = cars.drop('Price', axis=1)
    x.info()
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
    build_predicts_plot(lr_pred, y_test, 'LinearRegression')
    build_predicts_plot(lasso_pred, y_test, 'Lasso')
    build_predicts_plot(ridge_pred, y_test, 'Ridge')
    build_predicts_plot(en_pred, y_test, 'ElasticNet')
    build_predicts_plot(rf_pred, y_test, 'RandomForest')

    print(separator)
    print('METRICS')
    metrics_df = pd.DataFrame({
        'LinearRegression': get_metrics(lr_pred, y_test),
        'Lasso': get_metrics(lasso_pred, y_test),
        'Ridge': get_metrics(ridge_pred, y_test),
        'ElasticNet': get_metrics(en_pred, y_test),
        'RandomForest': get_metrics(rf_pred, y_test),
    }, index=['RMSE', 'R2']).T.sort_values(by='R2', ascending=False)
    print(metrics_df)

    print(separator)
    print('FEATURE IMPORTANCE')
    feature_importance = dict(zip(rf_model.feature_names_in_, rf_model.feature_importances_))
    for feature, value in dict(sorted(feature_importance.items(), key=lambda item: item[1])).items():
        print(f'{feature} -> {round(value, 2)}')
    print(separator)


if __name__ == '__main__':
    args_parser = argparse.ArgumentParser()
    args_parser.add_argument("-v", dest="verbose", action=argparse.BooleanOptionalAction)
    args = args_parser.parse_args()
    raise SystemExit(run(args.verbose))
