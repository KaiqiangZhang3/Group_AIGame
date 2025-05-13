import pygame
import sys
from src.settings import *

class Menu:
    """Handles the main menu screen and input."""
    def __init__(self, game_instance):
        self.display_surface = game_instance.screen
        self.game = game_instance

        self.font = pygame.font.Font(None, MENU_FONT_SIZE)

        self.selected_option = 0
        self.option_rects = []

        self._update_options_list() 
        self._setup_options()

    def _update_options_list(self):
        """Updates the list of menu options, including the dynamic voice toggle text."""
        voice_status = "ON" if self.game.voice_recognition_enabled else "OFF"
        self.options = [
            "Start Game",
            f"Voice Recognition: {voice_status}",
            "Exit"
        ]

    def _setup_options(self):
        """Calculates the positions for menu options."""
        self.option_rects = []
        total_height = 0
        temp_surfs = []
        for option_text in self.options:
            surf = self.font.render(option_text, True, WHITE) 
            temp_surfs.append(surf)
            total_height += surf.get_height() + 15 
        total_height -= 15 

        start_y = (SCREEN_HEIGHT - total_height) // 2
        current_y = start_y

        for i, option_text in enumerate(self.options):
            text_surf = temp_surfs[i] 
            text_rect = text_surf.get_rect(center=(SCREEN_WIDTH / 2, current_y + text_surf.get_height() / 2))
            self.option_rects.append(text_rect)
            current_y += text_surf.get_height() + 15 

    def draw(self):
        """Draws the menu options on the screen."""
        self.display_surface.fill(BLACK)
        self._update_options_list() 
        for i, option_text in enumerate(self.options):
            color = RED if i == self.selected_option else WHITE
            text_surf = self.font.render(option_text, True, color)
            if i < len(self.option_rects):
                text_rect = self.option_rects[i]
            else:
                text_rect = text_surf.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + i * 60))
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
            elif event.key == pygame.K_v: 
                for i, option_text in enumerate(self.options):
                    if "Voice Recognition" in option_text:
                        self.selected_option = i
                        self.select_option()
                        break
            elif event.key == pygame.K_r: 
                if self.game.level_manager.level:
                    self.game.level_manager.level.reset_player_to_respawn()
            elif event.key == pygame.K_m: 
                self.return_to_menu() 

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
        self._update_options_list() 
        selected_text = self.options[self.selected_option]
        print(f"Menu option selected: {selected_text}")

        if selected_text == "Start Game":
            self.game.level_manager.game_entry() 
            if self.game.voice_recognition_enabled and self.game.voice_recognizer.model:
                self.game.try_start_voice_recognition()
        elif "Voice Recognition" in selected_text:
            self.game.voice_recognition_enabled = not self.game.voice_recognition_enabled
            if self.game.voice_recognition_enabled:
                if self.game.voice_recognizer.model:
                    print("Menu: Enabling and starting voice recognition.")
                    self.game.try_start_voice_recognition()
                else:
                    print("Menu: Cannot enable voice recognition, Vosk model not loaded.")
                    self.game.voice_recognition_enabled = False 
            else:
                print("Menu: Disabling and stopping voice recognition.")
                self.game.try_stop_voice_recognition()
            self._update_options_list() 
            self._setup_options()     
        elif selected_text == "Exit":
            pygame.quit()
            sys.exit()

    def return_to_menu(self):
        """Return to the main menu."""
        print("Returning to menu...")
        if self.game.level_manager.level:
             self.game.level_manager.level.reset_checkpoints() 
             self.game.level_manager.level = None 
        self.game.level_manager.current_level_index = 0 
        self.game.current_state = GameState.MENU 
