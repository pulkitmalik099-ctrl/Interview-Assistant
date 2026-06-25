# Walkthrough: AI Interview Copilot (Upgraded)

We have successfully upgraded the AI Interview Copilot by incorporating key features inspired by the `nohairblingbling` repository:
1. **📁 Custom Knowledge Base**: Automatically scanning a local `context/` folder, extracting text from resumes or study guides (supporting `.txt` and `.pdf` files), and injecting it into the Gemini API prompt.
2. **🔊 Optional Text-To-Speech (TTS)**: An audio toggle switch in the overlay control bar to whisper suggested responses into your earphones in a background thread using the offline Windows voice synthesizer.
3. **🎙️ Free speech-to-text transcription**: Uses Google's free Web Speech API locally (via the `SpeechRecognition` library) to transcribe your questions on the fly with **zero API key requirements or costs**. Your transcribed question is displayed instantly, even in Mock Mode or when the Gemini API key is missing.
4. **⚙️ Interactive Settings Panel**: A settings gear button (`⚙`) in the control bar allows you to select your audio input device from a dropdown list, paste your Gemini API key securely, and calibrate the VAD threshold/silence duration. Saving settings writes them back to your `.env` file and restarts the audio engine dynamically!
5. **📐 Auto-Resizing Window & Reader-Friendly Typography**: The overlay window height automatically adjusts to fit suggested answers (up to a reasonable max height), eliminating manual scrolling. Text is rendered using a clean `Segoe UI` font with paragraph line spacing and formatted bold/bullet elements (stripping raw Markdown symbols).

The codebase and launcher are fully synchronized to your repository:
🔗 [Interview-Assistant Repo](https://github.com/pulkitmalik099-ctrl/Interview-Assistant)

---

## ⚙️ 1. Interactive Settings Panel & Calibration

1. Run the Copilot using **`run.bat`** (either Real Mode or Offline Mock Test Mode).
2. Click the gear icon (**`⚙`**) on the control bar.
3. A styling-matching **Configuration Settings** modal window will open.
4. **Configure Settings**:
   - **Gemini API Key**: Paste your key here (e.g. from [Google AI Studio](https://aistudio.google.com/)). You can check the *Show API Key* box to verify it.
   - **Audio Input Device**: Choose your exact microphone (e.g., your built-in *Microphone Array* or connected *AirPods*) directly from the dropdown. No command-line ID lookups needed!
   - **Sensitivity (Threshold)**: Adjust how easily the VAD triggers. If the bulb gets stuck on `RECORDING` from static noise, increase this (e.g., to `0.012` or `0.015`). If it doesn't pick up your voice, decrease it (e.g., to `0.005` or `0.007`).
   - **Silence Duration**: The duration of silence in seconds that determines when you've finished asking the question.
5. Click **`Save Settings`**: The new config is saved to your `.env` file, the active variables are updated, and the audio recording thread is gracefully stopped and restarted with the new microphone and sensitivity values instantly.

---

## 🎙️ 2. Free Speech Recognition Fallback

Even if you have no Gemini API key set:
1. Speak a question into your microphone.
2. Once silence is reached, the VAD engine will record, pack the WAV, and transcribe it using a free Google Web Speech API.
3. **Immediate Question Print**: Your exact spoken question will show up in the **`LAST QUESTION:`** label immediately!
4. **Missing Key Handling**: If your Gemini API Key is not set, the **`SUGGESTED ANSWER:`** panel will show a friendly reminder prompting you to open settings and configure your key, while still proving that your audio stream, VAD, and transcription are fully operational.
5. **Text-Based Gemini Query**: Once you set your API key, the assistant sends the transcribed *text* to Gemini rather than raw audio bytes. This results in **significantly faster answers, lower latency, and reduced bandwidth usage**.

---

## 📁 3. Using Custom Context (Resume / PDF Scanner)

1. Navigate to your workspace directory `c:\Users\Niyu\Downloads\Learning\Practical\`.
2. Locate the folder named **`context/`**.
3. Copy and paste your **resume (PDF or TXT)**, cover letter, cheat-sheets, or specific preparation documents into this folder.
4. Run the Copilot.
5. **Startup Verification**: On startup, the console window will list the loaded files:
   ```text
   === Configuration ===
   Device: 1
   Threshold: 0.007
   Mock Mode: Enabled
   Custom Context Loaded: Yes (3150 chars)
   ```
6. **AI Customization**: When you ask a question, Gemini will automatically cross-reference your uploaded files to answer from your experience!

---

## 🔊 4. Using Text-To-Speech (TTS) Whispering

1. On the control bar, click the red button **`[TTS: OFF]`**. It will turn green and read **`[TTS: ON]`**.
2. You will hear an offline computer voice whisper *"Voice feedback activated"* through your audio output/earphones.
3. Speak a question and stop talking.
4. As soon as the generated answer is suggested, the background thread will read the response points aloud to you automatically.
5. Click **`[TTS: ON]`** again to toggle it back to **`OFF`** at any time.

---

## 🎮 General Controls & Interface

- **🎤 HEADER BAR**: Click and hold to **drag the window** anywhere on your desktop screen.
- **✕ (Close)**: Exits the application and shuts down all audio/TTS threads.
- **⛶ (Compact/Restore)**: Toggle to shrink the window into a small 160x40 pixel widget showing only the live state bulb and volume meter.
- **Status Indicator**:
  - `LISTENING` (Green): Monitoring silence/voice activity.
  - `RECORDING...` (Red): Active speaking segment is being captured.
  - `THINKING...` (Orange): Simulating/generating answer.
  - `ANSWER READY` (Blue): Displaying the transcribed question and suggested response.
- **Save**: Open a styled file explorer dialog to export the full conversation transcript as a `.txt` file.
- **Automatic Clipboard**: Any generated answer is automatically copied to your clipboard so you can paste it instantly (`Ctrl + V`).
- **Session log**: Every query and response is appended in real-time to a local file `interview_session.log` as a permanent back-up.
