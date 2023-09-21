from flask import Flask, request, jsonify
import opendp.prelude as dp
from typing import List
from flask_cors import CORS


dp.enable_features("contrib")
app = Flask(__name__)
CORS(app)


@app.route('/dp-mean', methods=['POST'])
def dp_mean():
    data = request.json['data']
    print(data)
    
    # Define Context
    context = dp.Context.compositor(
        data=data,
        privacy_unit=dp.unit_of(contributions=1),
        privacy_loss=dp.loss_of(epsilon=1.0),
        domain=dp.domain_of(List[int]),
        split_evenly_over=2
    )
    
    # Compute DP mean
    dp_sum = context.query().clamp((0, 10)).sum().laplace()
    dp_count = context.query().clamp((0, 10)).count().laplace()
    
    mean_result = dp_sum.release() / dp_count.release()
    
    return jsonify({"dp_mean": mean_result})

if __name__ == '__main__':
    app.run(port=5000)
