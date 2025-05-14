import vosk
import sounddevice as sd
import threading
import json
import queue
import time # Added for sleep on error
from src.settings import VOSK_MODEL_PATH, VOSK_SAMPLE_RATE, VOSK_CHANNELS, VOSK_DEVICE_ID, VOICE_COMMAND_JUMP

class VoiceRecognizer:
    """Handles offline voice recognition using Vosk."""

    def __init__(self, input_buffer, model_path=VOSK_MODEL_PATH):
        """
        Initializes the Vosk model and recognizer.
        Args:
            input_buffer: An instance of the game's InputBuffer.
            model_path: Path to the Vosk language model directory.
        """
        self.input_buffer = input_buffer
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
        print("Vosk recognizer created. Listening for 'jump'...")

        detected_jump_in_current_segment = False

        while self._listening_flag:
            try:
                data = self.audio_queue.get(timeout=0.05)
                
                if self.recognizer.AcceptWaveform(data):
                    detected_jump_in_current_segment = False
                    result = json.loads(self.recognizer.Result())
                    command = result.get('text', '').lower()
                    print(f"Final recognized: {command}") 

                else:
                    partial_result = json.loads(self.recognizer.PartialResult())
                    partial_command = partial_result.get('partial', '').lower()

                    if "jump" in partial_command and not detected_jump_in_current_segment:
                        print("Vosk (partial): JUMP detected! Adding to input buffer.")
                        self.input_buffer.add_input(VOICE_COMMAND_JUMP)
                        detected_jump_in_current_segment = True

            except queue.Empty:
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
        # Dummy InputBuffer for testing
        class DummyInputBuffer:
            def __init__(self):
                self.inputs = []
            def add_input(self, command):
                print(f"InputBuffer received: {command}")
                self.inputs.append(command)
            def get_and_remove_input(self, command):
                if command in self.inputs:
                    self.inputs.remove(command)
                    return True
                return False

        test_input_buffer = DummyInputBuffer()
        recognizer = VoiceRecognizer(input_buffer=test_input_buffer, model_path=VOSK_MODEL_PATH)
        if recognizer.model: # Only start if model loaded
            recognizer.start_listening()
            print("Say 'jump'. Listening for 10 seconds...")
            try:
                time.sleep(10) # Listen for 10 seconds
            except KeyboardInterrupt:
                print("Test interrupted.")
            finally:
                recognizer.stop_listening()
                print("Test finished.")
        else:
            print("Could not run test: Vosk model failed to load.")
