import os
import sys
import time
import queue
import ctypes
import threading
import io
import argparse
import numpy as np
import sounddevice as sd
import soundfile as sf
import google.generativeai as genai
import pyperclip
from dotenv import load_dotenv

# Import Tkinter for GUI
import tkinter as tk
from tkinter import font as tkfont
from tkinter import scrolledtext

# Load environment variables
load_dotenv()

# Initialize API Key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY and GEMINI_API_KEY != "YOUR_GEMINI_API_KEY_HERE":
    genai.configure(api_key=GEMINI_API_KEY)

# Global Queues and Variables for Thread Communication
gui_queue = queue.Queue()
audio_buffer = []
is_recording = False
current_rms = 0.0

# WDA_EXCLUDEFROMCAPTURE hides the window from Zoom/Teams/Screenshots on Windows
WDA_EXCLUDEFROMCAPTURE = 0x00000011
WDA_MONITOR = 0x00000001

class InterviewCopilotGUI:
    def __init__(self, root, threshold, silence_duration):
        self.root = root
        self.threshold = threshold
        self.silence_duration = silence_duration
        self.font_size = 11
        self.is_compact = False
        
        # Configure Root Window
        self.root.title("AI Interview Copilot")
        self.root.overrideredirect(True)  # Borderless
        self.root.attributes("-topmost", True)  # Always on top
        self.root.attributes("-alpha", 0.95)  # Glassmorphic transparency
        self.root.configure(bg="#1E1E2E")  # Dark Slate Blue/Purple theme
        
        # Default geometry: width 400, height 300, positioned at top-right
        screen_width = self.root.winfo_screenwidth()
        self.normal_width = 400
        self.normal_height = 350
        self.compact_width = 160
        self.compact_height = 40
        
        x = screen_width - self.normal_width - 40
        y = 50
        self.root.geometry(f"{self.normal_width}x{self.normal_height}+{x}+{y}")
        
        # Make window draggable
        self.root.bind("<Button-1>", self.start_drag)
        self.root.bind("<B1-Motion>", self.drag_window)
        self._drag_data = {"x": 0, "y": 0}
        
        # Initialize UI Components
        self.create_widgets()
        
        # Exclude from capture (hide from screen shares)
        self.root.after(100, self.apply_display_affinity)
        
        # Start queue processing
        self.process_queue()
        
    def apply_display_affinity(self):
        """Applies the display affinity to exclude the window from screen capture."""
        try:
            self.root.update_idletasks()
            hwnd = self.root.winfo_id()
            user32 = ctypes.windll.user32
            # Try WDA_EXCLUDEFROMCAPTURE (hides completely, showing background behind it)
            res = user32.SetWindowDisplayAffinity(hwnd, WDA_EXCLUDEFROMCAPTURE)
            if res:
                self.log_message("System", "Overlay hidden from screen capture.")
            else:
                # Fallback to WDA_MONITOR (shows as a black box in recordings)
                res_fallback = user32.SetWindowDisplayAffinity(hwnd, WDA_MONITOR)
                if res_fallback:
                    self.log_message("System", "Overlay blacked out in screen capture.")
                else:
                    self.log_message("System", "Warning: Could not enable screen-capture protection.")
        except Exception as e:
            self.log_message("System", f"Affinity error: {e}")

    def create_widgets(self):
        # Master Frame
        self.main_frame = tk.Frame(self.root, bg="#1E1E2E", bd=1, highlightbackground="#313244", highlightthickness=1)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 1. Title/Header Bar
        self.header = tk.Frame(self.main_frame, bg="#252538", height=30)
        self.header.pack(fill=tk.X)
        
        self.title_label = tk.Label(self.header, text="🎤 INTERVIEW COPILOT", fg="#C8C0E9", bg="#252538", font=("Helvetica", 9, "bold"))
        self.title_label.pack(side=tk.LEFT, padx=10)
        
        # Quick close and minimize buttons
        self.close_btn = tk.Button(self.header, text="✕", command=self.quit_app, bg="#252538", fg="#F38BA8", bd=0, activebackground="#F38BA8", activeforeground="#1E1E2E", font=("Helvetica", 9, "bold"), width=3)
        self.close_btn.pack(side=tk.RIGHT, padx=2)
        
        self.minimize_btn = tk.Button(self.header, text="⛶", command=self.toggle_compact, bg="#252538", fg="#A6E3A1", bd=0, activebackground="#A6E3A1", activeforeground="#1E1E2E", font=("Helvetica", 9, "bold"), width=3)
        self.minimize_btn.pack(side=tk.RIGHT, padx=2)
        
        # 2. Control & Status Bar
        self.control_bar = tk.Frame(self.main_frame, bg="#1E1E2E", height=25)
        self.control_bar.pack(fill=tk.X, padx=10, pady=5)
        
        # Status Bulb
        self.status_bulb = tk.Canvas(self.control_bar, width=12, height=12, bg="#1E1E2E", bd=0, highlightthickness=0)
        self.status_bulb.pack(side=tk.LEFT, pady=3)
        self.status_oval = self.status_bulb.create_oval(2, 2, 10, 10, fill="#A6E3A1")  # Green default
        
        self.status_label = tk.Label(self.control_bar, text="LISTENING", fg="#A6E3A1", bg="#1E1E2E", font=("Helvetica", 8, "bold"))
        self.status_label.pack(side=tk.LEFT, padx=5)
        
        # Volume meter
        self.vol_label = tk.Label(self.control_bar, text="Vol:", fg="#7F849C", bg="#1E1E2E", font=("Helvetica", 8))
        self.vol_label.pack(side=tk.LEFT, padx=(10, 2))
        
        self.vol_canvas = tk.Canvas(self.control_bar, width=80, height=8, bg="#313244", bd=0, highlightthickness=0)
        self.vol_canvas.pack(side=tk.LEFT, pady=5)
        self.vol_bar = self.vol_canvas.create_rectangle(0, 0, 0, 8, fill="#A6E3A1")
        
        # Font adjustment buttons
        self.font_dec = tk.Button(self.control_bar, text="A-", command=self.decrease_font, bg="#313244", fg="#CDD6F4", bd=0, font=("Helvetica", 7, "bold"), width=2)
        self.font_dec.pack(side=tk.RIGHT, padx=2)
        
        self.font_inc = tk.Button(self.control_bar, text="A+", command=self.increase_font, bg="#313244", fg="#CDD6F4", bd=0, font=("Helvetica", 7, "bold"), width=2)
        self.font_inc.pack(side=tk.RIGHT, padx=2)
        
        self.clear_btn = tk.Button(self.control_bar, text="Clear", command=self.clear_text, bg="#313244", fg="#CDD6F4", bd=0, font=("Helvetica", 8), width=5)
        self.clear_btn.pack(side=tk.RIGHT, padx=10)
        
        # 3. Question display pane
        self.question_frame = tk.Frame(self.main_frame, bg="#181825")
        self.question_frame.pack(fill=tk.X, padx=10, pady=(0, 5))
        
        self.q_title = tk.Label(self.question_frame, text="LAST QUESTION:", fg="#89B4FA", bg="#181825", font=("Helvetica", 8, "bold"), anchor="w")
        self.q_title.pack(fill=tk.X, padx=5, pady=2)
        
        self.q_text = tk.Label(self.question_frame, text="Waiting for question...", fg="#BAC2DE", bg="#181825", font=("Helvetica", 9, "italic"), wraplength=370, justify=tk.LEFT, anchor="w")
        self.q_text.pack(fill=tk.X, padx=5, pady=(0, 5))
        
        # 4. Suggested Answer pane (Scrollable)
        self.answer_frame = tk.Frame(self.main_frame, bg="#1E1E2E")
        self.answer_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        self.a_title = tk.Label(self.answer_frame, text="SUGGESTED ANSWER:", fg="#89DCEB", bg="#1E1E2E", font=("Helvetica", 8, "bold"), anchor="w")
        self.a_title.pack(fill=tk.X, pady=(0, 2))
        
        self.answer_text = scrolledtext.ScrolledText(self.answer_frame, wrap=tk.WORD, bg="#11111B", fg="#CDD6F4", insertbackground="white", bd=0, font=("Helvetica", self.font_size))
        self.answer_text.pack(fill=tk.BOTH, expand=True)
        self.answer_text.insert(tk.END, "Suggested responses will appear here dynamically in real-time.\n\nTips:\n- Adjust AUDIO_THRESHOLD in .env if it picks up static noise.\n- Make sure your speaker audio device is selected for Zoom/Meet calls.")
        self.answer_text.configure(state=tk.DISABLED)
        
        # Custom Scrollbar Styling (Minimal support in Tkinter)
        self.answer_text.vbar.configure(troughcolor="#11111B", bg="#313244")
        
    def start_drag(self, event):
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y
        
    def drag_window(self, event):
        x = self.root.winfo_x() - self._drag_data["x"] + event.x
        y = self.root.winfo_y() - self._drag_data["y"] + event.y
        self.root.geometry(f"+{x}+{y}")
        
    def toggle_compact(self):
        self.is_compact = not self.is_compact
        if self.is_compact:
            # Switch to compact mode (just show status and volume, hide the panels)
            self.question_frame.pack_forget()
            self.answer_frame.pack_forget()
            self.minimize_btn.configure(text="⛶")
            
            # Reduce window size
            x = self.root.winfo_x()
            y = self.root.winfo_y()
            self.root.geometry(f"{self.compact_width}x{self.compact_height}+{x}+{y}")
        else:
            # Restore normal mode
            self.question_frame.pack(fill=tk.X, padx=10, pady=(0, 5))
            self.answer_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
            self.minimize_btn.configure(text="⛶")
            
            x = self.root.winfo_x()
            y = self.root.winfo_y()
            self.root.geometry(f"{self.normal_width}x{self.normal_height}+{x}+{y}")
            
    def set_status(self, status, color):
        self.status_label.configure(text=status, fg=color)
        self.status_bulb.itemconfig(self.status_oval, fill=color)
        
    def update_volume(self, rms_val):
        # Normalize RMS (typically 0.0 to 0.1 for speaking)
        val = min(rms_val / (self.threshold * 3), 1.0)
        width = int(val * 80)
        
        # Change color based on volume compared to threshold
        color = "#F38BA8" if rms_val > self.threshold else "#A6E3A1"
        
        self.vol_canvas.coords(self.vol_bar, 0, 0, width, 8)
        self.vol_canvas.itemconfig(self.vol_bar, fill=color)
        
    def log_message(self, sender, text):
        print(f"[{sender}] {text}")
        
    def update_content(self, question, answer):
        # Update Question Label
        self.q_text.configure(text=question, font=("Helvetica", 9, "bold"), fg="#CDD6F4")
        
        # Update Answer ScrollText
        self.answer_text.configure(state=tk.NORMAL)
        self.answer_text.delete(1.0, tk.END)
        self.answer_text.insert(tk.END, answer)
        self.answer_text.configure(state=tk.DISABLED)
        
        # Copy to clipboard
        try:
            pyperclip.copy(answer)
        except Exception as e:
            self.log_message("Clipboard", f"Error: {e}")
            
    def clear_text(self):
        self.q_text.configure(text="Waiting for question...", font=("Helvetica", 9, "italic"), fg="#BAC2DE")
        self.answer_text.configure(state=tk.NORMAL)
        self.answer_text.delete(1.0, tk.END)
        self.answer_text.insert(tk.END, "Suggested responses will appear here dynamically.")
        self.answer_text.configure(state=tk.DISABLED)
        
    def increase_font(self):
        self.font_size = min(self.font_size + 1, 20)
        self.answer_text.configure(font=("Helvetica", self.font_size))
        
    def decrease_font(self):
        self.font_size = max(self.font_size - 1, 8)
        self.answer_text.configure(font=("Helvetica", self.font_size))
        
    def quit_app(self):
        self.root.destroy()
        sys.exit(0)
        
    def process_queue(self):
        """Processes messages sent from the audio/processing thread."""
        try:
            while True:
                msg_type, data = gui_queue.get_nowait()
                if msg_type == "STATUS":
                    self.set_status(data["status"], data["color"])
                elif msg_type == "VOLUME":
                    self.update_volume(data)
                elif msg_type == "RESULT":
                    self.update_content(data["question"], data["answer"])
                    self.set_status("ANSWER READY", "#89B4FA")
                elif msg_type == "ERROR":
                    self.set_status("ERROR", "#F38BA8")
                    self.update_content("Error encountered", data)
                gui_queue.task_done()
        except queue.Empty:
            pass
        # Run this check every 50ms
        self.root.after(50, self.process_queue)

