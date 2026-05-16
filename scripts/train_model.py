"""
train_model.py

Train a linear regression model using mtcars.csv and save trained model to disk.

Predictors: weight (wt), quarter-mile time (qsec), and transmission type (am)
Response: mpg 
"""
import pandas as pd
from sklearn.linear_model import LinearRegression
import joblib


def train_model() -> None:
    """Train and save linear regression model."""

    # Load dataset
    mtcars = pd.read_csv('mtcars.csv')

    # Split into X and y ('mpg')
    RESPONSE_COL = 'mpg' #define 'mpg' as the response
    X = mtcars[['wt','qsec','am']] # get df of predictors 
    y = mtcars[RESPONSE_COL]

    # Instantiate model
    lr_model = LinearRegression()

    print('Training linear regression model...')
    # Fit model
    lr_model.fit(X, y)
    print(f'\nModel training completed with {X.columns.tolist()} predictors.')

    # Save trained model
    joblib.dump(lr_model, "models/model.pkl")
    print('\nModel saved to models/model.pkl.')


if __name__ == "__main__":
    train_model()
