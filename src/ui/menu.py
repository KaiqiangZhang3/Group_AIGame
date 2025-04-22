import pygame
import sys
from src.settings import *

class Menu:
    """Handles the main menu screen and input."""
    def __init__(self, game_instance):
        self.display_surface = game_instance.screen
        self.game = game_instance

        self.font = pygame.font.Font(None, MENU_FONT_SIZE)

        # Define base menu options
        self.options = ["Start Game", "Toggle Camera", "Exit"]
        self.selected_option = 0
        self.option_rects = []

        self._setup_options()

    def _setup_options(self):
        """Calculates the positions for menu options."""
        self.option_rects = []
        total_height = len(self.options) * (MENU_FONT_SIZE + 20)
        start_y = (SCREEN_HEIGHT - total_height) // 2

        for i, option in enumerate(self.options):
            text_surf = self.font.render(option, True, WHITE)
            text_rect = text_surf.get_rect(center=(SCREEN_WIDTH / 2, start_y + i * (MENU_FONT_SIZE + 20)))
            self.option_rects.append(text_rect)

    def draw(self):
        """Draws the menu options on the screen."""
        self.display_surface.fill(BLACK)

        for i, option in enumerate(self.options):
            # Determine the text to display dynamically for camera option
            text_to_render = option
            if option == "Toggle Camera":
                status = "ON" if self.game.camera_enabled else "OFF"
                text_to_render = f"Camera: {status}"

            color = RED if i == self.selected_option else WHITE
            text_surf = self.font.render(text_to_render, True, color)
            text_rect = self.option_rects[i]
            self.display_surface.blit(text_surf, text_rect)

    def draw_menu(self):
        self.display_surface.fill(BLACK)
        title_text = self.game.font.render('Main Menu', True, WHITE)
        start_text = self.game.small_font.render('Press ENTER to Start', True, WHITE)
        quit_text = self.game.small_font.render('Press ESC to Quit', True, WHITE)
        self.display_surface.blit(title_text, title_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/3)))
        self.display_surface.blit(start_text, start_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2)))
        self.display_surface.blit(quit_text, quit_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 40)))

    def draw_death_screen(self):
        self.display_surface.fill(BLACK)
        death_text = self.game.font.render('You Died!', True, RED)
        respawn_text = self.game.small_font.render('Press [R] to Respawn', True, WHITE)
        menu_text = self.game.small_font.render('Press [M] for Main Menu', True, WHITE)
        self.display_surface.blit(death_text, death_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/3)))
        self.display_surface.blit(respawn_text, respawn_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2)))
        self.display_surface.blit(menu_text, menu_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 40)))

    def draw_game_over_screen(self):
        self.display_surface.fill(BLACK)
        over_text = self.game.font.render('All Levels Complete!', True, GREEN)
        menu_text = self.game.small_font.render('Press [M] for Main Menu', True, WHITE)
        self.display_surface.blit(over_text, over_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/3)))
        self.display_surface.blit(menu_text, menu_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2)))

    def handle_input(self, event):
        """Handles keyboard and mouse input for the menu."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP or event.key == pygame.K_w:
                self.selected_option = (self.selected_option - 1) % len(self.options)
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                self.selected_option = (self.selected_option + 1) % len(self.options)
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                self.select_option()
            elif event.key == pygame.K_r: # Respawn
                if self.game.level_manager.level:
                    self.game.level_manager.level.reset_player_to_respawn()
            elif event.key == pygame.K_m: # Return to Menu
                self.return_to_menu() # Handles level cleanup and state change

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: 
                mouse_pos = event.pos
                for i, rect in enumerate(self.option_rects):
                    if rect.collidepoint(mouse_pos):
                        self.selected_option = i
                        self.select_option()
                        break

        elif event.type == pygame.MOUSEMOTION:
             mouse_pos = event.pos
             for i, rect in enumerate(self.option_rects):
                 if rect.collidepoint(mouse_pos):
                     self.selected_option = i
                     break

    def select_option(self):
        """Executes the action for the selected menu option."""
        # Get the base option identifier (not the dynamic text)
        base_option_text = self.options[self.selected_option]
        print(f"Menu option selected: {base_option_text}")

        if base_option_text == "Start Game":
            self.game.level_manager.game_entry() # Load the first level
        elif base_option_text == "Toggle Camera":
            self.game.toggle_camera() # Call the toggle method in Game class
            # We need to recalculate menu layout if text length changes significantly, but ON/OFF should be similar
            # self._setup_options() # Optional: Recalculate if needed
        elif base_option_text == "Exit":
            pygame.quit()
            sys.exit()

    def return_to_menu(self):
        """Return to the main menu."""
        print("Returning to menu...")
        if self.game.level_manager.level:
             self.game.level_manager.level.reset_checkpoints() # Reset checkpoints before leaving
             self.game.level_manager.level = None # Unload the level
        self.game.level_manager.current_level_index = 0 # Reset level index? Optional.
        self.game.current_state = GameState.MENU # Use Enum member
