class Reflection():
    def __init__(self, llm, history_limit=100):
        self.llm = llm
        self.chat_history = []  # Lưu lịch sử hội thoại
        self.history_limit = history_limit  # Giới hạn số lượng tin nhắn lưu lại

    def clear_histories(self):
        self.chat_history.clear()

    def format_chat_data(self):
        formatted_text = ""

        for message in self.chat_history:
            role = message['role']
            # Duyệt tất cả content nếu có nhiều phần
            for part in message['content']:
                if part['type'] == 'text':
                    text = part['text']
                    formatted_text += f"{role}: {text}\n"
        return formatted_text.strip()


    def _get_relevant_context(self, query):
        """Kiểm tra xem query có liên quan đến lịch sử hội thoại không."""
        if not self.chat_history:
            return query  # Nếu chưa có lịch sử, trả về query gốc
        
        histories_convertString = self.format_chat_data()

        higherLevelSummariesPrompt = f""" Với lịch sử trò chuyện : "{histories_convertString}"
        
        và câu hỏi mới nhất của người dùng: "{query}" 
        hãy tham chiếu đến ngữ cảnh trong lịch sử trò chuyện, hãy xây dựng một câu độc lập có thể hiểu được mà không cần lịch sử trò chuyện.
        KHÔNG trả lời câu hỏi, chỉ cần định dạng lại câu hỏi nếu cần và nếu không liên quan đến ngữ cảnh hiện tại thì trả về nguyên trạng.
        Hãy chỉ trả về câu hỏi, không giải thích gì thêm.
        """

        print("++++++++++++++++++++REFLECTION++++++++++++++++++++++++\n", higherLevelSummariesPrompt)
        completion = self.llm.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": higherLevelSummariesPrompt}]
        )
        print("@@@@@ REFECTION OUTPUT",completion.choices[0].message.content)
        return completion.choices[0].message.content

    def __call__(self, chatHistory):
        """Xử lý query mới, cập nhật lịch sử hội thoại và kiểm tra ngữ cảnh."""
        
        # ✅ Thêm vào lịch sử chat thay vì ghi đè
        self.chat_history.extend(chatHistory)

        # ✅ Giới hạn số lượng tin nhắn được lưu
        self.chat_history = self.chat_history[-self.history_limit:]

        # # ✅ Lấy câu hỏi mới nhất
        last_message = chatHistory[-1]["content"][0]["text"]

        # ✅ Reformulate query dựa trên lịch sử hội thoại
        reformulated_query = self._get_relevant_context(last_message)

        return reformulated_query