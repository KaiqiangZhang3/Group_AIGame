import vosk
import sounddevice as sd
import threading
import json
import queue
import time # Added for sleep on error
from src.settings import VOSK_MODEL_PATH, VOSK_SAMPLE_RATE, VOSK_CHANNELS, VOSK_DEVICE_ID, VOICE_COMMAND_PHRASES

class VoiceRecognizer:
    """Handles offline voice recognition using Vosk."""

    def __init__(self, game_instance, model_path=VOSK_MODEL_PATH):
        """
        Initializes the Vosk model and recognizer.
        Args:
            game_instance: An instance of the game's Game class.
            model_path: Path to the Vosk language model directory.
        """
        self.game_instance = game_instance
        self.model_path = model_path
        self.model = None
        self.recognizer = None
        self.stream = None
        self._listening_flag = False
        self.thread = None
        self.audio_queue = queue.Queue()

        try:
            if not VOSK_MODEL_PATH:
                raise ValueError("VOSK_MODEL_PATH is not set in settings.py")
            self.model = vosk.Model(self.model_path)
            print(f"Vosk model loaded successfully from {self.model_path}")
        except Exception as e:
            print(f"Error loading Vosk model from '{self.model_path}': {e}")
            print("Please ensure VOSK_MODEL_PATH in settings.py points to a valid Vosk model directory.")
            print("You can download models from: https://alphacephei.com/vosk/models")
            self.model = None # Ensure model is None if loading failed

    def _process_audio(self):
        if not self.model:
            print("Vosk model not loaded. Cannot process audio.")
            self._listening_flag = False
            return

        self.recognizer = vosk.KaldiRecognizer(self.model, VOSK_SAMPLE_RATE)
        print("Vosk recognizer created. Listening...")

        while self._listening_flag:
            try:
                data = self.audio_queue.get(timeout=0.05)
                command_processed_from_partial = False

                # Process partial result for immediate commands
                # Check PartialResult only if data was actually fed for this iteration,
                # otherwise, it might return stale partials if AcceptWaveform wasn't true before.
                # However, AcceptWaveform itself consumes data, so we check partial *before* full AcceptWaveform.
                partial_result_json = self.recognizer.PartialResult()
                partial_result_dict = json.loads(partial_result_json)
                partial_text = partial_result_dict.get('partial', '').strip().lower()

                if partial_text: # Only process if there's actual partial text
                    # print(f"Vosk Partial: '{partial_text}'") # Optional: for debugging
                    for command_phrase in VOICE_COMMAND_PHRASES:
                        # Using '==' for exact match, suitable for simple commands like "jump"
                        if partial_text == command_phrase:
                            print(f"Vosk: Partial recognized command: '{command_phrase}'")
                            if self.game_instance:
                                self.game_instance.handle_recognized_speech(command_phrase)
                            # IMPORTANT: Reset the recognizer to prevent this segment
                            # from being re-processed by recognizer.Result() or stale partials.
                            self.recognizer.Reset() 
                            command_processed_from_partial = True
                            break # Command found and processed, exit loop
                
                if command_processed_from_partial:
                    # If a command was handled from partial, we might want to clear the audio queue
                    # or just continue to avoid processing the same audio chunk again with Result().
                    # For now, just continue, as Reset() should prevent re-processing of the *recognized text*.
                    continue 

                # Process full result (if no command from partial or if partial was empty)
                if self.recognizer.AcceptWaveform(data):
                    result_json = self.recognizer.Result()
                    result_dict = json.loads(result_json)
                    recognized_text = result_dict.get('text', '').strip().lower()
                    
                    # print(f"Vosk Final recognized: '{recognized_text}'") 
                    if self.game_instance and recognized_text: # Ensure text is not empty
                        self.game_instance.handle_recognized_speech(recognized_text)
                # else:
                    # For debugging, can print partial result if not a full phrase yet
                    # partial_result_debug = json.loads(self.recognizer.PartialResult())
                    # if partial_result_debug.get('partial', ''):
                    #     print(f"Vosk Partial (no full phrase yet): '{partial_result_debug['partial']}'")

            except queue.Empty:
                # This is normal, means no audio data in the queue for this timeout period
                continue
            except Exception as e:
                print(f"Error in Vosk audio processing: {e}")
                time.sleep(0.1)

    def _audio_callback(self, indata, frames, time, status):
        """This is called (from a separate thread) for each audio block."""
        if status:
            print(f"Sounddevice status: {status}")
        self.audio_queue.put(bytes(indata))

    def start_listening(self):
        """Starts listening for voice commands in a background thread."""
        if not self.model: # Don't start if model failed to load
            print("Cannot start listening: Vosk model not loaded.")
            return
        if self.is_listening():
            print("Already listening.")
            return

        self._listening_flag = True
        try:
            # Query devices if VOSK_DEVICE_ID is None to help user choose
            if VOSK_DEVICE_ID is None:
                print("Available audio input devices:")
                print(sd.query_devices())
                print("Please set VOSK_DEVICE_ID in settings.py if default is not correct.")
                # Attempt to use default device
                device_id_to_use = sd.default.device[0] 
            else:
                device_id_to_use = VOSK_DEVICE_ID

            self.stream = sd.InputStream(
                samplerate=VOSK_SAMPLE_RATE,
                channels=VOSK_CHANNELS,
                dtype='int16', # Vosk expects 16-bit PCM
                device=device_id_to_use, 
                callback=self._audio_callback,
                blocksize=400,
            )
            self.stream.start()
            print(f"Sounddevice stream started on device ID {device_id_to_use} with samplerate {VOSK_SAMPLE_RATE}.")
        except Exception as e:
            print(f"Error starting sounddevice stream: {e}")
            self._listening_flag = False
            return

        self.thread = threading.Thread(target=self._process_audio, daemon=True)
        self.thread.start()
        print("Voice recognizer thread started.")

    def stop_listening(self):
        """Stops listening for voice commands."""
        if not self.is_listening():
            # print("Not currently listening.")
            return
        
        print("Stopping voice recognizer...")
        self._listening_flag = False # Signal the processing thread to stop

        if self.stream:
            try:
                self.stream.stop()
                self.stream.close()
                print("Sounddevice stream stopped and closed.")
            except Exception as e:
                print(f"Error stopping sounddevice stream: {e}")
            self.stream = None
        
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1.0) # Wait for the thread to finish
            if self.thread.is_alive():
                print("Voice recognizer thread did not stop in time.")
        self.thread = None
        # Clear the queue in case there's lingering data
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
            except queue.Empty:
                break
        print("Voice recognizer stopped.")

    def is_listening(self):
        """Returns True if the recognizer is actively listening, False otherwise."""
        return self._listening_flag and self.thread is not None and self.thread.is_alive()

