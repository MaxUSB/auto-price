import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from modules.utils import get_data
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.linear_model import LinearRegression, Lasso, Ridge, ElasticNet

separator = '=================================================================================================='

features = ['Price', 'Mark', 'City', 'Owners', 'Year', 'Mileage', 'Horsepower', 'Model', 'Pts', 'Transmission', 'FuelType', 'GearType', 'Tax', 'Trunk', 'Capacity', 'Acceleration', 'Clearance', 'PriceSegment']

cars = get_data('autoru_learn.csv', 'raw')
cars = cars[features].dropna()


def build_cat_feature_plot(x, grid_place, rows_count):
    plt.subplot(rows_count, 1, grid_place)
    sns.countplot(data=cars, x=x)
    plt.title(x)


def build_num_feature_plot(x, grid_place, rows_count):
    plt.subplot(rows_count, 1, grid_place)
    plt.boxplot(cars[x], vert=False)
    plt.title(x)


def build_price_distribution(x, field_value, grid_place, rows_count):
    plt.subplot(rows_count, 2, grid_place)
    plt.hist(x)
    plt.title(field_value)


def build_predicts_plot(prediction, y, model):
    plt.figure(figsize=(7, 7))
    plt.scatter(y, prediction)
    plt.title(model)
    plt.plot([0, max(y)], [0, max(prediction)])
    plt.xlabel('Real Price')
    plt.ylabel('Predicted Price')
    plt.show()


def get_metrics(prediction, y):
    r2 = r2_score(y, prediction)
    rmse = mean_squared_error(y, prediction, squared=False)
    return [r2, rmse]


def get_relative_error(prediction, y):
    prediction = pd.Series(prediction).rename('Prediction')
    y = y.reset_index(drop=True)
    result = pd.concat([prediction, y], axis=1)
    return result.apply(lambda row: abs(row['Price'] - row['Prediction']) / row['Price'], axis=1)


def run():
    global cars
    # cars = cars[(cars['PriceSegment'] == 'ECONOMY')]
    # cars = cars[(cars['PriceSegment'] == 'MEDIUM') | (cars['PriceSegment'] == 'PREMIUM')]
    cars = cars.drop(columns=['PriceSegment'])
    cars['Owners'] = cars['Owners'].astype(str)

    print(separator)
    print('CAT FEATURES ANALYZE')
    grid_place = 1
    plt.figure(figsize=(10, 20))
    exclude_cat_features = ['City', 'Mark', 'Model', 'Pts']
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
    for x in num_features:
        q75, q25 = np.percentile(cars.loc[:, x], [75, 25])
        qr = q75 - q25
        min_val = q25 - (1.5 * qr)
        max_val = q75 + (1.5 * qr)
        cars.loc[cars[x] < min_val, x] = np.nan
        cars.loc[cars[x] > max_val, x] = np.nan
    cars = cars.dropna()

    print(separator)
    print('MARKS AND MODELS PRICE DISTRIBUTION')
    for field in ['Mark', 'Model']:
        grid_place = 1
        field_values = cars[field].unique()[:6]
        plt.figure(figsize=(5, 5))
        for field_value in field_values:
            build_price_distribution(cars[cars[field] == field_value]['Price'], field_value, grid_place, int(len(field_values) / 2))
            grid_place += 1
        plt.tight_layout()
        plt.show()

    print(separator)
    print('FEATURE ENCODING')
    cars = cars[cars['FuelType'].isin(['GASOLINE', 'DIESEL'])]
    cars['GearType'] = cars['GearType'].apply(lambda x: 1 if x == 'ALL_WHEEL_DRIVE' else 0)
    cars['Transmission'] = cars['Transmission'].apply(lambda x: 1 if x == 'MECHANICAL' else 0)
    cars['Pts'] = cars['Pts'].apply(lambda x: 1 if x == 'ORIGINAL' else 0)
    cars['FuelType'] = cars['FuelType'].apply(lambda x: 1 if x == 'GASOLINE' else 0)
    cars['Owners'] = cars['Owners'].astype('float64').astype('int64')
    mark_median_prices = cars.groupby('Mark', as_index=False)['Price'].median()  # dict of Marks for predictor
    cars = cars.merge(mark_median_prices, how='left', on='Mark', suffixes=('', 'Mean')).drop(columns=['Mark']).rename(columns={'PriceMean': 'Mark'})
    model_median_prices = cars.groupby('Model', as_index=False)['Price'].median()  # dict of Models for predictor
    cars = cars.merge(model_median_prices, how='left', on='Model', suffixes=('', 'Mean')).drop(columns=['Model']).rename(columns={'PriceMean': 'Model'})
    cars['CityID'] = cars['City'].astype('category').cat.codes
    cities_id = cars[['City', 'CityID']].drop_duplicates()  # dict of Cities for predictor
    cars['City'] = cars['CityID']
    cars.drop(columns=['CityID'], inplace=True)
    print(cars.head())

    print(separator)
    print('CORRELATION PLOT')
    binary_features = [col for col in cars.columns if len(cars[col].unique()) == 2]
    correlation_features = num_features + binary_features + ['Price']
    plt.figure(figsize=(40, 35))
    sns.set(font_scale=4)
    sns.heatmap(cars[correlation_features].corr(method='spearman'), annot=True, fmt='.2f')
    plt.show()

    print(separator)
    print('FINAL FEATURES')
    final_features = ['Price', 'City', 'Mark', 'Model', 'Owners', 'Year', 'Mileage', 'Horsepower']
    cars = cars[final_features]
    int_final_features = [feature for feature in final_features if feature not in ['Mark', 'Model']]
    cars[int_final_features] = cars[int_final_features].astype(int)
    cars.info()

    print(separator)
    print('FIT MODELS AND PREDICT')
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
    }, index=['R2', 'RMSE']).T.sort_values(by=['R2', 'RMSE'], ascending=[False, True])
    print(metrics_df)

    print(separator)
    print('RELATIVE ERRORS')
    relative_errors_df = pd.DataFrame({
        'LinearRegression': get_relative_error(lr_pred, y_test),
        'Lasso': get_relative_error(lasso_pred, y_test),
        'Ridge': get_relative_error(ridge_pred, y_test),
        'ElasticNet': get_relative_error(en_pred, y_test),
        'RandomForest': get_relative_error(rf_pred, y_test),
    })
    relative_errors_describe = relative_errors_df.describe()
    relative_errors_describe.loc['count'] = relative_errors_describe.loc['count'].astype(int).astype(str)
    print(relative_errors_describe)

    print(separator)
    print('FEATURE IMPORTANCE')
    feature_importance = dict(zip(rf_model.feature_names_in_, rf_model.feature_importances_))
    for feature, value in dict(sorted(feature_importance.items(), key=lambda item: item[1])).items():
        print(f'{feature} -> {round(value, 2)}')

    print(separator)
    print('ERROR MODEL')
    error_model = RandomForestRegressor(random_state=369)
    error_model.fit(x_test, relative_errors_df['RandomForest'])
    error_model_pred = error_model.predict(x_test)
    error_metrics_df = pd.DataFrame({
        'ErrorModel': get_metrics(error_model_pred, relative_errors_df['RandomForest']),
    }, index=['R2', 'RMSE']).T
    print(error_metrics_df)
    print(separator)


if __name__ == '__main__':
    raise SystemExit(run())