# Audio Stream Callback
def audio_callback(indata, frames, time_info, status):
    global current_rms
    if status:
        print(f"[Audio Stream Status] {status}", file=sys.stderr)
    
    # Calculate current signal RMS (volume level)
    # Subtract mean to remove DC offset
    clean_data = indata - np.mean(indata)
    current_rms = np.sqrt(np.mean(clean_data**2))
    
    # Send current volume to GUI queue
    gui_queue.put(("VOLUME", current_rms))
    
    # If we are recording, buffer the audio data
    if is_recording:
        audio_buffer.append(indata.copy())

# Audio Monitor Thread
def audio_monitor_thread(device_idx, threshold, silence_duration, samplerate=16000):
    global is_recording, audio_buffer
    
    # Use blocksize of 1600 samples (100ms at 16kHz)
    block_size = int(samplerate * 0.1) 
    
    print(f"[Monitor] Starting audio capture on device: {device_idx if device_idx is not None else 'Default'}")
    print(f"[Monitor] Threshold: {threshold}, Silence timeout: {silence_duration}s")
    
    # State tracking
    state = "SILENT"
    silence_start_time = None
    
    try:
        with sd.InputStream(device=device_idx, channels=1, samplerate=samplerate, 
                            blocksize=block_size, callback=audio_callback):
            while True:
                time.sleep(0.05)
                
                # State Machine Processing
                if state == "SILENT":
                    if current_rms > threshold:
                        # Speech detected
                        state = "RECORDING"
                        is_recording = True
                        audio_buffer = []  # Clear buffer
                        gui_queue.put(("STATUS", {"status": "RECORDING...", "color": "#F38BA8"}))
                        print("[Audio Engine] Speaking detected...")
                        
                elif state == "RECORDING":
                    if current_rms <= threshold:
                        # Voice dropped below threshold, start waiting for silence
                        state = "SILENCE_WAIT"
                        silence_start_time = time.time()
                        
                elif state == "SILENCE_WAIT":
                    if current_rms > threshold:
                        # Voice resumed, go back to recording
                        state = "RECORDING"
                    else:
                        # Check if silence duration has elapsed
                        elapsed = time.time() - silence_start_time
                        if elapsed >= silence_duration:
                            # Finished speaking! Trigger answering
                            state = "SILENT"
                            is_recording = False
                            
                            # Check if recorded audio is long enough (at least 1 second)
                            # 10 blocks = 1 second at 100ms per block
                            if len(audio_buffer) >= 10:
                                print(f"[Audio Engine] Silence timeout reached. Processing {len(audio_buffer)*0.1:.1f}s of audio...")
                                gui_queue.put(("STATUS", {"status": "THINKING...", "color": "#FAB387"}))
                                
                                # Package buffer data
                                recorded_data = np.concatenate(audio_buffer, axis=0)
                                audio_buffer = []
                                
                                # Spin off API call to a separate thread to keep audio stream responsive
                                threading.Thread(target=process_audio_with_gemini, 
                                                 args=(recorded_data, samplerate), 
                                                 daemon=True).start()
                            else:
                                print("[Audio Engine] Captured segment too short, ignoring.")
                                gui_queue.put(("STATUS", {"status": "LISTENING", "color": "#A6E3A1"}))
                                audio_buffer = []
                                
    except Exception as e:
        print(f"[Audio Engine] Stream Error: {e}", file=sys.stderr)
        gui_queue.put(("ERROR", f"Audio stream error: {e}"))

