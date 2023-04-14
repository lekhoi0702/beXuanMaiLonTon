import socket
import struct
import tkinter as tk
from tkinter import messagebox
import threading
# Hàm gửi dữ liệu
def send_data():
    # Lấy địa chỉ multicast group, port, và dữ liệu từ giao diện người dùng
    group = group_entry.get()
    port = port_entry.get()
    data = data_entry.get()

    try:
        # Kiểm tra tính hợp lệ của địa chỉ multicast group và port
        socket.inet_aton(group)
        port = int(port)
    except (socket.error, ValueError):
        messagebox.showerror("Lỗi", "Địa chỉ multicast group hoặc port không hợp lệ!")
        return

    # Tạo socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)

    # Gửi dữ liệu qua multicast
    sock.sendto(data.encode(), (group, port))


# Khởi tạo biến đánh dấu trạng thái của việc nhận dữ liệu
receiving = False
# Khai báo biến global sock để lưu socket
sock = None
# Hàm nhận dữ liệu
def start_receiver():
    global receiving
    global sock
    # Tạo socket và thực hiện các thao tác cấu hình kết nối
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Kiểm tra nếu đang nhận dữ liệu thì không cho bắt đầu nhận mới
    if receiving:
        messagebox.showinfo("Thông báo", "Đang trong quá trình nhận dữ liệu!")
        return
    # Lấy địa chỉ multicast group và port từ giao diện người dùng
    group = group_entry.get()
    port = port_entry.get()

    try:
        # Kiểm tra tính hợp lệ của địa chỉ multicast group và port
        socket.inet_aton(group)
        port = int(port)
    except (socket.error, ValueError):
        messagebox.showerror("Lỗi", "Địa chỉ multicast group hoặc port không hợp lệ!")
        return

    # Tạo socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Bind địa chỉ và port cho socket
    sock.bind(('', port))

    # Chuyển đổi địa chỉ multicast group sang dạng binary
    mreq = struct.pack("4sl", socket.inet_aton(group), socket.INADDR_ANY)

    # Tham gia vào multicast group
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    # Cập nhật trạng thái của biến receiving
    receiving = True

    # Hàm xử lý đa luồng để nhận dữ liệu từ multicast group
    def receive_data():
        global receiving, sock
        while receiving:
            # Nhận dữ liệu từ multicast group
            data, addr = sock.recvfrom(10240)
            # Sử dụng hàm insert của giao diện đồ họa để thêm dữ liệu vào Text widget
            message_text.insert(tk.END, data.decode())

    # Tạo một thread mới để chạy hàm receive_data()
    receiver_thread = threading.Thread(target=receive_data)
    # Đánh dấu thread là daemon, để khi chương trình chạy xong, thread này cũng sẽ tự động kết thúc
    receiver_thread.daemon = True
    # Bắt đầu chạy thread
    receiver_thread.start()


# Hàm dừng nhận dữ liệu
def stop_receive():
    global receiving, sock
    if receiving:
        receiving = False
        # Thông báo đã dừng nhận dữ liệu
        messagebox.showinfo("Thông báo", "Đã dừng nhận dữ liệu!")
        # Đóng socket để kết thúc việc nhận dữ liệu ngay lập tức
        sock.close()
# Tạo giao diện đồ họa
root = tk.Tk()
root.title("Multicast App")

# Tạo các thành phần giao diện
group_label = tk.Label(root, text="Địa chỉ multicast group:")
group_label.pack()
group_entry = tk.Entry(root)
group_entry.pack()

port_label = tk.Label(root, text="Port:")
port_label.pack()
port_entry = tk.Entry(root)
port_entry.pack()

data_label = tk.Label(root, text="Nội dung dữ liệu:")
data_label.pack()
data_entry = tk.Entry(root)
data_entry.pack()

send_button = tk.Button(root, text="Gửi", command=send_data)
send_button.pack()

start_button = tk.Button(root, text="Bắt đầu nhận", command=start_receiver)
start_button.pack()

message_label = tk.Label(root, text="Dữ liệu nhận được:")
message_label.pack()
message_text = tk.Text(root)
message_text.pack()


stop_button = tk.Button(root, text="Ngừng nhận", command=stop_receive)
stop_button.pack()

root.mainloop()
