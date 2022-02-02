from flask import Flask, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)
 
@app.route('/api/core/<path:doi>')
def get_rec_from_doi( doi ):
    from algo import algofst
    res = algofst( [ doi ] )

    return jsonify( [ art.toJson() for art in res ] )

app.run(host='0.0.0.0', port=8080)

if __name__ == '__main__':
    app.run(debug=True)
    