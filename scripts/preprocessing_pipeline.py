# ===================================
# Fonctions preprocessing et pipeline
# ===================================

import logging

from sklearn.model_selection import train_test_split, KFold, cross_validate
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def separation_X_y(df):
    target_col = "yield"

    feature_df = df.drop(columns=[target_col]).copy()

    categorical_cols = feature_df.select_dtypes(include=["object", "category", "bool"]).columns.tolist()
    numeric_cols = feature_df.select_dtypes(include=["number"]).columns.tolist()

    logging.info(f"Colonnes numériques : {numeric_cols}")
    logging.info(f"Colonnes catégorielles : {categorical_cols}")

    X = feature_df.copy()
    y = df[target_col].copy()

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=42
    )

    return X_train, X_test, y_train, y_test, categorical_cols, numeric_cols


def preparation_pipeline(numeric_cols, categorical_cols, model):
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), numeric_cols),
            ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_cols)
        ]
    )

    pipeline = Pipeline(steps=[
        ("preprocessor", preprocessor),
        ("model", model)
    ])

    return pipeline


def cross_validation(pipeline, X_train, y_train):
    cv = KFold(n_splits=5, shuffle=True, random_state=42)

    scoring = {
        "mse": "neg_mean_squared_error",
        "mae": "neg_mean_absolute_error",
        "mape": "neg_mean_absolute_percentage_error",
        "r2": "r2"
    }

    cv_results = cross_validate(
        pipeline,
        X_train,
        y_train,
        cv=cv,
        scoring=scoring,
        n_jobs=-1
    )

    return cv_results


def train_predict(pipeline, X_train, y_train, X_test):
    pipeline.fit(X_train, y_train)
    y_pred = pipeline.predict(X_test)

    return y_pred