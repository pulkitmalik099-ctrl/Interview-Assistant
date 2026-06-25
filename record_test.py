import sounddevice as sd
import soundfile as sf
import numpy as np
import os

def record_test():
    print("==================================================")
    print("            MICROPHONE RECORDING TEST             ")
    print("==================================================")
    print("Recording will start in 1 second...")
    print("Please SPEAK LOUDLY into your microphone for 5 seconds!")
    print("--------------------------------------------------")
    
    fs = 16000
    duration = 5.0
    
    try:
        # Record from default device (Device 0)
        recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, device=0)
        
        # Countdown
        for i in range(5, 0, -1):
            print(f"Recording... {i} seconds remaining")
            time_left = 1.0
            # simple delay sleep
            import time
            time.sleep(time_left)
            
        sd.wait()
        
        # Calculate RMS
        clean_rec = recording - np.mean(recording)
        rms = np.sqrt(np.mean(clean_rec**2))
        
        # Save as WAV file
        file_name = "test_mic_recording.wav"
        sf.write(file_name, recording, fs)
        
        print("\n================== TEST COMPLETE ==================")
        print(f"Signal Level (RMS) detected: {rms:.5f}")
        print(f"File Saved: {os.path.abspath(file_name)}")
        print("--------------------------------------------------")
        print("INSTRUCTIONS:")
        print("Please go to your file explorer and double-click the file")
        print("'test_mic_recording.wav' to play it.")
        print("- If you hear your voice: The microphone is active, and we need to tweak settings.")
        print("- If you hear absolute silence: Your microphone is muted in Windows Settings.")
        print("==================================================")
    except Exception as e:
        print(f"Error during recording: {e}")

if __name__ == "__main__":
    record_test()
