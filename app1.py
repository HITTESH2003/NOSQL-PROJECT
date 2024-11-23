# from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, session
# from flask_pymongo import PyMongo
# from flask_bcrypt import Bcrypt
# import pandas as pd
# import tensorflow as tf
# from functools import wraps
# from werkzeug.security import check_password_hash
# from pymongo import MongoClient
# from datetime import datetime
# import numpy as np
# import random
# from flask_login import LoginManager, UserMixin, login_required, current_user, login_user, logout_user
# from bson import ObjectId
# import datetime


# app = Flask(__name__)
# app.config["MONGO_URI"] = "mongodb://localhost:27017/recommender"
# app.config['SECRET_KEY'] = 'yoursecretkey'  # Set securely for production
# mongo = PyMongo(app)  
# bcrypt = Bcrypt(app)

# # Initialize LoginManager
# login_manager = LoginManager()
# login_manager.init_app(app)
# login_manager.login_view = 'login'  # User login view

# # MongoDB Connection
# client = MongoClient('mongodb://localhost:27017/')
# db = client['recommender']
# mobile_collection = db['mobile_details']
# user_collection = db['users']
# search_collection = db['search_history']
# preference_collection = db['preferences']

# # Load the dataset
# df = pd.read_csv('/Users/hitteshkumarm/Desktop/COLLEGE/7th sem/RECOMMENDER SYSTEMS/PROJECT/mobile_recommendation_system_dataset.csv')
# df['brand'] = df['name'].apply(lambda x: x.split()[0])
# data = df.to_dict(orient='records')
# if mobile_collection.count_documents({}) == 0:
#     mobile_collection.insert_many(data)

# # Load the trained recommendation model
# model = tf.keras.models.load_model(
#     '/Users/hitteshkumarm/Desktop/COLLEGE/7th sem/RECOMMENDER SYSTEMS/PROJECT/model.h5',
#     custom_objects={'mse': tf.keras.losses.MeanSquaredError()}
# )

# # User loader for Flask-Login
# @login_manager.user_loader
# def load_user(user_id):
#     user = user_collection.find_one({'_id': ObjectId(user_id)})
#     if user:
#         return User(user)
#     return None

# # User class
# class User(UserMixin):
#     def __init__(self, user_data):
#         self.id = str(user_data['_id'])
#         self.username = user_data['username']
#         self.is_admin = user_data.get('is_admin', False)

#     def get_id(self):
#         return self.id

# # Custom decorator for login with role check
# def role_required(role):
#     def decorator(f):
#         @wraps(f)
#         def decorated_function(*args, **kwargs):
#             if 'user_id' not in session:
#                 return redirect(url_for('login'))
#             if role == 'admin' and not session.get('is_admin'):
#                 flash('Admin access only!', 'danger')
#                 return redirect(url_for('login'))
#             return f(*args, **kwargs)
#         return decorated_function
#     return decorator

# # Home route
# @app.route('/', methods=['GET', 'POST'])
# def index():
#     search_query = request.form.get('search')  # Get the search query from the form
#     if search_query:
#         # Query MongoDB to find mobiles matching the search query, ordered by rating
#         mobiles = list(mobile_collection.find({"name": {"$regex": search_query, "$options": "i"}})
#                        .sort("ratings", -1)  # Sort by rating in descending order
#                        .limit(5))  # Limit to top 5
#     else:
#         # If no search query, return all mobiles (you can change this to other logic)
#         mobiles = list(mobile_collection.find().sort("ratings", -1).limit(5))
    
#     return render_template('index.html', mobiles=mobiles)


# # Recommend mobile function
# def recommend_mobile(brand, ram=None, storage=None):
#     filtered_df = df[df['brand'].str.lower() == brand.lower()]
#     if ram:
#         filtered_df = filtered_df[filtered_df['ram'] == ram]
#     if storage:
#         filtered_df = filtered_df[filtered_df['storage'] == storage]
#     if filtered_df.empty:
#         return None
#     top_rated = filtered_df.sort_values(by='ratings', ascending=False).head(5)
#     return top_rated.to_dict(orient='records')

# # Recommendation route
# @app.route('/recommend', methods=['POST'])
# @login_required
# def recommend():
#     data = request.get_json()
#     brand = data.get('brand')
#     if not brand:
#         return jsonify({'error': 'Brand field is required'}), 400
#     recommendations = recommend_mobile(brand, data.get('ram'), data.get('storage'))
#     return jsonify({'recommendations': recommendations or []})

