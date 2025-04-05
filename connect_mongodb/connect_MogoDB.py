import pymongo
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

mongodbUrl = os.getenv("MONGODB_URL")
dbName = os.getenv("DB_NAME")
dbCollection = os.getenv("DB_COLLECTION")

client = pymongo.MongoClient(mongodbUrl)

db = client[dbName]  # Chọn database
collection = db[dbCollection]  # Chọn collection (bảng)

# 3. Đọc file CSV
csv_filename = "table_data.csv" 
df = pd.read_csv(csv_filename)

# 4. Chuyển DataFrame thành danh sách dictionary
data = df.to_dict(orient="records")


# 5. Insert vào MongoDB
collection.insert_many(data)

print("Data from CSV inserted successfully into MongoDB!")
