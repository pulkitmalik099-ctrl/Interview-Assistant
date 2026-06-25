import tkinter as tk
from tkinter import scrolledtext
import ctypes

WDA_EXCLUDEFROMCAPTURE = 0x00000011

class TestGUI:
    def __init__(self, root):
        self.root = root
        self.font_size = 11
        
        self.root.title("GUI Render Test")
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", 0.95)
        self.root.configure(bg="#1E1E2E")
        
        # Center the test window on screen
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        w = 400
        h = 400
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.root.geometry(f"{w}x{h}+{x}+{y}")
        
        # Draggable window
        self.root.bind("<Button-1>", self.start_drag)
        self.root.bind("<B1-Motion>", self.drag_window)
        self._drag_data = {"x": 0, "y": 0}
        
        self.create_widgets()
        
        # Apply invisibility
        self.root.after(100, self.apply_display_affinity)
        
    def start_drag(self, event):
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y
        
    def drag_window(self, event):
        x = self.root.winfo_x() - self._drag_data["x"] + event.x
        y = self.root.winfo_y() - self._drag_data["y"] + event.y
        self.root.geometry(f"+{x}+{y}")
        
    def apply_display_affinity(self):
        try:
            self.root.update_idletasks()
            hwnd = self.root.winfo_id()
            user32 = ctypes.windll.user32
            res = user32.SetWindowDisplayAffinity(hwnd, WDA_EXCLUDEFROMCAPTURE)
            print(f"Set Display Affinity Result: {res}")
        except Exception as e:
            print(f"Affinity Error: {e}")
            
    def create_widgets(self):
        self.main_frame = tk.Frame(self.root, bg="#1E1E2E", bd=1, highlightbackground="#313244", highlightthickness=1)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        self.header = tk.Frame(self.main_frame, bg="#252538", height=30)
        self.header.pack(fill=tk.X)
        
        self.title_label = tk.Label(self.header, text="🎤 GUI RENDER TEST", fg="#C8C0E9", bg="#252538", font=("Helvetica", 9, "bold"))
        self.title_label.pack(side=tk.LEFT, padx=10)
        
        self.close_btn = tk.Button(self.header, text="✕", command=self.root.destroy, bg="#252538", fg="#F38BA8", bd=0, width=3)
        self.close_btn.pack(side=tk.RIGHT, padx=2)
        
        # Question Area
        self.q_frame = tk.Frame(self.main_frame, bg="#181825")
        self.q_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.q_title = tk.Label(self.q_frame, text="LAST QUESTION:", fg="#89B4FA", bg="#181825", font=("Helvetica", 8, "bold"), anchor="w")
        self.q_title.pack(fill=tk.X, padx=5, pady=2)
        
        self.q_text = tk.Label(self.q_frame, text="Waiting for simulation...", fg="#BAC2DE", bg="#181825", font=("Helvetica", 9, "italic"), wraplength=370, justify=tk.LEFT, anchor="w")
        self.q_text.pack(fill=tk.X, padx=5, pady=(0, 5))
        
        # Answer Area
        self.a_frame = tk.Frame(self.main_frame, bg="#1E1E2E")
        self.a_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        self.a_title = tk.Label(self.a_frame, text="SUGGESTED ANSWER:", fg="#89DCEB", bg="#1E1E2E", font=("Helvetica", 8, "bold"), anchor="w")
        self.a_title.pack(fill=tk.X, pady=(0, 2))
        
        self.answer_text = scrolledtext.ScrolledText(self.a_frame, wrap=tk.WORD, bg="#11111B", fg="#CDD6F4", bd=0, font=("Helvetica", self.font_size))
        self.answer_text.pack(fill=tk.BOTH, expand=True)
        self.answer_text.insert(tk.END, "Click the button below to simulate voice detection.")
        self.answer_text.configure(state=tk.DISABLED)
        
        # Test Button
        self.btn_frame = tk.Frame(self.main_frame, bg="#1E1E2E")
        self.btn_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=10)
        
        self.simulate_btn = tk.Button(self.btn_frame, text="[ Simulate Question & Answer ]", command=self.simulate, bg="#A6E3A1", fg="#1E1E2E", font=("Helvetica", 10, "bold"), height=2)
        self.simulate_btn.pack(fill=tk.X, padx=20)
        
    def simulate(self):
        self.q_text.configure(text="How does this look?", font=("Helvetica", 9, "bold"), fg="#CDD6F4")
        
        self.answer_text.configure(state=tk.NORMAL)
        self.answer_text.delete(1.0, tk.END)
        self.answer_text.insert(tk.END, "- **GUI status**: Renders perfectly!\n- **Draggability**: Try dragging the window by holding the header.\n- **Invisibility**: Take a screenshot; this window will disappear.\n- **Clipboard**: This text was copied to your clipboard!")
        self.answer_text.configure(state=tk.DISABLED)
        
        import pyperclip
        pyperclip.copy("GUI Works successfully!")

if __name__ == "__main__":
    root = tk.Tk()
    app = TestGUI(root)
    root.mainloop()
