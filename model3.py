import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from surprise import Dataset, Reader, SVD
from surprise.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import re
import pickle


# Load the dataset (replace 'your_path' with the actual path)
file_path = '/Users/hitteshkumarm/Desktop/COLLEGE/7th sem/RECOMMENDER SYSTEMS/PROJECT/mobile_recommendation_system_dataset.csv'  # Adjust path as needed
mobile_data = pd.read_csv(file_path)

# 1. Clean the 'price' column by removing any non-numeric characters
mobile_data['price'] = mobile_data['price'].replace('[₹,]', '', regex=True).astype(float)

# 2. Handle missing values in the 'corpus' column (fill with an empty string)
mobile_data['corpus'].fillna('', inplace=True)

# 3. Normalize the 'ratings' and 'price' columns
scaler = MinMaxScaler()
mobile_data[['ratings', 'price']] = scaler.fit_transform(mobile_data[['ratings', 'price']])

# 4. Extract storage and RAM from 'corpus' for context-aware recommendation
def extract_ram_storage(corpus):
    ram_search = re.search(r'RAM(\d+)', corpus)
    ram = int(ram_search.group(1)) if ram_search else np.nan

    storage_search = re.search(r'Storage(\d+)', corpus)
    storage = int(storage_search.group(1)) if storage_search else np.nan

    return ram, storage

# Apply the extraction function
mobile_data[['RAM', 'Storage']] = mobile_data['corpus'].apply(lambda x: pd.Series(extract_ram_storage(x)))
mobile_data[['RAM', 'Storage']] = mobile_data[['RAM', 'Storage']].fillna(0)  # Fill NaN values with 0

# Normalize RAM and Storage
mobile_data[['RAM', 'Storage']] = scaler.fit_transform(mobile_data[['RAM', 'Storage']])

# 5. Simulate user IDs for demonstration purposes (since user data is not present)
mobile_data['user_id'] = np.random.randint(1, 100, mobile_data.shape[0])  # Simulate 100 users

# Prepare the data for the recommender system
reader = Reader(rating_scale=(0, 1))  # Rating scale normalized between 0 and 1
data = Dataset.load_from_df(mobile_data[['user_id', 'name', 'ratings']], reader)

# 6. Split the data into training and testing sets
trainset, testset = train_test_split(data, test_size=0.2)

# 7. Implement the SVD algorithm (Collaborative Filtering)
svd = SVD()

# Train the model
svd.fit(trainset)

# Test the model
predictions = svd.test(testset)

# 8. Evaluate the model using Root Mean Squared Error (RMSE)
rmse = mean_squared_error([pred.r_ui for pred in predictions], [pred.est for pred in predictions], squared=False)
print(f"RMSE: {rmse:.4f}")
# Define the user ID for whom you want recommendations
specific_user_id = 18  # Change this to the desired user ID

# 9. Generate predictions for all mobiles for the specific user
all_mobiles = mobile_data[['name']].copy()  # Get all mobile names
user_mobiles = mobile_data[['name', 'user_id']]  # Get mobiles rated by the user
rated_mobile_names = user_mobiles[user_mobiles['user_id'] == specific_user_id]['name'].unique()

# Create predictions for all mobiles not rated by the specific user
predictions_for_user = []
for mobile in all_mobiles['name']:
    if mobile not in rated_mobile_names:
        pred = svd.predict(specific_user_id, mobile)
        predictions_for_user.append((mobile, pred.est))

# 10. Sort predictions by estimated rating and get top 5
top_5_recommendations = sorted(predictions_for_user, key=lambda x: x[1], reverse=True)[:5]

# 11. Display top 5 mobile recommendations
print("Top 5 Mobile Recommendations for User ID", specific_user_id)
for mobile, estimated_rating in top_5_recommendations:
    print(f"Mobile: {mobile}, Estimated Rating: {estimated_rating:.4f}")


# After training the SVD model:
with open('svd_model.pkl', 'wb') as model_file:
    pickle.dump(svd, model_file)