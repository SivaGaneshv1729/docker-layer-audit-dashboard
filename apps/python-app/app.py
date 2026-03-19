from flask import Flask
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

app = Flask(__name__)

@app.route('/')
def hello():
    # Simulate some work with the libraries
    X = np.array([[1], [2], [3]])
    y = np.array([2, 4, 6])
    model = LinearRegression().fit(X, y)
    return f'Hello from Python ML! Intercept is {model.intercept_}'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
