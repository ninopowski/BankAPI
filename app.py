from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from aux_functions import user_exist, verify_pw, verify_credentials, ret_map, check_amount


# initialize flask
app = Flask(__name__)
api = Api(app)

# connect to mongodb
client = MongoClient("mongodb://localhost:27017/bank")

# create the db
db = client.BankAPI
users = db["Users"]



class Register(Resource):
    def post(self):
        posted_data = request.get_json()

        username = posted_data["username"]
        password = posted_data["password"]

        if user_exist(username):
            return jsonify(ret_map(301, "User exist"))

        hashed_and_salted_pw = generate_password_hash(
            password=password,
            method="pbkdf2:sha256",
            salt_length=16
        )
        users.insert_one(
            {
                "username": username,
                "password": hashed_and_salted_pw,
                "own": 0,
                "debt": 0
            }
        )
        return jsonify(ret_map(200, "User registered"))


class Transfer(Resource):
    def post(self):
        posted_data = request.get_json()

        username = posted_data["username"]
        password = posted_data["password"]
        transfer_to_user = posted_data["transfer to"]
        amount = posted_data["amount"]

        return_map, error = verify_credentials(username, password)

        if error:
            return jsonify(return_map)

        if not check_amount(amount):
            return jsonify(ret_map(304, "Amount value invalid."))


        user = users.find_one({"username": transfer_to_user})
        if not user:
            return jsonify(ret_map(302, "User you wish to transfer to doesn't exist."))

        new_amount = user["own"] + amount
        users.update_one({"username": transfer_to_user}, {"$set": {"own": new_amount}})
        return jsonify(ret_map(200, f"Successfuly transfered {amount}"))


class Add(Resource):
    def post(self):
        posted_data = request.get_json()

        username = posted_data["username"]
        password = posted_data["password"]
        amount = posted_data["amount"]

        if not check_amount(amount):
            return jsonify(ret_map(304, "Amount value invalid."))

        return_map, error = verify_credentials(username, password)
        if error:
            return jsonify(return_map)

        saldo = users.find_one({"username": username})["own"]
        users.update_one({"username": username}, {"$set": {"own": saldo+amount }})
        return jsonify(ret_map(200, f"Amount of {amount} added to account"))


class Balance(Resource):
    def post(self):
        posted_data = request.get_json()

        username = posted_data["username"]
        password = posted_data["password"]

        return_map, error = verify_credentials(username, password)
        if error:
            return jsonify(return_map)

        user = users.find_one({"username": username})
        return jsonify(
            {
                "username": user["username"],
                "own": user["own"],
                "debt": user["debt"]
            }
        )





api.add_resource(Register, "/register")
api.add_resource(Transfer, "/transfer")
api.add_resource(Add, '/add')
api.add_resource(Balance, "/balance")

if __name__ == "__main__":
    app.run(debug=True)