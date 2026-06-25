import sys
import os
import traceback

def run_diagnostics():
    report = []
    report.append("==========================================")
    report.append("       COPILOT SYSTEM SELF-CHECK          ")
    report.append("==========================================")
    report.append(f"Python Version: {sys.version}")
    report.append(f"CWD: {os.getcwd()}")
    report.append("------------------------------------------\n")
    
    # 1. Test Package Imports
    report.append("[1] Testing Package Imports...")
    required_packages = [
        ("tkinter", "tk"),
        ("sounddevice", "sd"),
        ("soundfile", "sf"),
        ("numpy", "np"),
        ("google.generativeai", "genai"),
        ("pyperclip", "pyperclip"),
        ("dotenv", "dotenv")
    ]
    
    imports_ok = True
    for pkg_name, import_name in required_packages:
        try:
            __import__(import_name)
            report.append(f"  -> {pkg_name}: OK")
        except ImportError as e:
            report.append(f"  -> {pkg_name}: FAILED (Error: {e})")
            imports_ok = False
            
    # 2. Test Tkinter Window Creation
    report.append("\n[2] Testing Tkinter GUI Subsystem...")
    try:
        import tkinter as tk
        root = tk.Tk()
        root.withdraw() # hide window
        root.update()
        root.destroy()
        report.append("  -> Tkinter GUI initialization: OK")
    except Exception as e:
        report.append("  -> Tkinter GUI initialization: FAILED")
        report.append(f"     Traceback:\n{traceback.format_exc()}")
        
    # 3. Test Audio InputStream
    report.append("\n[3] Testing Audio Input Streams...")
    try:
        import sounddevice as sd
        import numpy as np
        
        # Check devices
        devices = sd.query_devices()
        report.append(f"  -> Total audio devices found: {len(devices)}")
        
        default_in = sd.default.device[0]
        report.append(f"  -> Default Input Device ID: {default_in}")
        
        # Test opening input stream on Device 0
        def dummy_callback(indata, frames, time, status):
            pass
            
        stream = sd.InputStream(device=0, channels=1, samplerate=16000, 
                                blocksize=1600, callback=dummy_callback)
        with stream:
            pass
        report.append("  -> Opening InputStream on Device 0: OK")
    except Exception as e:
        report.append("  -> Opening InputStream on Device 0: FAILED")
        report.append(f"     Traceback:\n{traceback.format_exc()}")
        
    # 4. Test Clipboard Access
    report.append("\n[4] Testing Pyperclip Clipboard Interface...")
    try:
        import pyperclip
        test_string = "Copilot Diagnostic Test"
        pyperclip.copy(test_string)
        pasted = pyperclip.paste()
        if pasted == test_string:
            report.append("  -> Pyperclip copy/paste: OK")
        else:
            report.append(f"  -> Pyperclip copy/paste: FAILED (Expected '{test_string}', got '{pasted}')")
    except Exception as e:
        report.append("  -> Pyperclip copy/paste: FAILED")
        report.append(f"     Traceback:\n{traceback.format_exc()}")
        
    # 5. Check Environment Config
    report.append("\n[5] Checking Environment Configuration (.env)...")
    if os.path.exists(".env"):
        report.append("  -> .env file exists: OK")
        try:
            from dotenv import load_dotenv
            load_dotenv()
            api_key = os.getenv("GEMINI_API_KEY")
            threshold = os.getenv("AUDIO_THRESHOLD")
            device_id = os.getenv("AUDIO_DEVICE_ID")
            
            report.append(f"  -> GEMINI_API_KEY set: {'Yes (Length: ' + str(len(api_key)) + ')' if api_key else 'No'}")
            report.append(f"  -> AUDIO_THRESHOLD: {threshold}")
            report.append(f"  -> AUDIO_DEVICE_ID: {device_id}")
        except Exception as e:
            report.append(f"  -> Reading .env: FAILED (Error: {e})")
    else:
        report.append("  -> .env file exists: FAILED (.env file missing)")

    report.append("\n==========================================")
    
    # Save report
    with open("diagnostic_results.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(report))
        
    print("Diagnostics complete. Saved to 'diagnostic_results.txt'.")

if __name__ == "__main__":
    run_diagnostics()
