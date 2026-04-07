# BÁO CÁO KẾT QUẢ KIỂM THỬ - TRAVELBUDDY AGENT
**Họ và tên:** Nguyễn Thị Hương Giang 
**MSSV:** 2A202600485
**Mô hình sử dụng:** Gemini-2.0-Flash (Google AI Studio)  
**Framework:** LangGraph + LangChain  

---

## 1. Danh sách Test Cases

### Test 1: Direct Answer (Chào hỏi & Điều hướng)
* **User:** "Xin chào! Tôi đang muốn đi du lịch nhưng chưa biết đi đâu"
* **Log hệ thống:**
    ```text
    TravelBuddy đang suy nghĩ...
       [ACTION] Trả lời trực tiếp
    ```
* **Kết quả:** Agent chào hỏi thân thiện và liệt kê 4 thông tin cần thiết (Nơi đi, Nơi đến, Ngân sách, Thời gian) theo đúng quy định trong `system_prompt.txt`.

---

### Test 2: Single Tool Call (Tra cứu chuyến bay)
* **User:** "Tìm giúp tôi chuyến bay đi từ Hà Nội đến Đà Nẵng"
* **Log hệ thống:**
    ```text
    TravelBuddy đang suy nghĩ...
       [ACTION] Gọi tool: search_flights ({'origin': 'Hà Nội', 'destination': 'Đà Nẵng'})
       [ACTION] Trả lời trực tiếp
    ```
* **Kết quả:** Agent nhận diện đúng điểm đi/đến, gọi tool thành công và liệt kê đủ danh sách các hãng bay kèm giá tiền từ database.

---

### Test 3: Multi-Step Tool Chaining (Lập kế hoạch phức hợp)
* **User:** "Tôi ở Hà Nội, muốn đi Phú Quốc 2 đêm, budget 5 triệu. Tư vấn giúp!"
* **Log hệ thống:**
    ```text
    TravelBuddy đang suy nghĩ...
       [ACTION] Gọi tool: search_flights ({'origin': 'Hà Nội', 'destination': 'Phú Quốc'})
       [ACTION] Gọi tool: search_hotels ({'max_price_per_night': 900000, 'city': 'Phú Quốc'})
       [ACTION] Gọi tool: calculate_budget ({'total_budget': 5000000, 'expenses': 'Vé máy bay khứ hồi Vietjet: 2200000, Khách sạn 2 đêm: 1100000, Ăn uống và đi lại dự kiến: 1700000'})
       [ACTION] Trả lời trực tiếp
    ```
* **Kết quả:** - Agent tự hiểu cần tìm vé máy bay trước.
    - Tự động trừ chi phí vé máy bay để tính ra `max_price_per_night` cho khách sạn.
    - Gọi tool tính toán ngân sách để đảm bảo không vượt quá 5 triệu.
    - Phản hồi đầy đủ các mục: Chuyến bay, Khách sạn, Tổng chi phí, Gợi ý thêm.

---

### Test 4: Missing Information (Hỏi lại khi thiếu thông tin)
* **User:** "Tôi muốn đặt khách sạn"
* **Log hệ thống:**
    ```text
    TravelBuddy đang suy nghĩ...
       [ACTION] Trả lời trực tiếp
    ```
* **Kết quả:** Agent không gọi tool bừa bãi khi chưa biết điểm đến. Nó thực hiện đúng `Rule #2` là yêu cầu người dùng cung cấp thêm thông tin để có thể tra cứu chính xác.

---

### Test 5: Guardrail / Refusal (Chặn yêu cầu không liên quan)
* **User:** "Giải giúp tôi bài tập lập tình về linked list"
* **Log hệ thống:**
    ```text
    TravelBuddy đang suy nghĩ...
       [ACTION] Trả lời trực tiếp
    ```
* **Kết quả:** Agent từ chối lịch sự và khẳng định vai trò là trợ lý du lịch theo đúng nội dung trong phần `<constraints>` của System Prompt.

---

## 2. Nhận xét về hoạt động của Agent
1.  **Khả năng suy luận (Reasoning):** Agent sử dụng Gemini-2.0-Flash có khả năng xử lý logic "multi-hop" rất tốt, biết kết quả của tool này để làm đầu vào cho tool kia.
2.  **Tính tuân thủ (Instruction Following):** Agent bám sát Persona, không bị lạc đề và giữ đúng định dạng JSON/Text yêu cầu.
3.  **Xử lý lỗi:** Hệ thống ổn định, không xảy ra lỗi crash khi người dùng nhập dữ liệu thiếu hoặc yêu cầu sai chuyên môn.