# Gemini API Integration
def process_audio_with_gemini(audio_data, samplerate):
    if not GEMINI_API_KEY or GEMINI_API_KEY == "YOUR_GEMINI_API_KEY_HERE":
        gui_queue.put(("ERROR", "Gemini API Key not set!\nPlease update the .env file with your GEMINI_API_KEY."))
        return

    try:
        # 1. Convert numpy array to WAV bytes in memory
        wav_io = io.BytesIO()
        sf.write(wav_io, audio_data, samplerate, format='WAV', subtype='PCM_16')
        audio_bytes = wav_io.getvalue()
        
        # 2. Call Gemini model directly with audio data
        model = genai.GenerativeModel("gemini-2.5-flash")
        
        prompt = (
            "You are an expert AI interview assistant. The attached audio contains the interviewer's question. "
            "Please perform the following tasks:\n"
            "1. Transcribe the question accurately.\n"
            "2. Provide a clear, structured, and professional answer to the question that the candidate can use. "
            "Keep it concise, direct, and easy to read quickly (e.g., using short bullet points).\n"
            "Format your output EXACTLY as follows:\n\n"
            "QUESTION: [Transcription of the question]\n"
            "ANSWER: [Your suggested answer]\n"
        )
        
        response = model.generate_content([
            {
                "mime_type": "audio/wav",
                "data": audio_bytes
            },
            prompt
        ])
        
        response_text = response.text
        print(f"[Gemini Response] Raw:\n{response_text}")
        
        # Parse the structured response
        question_part = "Could not transcribe question clearly."
        answer_part = response_text
        
        if "QUESTION:" in response_text and "ANSWER:" in response_text:
            parts = response_text.split("ANSWER:")
            question_part = parts[0].replace("QUESTION:", "").strip()
            answer_part = parts[1].strip()
        elif "QUESTION:" in response_text:
            question_part = response_text.replace("QUESTION:", "").strip()
            answer_part = "Unable to generate answer structure."
        
        # Send results back to GUI
        gui_queue.put(("RESULT", {"question": question_part, "answer": answer_part}))
        gui_queue.put(("STATUS", {"status": "LISTENING", "color": "#A6E3A1"}))
        
    except Exception as e:
        print(f"[Gemini API Error] {e}", file=sys.stderr)
        gui_queue.put(("ERROR", f"Gemini API Error: {e}"))