# Example Usage (for testing this module directly, not part of the game integration)
if __name__ == '__main__':
    import time
    # Create a dummy VOSK_MODEL_PATH in settings.py or override here for testing
    # For example, if you downloaded 'vosk-model-small-en-us-0.15' and unzipped it
    # in your project root:
    # test_model_path = "vosk-model-small-en-us-0.15"
    
    # This will fail if VOSK_MODEL_PATH is not correctly set in settings.py
    # or if the model isn't downloaded to that path.
    if not VOSK_MODEL_PATH or VOSK_MODEL_PATH == "path/to/your/vosk-model-en-us": # Default placeholder
        print("Skipping __main__ test: VOSK_MODEL_PATH is not configured or is a placeholder.")
        print("Please download a Vosk model and update VOSK_MODEL_PATH in settings.py.")
    else:
        class DummyGameInstance:
            def __init__(self):
                self.input_buffer = []
            def handle_recognized_speech(self, text):
                print(f"DummyGameInstance received speech: '{text}'")
                # Simplified test: if 'jump' in text, add to buffer
                if "jump" in text:
                    self.input_buffer.append("VOICE_JUMP") # Use a placeholder if VOICE_COMMAND_JUMP is not imported

        test_game_instance = DummyGameInstance()
        recognizer = VoiceRecognizer(game_instance=test_game_instance, model_path=VOSK_MODEL_PATH)
        if recognizer.model: # Only start if model loaded
            recognizer.start_listening()
            print("Say something. Listening for 10 seconds...")
            try:
                time.sleep(10) # Listen for 10 seconds
            except KeyboardInterrupt:
                print("Test interrupted.")
            finally:
                recognizer.stop_listening()
                print("Test finished.")
        else:
            print("Could not run test: Vosk model failed to load.")
