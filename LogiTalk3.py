import base64
import io
import threading

from socket import*
from customtkinter import*
from PIL import Image

class MW(CTk):
    def __init__(self):
        super().__init__()
        self.geometry("400x300")
        self.title("LogiTalk")
        self.username = "Артур"
        self.label = None
        self.menu_frame = CTkFrame(self,width=30,height=300)
        self.menu_frame.pack_propagate(False)
        self.menu_frame.place(x=0,y=0)
        self.is_sh_m = False
        self.sp_anm_m = -20
        self.btn = CTkButton(self, text="🕳",
                             command=self.tgl_sh_m,
                             width=30)
        self.btn.place(x=0,y=0)
        self.ch_fd = CTkScrollableFrame(self)
        self.ch_fd.place(x=0,y=0)

        self.mess_enr = CTkEntry(self,
                                 placeholder_text="Введіть повідомлення: ",
                                 height=40)
        self.mess_enr.place(x=0,y=0)

        self.send_btn = CTkButton(self, text="✈",
                                  width=50,height=50,
                                  command=self.send_mess)
        self.send_btn.place(x=0,y=0)

        self.open_img = CTkButton(self,text="🗺",
                                  width=50, height=50,
                                  command=self.open_image)
        self.open_img.place(x=0,y=0)
        self.adaptive()

        self.add_mess("Демонстрація відображення зображення: ",
                      CTkImage(Image.open("media_button.jpg"), size=(300,300)))

        try:
            self.sock = socket(AF_INET,SOCK_STREAM)
            self.sock.connect(('6.tcp.eu.ngrok.io',16077))
            hello = f"TEXT@{self.username}@..."
            self.sock.send(hello.encode('utf-8'))
            threading.Thread(target=self.recv_mess,
                             daemon=True).start()

        except Exception as e:
            self.add_mess(f"Не вдалося підключитися до сервера: {e}")

    def tgl_sh_m(self):
        if self.is_sh_m:
            self.is_sh_m = False
            self.sp_anm_m *= -1
            self.btn.configure(text="🏴")
            self.sh_m()
        else:
            self.is_sh_m = True
            self.sp_anm_m *= -1
            self.btn.configure(text="🏳")
            self.sh_m()

            self.label = CTkLabel(self.menu_frame, text="Ім'я")
            self.label.pack(pady=30)
            self.entry = CTkEntry(self.menu_frame,
                                  placeholder_text="Ваш нік...")
            self.entry.pack()

            self.save_btn = CTkButton(self.menu_frame, text="Зберегти",
                                      command=self.save_name)
            self.save_btn.pack()

    def sh_m(self):
        self.menu_frame.configure(width=self.menu_frame.winfo_width() + self.sp_anm_m)
        if not self.menu_frame.winfo_width() >= 200 and self.is_sh_m:
            self.after(10,self.sh_m)
        elif self.menu_frame.winfo_width() >= 60 and not self.is_sh_m:
            self.after(10,self.sh_m)
            if self.label:
                self.label.destroy()
            if getattr(self, "entry", None):
                self.entry.destroy()
            if getattr(self, "save_btn", None):
                self.save_btn.destroy()
    def save_name(self):
       new_name = self.entry.get().strip()
       if new_name:
           self.username = new_name
           self.add_mess(f"Ваш новий нік: {self.username}")

    def adaptive(self):
        self.menu_frame.configure(height=self.winfo_height())
        self.ch_fd.place(x=self.menu_frame.winfo_width())
        self.ch_fd.configure(width=self.winfo_height() - self.menu_frame.winfo_width() - 20,
                             height=self.winfo_height() - 40)
        self.send_btn.place(x=self.winfo_width() - 50,
                            y=self.winfo_height() - 40)
        self.mess_enr.place(x=self.menu_frame.winfo_width(),
                            y=self.send_btn.winfo_y())
        self.mess_enr.configure(width=self.winfo_width() - self.menu_frame.winfo_width() - 110)
        self.open_img.place(x=self.winfo_width() - 105,
                            y=self.send_btn.winfo_y())
        self.after(50, self.adaptive)

    def add_mess(self, message, img = None):
        mess_frame = CTkFrame(self.ch_fd, fg_color="grey")
        mess_frame.pack(pady=5, anchor="w")
        wr_size = self.winfo_width() - self.menu_frame.winfo_width() - 40

        if not img:
            CTkLabel(mess_frame, text=message, wraplength=wr_size,
                     text_color='white', justify="left").pack(pady=5, padx=10)
        else:
            CTkLabel(mess_frame, text=message, wraplength=wr_size,
                     text_color='white',
                     image=img,
                     compound="top",
                     justify="left").pack(pady=5, padx=10)
    def send_mess(self):
        message = self.mess_enr.get()
        if message:
            self.add_mess(f"{self.username} : {message}")
            data = f"TEXT@{self.username}@{message}\n"
            try:
                self.sock.sendall((data.encode()))
            except:
                pass
            self.mess_enr.delete(0, END)

    def recv_mess(self):
        buffer = ("")
        while True:
            try:
                chunk = self.sock.recv(4096)
                if not chunk:
                    break
                buffer += chunk.decode('utf-8', errors="ignore")

                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    self.handle_line(line.strip())
            except:
                break
        self.sock.close()

    def handle_line(self, line):
        if not line:
            return
        parts = line.split("@", 3)
        msg_type = parts[0]

        if msg_type == "TEXT":
         if len(parts) >= 3:
                 auth = parts[1]
                 message = parts[2]
                 self.add_mess(f"{auth} : {message}")
         elif msg_type == "IMAGE":
             if len(parts) >= 4:
                 auth = parts[1]
                 filename = parts[2]
                 b64_img = parts[3]

                 try:
                     img_data = base64.b64decode(b64_img)
                     pil_img = Image.open(io.BytesIO(img_data))
                     ctk_img = CTkImage(pil_img, size=(300,300))
                     self.add_mess(f"{auth} надіслав(ла) зображення: {filename}",
                                   img=ctk_img)
                 except Exception as e:
                     self.add_mess(f"Помилка відображення зображення: {e}")
         else:
             self.add_mess(line)

    def open_image(self):
        file_name = filedialog.askopenfilename()
        if not file_name:
            return
        try:
            with open(file_name, "rb") as f:
                raw = f.read()
            b64_data = base64.b64encode(raw).decode()
            short_name = os.path.basename(file_name)
            data = f"IMAGE@{self.username}@{short_name}@{b64_data}\n"
            self.sock.sendall(data.encode())
            self.add_mess('',
                          CTkImage(light_image=Image.open(file_name),
                                   size=(300,300)))
        except Exception as e:
              self.add_mess(f"Не вдалося надіслати зображення: {e}")

if __name__ == "__main__":
    win = MW()
    win.mainloop()