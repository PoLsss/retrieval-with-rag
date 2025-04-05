
## UIT Course Chatbot with RAG 

An intelligent Chatbot system based on the Retrieval-Augmented Generation (RAG) model, allowing users to query information about UIT courses through natural conversation.
The Chatbot combines Semantic Routing, MongoDB, Reflection, and LLM to provide flexible responses to both course-related questions and casual chitchat.

### Feature
  - 🔍 Retrieve course information from MongoDB through natural language questions.

  - 🧠 Semantic Router: Intelligently classify questions as "course-related" or "chitchat," then route them to the appropriate system.

  - 🧩 RAG (Retrieval-Augmented Generation): Combine real-world knowledge from the internal database with the language capabilities of LLM to generate contextually accurate responses.

  - 🔄 Reflection module: Understand the conversation context based on the chat history.

  - 💬 A user-friendly, intuitive web interface.

### User Interface Demo
https://github.com/user-attachments/assets/0737bf32-19df-4775-8f81-b712530efe54

### Chatbot Architecture
![Image](https://github.com/user-attachments/assets/7dbd1357-e8d0-42b4-bfa0-1770ad87e2d2)


### Set up

#### 1. Installation
This code requires Python >= 3.9.

```
git clone https://github.com/PoLsss/retrieval-with-rag.git
cd retrieval-with-rag
```
#### 2. Install the necessary libraries using the command below:

```
pip install -r requirements.txt
```

#### 3. Environment Variables

Create a file named .env and add the following lines, replacing placeholders with your actual values:

```
TAVILY_API_KEY
MONGODB_URL=
EMBEDDING_MODEL=
DB_NAME=
DB_COLLECTION=
OPENAI_API_KEY=
```

- TAVILY_API_KEY: Your key to access the Tavily search.
- MONGODB_URI: URI of your MongoDB Atlas instance.
- EMBEDDING_MODEL: Name of the embedding model you're using for text embedding.
- DB_NAME: Name of the database in your MongoDB Atlas.
- DB_COLLECTION: Name of the collection within the database.
- OPENAI_API_KEY: Your key to access the OpenAI API.

#### 4. Data

Prepare your data following the file 'table_data.csv':

For this project, we are using MongoDB Atlas for Vector Search. Make sure you create a Vector Search Index [follow this documment](https://www.mongodb.com/docs/atlas/atlas-vector-search/vector-search-overview/).

#### 5. Edit your Prompt in serve.py

In the server.py file, you can see that we used the prompt like this. This prompt was enhanced by adding information about your products to it.

```
       f""" Bạn hãy trở thành chuyên gia tu vấn khóa học của Trường Đại Học Công Nghệ Thông Tin, với câu hỏi như sau: \n "{inital_query}."\n
            Và bạn được cung cấp một số thông tin về khóa học như sau: "{info_course_list}"\n
            Hãy tư vấn cho sinh viên.
            Lưu ý, CHỈ TƯ VẤN TRỰC TIẾP, KHÔNG NÓI NHỮNG CÂU NHƯ "DỰA VÀO THÔNG TIN TUI CÓ".
            - Trực triếp trả lời thẳng vào vấn đề.
            """
```

- inital_query: Query from the user.
- info_course_list: Information we get from our database.


#### 5. Run server

```
python server.py
```

#### 6. Start the website

run file "index.html"
