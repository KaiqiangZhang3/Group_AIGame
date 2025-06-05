import pygame
import sys
from src.settings import GameState

def events_handler(events, game_instance):   
    for event in events:
        event_handler(event, game_instance) # Handle events for the current state

def event_handler(event, game_instance):
    """Handle events for the current game state."""
    match event.type:
        case pygame.QUIT:
            pygame.quit()
            sys.exit()
        case pygame.KEYDOWN:
            keyboard_handler(event, game_instance)  # Delegate to keyboard handler
        case _:
            pass

def keyboard_handler(event, game_instance):
    """Handle keyboard input based on the current game state."""
    match game_instance.current_state:
        case GameState.PLAYING:  # Use Enum member
            # Special case for 'N' key to advance to next level
            if event.key == pygame.K_n:
                # Skip to next level immediately
                print("Skipping to next level...")
                game_instance.level_manager.next_level()
            else:
                game_instance.input_buffer.add_input(event.key)  # Buffer other key presses
        case _:
            game_instance.menu.handle_input(event)  # Assuming Menu has handle_input

def player_input(game_instance):
    """Process player input for the current game state."""
    match game_instance.current_state:
        case GameState.PLAYING:  # Use Enum member
            # Voice jump is now handled by Player.process_input via VOICE_COMMAND_JUMP in buffer
            # Process buffered keyboard/controller/voice inputs via Player class
            if game_instance.level_manager and game_instance.level_manager.level and game_instance.level_manager.level.player:
                game_instance.level_manager.level.player.process_input(game_instance.input_buffer)
        case _:
            pass  # No player input to process in other states

def draw_frame(game_instance, dt):
    """Draw a single frame of the game, using delta time for updates."""
    match game_instance.current_state:
        case GameState.MENU: # Use Enum member
            game_instance.menu.draw() # Use the interactive draw method
        case GameState.PLAYING: # Use Enum member
            if game_instance.level_manager.level:
                game_instance.level_manager.level.run(dt) # Update logic AND draw level content here, now with dt
            else:
                # Safety check: If in PLAYING state but no level, return to menu
                print("Warning: PLAYING state with no level loaded. Returning to menu.")
                game_instance.menu.return_to_menu()
        case GameState.DEATH_SCREEN: # Use Enum member
            game_instance.menu.draw_death_screen() # Placeholder call
        case GameState.GAME_OVER: # Use Enum member
            game_instance.menu.draw_game_over_screen() # Placeholder call
        case _:
            print("Unknown game state. Returning to menu.")
            game_instance.menu.return_to_menu()