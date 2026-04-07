from langchain_core.tools import tool

# ==========================================
# MOCK DATABASE
# ==========================================
FLIGHTS_DB = {
    ("Hà Nội", "Đà Nẵng"): [
        {"airline": "Vietjet", "time": "08:00", "price": 890000},
        {"airline": "Vietnam Airlines", "time": "10:30", "price": 1450000},
        {"airline": "Bamboo", "time": "14:00", "price": 1150000},
        {"airline": "Vietjet", "time": "19:00", "price": 750000}
    ],
    ("Hà Nội", "Phú Quốc"): [
        {"airline": "Vietjet", "time": "09:00", "price": 1100000},
        {"airline": "Vietnam Airlines", "time": "13:00", "price": 2200000}
    ],
    ("Hồ Chí Minh", "Đà Nẵng"): [
        {"airline": "Bamboo", "time": "07:30", "price": 950000},
        {"airline": "Vietjet", "time": "15:00", "price": 850000}
    ],
    ("Hồ Chí Minh", "Phú Quốc"): [
        {"airline": "Vietnam Airlines", "time": "10:00", "price": 1200000},
        {"airline": "Vietjet", "time": "16:00", "price": 650000}
    ]
}

HOTELS_DB = {
    "Đà Nẵng": [
        {"name": "Muong Thanh Luxury", "stars": 5, "price": 1800000, "area": "Biển Mỹ Khê", "rating": 4.6},
        {"name": "Aria Hotel", "stars": 4, "price": 950000, "area": "Trung tâm", "rating": 4.3},
        {"name": "Sea View Hostel", "stars": 2, "price": 350000, "area": "Biển Mỹ Khê", "rating": 4.0},
        {"name": "Novotel", "stars": 5, "price": 2500000, "area": "Sông Hàn", "rating": 4.8}
    ],
    "Phú Quốc": [
        {"name": "Vinpearl Resort", "stars": 5, "price": 3200000, "area": "Bắc Đảo", "rating": 4.7},
        {"name": "Sunset Sanato", "stars": 4, "price": 1500000, "area": "Bãi Trường", "rating": 4.5},
        {"name": "Blue Ocean Homestay", "stars": 3, "price": 550000, "area": "Dương Đông", "rating": 4.2}
    ],
    "Hà Nội": [
        {"name": "Lotte Hotel", "stars": 5, "price": 2800000, "area": "Ba Đình", "rating": 4.8},
        {"name": "Old Quarter Boutique", "stars": 4, "price": 1200000, "area": "Hoàn Kiếm", "rating": 4.5},
        {"name": "Hanoi Backpackers", "stars": 2, "price": 250000, "area": "Hoàn Kiếm", "rating": 4.1}
    ],
    "Hồ Chí Minh": [
        {"name": "Park Hyatt", "stars": 5, "price": 4500000, "area": "Quận 1", "rating": 4.9},
        {"name": "Liberty Central", "stars": 4, "price": 1600000, "area": "Quận 1", "rating": 4.4},
        {"name": "Bui Vien Hostel", "stars": 2, "price": 200000, "area": "Quận 1", "rating": 3.9}
    ]
}

def format_currency(amount: int) -> str:
    """Hàm hỗ trợ format tiền tệ VNĐ"""
    return f"{amount:,.0f}đ".replace(",", ".")

# ==========================================
# TOOL THỰC THI
# ==========================================

