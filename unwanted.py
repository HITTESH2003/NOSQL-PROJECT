
# def get_personalized_recommendation(user_id, n_items):
#     """
#     Generates personalized recommendations for a given user based on a trained model.
    
#     Args:
#     - user_id (int): The ID of the user for whom we want to generate recommendations.
#     - n_items (int): The number of items (mobiles) available in the dataset.
    
#     Returns:
#     - DataFrame: A DataFrame containing the top recommended items for the user.
#     """
#     user_ids = np.array([user_id] * n_items)
#     item_ids = np.arange(n_items)

#     # Get predicted ratings for all items for the user
#     predicted_ratings = model.predict([user_ids, item_ids])
#     top_indices = predicted_ratings.argsort()[-5:][::-1]  # Get top 5 recommendations
#     top_recommendations = df.iloc[top_indices]

#     return top_recommendations


# @app.route('/personalised-recommendation')
# @login_required
# def personalised_recommendation():
#     # Get user ID from session, ensure it is an integer
#     user_id = session.get('user_id')
    
#     if user_id is None:
#         user_id = 18  # Default to a sample user ID if session doesn't have a user_id

#     # Ensure user_id is an integer
#     try:
#         user_id_int = int(user_id)
#     except ValueError:
#         # If the user_id is not a valid integer, return an error or fallback
#         flash('Invalid user ID.', 'danger')
#         return redirect(url_for('home'))

#     n_items = len(df)  # Total number of items in the dataset

#     try:
#         # Get personalized recommendations using the helper function
#         top_recommendations = get_personalized_recommendation(user_id_int, n_items)

#         # Pass the recommendations to the HTML page
#         return render_template('personalised_recommendation.html', recommended_items=top_recommendations.to_dict(orient='records'))

#     except Exception as e:
#         print("Error during prediction:", str(e))
#         flash('An error occurred while generating recommendations.', 'danger')
#         return redirect(url_for('home'))
