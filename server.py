import socket
import threading
import json
import time

# --- CẤU HÌNH SERVER VÀ DỮ LIỆU ---
HOST = '127.0.0.1'  # Địa chỉ IP nội bộ
PORT = 8888         # Cổng kết nối
BUFFER_SIZE = 1024

# Dữ liệu vé (True = Ghế trống, False = Đã đặt)
BOOKING_DATA = {
    "Avengers: Endgame": {
        "10:00": [True, True, True, True, False], # Ghế 5 đã đặt
        "14:00": [True, True, True, True, True] 
    },
    "Spider-Man: No Way Home": {
        "18:00": [True, True, True, True, True],
        "21:00": [False, True, True, True, True] # Ghế 1 đã đặt
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
    parts = request.split(':')
    command = parts[0]
    
    if command == "GET_MOVIES":
        # Trả về danh sách phim và suất chiếu (dưới dạng JSON)
        movies_info = {
            movie: list(showtimes.keys())
            for movie, showtimes in BOOKING_DATA.items()
        }
        return json.dumps(movies_info)

    elif command == "GET_SEATS" and len(parts) == 3:
        # Cú pháp: GET_SEATS:Tên Phim:Suất Chiếu
        movie_title = parts[1]
        showtime = parts[2]
        
        if movie_title in BOOKING_DATA and showtime in BOOKING_DATA[movie_title]:
            seats = BOOKING_DATA[movie_title][showtime]
            # Trả về trạng thái ghế và tổng số ghế
            return json.dumps({"seats": seats, "total": len(seats)})
        else:
            return "ERROR: Phim hoặc suất chiếu không hợp lệ."

    elif command == "BOOK_SEAT" and len(parts) == 4:
        # Cú pháp: BOOK_SEAT:Tên Phim:Suất Chiếu:Số Ghế (Index từ 1)
        movie_title = parts[1]
        showtime = parts[2]
        try:
            seat_index = int(parts[3]) - 1 # Chuyển từ số ghế (1, 2, 3...) sang index (0, 1, 2...)
        except ValueError:
            return "ERROR: Số ghế không hợp lệ."

        if movie_title in BOOKING_DATA and showtime in BOOKING_DATA[movie_title]:
            seats = BOOKING_DATA[movie_title][showtime]
            
            if 0 <= seat_index < len(seats):
                if seats[seat_index] is True:
                    # Cập nhật trạng thái đặt vé
                    BOOKING_DATA[movie_title][showtime][seat_index] = False
                    print(f"[BOOKING] Đã đặt thành công: {movie_title} - {showtime} - Ghế {seat_index + 1}")
                    return f"SUCCESS: Đã đặt thành công ghế {seat_index + 1} cho phim {movie_title}."
                else:
                    return f"ERROR: Ghế {seat_index + 1} đã có người đặt."
            else:
                return "ERROR: Số ghế nằm ngoài phạm vi."
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