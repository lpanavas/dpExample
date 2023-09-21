from flask import Flask, request, jsonify
import opendp.prelude as dp
from typing import List

import pandas as pd
from flask_cors import CORS

dp.enable_features("contrib")
app = Flask(__name__)
CORS(app)

def load_and_filter_data(file_path: str) -> list:
    df = pd.read_csv(file_path)  # Removed quotes around file_path
    return list(df.iloc[:, 0])  # Assuming age is in the first column

@app.route('/dp-mean', methods=['POST'])
def dp_mean():
    epsilon = float(request.json.get('epsilon', 1.0))  # Default to 1.0 if epsilon is not provided
    file_path = 'https://raw.githubusercontent.com/opendp/opendp/83d2e2a73d8d1c5164bc57663823bc27f982d2c1/docs/source/data/PUMS_california_demographics_1000/data.csv'
    
    try:
        data = load_and_filter_data(file_path)
    except FileNotFoundError:
        return jsonify({"error": "File not found"}), 400
    
    context = dp.Context.compositor(
        data=data,
        privacy_unit=dp.unit_of(contributions=1),
        privacy_loss=dp.loss_of(epsilon=epsilon),
        domain=dp.domain_of(List[int]),
        split_evenly_over=2
    )

    dp_sum = context.query().clamp((0, 100)).sum().laplace()
    dp_count = context.query().clamp((0, 100)).count().laplace()

    mean_result = dp_sum.release() / dp_count.release()

    return jsonify({"dp_mean": mean_result})

if __name__ == '__main__':
    app.run(port=5000)