@tool
def search_flights(origin: str, destination: str) -> str:
    """
    Tìm kiếm các chuyến bay giữa hai thành phố.
    Tham số:
    - origin: thành phố khởi hành (VD: 'Hà Nội', 'Hồ Chí Minh')
    - destination: thành phố đến (VD: 'Đà Nẵng', 'Phú Quốc')
    Trả về danh sách chuyến bay với hãng, giờ bay, giá vé.
    Nếu không tìm thấy, trả về thông báo.
    """
    try:
        route = (origin, destination)
        reverse_route = (destination, origin)
        
        flights = FLIGHTS_DB.get(route)
        
        # Nếu không có chiều đi, thử tìm chiều ngược lại
        if not flights:
            flights = FLIGHTS_DB.get(reverse_route)
            if flights:
                return f"Không có chuyến bay thẳng từ {origin} đến {destination}. Nhưng có chiều ngược lại từ {destination} về {origin}."
            return f"Không tìm thấy chuyến bay từ {origin} đến {destination}."

        result = f"Chuyến bay từ {origin} đến {destination}:\n"
        for f in flights:
            result += f"- {f['airline']} | {f['time']} | {format_currency(f['price'])}\n"
        return result
    except Exception as e:
        return f"Lỗi khi tra cứu chuyến bay: {str(e)}"


@tool
def search_hotels(city: str, max_price_per_night: int = 99999999) -> str:
    """
    Tìm kiếm khách sạn tại một thành phố, có thể lọc theo giá tối đa mỗi đêm.
    Tham số:
    - city: tên thành phố (VD: 'Đà Nẵng', 'Phú Quốc', 'Hồ Chí Minh')
    - max_price_per_night: giá tối đa mỗi đêm (VNĐ), mặc định không giới hạn
    Trả về danh sách khách sạn phù hợp với tên, số sao, giá, khu vực, rating.
    """
    try:
        hotels = HOTELS_DB.get(city)
        if not hotels:
            return f"Hiện chưa có dữ liệu khách sạn tại thành phố {city}."

        # Lọc theo giá và sắp xếp theo rating giảm dần
        filtered_hotels = [h for h in hotels if h['price'] <= max_price_per_night]
        sorted_hotels = sorted(filtered_hotels, key=lambda x: x['rating'], reverse=True)

        if not sorted_hotels:
            return f"Không tìm thấy khách sạn tại {city} với giá dưới {format_currency(max_price_per_night)}/đêm. Hãy thử tăng ngân sách."

        result = f"Khách sạn tại {city} (Giá <= {format_currency(max_price_per_night)}/đêm):\n"
        for h in sorted_hotels:
            result += f"- {h['name']} ({h['stars']} sao) | {h['area']} | Rating: {h['rating']} | Giá: {format_currency(h['price'])}/đêm\n"
        return result
    except Exception as e:
        return f"Lỗi khi tra cứu khách sạn: {str(e)}"


@tool
def calculate_budget(total_budget: int, expenses: str) -> str:
    """
    Tính toán ngân sách còn lại sau khi trừ các khoản chi phí.
    Tham số:
    - total_budget: tổng ngân sách ban đầu (VNĐ)
    - expenses: chuỗi mô tả các khoản chi, định dạng 'tên_khoản: số_tiền, tên_khoản: số_tiền'
    """
    try:
        parsed_expenses = {}
        items = expenses.split(',')
        
        # Parse chuỗi thành dictionary
        for item in items:
            if ':' in item:
                name, cost_str = item.split(':')
                parsed_expenses[name.strip()] = int(cost_str.strip())
        
        total_spent = sum(parsed_expenses.values())
        remaining = total_budget - total_spent

        # Tạo bảng kết quả
        result = "Bảng chi phí:\n"
        for name, cost in parsed_expenses.items():
            result += f"- {name.capitalize()}: {format_currency(cost)}\n"
        result += "---\n"
        result += f"Tổng chi: {format_currency(total_spent)}\n"
        result += f"Ngân sách ban đầu: {format_currency(total_budget)}\n"
        
        if remaining >= 0:
            result += f"Còn lại: {format_currency(remaining)}\n"
        else:
            result += f"⚠️ CẢNH BÁO: Vượt ngân sách {format_currency(abs(remaining))}! Cần điều chỉnh lại lựa chọn."
            
        return result
    except ValueError:
        return "Lỗi format expenses. Vui lòng truyền chuỗi đúng định dạng, ví dụ: 'vé_máy_bay: 890000, khách_sạn: 650000'"
    except Exception as e:
        return f"Lỗi khi tính toán ngân sách: {str(e)}"