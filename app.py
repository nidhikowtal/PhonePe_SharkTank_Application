from flask_cors import CORS
from flask_pymongo import PyMongo
from flask import Flask, request, jsonify
import pymongo

MONGO_URI = "mongodb://localhost:27017/xhartank"

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
app.config['MONGO_URI'] = MONGO_URI
mongo = PyMongo(app)

CORS(app)
db = mongo.db.pitch_database

# index route

@app.route("/")
def index():
    return "Backend of the application is created."

# create a pitch

@app.route("/pitches", methods=['POST'])
def create_pitch():
    try : 
        entrepreneur = request.json['entrepreneur']
        pitchTitle = request.json['pitchTitle']
        pitchIdea = request.json['pitchIdea']
        askAmount = request.json['askAmount']
        equity = request.json['equity']
        pitch_data = {
            "_id":db.count_documents({})+1,
            "entrepreneur": entrepreneur,
            "pitchTitle": pitchTitle,
            "pitchIdea": pitchIdea,
            "askAmount": (askAmount),
            "equity": (equity),
            "offers": []
        }
        print(pitch_data)

        if entrepreneur == "" or pitchTitle == "" or pitchIdea == "" or str(askAmount).isalpha() or str(equity).isalpha() or int(equity) > 100 or int(equity) < 0:
                return jsonify("Invalid Request Body"),  400

           
        pitch_id = db.insert_one(pitch_data).inserted_id
      
        return_data = {'id' : str(pitch_id)}
        print(pitch_id)
        return jsonify(return_data) , 200
    except Exception as ex:
        print(ex)
        return jsonify("Invalid Request Body"),  400

# make an offer

@app.route("/pitches/<int:pitch_id>/makeOffer", methods=['POST'])
def make_offer(pitch_id):
    try:
        p = db.find_one({'_id' :pitch_id})
              
        if(p is None):
            return jsonify("Pitch Not Found"),  404
      
        investor = request.json['investor']
        amount = request.json['amount']
        equity = request.json['equity']
        comment = request.json['comment']

        if investor == "" or str(equity).isalpha() or str(amount).isalpha() or int(equity) > 100 or int(equity) < 0:
                return jsonify("Invalid Request Body"),  400

        offer_id = len(p['offers'])+1
        offer_data = {
            "id":offer_id,
            "investor": investor,
            "amount": (amount),
            "equity": (equity),
            "comment": comment,
        }
        
        previous = p['offers']
     
        previous.append(offer_data)
        filter = { '_id' : pitch_id}
        newvalues = { "$set": { 'offers': previous } }
        db.update_one(filter,newvalues)
        return_data = {'id' : str(offer_id)}
       
        return jsonify(return_data) , 200

    except Exception as ex:
        print(ex)
        return jsonify("Invalid Request Body"),  400


# get all the pitches in the system

@app.route("/pitches", methods=['GET'])
def getAllPitches():
    pitch_data = []
    for d in db.find().sort('_id' , pymongo.DESCENDING):
        pitch_data.append({
            'id': str(d['_id']),
            'entrepreneur': d['entrepreneur'],
            'pitchTitle': d['pitchTitle'],
            'pitchIdea' : d['pitchIdea'],
            'askAmount': d['askAmount'],
            'equity': d['equity'],
            'offers': d['offers']
        })
    return jsonify(pitch_data), 200



# get a single pitch

@app.route("/pitches/<int:pitch_id>", methods=['GET'])
def get_pitch(pitch_id):

    try:
        d = db.find_one({'_id' :pitch_id})
        if(d is None):
            return jsonify("Pitch Not Found"),  404
        
        pitch_data = {
            'id': str(d['_id']),
            'entrepreneur': d['entrepreneur'],
            'pitchTitle': d['pitchTitle'],
            'pitchIdea' : d['pitchIdea'],
            'askAmount': d['askAmount'],
            'equity': d['equity'],
            'offers': d['offers']
        }
        return jsonify(pitch_data), 200
    except Exception as ex:
        print(ex)
        return jsonify("Pitch Not Found"),  404



if __name__ == "__main__":
    app.run(host="localhost", port=8000, debug=True)