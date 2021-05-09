import flask
import pymongo
from datetime import datetime
from bson.objectid import ObjectId
from flask_cors import CORS, cross_origin
from pymongo import MongoClient
from flask import jsonify, request
import json
import csv
import uuid
import razorpay
import recommend

rzClient = razorpay.Client(
    auth=("rzp_test_SZp0P0isnoUWrQ", "IY2Y79U7XfAUlq6drsSFM7Bk"))

app = flask.Flask(__name__)
cors = CORS(app)
app.config["DEBUG"] = True
app.config['CORS_HEADERS'] = 'Content-Type'

client = MongoClient(
    'mongodb+srv://ajay:test@cluster0.ttuw9.mongodb.net/myFirstDatabase?retryWrites=true&w=majority')

db = client["bs-mart"]


@app.route('/test', methods=['GET'])
@cross_origin()
def test():
    result = []
    categories = ["groceries", "beverages", "fruits", "veggies"]
    for i in range(0, len(categories)):
        for j in range(0, 2):
            result.append({
                "name": "product "+str(i)+str(j),
                "price": 10,
                "shipping": True,
                "category": categories[i],
                "rating": 4.5,
                "image": "https://images.squarespace-cdn.com/content/v1/59d2bea58a02c78793a95114/1604517546555-J765GMQHYO74IFMZ2RWQ/ke17ZwdGBToddI8pDm48kFHDcct_fltA3KLnvRyGws9Zw-zPPgdn4jUwVcJE1ZvWQUxwkmyExglNqGp0IvTJZUJFbgE-7XRK3dMEBRBhUpz_xmy3d2yisJKMB5olewvGU1zvsFHW7wcxXg-c1peyE_IzyNgEDA6BxhwvJ1j-egw/iphone+12.png",
                "images": ["https://images.squarespace-cdn.com/content/v1/59d2bea58a02c78793a95114/1604517546555-J765GMQHYO74IFMZ2RWQ/ke17ZwdGBToddI8pDm48kFHDcct_fltA3KLnvRyGws9Zw-zPPgdn4jUwVcJE1ZvWQUxwkmyExglNqGp0IvTJZUJFbgE-7XRK3dMEBRBhUpz_xmy3d2yisJKMB5olewvGU1zvsFHW7wcxXg-c1peyE_IzyNgEDA6BxhwvJ1j-egw/iphone+12.png", "https://images.squarespace-cdn.com/content/v1/59d2bea58a02c78793a95114/1604517546555-J765GMQHYO74IFMZ2RWQ/ke17ZwdGBToddI8pDm48kFHDcct_fltA3KLnvRyGws9Zw-zPPgdn4jUwVcJE1ZvWQUxwkmyExglNqGp0IvTJZUJFbgE-7XRK3dMEBRBhUpz_xmy3d2yisJKMB5olewvGU1zvsFHW7wcxXg-c1peyE_IzyNgEDA6BxhwvJ1j-egw/iphone+12.png"],
                "description": "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.",

            })
    db["products"].insert_many(result)
    return jsonify({
        "message": "success"
    })


@app.route('/getRecommendations', methods=['POST'])
@cross_origin()
def getRecommendations():
    data = request.get_json(force=True)
    name = data["name"]
    search = recommend.show_recommendations(name)
    query = db['products'].find()
    results = []
    resultId = []
    for product in query:
        for key in search:
            if key.lower() in product["description"].lower() and product["name"] != name:
                temp = product
                temp["_id"] = str(temp["_id"])
                if temp["_id"] not in resultId:
                    results.append(temp)
                    resultId.append(temp["_id"])
    return jsonify({
        "message": results
    })


@app.route('/importdata', methods=['GET'])
@cross_origin()
def importdata():
    productsFilePath = "products.csv"
    categoriesFilePath = "categories.json"
    products = []
    with open(productsFilePath) as productsFile:
        productsCsv = csv.DictReader(productsFile)
        for rows in productsCsv:
            product = {}
            for col in rows.keys():
                product[col] = rows[col]
            product["rating"] = float(product["rating"])
            product["images"] = product["images"].split(",")
            products.append(product)
    with open(categoriesFilePath) as categoriesFile:
        categories = json.load(categoriesFile)
        #products[rows["id"]] = rows
    db["products"].delete_many({})
    db["products"].insert_many(products)
    db["categories"].delete_many({})
    db["categories"].insert_many(categories)
    return jsonify({
        "message": "success"
    })


@ app.route('/search', methods=['POST'])
@ cross_origin()
def search():
    data = request.get_json(force=True)
    search = data["search"]
    query = db['products'].find()
    results = []
    for product in query:
        if search.lower() in product["name"].lower():
            temp = product
            temp["_id"] = str(temp["_id"])
            results.append(temp)
    return jsonify({
        "message": results
    })


@ app.route('/getCat', methods=['GET'])
@ cross_origin()
def getCat():
    result = db['categories'].find()
    cats = []
    for i in result:
        cats.append({
            "name": i["name"],
            "image": i["image"]
        })
    # print(cats)
    return jsonify({
        "message": cats
    })


@ app.route('/getProducts', methods=['GET'])
@ cross_origin()
def getProducts():
    result = db['products'].find()
    prods = []
    for i in result:
        i["_id"] = str(i["_id"])
        prods.append(i)
    # print(cats)
    return jsonify({
        "message": prods
    })


