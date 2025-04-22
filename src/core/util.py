import pygame
import sys
import cv2      # Import OpenCV
import numpy as np # Import numpy for array manipulation
from src.settings import GameState, VOICE_COMMAND_EVENT, NEXT_LEVEL_VOICE_EVENT, BLACK, SCREEN_WIDTH, SINGING_DETECTED_EVENT, SINGING_EFFECT_DURATION

# Define VOICE_COMMAND_EVENT here or import it reliably
# Defining it here for simplicity, but ideally it should be in a shared location like settings

def events_handler(game, event):
    """Handles all Pygame events."""
    # Removed the loop: pygame.event.get() is now handled in game.run()
    # We process the single event passed to this function

    if event.type == pygame.QUIT:
        pygame.quit()
        sys.exit()
    elif event.type == pygame.KEYDOWN:
        keyboard_handler(event, game)  # Delegate to keyboard handler
    elif event.type == VOICE_COMMAND_EVENT:
        print("Received JUMP event from voice listener in events_handler.") # Optional debug
        # Only jump if the game is in the PLAYING state and player exists
        if game.current_state == GameState.PLAYING and game.level_manager.level and game.level_manager.level.player:
            # Call jump directly, bypassing the input buffer for immediate voice response
            print("Triggering jump directly from voice event.") # Optional debug
            game.level_manager.level.player.movement_state.jump()
            # Alternatively, if jump should be immediate regardless of buffer:
            # game.level_manager.level.player.movement_state.jump()
    elif event.type == NEXT_LEVEL_VOICE_EVENT:
        print("Received NEXT_LEVEL event from voice listener.") # Optional debug
        # Only advance level if in PLAYING state
        if game.current_state == GameState.PLAYING:
            print("Advancing to next level via voice command.")
            game.level_manager.next_level() # Call the level manager's method
    elif event.type == SINGING_DETECTED_EVENT:
        # print("Event: Singing detected!") # Optional debug print
        if game.current_state == GameState.PLAYING and game.level_manager.level and game.level_manager.level.player:
            # Reset the timer on the player object
            game.level_manager.level.player.singing_effect_timer = SINGING_EFFECT_DURATION

def keyboard_handler(event, game):
    """Handle keyboard input based on the current game state."""
    match game.current_state:
        case GameState.PLAYING:  # Use Enum member
            game.input_buffer.add_input(event.key)  # Buffer the key press
        case _:
            game.menu.handle_input(event)  # Assuming Menu has handle_input

def player_input(game):
    """Process player input for the current game state."""
    match game.current_state:
        case GameState.PLAYING:  # Use Enum member
            # Player movement is handled by LevelManager based on buffered input
            # Handle continuous inputs (like holding left/right)
            keys = pygame.key.get_pressed() # Get currently held keys
            game.level_manager.level.player.process_input(game.input_buffer)  # Assuming player has process_input method
        case _:
            pass  # No player input to process in other states

def cv2_to_pygame_surface(cv2_image):
    """Convert an OpenCV image (BGR) to a Pygame surface (RGB)."""
    # Check if image is valid
    if cv2_image is None:
        return None
    # OpenCV uses BGR, Pygame uses RGB. Convert color space.
    rgb_image = cv2.cvtColor(cv2_image, cv2.COLOR_BGR2RGB)
    # OpenCV stores image data row by row, but Pygame needs it column by column (transposed).
    # Also, flip it vertically for correct orientation in Pygame.
    pygame_surface = pygame.surfarray.make_surface(np.rot90(rgb_image))
    # The above might display sideways depending on camera/opencv/pygame versions.
    # Alternative if the above is sideways:
    # pygame_surface = pygame.surfarray.make_surface(rgb_image.swapaxes(0, 1))
    return pygame_surface

def draw_frame(game):
    """Draws the current game frame based on the game state."""
    game.screen.fill(BLACK) # Clear screen with black background

    # Draw Camera Feed in top-right corner if camera is available
    camera_width = 160 # Desired display width for camera feed
    camera_height = 120 # Desired display height
    # Only draw if camera is enabled AND initialized
    if game.camera_enabled and game.cap and game.cap.isOpened():
        success, frame = game.cap.read() # Read a frame
        if success:
            # Convert and resize the frame
            frame = cv2.resize(frame, (camera_width, camera_height))
            pygame_surface = cv2_to_pygame_surface(frame)
            if pygame_surface:
                # Position camera feed in top right corner
                camera_x = SCREEN_WIDTH - camera_width - 10 # 10px padding
                camera_y = 10 # 10px padding
                game.screen.blit(pygame_surface, (camera_x, camera_y))
        else:
            # Optional: Draw a placeholder if reading fails
            pass

    # Draw based on game state
    match game.current_state:
        case GameState.MENU:
            game.menu.draw() # Call the method that uses the options list
        case GameState.PLAYING: # Use Enum member
            if game.level_manager.level:
                game.level_manager.level.run() # Update logic AND draw level content here
            else:
                # Safety check: If in PLAYING state but no level, return to menu
                print("Warning: PLAYING state with no level loaded. Returning to menu.")
                game.menu.return_to_menu()
        case GameState.DEATH_SCREEN: # Use Enum member
            game.menu.draw_death_screen() # Placeholder call
        case GameState.GAME_OVER: # Use Enum member
            game.menu.draw_game_over_screen() # Placeholder call
        case _:
            print("Unknown game state. Returning to menu.")
            game.menu.return_to_menu()