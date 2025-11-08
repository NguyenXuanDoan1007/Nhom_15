import socket
import threading
import json
import time

# --- CẤU HÌNH SERVER VÀ DỮ LIỆU ---
HOST = '127.0.0.1'  # Địa chỉ IP nội bộ
PORT = 8888         # Cổng kết nối
BUFFER_SIZE = 1024

# Dữ liệu vé (True = Ghế trống, False = Đã đặt)
# Sử dụng tên phim không dấu và khớp với dữ liệu bạn cung cấp.
BOOKING_DATA = {
    "Bo Tu Bao Thu": {
        "10:00": [True, True, True, True, True], # Ghế 5 đã đặt
        "14:00": [True, True, True, True, True] 
    },
    
    "Cuc Vang Cua Ngoai": {
        "18:30": [True, True, True, True, True],
        "20:30": [True, True, True, True, True]
    },
    
    "Spider-Man": {
        "18:00": [True, True, True, True, True],
        "21:00": [True, True, True, True, True] # Ghế 1 đã đặt
    }
}

def handle_client(client_socket):
    """Xử lý các yêu cầu từ Client."""
    print(f"[SERVER] Client đã kết nối từ: {client_socket.getpeername()}")
    
    try:
        while True:
            # Nhận dữ liệu từ client
            request_data = client_socket.recv(BUFFER_SIZE).decode('utf-8')
            if not request_data:
                break

            print(f"[SERVER] Nhận yêu cầu: {request_data}")
            response = process_request(request_data)
            
            # Gửi phản hồi lại client
            client_socket.sendall(response.encode('utf-8'))
            
            # Nếu lệnh là QUIT, ngắt kết nối
            if request_data == "QUIT":
                break

    except ConnectionResetError:
        print("[SERVER] Client ngắt kết nối đột ngột.")
    except Exception as e:
        print(f"[SERVER] Lỗi xử lý Client: {e}")
    finally:
        client_socket.close()
        print(f"[SERVER] Đóng kết nối với Client.")


def process_request(request):
    """Phân tích yêu cầu và trả về phản hồi."""
    # Sửa lỗi: Dùng | làm ký tự phân tách lệnh
    parts = request.split('|') 
    command = parts[0]
    
    if command == "GET_MOVIES":
        # Trả về danh sách phim và suất chiếu (dưới dạng JSON)
        movies_info = {
            movie: list(showtimes.keys())
            for movie, showtimes in BOOKING_DATA.items()
        }
        return json.dumps(movies_info)

    elif command == "GET_SEATS" and len(parts) == 3:
        # Cú pháp: GET_SEATS|Tên Phim|Suất Chiếu
        movie_title = parts[1]
        showtime = parts[2]
        
        if movie_title in BOOKING_DATA and showtime in BOOKING_DATA[movie_title]:
            seats = BOOKING_DATA[movie_title][showtime]
            # Trả về trạng thái ghế và tổng số ghế
            return json.dumps({"seats": seats, "total": len(seats)})
        else:
            return "ERROR: Phim hoặc suất chiếu không hợp lệ."

    # LOGIC ĐẶT NHIỀU GHẾ ĐÃ ĐƯỢC CẬP NHẬT
    elif command == "BOOK_SEAT" and len(parts) == 4:
        # Cú pháp: BOOK_SEAT|Tên Phim|Suất Chiếu|Số Ghế 1,2,3...
        movie_title = parts[1]
        showtime = parts[2]
        seats_to_book_str = parts[3] # Chuỗi số ghế: "1,2,5"

        # Chia chuỗi số ghế thành danh sách các số ghế hợp lệ
        seat_numbers = [s.strip() for s in seats_to_book_str.split(',') if s.strip().isdigit()]

        if not seat_numbers:
            return "ERROR: Không tìm thấy số ghế hợp lệ nào để đặt."

        # Danh sách kết quả để trả về Client
        booking_results = []
        
        if movie_title in BOOKING_DATA and showtime in BOOKING_DATA[movie_title]:
            available_seats = BOOKING_DATA[movie_title][showtime]
            
            for seat_num_str in seat_numbers:
                try:
                    # Chuyển từ số ghế (1, 2, 3...) sang index (0, 1, 2...)
                    seat_index = int(seat_num_str) - 1 
                except ValueError:
                    booking_results.append(f"Ghế {seat_num_str} (Lỗi định dạng)")
                    continue

                if 0 <= seat_index < len(available_seats):
                    if available_seats[seat_index] is True:
                        # Đặt ghế và cập nhật trạng thái
                        BOOKING_DATA[movie_title][showtime][seat_index] = False
                        booking_results.append(f"Ghế {seat_num_str} (THÀNH CÔNG)")
                    else:
                        booking_results.append(f"Ghế {seat_num_str} (ĐÃ ĐẶT)")
                else:
                    booking_results.append(f"Ghế {seat_num_str} (Ngoại phạm vi)")
            
            # Ghi log và trả về kết quả
            log_message = f"[BOOKING] Kết quả đặt vé cho {movie_title} - {showtime}: {', '.join(booking_results)}"
            print(log_message)
            return f"SUCCESS: Kết quả đặt vé: {', '.join(booking_results)}"

        else:
            return "ERROR: Phim hoặc suất chiếu không hợp lệ."
            
    elif command == "QUIT":
        return "QUITTING"
    
    else:
        return "ERROR: Lệnh không xác định. Vui lòng thử GET_MOVIES."


def start_server():
    """Khởi động Server."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.bind((HOST, PORT))
        server.listen(5)
        print(f"*** SERVER ĐÃ KHỞI ĐỘNG ***")
        print(f"Lắng nghe tại {HOST}:{PORT}")
        
        while True:
            client_socket, addr = server.accept()
            # Sử dụng luồng (thread) để xử lý nhiều client đồng thời
            client_handler = threading.Thread(target=handle_client, args=(client_socket,))
            client_handler.start()

    except Exception as e:
        print(f"Lỗi khởi động Server: {e}")
    finally:
        server.close()

if __name__ == "__main__":
    start_server()