# Main Entry Point
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI Interview Copilot")
    parser.add_argument("--list-devices", "-l", action="store_true", help="List available audio input devices and exit")
    parser.add_argument("--device", "-d", type=str, default=None, help="Audio device ID or name to record from")
    parser.add_argument("--threshold", "-t", type=float, default=None, help="Amplitude threshold to trigger recording")
    parser.add_argument("--silence", "-s", type=float, default=None, help="Silence duration (seconds) to trigger processing")
    
    args = parser.parse_args()
    
    # 1. Handle device listing
    if args.list_devices:
        print("\n=== AVAILABLE AUDIO INPUT DEVICES ===")
        devices = sd.query_devices()
        host_apis = sd.query_hostapis()
        for idx, d in enumerate(devices):
            api_name = host_apis[d['hostapi']]['name']
            is_input = d['max_input_channels'] > 0
            is_default = " (Default)" if idx == sd.default.device[0] else ""
            loopback_str = " [Loopback]" if d.get('is_loopback') or "loopback" in d['name'].lower() else ""
            
            if is_input:
                print(f"Device ID {idx}: {d['name']} ({api_name}) - Channels: {d['max_input_channels']}{is_default}{loopback_str}")
        print("=====================================\n")
        sys.exit(0)
        
    # 2. Resolve Config Values (Command-line overrides .env)
    env_device_id = os.getenv("AUDIO_DEVICE_ID")
    device_id = args.device if args.device is not None else env_device_id
    if device_id is None or str(device_id).strip() == "" or str(device_id).lower() == "none":
        device_idx = None
    else:
        try:
            device_idx = int(device_id)
        except ValueError:
            # Match device by name substring
            found = False
            for idx, d in enumerate(sd.query_devices()):
                if device_id.lower() in d['name'].lower() and d['max_input_channels'] > 0:
                    device_idx = idx
                    found = True
                    break
            if not found:
                print(f"[Config] Could not find input device matching name '{device_id}', using default.")
                device_idx = None
                
    env_threshold = float(os.getenv("AUDIO_THRESHOLD", "0.015"))
    threshold = args.threshold if args.threshold is not None else env_threshold
    
    env_silence = float(os.getenv("SILENCE_DURATION", "2.0"))
    silence_duration = args.silence if args.silence is not None else env_silence
    
    # Print configuration details
    print("=== Configuration ===")
    print(f"Device: {device_idx if device_idx is not None else 'Default'}")
    print(f"Threshold: {threshold}")
    print(f"Silence Duration: {silence_duration}s")
    print(f"Gemini API Configured: {'Yes' if GEMINI_API_KEY else 'No (Make sure to update .env)'}")
    print("=====================")
    
    # 3. Start Audio Recording / Monitor Thread
    audio_thread = threading.Thread(target=audio_monitor_thread, 
                                    args=(device_idx, threshold, silence_duration), 
                                    daemon=True)
    audio_thread.start()
    
    # 4. Start GUI in Main Thread
    root = tk.Tk()
    app = InterviewCopilotGUI(root, threshold, silence_duration)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("[System] Exiting due to keyboard interrupt.")
        sys.exit(0)
