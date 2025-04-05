class SemanticRouter():
    def __init__(self, llm):
        self.llm = llm  # Lưu LLM của OpenAI

    def guide(self, query):
        prompt = f"""
        Người dùng vừa nhập: "{query}"

        Nhiệm vụ của bạn:
        - Xác định xem câu người dùng vừa nhập có liên quan đến các khóa học về công nghệ thông tin và và khóa học về tiếng anh hay không.
        - Nếu **có liên quan**, trả về **chính xác cụm từ "course"**.
        - Nếu **không liên quan**, trả về **chính xác cụm từ "chatchit"**.
        - Chỉ trả về một trong hai cụm từ trên, không giải thích thêm.
        Lưu ý quan trọng:
        - Một câu có vẻ không liên quan đến khóa học nhưng nếu đề cập đến **mã môn học** (VÍ DỤ: "Mã môn DS102 là gì?" hoặc "MSH203") thì vẫn được coi là liên quan đến khóa học.
        """
        # print("*************************ROUTER*********************************\n: ", prompt)
        response = self.llm.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )

        print("OUTPUT ROUTER: ", response.choices[0].message.content.strip())
        return response.choices[0].message.content.strip()
