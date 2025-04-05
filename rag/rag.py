import pymongo
from sentence_transformers import SentenceTransformer
from rapidfuzz import process
import re

def clean_query(user_query):
    # Loại bỏ từ "và" và các dấu câu
    cleaned_query = re.sub(r'[.,;!?()""\']|và |với ', '', user_query)
    # Loại bỏ khoảng trắng thừa
    cleaned_query = re.sub(r'\s+', ' ', cleaned_query).strip()
    return cleaned_query

def extract_ma_mon_hoc(user_query):
    """
    Tìm mã môn học từ câu hỏi của người dùng. Mã môn học có dạng 2-5 chữ cái + 3-4 số
    """

    pattern = r"\b[A-Z]{2,}\d{2,}[A-Z]?\b"
    result =  re.findall(pattern, user_query.upper())

    if result:
        # Sao chép chuỗi ban đầu
        modified_query = user_query
        # Xóa tất cả các mã môn học trong chuỗi
        for ma in result:
            modified_query = modified_query.replace(ma, "")

        modified_query = clean_query(modified_query)
        return result, modified_query
    
    return [], user_query


def extract_course_name_fuzzy(user_query, all_course_names, threshold=90, top_n=5):
    """
    Tìm tên môn học gần đúng dựa vào độ tương đồng (fuzzy matching),
    sắp xếp theo độ tương đồng giảm dần và trả về top_n kết quả.
    """
    found = []
    
    for name in all_course_names:
        match = process.extractOne(user_query, [name])
        if match and match[1] >= threshold:  # Nếu độ tương đồng lớn hơn threshold
            found.append((name, match[1]))  # Lưu tên môn học và độ tương đồng
    
    # Sắp xếp theo độ tương đồng giảm dần và lấy top_n kết quả
    found.sort(key=lambda x: x[1], reverse=True)
    
    result = [(course[0], course[1]) for course in found[:top_n]]
    
    # In kết quả
    for course, score in result:
        print(f"Course: {course}, Score: {score}")
    
    # Trả về danh sách tên môn học
    return [course[0] for course in result]


def get_courses_by_ma_mh(ma_mh_list, collection):
    """
    Tìm các môn học trong MongoDB dựa vào danh sách mã môn học
    """
    return list(collection.find({"Mã MH": {"$in": ma_mh_list}}, {"_id": 0}))

def get_courses_by_name(name_list, collection):
    """
    Tìm các môn học trong MongoDB dựa vào danh sách tên môn học
    """
    return list(collection.find({"Tên MH": {"$in": name_list}}, {"_id": 0}))

def semanticSearch(user_query, collection, embedding_model, threshold=0.5):
    """
    Tìm kiếm các môn học thông qua vector search
    """
    query_embedding = embedding_model.encode([user_query])[0].tolist()
    pipeline = [
        {
            "$vectorSearch": {
                "queryVector": query_embedding,
                "path": "embedding",
                "numCandidates": 100,
                "limit": 5,
                "index": "vector_index"
            }
        },
        {
            "$project": {
                "Mã MH": 1,
                "Tên MH": 1,
                "Tóm tắt môn học": 1,
                "score": {"$meta": "vectorSearchScore"}
            }
        }
    ]
    results = list(collection.aggregate(pipeline))
    # Lọc kết quả theo threshold
    filtered_results = [result for result in results if result.get('score', 0) >= threshold]
    return filtered_results


class RAG():
    def __init__(self,
                 mongodbUrl,
                 dbName,
                 dbCollection,
                 llm,
                 limitReturn,
                 modelEmbeddingName):
        self.client = pymongo.MongoClient(mongodbUrl)
        self.db = self.client[dbName] 
        self.collection = self.db[dbCollection]
        self.embedding_model = SentenceTransformer(modelEmbeddingName)
        self.llm = llm
        self.limitReturn = limitReturn


    def get_all_course_names(self):
        return [doc["Tên MH"] for doc in self.collection.find({}, {"Tên MH": 1})]

    def enhance_prompt(self, user_query):

        all_course_names = self.get_all_course_names()

        # Bước 1: Tìm mã môn học trong câu hỏi
        ma_mh_list, user_query = extract_ma_mon_hoc(user_query)
        # print(user_query)
        found_courses = []

        if ma_mh_list:
            print("Vào tìm Mã MH")
            # Tìm môn học theo mã môn học
            results_by_ma = get_courses_by_ma_mh(ma_mh_list, self.collection)
            found_courses.extend(results_by_ma)

        # Bước 2: Tìm tên môn học gần đúng (fuzzy matching)
        found_names = extract_course_name_fuzzy(user_query, all_course_names, threshold=88, top_n=5)
        if found_names:
            print("Vào Tìm Tên MH")
            # Tìm môn học theo tên môn học gần đúng
            results_by_name = get_courses_by_name(found_names, self.collection)
            found_courses.extend(results_by_name)

        # Bước 3: Fallback – Semantic search nếu không tìm được
        if not found_courses:
            print("Không tìm thấy mã hoặc tên rõ ràng. Đang sử dụng vector search...")
            results_by_vector = semanticSearch(user_query, self.collection, self.embedding_model, threshold=0.5)
            found_courses.extend(results_by_vector)

        # In kết quả tìm kiếm
        if found_courses:
            for r in found_courses:
                print(f" {r['Tên MH']} ({r['Mã MH']})")
                print(f" {r['Tóm tắt môn học']}\n")
        else:
            print(" Không tìm thấy kết quả!")

        # Trả về danh sách với chỉ các thuộc tính cần thiết
        found_courses_filtered = [{"Tên MH": r['Tên MH'], "Mã MH": r['Mã MH'], "Tóm tắt môn học": r['Tóm tắt môn học']} for r in found_courses]
        return found_courses_filtered
    
    def query_lower(self, text):
        return text.lower()
    
    def generate_content(self, prompt):
        return self.llm.invoke(prompt)
    