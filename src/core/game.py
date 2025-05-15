import pygame
from src.settings import *
from src.ui.menu import Menu
from src.levels.level_manager import LevelManager
from src.core.util import events_handler, draw_frame, player_input
from src.core.input_buffer import InputBuffer
from src.core.voice_recognizer import VoiceRecognizer

class Game:
    """Main game class managing states, levels, and menus."""
    def __init__(self):
        """Initialize Pygame, display, clock, and game state."""
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(GAME_NAME) # Set a window title
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 74) # Fallback
        self.small_font = pygame.font.SysFont(None, 36)
        print("Starting game...")

        self.input_buffer = InputBuffer() # Initialize input buffer
        self.current_state = GameState.MENU # Start in the menu

        # Initialize voice recognition enabled flag before Menu instantiation
        self.voice_recognition_enabled = VOICE_RECOGNITION_ENABLED_BY_DEFAULT

        self.menu = Menu(self)
        self.level_manager = LevelManager(self) # Pass self to LevelManager

        # Voice recognition setup
        self.voice_recognizer = VoiceRecognizer(game_instance=self) # Pass self (game_instance)
        if self.voice_recognizer.model:
            if self.voice_recognition_enabled:
                print("Game: Vosk model loaded, voice recognition enabled and starting.")
                self.voice_recognizer.start_listening()
            else:
                print("Game: Vosk model loaded, but voice recognition is disabled by default.")
        else:
            print("Game: Vosk model not loaded, voice commands will be disabled regardless of toggle.")
            self.voice_recognition_enabled = False # Force disable if model isn't there

    def try_start_voice_recognition(self):
        """Starts voice recognition if enabled, model loaded, and not already listening."""
        if self.voice_recognition_enabled and self.voice_recognizer and self.voice_recognizer.model:
            if not self.voice_recognizer.is_listening():
                print("Game: Starting voice recognition...")
                self.voice_recognizer.start_listening()
            else:
                print("Game: Voice recognition already active.")
        elif not self.voice_recognizer.model:
            print("Game: Cannot start voice recognition, Vosk model not loaded.")
        else:
            print("Game: Voice recognition is disabled by toggle.")

    def try_stop_voice_recognition(self):
        """Stops voice recognition if it's currently active."""
        if self.voice_recognizer and self.voice_recognizer.is_listening():
            print("Game: Stopping voice recognition...")
            self.voice_recognizer.stop_listening()
        else:
            print("Game: Voice recognition is not currently active or recognizer not initialized.")

    def handle_recognized_speech(self, text):
        """Processes recognized speech, distinguishing commands from ambient speech."""
        if not text: # Ignore empty speech results
            return

        normalized_text = text.strip().lower()
        print(f"Game handling speech: '{normalized_text}'")

        # Check if the recognized text is a predefined command
        if normalized_text in VOICE_COMMAND_PHRASES:
            # Handle known commands (currently only "jump")
            if normalized_text == "jump": # Assuming "jump" is in VOICE_COMMAND_PHRASES
                print(f"Game: Recognized command '{normalized_text}'. Adding to input buffer.")
                self.input_buffer.add_input(VOICE_COMMAND_JUMP)
            # Add other commands here if needed, e.g.:
            # elif normalized_text == "dash":
            #     self.input_buffer.add_input(VOICE_COMMAND_DASH) 
        else:
            # If not a command, treat as ambient speech for light expansion
            # Ensure player exists and is part of the current level setup
            if self.current_state == GameState.PLAYING and self.level_manager and self.level_manager.level and self.level_manager.level.player:
                print(f"Game: Recognized ambient speech '{normalized_text}'. Notifying player.")
                self.level_manager.level.player.notify_ambient_speech()
            else:
                print(f"Game: Ambient speech '{normalized_text}' ignored (not in PLAYING state or player not ready).")

    def run(self):
        try:
            while True:
                dt = self.clock.tick(FPS) / 1000.0 # Calculate delta time in seconds

                # --- Event Handling ---
                events_handler(pygame.event.get(), self)
                player_input(self) # Process player input based on the current state
                draw_frame(self, dt) # Draw the current frame based on state, pass dt
                self.input_buffer.clear_expired_inputs() # Clear expired inputs from the buffer
                # --- Final Update --- 
                pygame.display.flip() # Update the full display surface once per frame
                # self.clock.tick(FPS) # dt calculation now handles this
        finally:
            # Ensure voice recognizer is stopped cleanly when game exits
            if hasattr(self, 'voice_recognizer') and self.voice_recognizer:
                print("Game: Stopping voice recognizer on exit...")
                self.voice_recognizer.stop_listening()