@ app.route('/updateProduct', methods=['POST'])
@ cross_origin()
def updateProduct():
    data = request.get_json(force=True)
    if "_id" in data.keys():
        filt = {"_id": ObjectId(data["_id"])}
        del data["_id"]
        db["products"].update_one(filt, {"$set": data})
    else:
        db["products"].insert_one(data)
    return jsonify({
        "message": "success"})


@ app.route('/deleteProduct', methods=['POST'])
@ cross_origin()
def deleteProduct():
    data = request.get_json(force=True)
    filt = {"_id": ObjectId(data["_id"])}
    del data["_id"]
    db["products"].delete_one(filt)
    return jsonify({
        "message": "success"})


@ app.route('/productsWCat', methods=['POST'])
@ cross_origin()
def getProdWCat():
    data = request.get_json(force=True)
    if data["category"] == "all":
        query = db['products'].find()
    else:
        query = db['products'].find({"category": data["category"]})
    results = []
    for i in query:
        results.append({
            "name": i["name"],
            "price": i["price"],
            "shipping": i["shipping"],
            "category": i["category"],
            "rating": i["rating"],
            "image": i["image"],
            "description": i["description"],
            "images": i["images"]
        })
    return jsonify({
        "message": results
    })


@ app.route('/productsWName', methods=['POST'])
@ cross_origin()
def productsWName():
    data = request.get_json(force=True)
    names = data["names"]
    query = db['products'].find()
    results = []
    for product in query:
        if product["name"] in names:
            temp = product
            del temp["_id"]
            results.append(temp)
    return jsonify({
        "message": results
    })


@ app.route('/updateUData', methods=['POST'])
@ cross_origin(origin="*")
def updateUData():
    data = request.get_json(force=True)
    # print(data)
    filt = {"uid": data["uid"]}
    if "googleId" in data.keys():
        filt = {"uid": data["uid"], "googleId": data["googleId"]}
    newData = {
        "uid": data["uid"],
        "googleId": data["googleId"] if "googleId" in data.keys() else "",
        "cart": data["cart"],
        "cartItems": data["cartItems"],
        "wishlist": data["wishlist"],
        "cartTotal": data["cartTotal"]
    }
    count = db["userData"].find(filt).count()
    if(count > 0):
        db["userData"].update_many(filt, {"$set": newData})
    else:
        db["userData"].insert_one(newData)
    return jsonify({
        "message": "success"
    })


@ app.route('/getUData', methods=['POST'])
@ cross_origin()
def getUData():
    data = request.get_json(force=True)
    filt = {"uid": data["uid"]}
    if "googleId" in data.keys():
        filt = {"googleId": data["googleId"]}
    result = db["userData"].find_one(filt)
    if not result:
        result = {}
        return jsonify({"message": result})
    total = 0
    for i in result["cartItems"]:
        total = total + (int(i["qty"]) * float(i["price"]))
        total = round(total, 2)
    # print(result)
    return jsonify({
        "message": {
            "cart": result["cart"],
            "cartItems": result["cartItems"],
            "wishlist": result["wishlist"],
            "cartTotal": total
        }
    })


@ app.route('/newOrder', methods=['POST'])
@ cross_origin()
def newOrder():
    data = request.get_json(force=True)
    data["orderId"] = str(uuid.uuid4())
    data["createdAt"] = datetime.now()
    db["orders"].insert_one(data)
    return jsonify({
        "message": "success"
    })


@ app.route('/pay', methods=['POST'])
@ cross_origin()
def pay():
    data = request.get_json(force=True)
    order_amount = float(data["amount"] * 100)
    order_currency = 'INR'
    order_receipt = str(uuid.uuid4())
    options = dict()
    options["amount"] = order_amount
    options["currency"] = order_currency
    options["receipt"] = order_receipt
    response = rzClient.order.create(data=options)
    # print(response)
    # db["payments"].insert_one(payment)
    return jsonify({
        "message": response})


@ app.route('/getOrders', methods=['POST'])
@ cross_origin()
def getOrders():
    data = request.get_json(force=True)
    filt = {"googleId": data["googleId"]}
    query = db["orders"].find(filt)
    results = []
    for i in query:
        temp = i
        del temp["_id"]
        results.append(temp)
    results.reverse()
    return jsonify({
        "message": results})


@ app.route('/getOrders', methods=['GET'])
@ cross_origin()
def getAllOrders():
    query = db["orders"].find()
    results = []
    for i in query:
        i["_id"] = str(i["_id"])
        results.append(i)
    results.reverse()
    return jsonify({
        "message": results})


@ app.route('/updateOrder', methods=['POST'])
@ cross_origin()
def updateOrder():
    data = request.get_json(force=True)
    filt = {"_id": ObjectId(data["_id"])}
    del data["_id"]
    db["orders"].update_one(filt, {"$set": data})
    return jsonify({
        "message": "success"})


@ app.route('/uploadProf', methods=['POST'])
@ cross_origin()
def uploadProf():
    data = request.get_json(force=True)
    filt = {"googleId": data["googleId"]}
    count = db["profiles"].find(filt).count()
    if(count > 0):
        db["profiles"].update_one(filt, {"$set": data})
    else:
        db["profiles"].insert_one(data)
    return jsonify({
        "message": "success"
    })


@ app.route('/getProf', methods=['POST'])
@ cross_origin()
def getProf():
    data = request.get_json(force=True)
    filt = {"googleId": data["googleId"]}
    result = db["profiles"].find_one(filt)
    return jsonify({
        "message": {
            "email": result["email"],
            "familyName": result["familyName"],
            "givenName": result["givenName"],
            "googleId": result["googleId"],
            "imageUrl": result["imageUrl"],
            "name": result["name"],
        }})


app.run()
