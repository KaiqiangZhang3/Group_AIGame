import pygame
from src.settings import GameState, SCREEN_WIDTH, SCREEN_HEIGHT, FPS, VOICE_COMMAND_EVENT, NEXT_LEVEL_VOICE_EVENT, SINGING_DETECTED_EVENT, SINGING_PITCH_STD_THRESHOLD
from src.ui.menu import Menu
from src.levels.level_manager import LevelManager
from src.core.util import events_handler, draw_frame, player_input
from src.core.input_buffer import InputBuffer
import speech_recognition as sr
import threading
import time
import cv2
import librosa # Import librosa
import numpy as np # Import numpy

class Game:
    """Main game class managing states, levels, and menus."""
    def __init__(self):
        """Initialize Pygame, display, clock, and game state."""
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Game with Voice & Camera") # Update caption
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 74) # Fallback
        self.small_font = pygame.font.SysFont(None, 36)
        print("Starting game...")

        self.input_buffer = InputBuffer() # Initialize input buffer
        self.current_state = GameState.MENU # Start in the menu
        self.menu = Menu(self)
        self.level_manager = LevelManager(self) # Pass self to LevelManager

        # Camera state (initially off)
        self.camera_enabled = False
        self.cap = None # Camera object, initially None

        # Start voice command listener thread
        self.listener_thread = threading.Thread(target=self.listen_for_commands, daemon=True)
        self.listener_thread.start()

    def run(self):
        while True:
            # --- Event Handling ---
            for event in pygame.event.get():
                events_handler(self, event) # Pass the current event

            # --- Logic/Updates --- (Should happen after event processing)
            player_input(self) # Process player input based on the current state (using buffered input)

            # --- Drawing --- (Should happen after logic updates)
            draw_frame(self) # Draw the current frame based on state

            # --- Buffer Cleanup ---
            self.input_buffer.clear_expired_inputs() # Clear expired inputs from the buffer

            # --- Final Update --- 
            pygame.display.flip() # Update the full display surface once per frame
            self.clock.tick(FPS)

        if self.cap:
            print("Releasing webcam.")
            self.cap.release() # Release the camera

    # Add the voice listener method here
    def listen_for_commands(self):
        """Listens for audio, analyzes for singing vs speech, and processes commands."""
        recognizer = sr.Recognizer()
        microphone = sr.Microphone()

        # Adjust for ambient noise once at the start
        with microphone as source:
            recognizer.adjust_for_ambient_noise(source, duration=1)
            print("Listening for commands...")

        while True:
            with microphone as source:
                try:
                    print("Listening... ", end="", flush=True)
                    # Listen for audio input (adjust timeout as needed)
                    # Increased timeout slightly to allow for slightly longer phrases/singing snippets
                    audio = recognizer.listen(source, timeout=7, phrase_time_limit=7)

                    # --- Librosa Analysis --- START --- 
                    # Get raw audio data
                    raw_data = audio.get_raw_data()
                    sample_rate = audio.sample_rate
                    sample_width = audio.sample_width

                    # Convert raw bytes to numpy array (assuming 16-bit PCM)
                    # TODO: Make dtype dependent on sample_width if needed
                    if sample_width == 2:
                        y = np.frombuffer(raw_data, dtype=np.int16)
                    else:
                        print(f"\nUnsupported sample width: {sample_width}. Skipping analysis.")
                        continue # Skip this audio chunk

                    # Convert to float and normalize
                    y = y.astype(np.float32) / np.iinfo(np.int16).max

                    # Estimate pitch (fundamental frequency f0)
                    # pyin provides f0, voiced_flag, voiced_probabilities
                    f0, voiced_flag, voiced_probs = librosa.pyin(y, 
                                                                  fmin=librosa.note_to_hz('C2'), 
                                                                  fmax=librosa.note_to_hz('C7'), 
                                                                  sr=sample_rate)

                    # Calculate standard deviation of pitch for voiced segments
                    # Use nanstd to ignore NaNs where pitch is not detected (unvoiced)
                    pitch_std_dev = np.nanstd(f0[voiced_flag])
                    # --- Librosa Analysis --- END --- 

                    # --- Classification & Command Recognition --- 
                    is_singing = False
                    if np.isnan(pitch_std_dev):
                        # If pitch variance calculation failed (e.g., mostly silence/unvoiced)
                        # Treat as potential speech for now, let recognizer decide
                        print("(Pitch unclear) ", end="", flush=True)
                        is_singing = False 
                    elif pitch_std_dev < SINGING_PITCH_STD_THRESHOLD:
                        print(f"Singing detected! (Pitch Std Dev: {pitch_std_dev:.2f})", flush=True)
                        is_singing = True
                        # Post event when singing is detected
                        pygame.event.post(pygame.event.Event(SINGING_DETECTED_EVENT))
                    else:
                        print(f"Speech detected. (Pitch Std Dev: {pitch_std_dev:.2f}) ", end="", flush=True)
                        is_singing = False

                    # Only try to recognize commands if classified as speech
                    if not is_singing:
                        try:
                            command = recognizer.recognize_google(audio).lower()
                            print(f"-> Recognized: '{command}'", flush=True)

                            # Post custom event for recognized commands
                            if "jump" in command:
                                pygame.event.post(pygame.event.Event(VOICE_COMMAND_EVENT, {'command': 'jump'}))
                            elif "next level" in command:
                                pygame.event.post(pygame.event.Event(NEXT_LEVEL_VOICE_EVENT))
                            # Add other commands here if needed
                        except sr.UnknownValueError:
                            print("-> Could not understand audio", flush=True)
                        except sr.RequestError as e:
                            print(f"\nCould not request results from Google service; {e}")

                except sr.WaitTimeoutError:
                    print(".", end="", flush=True) # Indicate listening periods without speech
                    pass # Continue listening
                except sr.RequestError as e:
                    print(f"Could not request results from speech recognition service; {e}")

    def enable_camera(self):
        """Tries to initialize and enable the camera."""
        if not self.cap:
            print("Attempting to enable camera...")
            self.cap = cv2.VideoCapture(0) # Try to open default webcam
            if self.cap and self.cap.isOpened():
                self.camera_enabled = True
                print("Webcam opened successfully.")
            else:
                print("Error: Could not open webcam.")
                self.cap = None # Ensure cap is None if failed
                self.camera_enabled = False
        else:
            # Camera already initialized, just ensure flag is set
            self.camera_enabled = True

    def disable_camera(self):
        """Disables and releases the camera."""
        print("Disabling camera...")
        if self.cap:
            self.cap.release()
            self.cap = None
        self.camera_enabled = False

    def toggle_camera(self):
        """Toggles the camera state between enabled and disabled."""
        if self.camera_enabled:
            self.disable_camera()
        else:
            self.enable_camera()

# This check ensures the game runs only when the script is executed directly
if __name__ == '__main__':
    game = Game()
    game.run()