from flask import Flask, jsonify
from flask import request
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)
 
@app.route('/api/core/rec', methods =['GET']) 
def get_rec_from_doi():

    data = request.get_json()

    if "doi" in data:
        from algo import algofst
        res = algofst( data["doi"] )
        
        return jsonify( [ art.toJson() for art in res ] )
    
    return "Error"
