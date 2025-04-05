from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from rag.rag import RAG
from reflection.reflection import Reflection
from langchain_openai import ChatOpenAI
from router import SemanticRouter
from langchain_community.tools.tavily_search import TavilySearchResults
import os
import openai
from dotenv import load_dotenv

load_dotenv()

os.environ["TAVILY_API_KEY"] = os.getenv("TAVILY_API_KEY")
tavily_search = TavilySearchResults(max_results=3)
mongodbUrl = os.getenv("MONGODB_URL")
dbName = os.getenv("DB_NAME")
dbCollection = os.getenv("DB_COLLECTION")
API_KEY = os.getenv("OPENAI_API_KEY")
llm = ChatOpenAI(api_key=API_KEY)
limitReturn = 5  ### Number of results return from semantic search.
modelEmbeddingName = os.getenv("MODEL_EMBEDDING")

rag = RAG(
        mongodbUrl = mongodbUrl,
        dbName = dbName,
        dbCollection = dbCollection,
        llm = llm,
        limitReturn = limitReturn,
        modelEmbeddingName = modelEmbeddingName
)

## semantic router
gpt = openai.OpenAI(api_key=API_KEY)
semanticRouter = SemanticRouter(llm=gpt)

### reflection
reflection = Reflection(llm=gpt)
# Flask Server Backend
app = Flask(__name__)

# Apply Flask CORS
CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route('/add', methods=['POST'])
@cross_origin(origin='*')

def handle_query():
    data = list(request.get_json())
    query = data[-1]["content"][0]["text"]
    inital_query = rag.query_lower(query)

    if not inital_query:
        return jsonify({'error': 'No query provided'}), 400

    reflect_query = reflection(data)
    query = reflect_query
    print("inital_query>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>: ", inital_query)
    print("query>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>: ", query)
    data.append({
        "role": "user",
        "content": [
            {   
                "type": "text",
                "text": inital_query,
            }
        ]
    })

    guidedRoute = semanticRouter.guide(query)  # Truy vấn semantic router


    if guidedRoute == "course":

        info_course_list = rag.enhance_prompt(query)

        if info_course_list: ### DB
            
            prompt = f""" Bạn hãy trở thành chuyên gia tu vấn khóa học của Trường Đại Học Công Nghệ Thông Tin, với câu hỏi như sau: \n "{inital_query}."\n
            Và bạn được cung cấp một số thông tin về khóa học như sau: "{info_course_list}"\n
            Hãy tư vấn cho sinh viên.
         
            Lưu ý, CHỈ TƯ VẤN TRỰC TIẾP, KHÔNG NÓI NHỮNG CÂU NHƯ "DỰA VÀO THÔNG TIN TUI CÓ".
            - Trực triếp trả lời thẳng vào vấn đề.
            """

            response = rag.generate_content(prompt)
            model_response = response.content
            # print("model_response: >>>>>>>>>>>>>>>>>>>>>>", model_response)

        else:  ## Search
            result_tavily = tavily_search.run(query)
            # Kiểm tra kết quả trả về
            if not result_tavily or len(result_tavily) == 0:
                return jsonify({
                    'content': [
                        {
                            "type": "text",
                            'text': "Xin lỗi, tôi không tìm thấy thông tin phù hợp trên Internet.",
                        }
                    ],
                    'role': 'model'
                })

            # Nếu Tavily có dữ liệu, xử lý và hiển thị kết quả
            model_response = "\n\n".join([
                f"🔎 **{item['title']}**\n{item['url']}\n📌 {item['content']}"
                for item in result_tavily
            ])
            return jsonify({
                    'content': [
                        {
                            "type": "text",
                            'text': model_response,
                        }
                    ],
                    'role': 'model'
                })

    else:  ### "LLMs"

        chatchit_query = f"""
                Bạn là trợ lý ảo của Trường Đại học Công nghệ Thông tin, tên là Đậu Đậu. 
                Vai trò của bạn là hỗ trợ và trò chuyện thân thiện với sinh viên trong mọi tình huống học tập, hành chính hoặc đời sống sinh viên. 
                Hãy phản hồi dựa trên nội dung sau từ sinh viên:

                "{inital_query}"
                """
        print("chatchit_query: >>>>>>>>>>>>>>>>>>>>>>>>>>>", chatchit_query)
        response = llm.invoke(chatchit_query)
        model_response = response.content
        
    return jsonify({
        'content': [
            {
                "type": "text",
                'text': model_response,
            }
        ],
        'role': 'model'
        })

@app.post("/reset")
def reset_session():
    reflection.clear_histories()
    print("CLEAR HISTORIES")
    return {"message": "Đã reset"}


if __name__ == '__main__':
    app.run(host='0.0.0.0', port='6868') 