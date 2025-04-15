import pygame
import sys
from .settings import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, RED, BLACK, MENU_FONT_SIZE

class Menu:
    """Handles the main menu screen and input."""
    def __init__(self, surface, game_instance):
        self.display_surface = surface
        self.game = game_instance

        self.font = pygame.font.Font(None, MENU_FONT_SIZE)

        self.options = ["Start Game", "Exit"]
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
            color = RED if i == self.selected_option else WHITE
            text_surf = self.font.render(option, True, color)
            text_rect = self.option_rects[i]
            self.display_surface.blit(text_surf, text_rect)

    def handle_input(self, event):
        """Handles keyboard and mouse input for the menu."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP or event.key == pygame.K_w:
                self.selected_option = (self.selected_option - 1) % len(self.options)
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                self.selected_option = (self.selected_option + 1) % len(self.options)
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                self.select_option()

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
        selected_text = self.options[self.selected_option]
        print(f"Menu option selected: {selected_text}")

        if selected_text == "Start Game":
            self.game.load_level(0) 
        elif selected_text == "Exit":
            pygame.quit()
            sys.exit()
