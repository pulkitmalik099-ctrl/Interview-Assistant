import time
import sounddevice as sd
import numpy as np

def test_devices():
    print("==================================================")
    print("          MICROPHONE DIAGNOSTIC UTILITY           ")
    print("==================================================")
    print("Please speak steadily into your microphone...")
    print("Testing all input devices for active signals...\n")
    
    devices = sd.query_devices()
    input_devices = []
    
    for idx, d in enumerate(devices):
        if d['max_input_channels'] > 0:
            input_devices.append((idx, d['name']))
            
    if not input_devices:
        print("ERROR: No input devices/microphones found on this system!")
        return

    active_device = None
    max_detected_rms = 0.0
    
    for idx, name in input_devices:
        print(f"Testing Device ID {idx}: {name}...")
        try:
            # Record 1.5 seconds of audio
            duration = 1.5
            fs = 16000
            recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, device=idx)
            sd.wait() # Wait until recording is finished
            
            # Calculate RMS
            clean_rec = recording - np.mean(recording)
            rms = np.sqrt(np.mean(clean_rec**2))
            
            print(f"   -> Signal Level (RMS): {rms:.5f}")
            if rms > max_detected_rms:
                max_detected_rms = rms
                if rms > 0.005:  # Consider it active if it registers a signal above static noise
                    active_device = idx
        except Exception as e:
            print(f"   -> Failed to record: {e}")
            
    print("\n================ DIAGNOSTIC REPORT ================")
    if active_device is not None:
        print(f"RECOMMENDED DEVICE ID: {active_device}")
        print(f"Signal Strength Registered: {max_detected_rms:.5f}")
        print("\nHow to configure:")
        print(f"1. Open your .env file")
        print(f"2. Set AUDIO_DEVICE_ID={active_device}")
        print(f"3. Set AUDIO_THRESHOLD={max_detected_rms * 0.4:.3f} (for good speech detection)")
    else:
        print("NO ACTIVE SIGNAL DETECTED!")
        print("Please make sure your microphone is not muted in Windows Settings,")
        print("and check that your headset/AirPods are active and connected.")
    print("===================================================")

if __name__ == "__main__":
    test_devices()
