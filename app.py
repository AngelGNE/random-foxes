import tkinter as tk
import requests
import sys
import threading
from api import random_fox
from PIL import Image, ImageTk
from io import BytesIO
from pathlib import Path
from tkinter import filedialog

TITLE = "Random Foxes"
WIN_SIZE = "600x600"
MAX_SIZE = (550, 550)
ICON = "Assets/RandomFox.ico"
WHINE = "Assets/fox_whine.wav"
SNIFF = "Assets/fox_sniff.wav"

def thread(func):
    def wrapper(*args, **kwargs):
        thread = threading.Thread(target=func, args=args, kwargs=kwargs, daemon=True)
        thread.start()
        return thread
    return wrapper

def resource_path(rel_path):
    try:
        base_path = Path(sys._MEIPASS)
    except Exception:
        base_path = Path(__file__).parent
    return base_path / rel_path

class RandomFoxApp:
    
    def __init__(self):
        self.root = tk.Tk()
        self.raw_img = None
        self.fox_img = None
        self.next_raw_img = None
        self.next_fox_img = None
        
        self.build_gui()
        self.__preload_fox()

    def build_gui(self):
        icon = ImageTk.PhotoImage(Image.open(resource_path(ICON)))
        self.root.iconphoto(False, icon)
        self.root.title(TITLE)
        self.root.geometry(WIN_SIZE)
        self.root.resizable(False, False)
        
        # Frames
        self.top = tk.Frame(self.root)
        self.frame0 = tk.Frame(self.top)
        self.frame1 = tk.Frame(self.top)

        self.top.pack(padx=15, pady=15)
        self.frame0.pack(pady=5)
        self.frame1.pack(pady=5)

        # frame0
        self.fox_button = tk.Button(self.frame0, text="Get floof!", command=self.show_fox)
        self.save_button = tk.Button(self.frame0, text="Save fox", command=self.save_fox)

        self.fox_button.pack(side="left", padx=10)
        self.save_button.pack(side="left", padx=10)

        # frame1
        self.img_label = tk.Label(self.frame1)
        self.img_label.pack()
        
    def show_fox(self):
        self.fox_button.config(state="disabled", text="Loading...")
        self.raw_img = self.next_raw_img
        self.fox_img = self.next_fox_img
        self.__update_img()
        self.play_sound(WHINE)
        self.__preload_fox()

    @thread
    def __preload_fox(self):
        raw_img = self.__download_fox()
        self.next_raw_img = raw_img
        if raw_img is not None:
            self.root.after(0, lambda: setattr(self, "next_fox_img", self.__bytes_to_img(raw_img)))
        else:
            self.root.after(0, lambda: setattr(self, "next_fox_img", None))
            
    def __download_fox(self):
        try:
            fox_data = random_fox()
            url = fox_data["image"]
            response = requests.get(url)
            return response.content
        except Exception as e:
            print(f"Unexpected error: {e}")
            return None      

    def __bytes_to_img(self, raw_img):
        if raw_img is None:
            return None
        img_bytes = Image.open(BytesIO(raw_img)).convert("RGB")
        img_bytes.thumbnail(MAX_SIZE, Image.LANCZOS)
        return ImageTk.PhotoImage(img_bytes)

    def __update_img(self):
        if self.fox_img:
            self.img_label.config(image=self.fox_img)
        else:
            self.img_label.config(text="Failed to load :<")
        self.fox_button.config(state="normal", text="Get floof!")

    def save_fox(self):
        if not self.fox_img:
            return
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[
                ("PNG files", "*.png"),
                ("JPEG files", "*.jpg"),
                ("All files", "*.*")
            ],
            title="Save Image As"
        )
        if not file_path:
            return
        try:
            with open(file_path, 'wb') as file:
                file.write(self.raw_img)
            self.play_sound(SNIFF)
        except Exception as e:
            print(f"Unexpected error: {e}")

    def play_sound(self, sound):
        try:
            import winsound
            winsound.PlaySound(resource_path(sound), winsound.SND_FILENAME | winsound.SND_ASYNC)
        except Exception as e:
            print(f"Unexpected error: {e}")
        
    def run(self):
        self.root.mainloop()
        
