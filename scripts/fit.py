# scripts/fit.py

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from category_encoders import CatBoostEncoder
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from catboost import CatBoostClassifier
import yaml
import os
import joblib

# обучение модели
def fit_model():
    # Прочитайте файл с гиперпараметрами params.yaml
    with open('params.yaml', 'r') as fd:
        params = yaml.safe_load(fd)

    # загрузите результат предыдущего шага: inital_data.csv
    data = pd.read_csv('data/initial_data.csv')

    # Определим типы признаков
    cat_features = data.select_dtypes(include='object')
    potential_binary_features = cat_features.nunique() == 2
    binary_cat_features = cat_features[potential_binary_features[potential_binary_features].index]
    other_cat_features = cat_features[potential_binary_features[~potential_binary_features].index]
    num_features = data.select_dtypes(['float', 'int'])

    # Создаем колонко-трансформер
    preprocessor = ColumnTransformer(
        [
            ('binary', OneHotEncoder(drop=params['one_hot_drop']), binary_cat_features.columns.tolist()),
            ('cat', CatBoostEncoder(return_df=False), other_cat_features.columns.tolist()),
            ('num', StandardScaler(), num_features.columns.tolist())
        ],
        remainder='drop',
        verbose_feature_names_out=False
    )

    # Инициализация модели с параметрами
    model = CatBoostClassifier(
        auto_class_weights=params['auto_class_weights']
    )

    # Объединяем препроцессор и модель в pipeline
    pipeline = Pipeline(
        [
            ('preprocessor', preprocessor),
            ('model', model)
        ]
    )

    # Обучаем модель (предполагается, что в data уже есть столбец 'target')
    pipeline.fit(data, data[params['target_col']])

    # Создаем директорию для модели, если ее нет
    os.makedirs('models', exist_ok=True)

    # Сохраняем обученную модель
    joblib.dump(pipeline, 'models/fitted_model.pkl')


if __name__ == '__main__':
    fit_model()