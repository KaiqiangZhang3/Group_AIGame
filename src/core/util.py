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
            game_instance.input_buffer.add_input(event.key)  # Buffer the key press
        case _:
            game_instance.menu.handle_input(event)  # Assuming Menu has handle_input

def player_input(game_instance):
    """Process player input for the current game state."""
    match game_instance.current_state:
        case GameState.PLAYING:  # Use Enum member
            game_instance.level_manager.level.player.process_input(game_instance.input_buffer)  # Assuming player has process_input method
        case _:
            pass  # No player input to process in other states

def draw_frame(game_instance):
    """Draw a single frame of the game."""
    match game_instance.current_state:
        case GameState.MENU: # Use Enum member
            game_instance.menu.draw_menu() # Placeholder call
        case GameState.PLAYING: # Use Enum member
            if game_instance.level_manager.level:
                game_instance.level_manager.level.run() # Update logic AND draw level content here
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