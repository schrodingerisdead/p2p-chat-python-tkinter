import socket
import threading
import pickle
import struct
from tkinter import Tk, Label, Button, Entry, filedialog, Frame, Toplevel, END
from tkinter.scrolledtext import ScrolledText
from PIL import Image, ImageTk
import os

# Global user profile picture variable
user_pfp = None
user_pfp_data = None

# Emoji paths (you can add more emojis as needed)
emoji_folder = "emojis"
emoji_files = [
    "u0001f4a9.png", "u0001f4af.png", "u0001f44a.png", "u0001f44c.png",
    "u0001f44d.png", "u0001f60d.png", "u0001f60e.png", "u0001f60f.png",
    "u0001f61b.png", "u0001f61d.png", "u0001f64f.png", "u0001f495.png",
    "u0001f496.png", "u0001f600.png", "u0001f602.png", "u0001f603.png",
    "u0001f605.png", "u0001f610.png", "u0001f618.png", "u0001f621.png",
    "u0001f624.png", "u0001f631.png", "u0001f632.png", "u0001f634.png",
    "u0001f637.png", "u0001f642.png", "u0001f920.png", "u0001f923.png",
    "u0001f928.png"
]

# Function to select a profile picture
def select_pfp():
    global user_pfp, user_pfp_data
    file_path = filedialog.askopenfilename()
    if file_path:
        user_pfp = Image.open(file_path)
        user_pfp = user_pfp.resize((50, 50), Image.Resampling.LANCZOS)
        user_pfp_data = pickle.dumps(user_pfp)

        display_pfp = ImageTk.PhotoImage(user_pfp)
        pfp_label.config(image=display_pfp)
        pfp_label.image = display_pfp

# Handle client messages
def handle_client(client_socket, is_server):
    while True:
        try:
            message_length = client_socket.recv(4)
            if not message_length:
                break
            length = struct.unpack('i', message_length)[0]
            data = client_socket.recv(length)
            message_data = pickle.loads(data)

            pfp_data = message_data['pfp']
            if message_data.get('is_image'):
                image_data = message_data['image']
                display_message(pfp_data, image_data, is_server, is_image=True)
            elif message_data.get('emoji'):
                emoji_file = message_data['emoji']
                display_message(pfp_data, emoji_file, is_server, is_emoji=True)
            else:
                message_text = message_data['text']
                display_message(pfp_data, message_text, is_server)
        except Exception as e:
            print(f"Error receiving message: {e}")
            break

# Display message function (updated to handle both emoji and normal messages)
def display_message(pfp_data, content, is_server, is_image=False, is_emoji=False):
    message_frame = Frame(chat_area)
    message_frame.pack(fill="x", pady=2)

    pfp_image = ImageTk.PhotoImage(pickle.loads(pfp_data))
    pfp_label = Label(message_frame, image=pfp_image)
    pfp_label.image = pfp_image
    pfp_label.pack(side="left", padx=5)

    if is_image:
        # Displaying an image
        image = Image.open(content)
        image = image.resize((100, 100), Image.Resampling.LANCZOS)
        image_tk = ImageTk.PhotoImage(image)
        content_label = Label(message_frame, image=image_tk)
        content_label.image = image_tk
    elif is_emoji:
        # Displaying an emoji image
        emoji_image = Image.open(content)
        emoji_image = emoji_image.resize((30, 30), Image.Resampling.LANCZOS)
        emoji_tk = ImageTk.PhotoImage(emoji_image)
        content_label = Label(message_frame, image=emoji_tk)
        content_label.image = emoji_tk
    else:
        # Displaying normal text
        content_label = Label(message_frame, text=content, anchor="w", justify="left")
    
    content_label.pack(side="left", padx=5, fill="x", expand=True)

# Start server
def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('127.0.0.1', 10000))
    server_socket.listen(1)
    print("Server started, waiting for connection...")

    client_socket, addr = server_socket.accept()
    print(f"Connection established with {addr}")

    threading.Thread(target=handle_client, args=(client_socket, True), daemon=True).start()
    server_gui(client_socket)

# Start client
def start_client(ip, port):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((ip, port))

    threading.Thread(target=handle_client, args=(client_socket, False), daemon=True).start()
    client_gui(client_socket)

