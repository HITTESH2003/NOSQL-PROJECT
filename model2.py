# # Step 1: Import Libraries
# import numpy as np
# import pandas as pd
# from sklearn.model_selection import train_test_split
# from sklearn.preprocessing import LabelEncoder
# import tensorflow as tf
# from tensorflow.keras.layers import Input, Embedding, Flatten, Dense, Concatenate
# from tensorflow.keras.models import Model

# # Load the dataset
# dataset = pd.read_csv("/Users/hitteshkumarm/Desktop/COLLEGE/7th sem/RECOMMENDER SYSTEMS/PROJECT/mobile_recommendation_system_dataset.csv")

# # Display the first few rows to understand the structure
# print("Dataset Preview:")
# print(dataset.head())

# # Step 3: Simulate User Interaction Data
# user_ids = np.random.randint(0, 100, 1000)  # 100 users
# item_ids = np.random.randint(0, len(dataset), 1000)  # 1000 interactions
# ratings = np.random.randint(1, 6, 1000)  # Ratings between 1 and 5

# # Encode item_ids to match with the dataset indices
# item_encoder = LabelEncoder()
# encoded_item_ids = item_encoder.fit_transform(item_ids)

# # Split data into training and testing sets
# X = np.column_stack((user_ids, encoded_item_ids))
# y = ratings
# X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# # Step 4: Define Model Parameters
# n_users = np.max(user_ids) + 1  # Adding 1 to ensure correct range
# n_items = len(dataset)

# # Build the Neural Collaborative Filtering model
# user_input = Input(shape=(1,), name="user_input")
# item_input = Input(shape=(1,), name="item_input")

# # Embedding layers for users and items
# user_embedding = Embedding(input_dim=n_users, output_dim=10, name="user_embedding")(user_input)
# item_embedding = Embedding(input_dim=n_items, output_dim=10, name="item_embedding")(item_input)

# # Flatten the embedding vectors
# user_vecs = Flatten()(user_embedding)
# item_vecs = Flatten()(item_embedding)

# # Concatenate user and item vectors
# concat = Concatenate()([user_vecs, item_vecs])

# # Fully connected layers
# dense1 = Dense(128, activation='relu')(concat)
# dense2 = Dense(64, activation='relu')(dense1)
# output = Dense(1)(dense2)  # Output layer (regression)

# # Build the model
# model = Model([user_input, item_input], output)
# model.compile(optimizer='adam', loss='mse')

# # Summarize the model
# model.summary()

# # Step 5: Train the Model
# model.fit([X_train[:, 0], X_train[:, 1]], y_train, epochs=5, batch_size=64, validation_split=0.1)

# # Step 6: Evaluate the Model
# loss = model.evaluate([X_test[:, 0], X_test[:, 1]], y_test)
# print(f"Test Loss: {loss}")

# # Step 7: Make Predictions for a Specific User
# user_id = 18  # Example user_id
# user_ids = np.array([user_id] * n_items)  # Repeat the user_id to match the number of items

# # Predict ratings for all items for the specific user
# predicted_ratings = model.predict([user_ids, np.arange(n_items)])

# # Get the indices of the top 5 rated items
# top_5_indices = np.argsort(predicted_ratings, axis=0)[-5:][::-1].flatten()  # Sort in descending order

# # Retrieve the top 5 items from the dataset
# recommended_items = dataset.iloc[top_5_indices]

# # Display the top 5 recommended items
# print("Top 5 Recommended Mobiles for User", user_id, ":")
# for idx, row in recommended_items.iterrows():
#     print(f"{idx+1}. {row['name']} - Predicted Rating: {predicted_ratings[idx][0]}")


# model.save('/Users/hitteshkumarm/Desktop/COLLEGE/7th sem/RECOMMENDER SYSTEMS/PROJECT/model.h5')

# # Custom function to register 'mse' for loading
# def custom_mse(y_true, y_pred):
#     return tf.keras.losses.mean_squared_error(y_true, y_pred)

# # Register the custom function
# tf.keras.utils.get_custom_objects().update({"mse": custom_mse})

# # # Now load the model
# # model = tf.keras.models.load_model('/Users/hitteshkumarm/Desktop/COLLEGE/7th sem/RECOMMENDER SYSTEMS/PROJECT/model.h5')

# model = tf.keras.models.load_model(
#     '/Users/hitteshkumarm/Desktop/COLLEGE/7th sem/RECOMMENDER SYSTEMS/PROJECT/model.h5', 
#     custom_objects={'mse': tf.keras.losses.MeanSquaredError()}
# )