# # Signup route
# @app.route('/signup', methods=['GET', 'POST'])
# def signup():
#     if request.method == 'POST':
#         username = request.form.get('username')
#         password = request.form.get('password')
#         confirm_password = request.form.get('confirm_password')
#         if password != confirm_password:
#             flash('Passwords do not match!', 'danger')
#             return redirect(url_for('signup'))
#         existing_user = user_collection.find_one({'username': username})
#         if existing_user:
#             flash('Username already exists!', 'danger')
#             return redirect(url_for('signup'))
#         hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
#         user_id = user_collection.insert_one({'username': username, 'password': hashed_password}).inserted_id
#         session['user_id'] = str(user_id)
#         session['username'] = username
#         flash('Signup successful!', 'success')
#         return redirect(url_for('select_preference'))
#     return render_template('signup.html')

# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
        
#         # Find the user in the MongoDB collection
#         user = user_collection.find_one({'username': username})
        
#         # Check if user exists and password is correct
#         if user and check_password_hash(user['password'], password): # Ensure hashed passwords are used
#             # Set session details for the logged-in user
#             session['username'] = username
#             flash('Login successful!', 'success')
#             return redirect(url_for('dashboard'))  # Redirect to the dashboard or homepage
#         else:
#             flash('Invalid username or password. Please try again.', 'danger')
#             return redirect(url_for('login'))
#     return render_template('login.html')

# # Admin login
# @app.route('/admin_login', methods=['GET', 'POST'])
# def admin_login():
#     if request.method == 'POST':
#         username = request.form.get('username')
#         password = request.form.get('password')
#         user = user_collection.find_one({'username': username, 'is_admin': True})
#         if user and bcrypt.check_password_hash(user['password'], password):
#             login_user(User(user))
#             session['user_id'] = str(user['_id'])
#             session['is_admin'] = True
#             return redirect(url_for('admin_dashboard'))
#         flash('Invalid admin credentials', 'danger')
#     return render_template('admin_login.html')

# # Admin dashboard
# @app.route('/admin_dashboard')
# def admin_dashboard():
#     # Fetch user data from MongoDB
#     users = mongo.db.user.find()
#     total_users = mongo.db.user.count_documents({})  # Count total users

#     # Fetch mobile details from MongoDB
#     mobiles = mongo.db.mobile_details.find()
#     total_mobiles = mongo.db.mobile_details.count_documents({})  # Count total mobiles

#     # Calculate average price and rating
#     avg_price = sum([mobile['price'] for mobile in mobiles]) / total_mobiles if total_mobiles else 0
#     avg_rating = sum([mobile['ratings'] for mobile in mobiles]) / total_mobiles if total_mobiles else 0

#     # Calculate price and rating distributions (for chart)
#     mobile_prices = [mobile['price'] for mobile in mobiles]
#     mobile_ratings = [mobile['ratings'] for mobile in mobiles]

#     # Format current time
#     current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

#     return render_template('admin_dashboard.html', 
#                            users=users, 
#                            total_users=total_users,
#                            total_mobiles=total_mobiles,
#                            avg_price=avg_price,
#                            avg_rating=avg_rating,
#                            mobile_prices=mobile_prices,
#                            mobile_ratings=mobile_ratings,
#                            current_time=current_time)

# # Preference selection
# @app.route('/select_preference', methods=['GET', 'POST'])
# def select_preference():
#     if request.method == 'POST':
#         user_id = session['user_id']
#         brand = request.form.get('brand')
#         preference_collection.update_one(
#             {'user_id': user_id},
#             {'$set': {'preferred_brand': brand, 'username': session['username'], 'user_id': user_id}},
#             upsert=True
#         )
#         flash('Preferences saved successfully!', 'success')
#         return redirect(url_for('home'))
#     brands = df['brand'].unique()
#     return render_template('select_preference.html', brands=brands)

# # Logout route
# @app.route('/logout')
# def logout():
#     session.pop('user_id', None)
#     session.pop('username', None)
#     session.pop('is_admin', None)
#     flash('Logged out successfully', 'success')
#     return redirect(url_for('login'))

# # Dashboard route
# @app.route('/dashboard')
# def dashboard():
#     all_mobiles = list(mobile_collection.find())
#     random_mobiles = random.sample(all_mobiles, min(len(all_mobiles), 5))
#     for mobile in random_mobiles:
#         mobile['int_rating'] = int(mobile['ratings'])
#     return render_template('dashboard.html', mobiles=random_mobiles)

# if __name__ == '__main__':
#     app.run(debug=True, port=5001)