# Server GUI
def server_gui(client_socket):
    window = Tk()
    window.title("P2P Chat - Server")
    window.configure(bg="#D3D3D3")  # Set background color of the chat window to grey
    window.geometry("500x600")  # Set max size for chat window

    global pfp_label
    pfp_label = Label(window, text="Select PFP", bg="#D3D3D3")
    pfp_label.pack(pady=5)

    select_pfp_button = Button(window, text="Choose PFP", command=select_pfp, bg="#E0E0E0")
    select_pfp_button.pack(pady=5)

    global chat_area
    chat_area = ScrolledText(window, wrap="word", state="disabled", bg="#D3D3D3", fg="#000000", width=50, height=20)  # Set max size
    chat_area.pack(padx=10, pady=10, fill="both", expand=True)

    entry_field = Entry(window)
    entry_field.pack(padx=10, pady=5, fill="x", expand=True)

    send_button = Button(window, text="Send", command=lambda: send_message(client_socket, entry_field), bg="#E0E0E0")
    send_button.pack(padx=10, pady=5)

    send_image_button = Button(window, text="Send Image", command=lambda: send_image(client_socket), bg="#E0E0E0")
    send_image_button.pack(padx=10, pady=5)

    emoji_button = Button(window, text="Choose Emoji", command=lambda: open_emoji_picker(client_socket), bg="#E0E0E0")
    emoji_button.pack(pady=5)

    window.mainloop()

# Client GUI
def client_gui(client_socket):
    window = Tk()
    window.title("P2P Chat - Client")
    window.configure(bg="#D3D3D3")  # Set background color of the chat window to grey
    window.geometry("500x600")  # Set max size for chat window

    global pfp_label
    pfp_label = Label(window, text="Select PFP", bg="#D3D3D3")
    pfp_label.pack(pady=5)

    select_pfp_button = Button(window, text="Choose PFP", command=select_pfp, bg="#E0E0E0")
    select_pfp_button.pack(pady=5)

    global chat_area
    chat_area = ScrolledText(window, wrap="word", state="disabled", bg="#D3D3D3", fg="#000000", width=50, height=20)  # Set max size
    chat_area.pack(padx=10, pady=10, fill="both", expand=True)

    entry_field = Entry(window)
    entry_field.pack(padx=10, pady=5, fill="x", expand=True)

    send_button = Button(window, text="Send", command=lambda: send_message(client_socket, entry_field), bg="#E0E0E0")
    send_button.pack(padx=10, pady=5)

    send_image_button = Button(window, text="Send Image", command=lambda: send_image(client_socket), bg="#E0E0E0")
    send_image_button.pack(padx=10, pady=5)

    emoji_button = Button(window, text="Choose Emoji", command=lambda: open_emoji_picker(client_socket), bg="#E0E0E0")
    emoji_button.pack(pady=5)

    window.mainloop()

# Send message to client
def send_message(client_socket, entry_field):
    message = entry_field.get()
    if message:
        message_data = {'text': message, 'pfp': user_pfp_data, 'is_image': False}
        serialized_message = pickle.dumps(message_data)

        message_length = len(serialized_message)
        client_socket.send(struct.pack('i', message_length))
        client_socket.send(serialized_message)

        chat_area.config(state="normal")
        display_message(user_pfp_data, message, True)
        chat_area.config(state="disabled")
        entry_field.delete(0, END)

# Send image to client
def send_image(client_socket):
    file_path = filedialog.askopenfilename()
    if file_path:
        message_data = {'image': file_path, 'pfp': user_pfp_data, 'is_image': True}
        serialized_message = pickle.dumps(message_data)

        message_length = len(serialized_message)
        client_socket.send(struct.pack('i', message_length))
        client_socket.send(serialized_message)

        chat_area.config(state="normal")
        display_message(user_pfp_data, file_path, True, is_image=True)
        chat_area.config(state="disabled")

# Open emoji picker window
def open_emoji_picker(client_socket):
    emoji_picker = Toplevel()
    emoji_picker.title("Select Emoji")
    emoji_picker.geometry("300x300")  # Setting the size of the emoji picker to square

    for emoji_file in emoji_files:
        emoji_path = os.path.join(emoji_folder, emoji_file)
        emoji_image = Image.open(emoji_path)
        emoji_image = emoji_image.resize((30, 30), Image.Resampling.LANCZOS)
        emoji_tk = ImageTk.PhotoImage(emoji_image)

        emoji_unicode = os.path.basename(emoji_file)

        emoji_button = Button(emoji_picker, image=emoji_tk, command=lambda ef=emoji_path: send_emoji(client_socket, ef))
        emoji_button.image = emoji_tk
        emoji_button.pack(side="left", padx=5, pady=5)


# Send emoji to client
def send_emoji(client_socket, emoji_path):
    message_data = {'emoji': emoji_path, 'pfp': user_pfp_data}
    serialized_message = pickle.dumps(message_data)

    message_length = len(serialized_message)
    client_socket.send(struct.pack('i', message_length))
    client_socket.send(serialized_message)

    # Display the emoji on the sender's side
    chat_area.config(state="normal")
    display_message(user_pfp_data, emoji_path, False, is_emoji=True)
    chat_area.config(state="disabled")

# Start server or client
if __name__ == "__main__":
    choice = input("Do you want to start as Server (s) or Client (c)? ").strip().lower()
    if choice == "s":
        start_server()
    elif choice == "c":
        ip = input("Enter the server IP: ").strip()
        port = 10000
        start_client(ip, port)
