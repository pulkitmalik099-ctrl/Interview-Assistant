# Task List: AI Interview Assistant Upgrades

- [x] Update `requirements.txt` to add `pypdf` and `pyttsx3`
- [x] Install new package dependencies inside the virtual environment
- [x] Create `context/` directory in the workspace folder
- [x] Implement context scanning logic in `interview_assistant.py`
  - [x] Implement `load_context_data()` to scan TXT and PDF files
  - [x] Integrate context string into Gemini prompt instructions
- [x] Implement TTS audio feedback system in `interview_assistant.py`
  - [x] Implement `speak_answer_async()` background worker using `pyttsx3`
  - [x] Add `[TTS: OFF/ON]` toggle button to the GUI control bar
  - [x] Hook TTS execution to new answer generation results
- [x] Verify execution and sync modifications to GitHub
- [x] Document upgrades in `walkthrough.md`

## Phase 2: Speech Recognition & GUI Settings Modal
- [x] Add `SpeechRecognition` to `requirements.txt`
- [x] Update `interview_assistant.py` with `stop_audio_event` and graceful thread shutdown/restart
- [x] Implement `speech_recognition` transcription in `process_audio_with_gemini`
  - [x] Convert audio bytes and run `recognize_google`
  - [x] Update GUI immediately with transcribed question
- [x] Implement GUI Settings Modal
  - [x] Add `⚙` button to control bar
  - [x] Implement `open_settings` TopLevel dialog with API key, device list dropdown, threshold, and silence duration controls
  - [x] Implement `save_settings_to_env` and auto-restart of the audio monitor stream
- [/] Verify functionality in mock and real modes
- [ ] Sync all code changes to GitHub repository
