from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, session
from pymongo import MongoClient
import pandas as pd
from bson import ObjectId
import random
from flask_login import LoginManager, UserMixin, login_required, current_user, login_user, logout_user
import datetime


app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Ensure this is a strong, secret key for security

# MongoDB setup (example)
client = MongoClient('mongodb://localhost:27017/')  # Replace with your MongoDB connection string
db = client['NOSQL_PROJ']
users_collection = db['users']  # Assuming a 'users' collection in your MongoDB
mobile_collection = db['mobile_details']



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Query MongoDB for the user
        user = users_collection.find_one({"username": username})
        
        if user and user['password'] == password:  # Directly compare plaintext passwords
            flash('Login successful!', 'success')
            return redirect(url_for('home'))  
        else:
            flash('Invalid username or password', 'danger')
            return redirect(url_for('login'))
    
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Get form data
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        # Check if passwords match
        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return redirect(url_for('signup'))
        
        # Check if username already exists
        existing_user = users_collection.find_one({"username": username})
        if existing_user:
            flash("Username already exists. Please choose a different one.", "warning")
            return redirect(url_for('signup'))

        # Insert new user into the database with plaintext password
        users_collection.insert_one({
            "username": username,
            "password": password  # Store plaintext password
        })
        
        flash("Signup successful! You can now log in.", "success")
        return redirect(url_for('login'))  # Redirect to login page after signup
    
    # Render the signup page for GET requests
    return render_template('signup.html')

@app.route('/')
def index():
    # Fetch mobile data from MongoDB
    mobiles = list(mobile_collection.find())
    return render_template('index.html', mobiles=mobiles)


# Home route that renders the home page
@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/dashboard')
def dashboard():
    # Fetch all mobile records from the database
    mobiles = list(mobile_collection.find())
    for mobile in mobiles:
        mobile['ratings'] = round(mobile['ratings'])  # Round the ratings to the nearest integer

    return render_template('dashboard.html', mobiles=mobiles)
    
    # # Render the dashboard template with the random mobiles
    # return render_template('dashboard.html', mobiles=random_mobiles, username="User") 

@app.route('/logout')
def logout():
    # You may want to clear the session or handle user logout here
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))  # Redirect to the login page after logout


db = client.recommender  # Adjust based on your MongoDB setup
mobile_details = db.mobile_details  # Your collection

def recommend_mobile(brand, ram=None, storage=None):
    query = {'brand': brand}
    if ram:
        query['ram'] = ram
    if storage:
        query['storage'] = storage
    recommendations = list(mobile_details.find(query).sort('ratings', -1).limit(5))  # Adjust the limit as needed

    # Process recommendations to include only relevant fields
    return [{
        'name': mobile['name'],
        'ratings': mobile['ratings'],
        'price': mobile['price'],
        'imgURL': mobile['imgURL'],
        'corpus': mobile['corpus']
    } for mobile in recommendations]


@app.route('/recommend', methods=['POST'])
def recommend():
    data = request.json
    brand = data.get('brand')
    ram = data.get('ram')
    storage = data.get('storage')
    
    # Call the recommend_mobile function
    recommendations = recommend_mobile(brand, ram, storage)
    
    # Check if recommendations exist
    if recommendations:
        return jsonify({'recommendations': recommendations})
    else:
        return jsonify({'error': 'No recommendations found for the specified criteria.'})
    
# @app.route('/admin-dashboard')
# def admin_dashboard():
#     # Fetch data from MongoDB
#     total_users = db.user.count_documents({})
#     total_mobiles = db.mobile_details.count_documents({})
#     total_brands = len(db.mobile_details.distinct('brand'))
    
#     # Calculate average price and rating
#     pipeline_avg_price = [{"$group": {"_id": None, "avg_price": {"$avg": "$price"}}}]
#     avg_price_result = list(db.mobile_details.aggregate(pipeline_avg_price))
#     avg_price = avg_price_result[0].get('avg_price', 0) if avg_price_result else 0
    
#     pipeline_avg_rating = [{"$group": {"_id": None, "avg_rating": {"$avg": "$ratings"}}}]
#     avg_rating_result = list(db.mobile_details.aggregate(pipeline_avg_rating))
#     avg_rating = avg_rating_result[0].get('avg_rating', 0) if avg_rating_result else 0

#     # Pass data to template
#     return render_template('admin_dashboard.html', 
#                            total_users=total_users, 
#                            total_mobiles=total_mobiles, 
#                            total_brands=total_brands, 
#                            avg_price=avg_price, 
#                            avg_rating=avg_rating)

@app.route('/admin-dashboard')
def admin_dashboard():
    # Fetch data from MongoDB
    total_users = db.user.count_documents({})
    total_mobiles = db.mobile_details.count_documents({})
    total_brands = len(db.mobile_details.distinct('brand')) if 'brand' in db.mobile_details.find_one() else 0

    # Calculate average price and rating
    pipeline_avg_price = [{"$group": {"_id": None, "avg_price": {"$avg": "$price"}}}]
    avg_price_result = list(db.mobile_details.aggregate(pipeline_avg_price))
    avg_price = avg_price_result[0].get('avg_price', 0) if avg_price_result else 0

    pipeline_avg_rating = [{"$group": {"_id": None, "avg_rating": {"$avg": "$ratings"}}}]
    avg_rating_result = list(db.mobile_details.aggregate(pipeline_avg_rating))
    avg_rating = avg_rating_result[0].get('avg_rating', 0) if avg_rating_result else 0

    # Fetch data for bar graph
    if 'brand' in db.mobile_details.find_one():
        pipeline_brand_count = [
            {"$group": {"_id": "$brand", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
    else:
        pipeline_brand_count = [
            {"$group": {"_id": "$name", "count": {"$sum": 1}}},  # Fallback to 'name'
            {"$sort": {"count": -1}}
        ]

    brand_count_data = list(db.mobile_details.aggregate(pipeline_brand_count))
    labels = [item['_id'] for item in brand_count_data]
    counts = [item['count'] for item in brand_count_data]

    # Pass data to template
    return render_template('admin_dashboard.html', 
                           total_users=total_users, 
                           total_mobiles=total_mobiles, 
                           total_brands=total_brands, 
                           avg_price=avg_price, 
                           avg_rating=avg_rating,
                           labels=labels,
                           counts=counts)



if __name__ == '__main__':
    app.run(debug=True, port=5001)
