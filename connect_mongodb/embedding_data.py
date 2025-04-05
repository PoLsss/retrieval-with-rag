from sentence_transformers import SentenceTransformer
import pymongo
import pandas as pd
import os
from dotenv import load_dotenv
load_dotenv()

mongodbUrl = os.getenv("MONGODB_URL")
dbName = os.getenv("DB_NAME")
dbCollection = os.getenv("DB_COLLECTION")
modelEmbeddingName = os.getenv("MODEL_EMBEDDING")

embedding_model = SentenceTransformer(modelEmbeddingName)
client = pymongo.MongoClient(mongodbUrl)


def get_embedding(sentence):
    if not sentence.strip():
        print("Embedding for empty text.")
        return []
    embedding = embedding_model.encode(sentence)
    return embedding.tolist()
    
db = client[dbName]  # Chọn database
collection = db[dbCollection]  # Chọn collection (bảng)


csv_filename = "RAG\connect_mongodb\\table_data.csv" 
df = pd.read_csv(csv_filename)

print("Inital DataFrame")
# print(df.head())

df['Summary'] = df['Mã MH'] + ": " + df['Tên MH'] + ": " + df['Tóm tắt môn học'] 

# print(df.head())

df['embedding'] = df['Summary'].apply(get_embedding)

df.drop(columns=["Summary"], inplace=True)

print("Processed DataFrame")


# collection.delete_many({})

data_enbeding = df.to_dict(orient="records")
collection.insert_many(data_enbeding)

print("Done -> Nhớ vào Search index để cài đặc tìm theo vector")