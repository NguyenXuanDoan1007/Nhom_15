import socket
import json

# --- CẤU HÌNH CLIENT ---
HOST = '127.0.0.1'
PORT = 8888
BUFFER_SIZE = 1024

def display_seat_status(seats_list):
    """Hiển thị trạng thái ghế một cách trực quan."""
    print("\n--- TRẠNG THÁI GHẾ ---")
    seat_map = ""
    for i, is_available in enumerate(seats_list):
        status = " (Trống) " if is_available else " [ĐÃ ĐẶT]"
        seat_map += f"| Ghế {i+1}{status}"
        if (i + 1) % 5 == 0: # Xuống dòng sau mỗi 5 ghế
            seat_map += " |\n"
    print(seat_map)
    print("----------------------\n")


def start_client():
    """Khởi động Client và giao tiếp với Server."""
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((HOST, PORT))
        print(f"*** CLIENT ĐÃ KẾT NỐI VỚI SERVER tại {HOST}:{PORT} ***")
        
        while True:
            # Giao diện người dùng
            print("\n--- MENU ---")
            print("1. Xem danh sách phim (get)")
            print("2. Đặt vé (book)")
            print("3. Thoát (quit)")
            choice = input("Nhập lựa chọn (1/2/3): ").strip().lower()
            
            request = ""
            
            if choice == '1' or choice == 'get':
                request = "GET_MOVIES"
            
            elif choice == '2' or choice == 'book':
                # BƯỚC 1: Yêu cầu xem phim và suất chiếu
                client.sendall("GET_MOVIES".encode('utf-8'))
                response = client.recv(BUFFER_SIZE).decode('utf-8')
                
                try:
                    movies_info = json.loads(response)
                    print("\nDANH SÁCH PHIM:")
                    for movie, times in movies_info.items():
                        print(f" - Phim: {movie:<30} | Suất chiếu: {', '.join(times)}")
                    
                    # BƯỚC 2: Người dùng chọn phim và suất
                    movie_choice = input("Nhập tên phim muốn xem: ").strip()
                    time_choice = input("Nhập suất chiếu: ").strip()
                    
                    if movie_choice and time_choice:
                        # BƯỚC 3: Yêu cầu trạng thái ghế
                        request = f"GET_SEATS|{movie_choice}|{time_choice}"
                        client.sendall(request.encode('utf-8'))
                        
                        seat_response = client.recv(BUFFER_SIZE).decode('utf-8')
                        
                        if seat_response.startswith("ERROR"):
                            print(f"[LỖI] {seat_response}")
                            continue

                        # Hiển thị trạng thái ghế
                        seat_data = json.loads(seat_response)
                        display_seat_status(seat_data['seats'])
                        
                        # BƯỚC 4: Người dùng chọn ghế
                        seat_number_input = input("Nhập số ghế bạn muốn đặt (1,2,3): ").strip()
                        if seat_number_input:
                            request = f"BOOK_SEAT|{movie_choice}|{time_choice}|{seat_number_input}"
                        else:
                            print("[LỖI] Lựa chọn ghế không hợp lệ.")
                            continue
                        
                except json.JSONDecodeError:
                    print(f"[LỖI PHẢN HỒI] Không thể phân tích dữ liệu phim: {response}")
                    continue
                
            elif choice == '3' or choice == 'quit':
                request = "QUIT"
            
            else:
                print("[CẢNH BÁO] Lựa chọn không hợp lệ.")
                continue

            # Gửi yêu cầu cuối cùng (hoặc lệnh thoát)
            client.sendall(request.encode('utf-8'))
            if request != "QUIT":
                final_response = client.recv(BUFFER_SIZE).decode('utf-8')
                print(f"[SERVER PHẢN HỒI] {final_response}")
            
            if request == "QUIT":
                print("Đã ngắt kết nối với Server.")
                break

    except ConnectionRefusedError:
        print(f"[LỖI] Không thể kết nối. Vui lòng đảm bảo Server ({HOST}:{PORT}) đang chạy.")
    except Exception as e:
        print(f"[LỖI CHUNG] {e}")
    finally:
        client.close()

if __name__ == "__main__":
    start_client()