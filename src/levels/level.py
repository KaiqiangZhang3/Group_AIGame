import pygame
from src.settings import *
from src.levels.tile import Tile
from src.player.player import Player
from src.entities.moving_spike import MovingSpike

class Level:
    """Manages the game level, including tiles, player, and interactions."""
    def __init__(self, level_data, surface, game_instance):
        self.display_surface = surface
        self.world_shift = 0
        self.game = game_instance

        # map size
        self.level_width = len(level_data[0]) * TILE_SIZE
        self.level_height = len(level_data) * TILE_SIZE

        # Sprite group setup
        self.visible_sprites = YSortCameraGroup(self.level_width, self.level_height)
        self.obstacle_sprites = pygame.sprite.Group()
        self.exit_sprites = pygame.sprite.Group()
        self.trap_sprites = pygame.sprite.Group()
        self.checkpoint_sprites = pygame.sprite.Group()

        # Player spawn and checkpoint tracking
        self.initial_player_pos = None
        self.last_checkpoint_pos = None
        self.player = None

        # Full illumination state
        self.full_illumination_active = False
        self.full_illumination_current_alpha = DARKNESS_COLOR[3] # Start with default darkness alpha

        self.setup_level(level_data)

    def setup_level(self, layout):
        """Creates tiles and player based on the layout."""
        # Clear groups and reset state for new level load
        self.visible_sprites.empty()
        self.obstacle_sprites.empty()
        self.exit_sprites.empty()
        self.trap_sprites.empty()
        self.checkpoint_sprites.empty()
        self.initial_player_pos = None
        self.last_checkpoint_pos = None
        self.player = None

        # Reset full illumination state on level setup/reset
        self.full_illumination_active = False
        self.full_illumination_current_alpha = DARKNESS_COLOR[3] # Reset to default darkness alpha

        for row_index, row in enumerate(layout):
            for col_index, cell in enumerate(row):
                x = col_index * TILE_SIZE
                y = row_index * TILE_SIZE
                pos = (x, y)

                if cell == 'X':
                    Tile(pos, [self.visible_sprites, self.obstacle_sprites], tile_type='platform')
                elif cell == 'S':
                    Tile(pos, [self.visible_sprites, self.trap_sprites], tile_type='trap')
                elif cell == 'E':
                    Tile(pos, [self.visible_sprites, self.exit_sprites], tile_type='exit')
                elif cell == 'C': 
                    # Checkpoint should NOT be an obstacle
                    tile = Tile(pos, [self.visible_sprites], tile_type='checkpoint') 
                    self.checkpoint_sprites.add(tile) # Add ONLY to the dedicated checkpoint group
                elif cell == 'M': 
                    # Create platform below the moving spike's path
                    Tile((x, y), [self.visible_sprites, self.obstacle_sprites])
                    # Create the Moving Spike itself (ensure it's added to traps)
                    MovingSpike((x, y), [self.visible_sprites, self.trap_sprites])
                elif cell == 'P': 
                    if not self.initial_player_pos:
                        self.initial_player_pos = pos

        self.initial_player_pos = self.initial_player_pos if self.initial_player_pos else (100, 100) # Fallback position
        self.player = Player(
            self.initial_player_pos,
            [self.visible_sprites],
            self.obstacle_sprites,
            self.trap_sprites,
            self.exit_sprites,
            self.trigger_level_complete, 
            self.trigger_player_death,
            self.game.input_buffer,
            self # Pass the level instance to the player
        )

    def trigger_level_complete(self):
        """Callback for when the player reaches the exit. Calls game's method."""
        self.game.level_manager.next_level()

    def trigger_player_death(self):
        """Callback for when the player hits a trap. Calls game's method."""
        self.game.current_state = GameState.DEATH_SCREEN

    def check_checkpoint_collisions(self):
        """Check for player collision with checkpoints and activate them."""
        if not self.player: return # Don't check if player doesn't exist

        collided_checkpoints = pygame.sprite.spritecollide(self.player, self.checkpoint_sprites, False)
        for checkpoint in collided_checkpoints:
            if not checkpoint.is_active:
                for cp in self.checkpoint_sprites:
                    if cp.is_active and cp != checkpoint:
                         cp.is_active = False
                         cp.image.fill(CHECKPOINT_YELLOW) 

                checkpoint.activate() # Visually activate
                self.last_checkpoint_pos = checkpoint.rect.topleft # Update last activated position

    def get_respawn_position(self):
        """Return the position where the player should respawn."""
        respawn_pos = self.last_checkpoint_pos if self.last_checkpoint_pos else self.initial_player_pos
        if not respawn_pos: 
            print("Error: Cannot determine respawn position!")
            return (100, 100) 
        return respawn_pos

    def reset_player_to_respawn(self):
        """Reset the player's state and position to the last checkpoint or start."""
        if self.player:
            respawn_pos = self.get_respawn_position()
            self.player.reset_state(respawn_pos)
            self.game.current_state = GameState.PLAYING
        else:
            print("Error: Attempted to reset player, but player does not exist.")

    def reset_checkpoints(self):
        """Reset all checkpoints to inactive state visually when leaving level."""
        self.last_checkpoint_pos = None 
        for checkpoint in self.checkpoint_sprites:
            if checkpoint.is_active:
                checkpoint.is_active = False
                checkpoint.image.fill(CHECKPOINT_YELLOW) 

    def start_full_illumination(self):
        """Initiates the full level illumination fade-in effect."""
        if not self.full_illumination_active and self.full_illumination_current_alpha == DARKNESS_COLOR[3]:
            # Only start if not already active/fading and at full darkness (or reset)
            print("Level: Starting full illumination sequence.")
            self.full_illumination_active = True

    def run(self, dt): # Added dt parameter
        """Update and draw all sprites in the level."""
        if not self.player: return 

        # Update full illumination fade
        if self.full_illumination_active and self.full_illumination_current_alpha > FULL_ILLUMINATION_TARGET_ALPHA:
            self.full_illumination_current_alpha -= FULL_ILLUMINATION_FADE_IN_SPEED * dt
            self.full_illumination_current_alpha = max(self.full_illumination_current_alpha, FULL_ILLUMINATION_TARGET_ALPHA)
        elif self.full_illumination_current_alpha <= FULL_ILLUMINATION_TARGET_ALPHA:
            # If target is reached, could set full_illumination_active = False if it's a one-time effect per trigger
            # For now, it will just stay at the target alpha once reached.
            pass 

        # --- Update game logic first ---
        self.visible_sprites.update(dt) # Pass dt to player.update() and other sprite updates
        self.check_checkpoint_collisions()

        # --- Then draw everything ---
        self.visible_sprites.custom_draw(self.player, self.full_illumination_current_alpha) # Pass current alpha


class YSortCameraGroup(pygame.sprite.Group):
    def __init__(self, level_width, level_height):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.half_width = self.display_surface.get_size()[0] // 2 if self.display_surface else SCREEN_WIDTH // 2
        self.half_height = self.display_surface.get_size()[1] // 2 if self.display_surface else SCREEN_HEIGHT // 2
        self.offset = pygame.math.Vector2()

        # map size
        self.level_width = level_width
        self.level_height = level_height

        # default background color and surface
        self.default_bg_color = (0, 0, 0)
        self.default_bg_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.default_bg_surf.fill(self.default_bg_color)

        # Darkness overlay surface (cached)
        self.darkness_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        self.darkness_surface.convert_alpha()

    def update(self, dt): # Add dt parameter
        """Update all sprites in the group, passing dt if they accept it."""
        for sprite in self.sprites():
            if hasattr(sprite, 'update'):
                # Check if sprite's update method expects dt
                # This is a bit of a simplification; proper way might involve inspect module
                # For now, assume if it has update, it can take dt (common pattern)
                try:
                    sprite.update(dt)
                except TypeError: # If it doesn't take dt, call without it
                    sprite.update()

    def custom_draw(self, player, current_darkness_alpha): # Added current_darkness_alpha
        """Draw layers, centering the camera on the player, and apply darkness effect."""
        if not self.display_surface:
            self.display_surface = pygame.display.get_surface()  # Try to get surface again
        if not self.display_surface:
            return  # Cannot draw

        # Calculate camera offset based on player center
        self.offset.x = player.rect.centerx - self.half_width
        self.offset.y = player.rect.centery - self.half_height

        # --- Clamp Camera Offset --- 
        max_x_offset = max(0, self.level_width - SCREEN_WIDTH)
        max_y_offset = max(0, self.level_height - SCREEN_HEIGHT)
        self.offset.x = max(0, min(self.offset.x, max_x_offset))
        self.offset.y = max(0, min(self.offset.y, max_y_offset))

        # --- Draw Default Background --- (This is the map's base color if needed)
        self.display_surface.blit(self.default_bg_surf, (0, 0))

        # --- Draw Map Background (Optional, can be part of sprites) ---
        map_rect = pygame.Rect(-self.offset.x, -self.offset.y, self.level_width, self.level_height)
        pygame.draw.rect(
            self.display_surface,
            (173, 216, 230),  # Light blue color for the map background
            map_rect
        )

        # Draw sprites sorted by Y (optional sort, depends on visuals)
        for sprite in sorted(self.sprites(), key=lambda sprite: sprite.rect.centery):
            offset_pos = sprite.rect.topleft - self.offset  # Calculate position relative to camera
            self.display_surface.blit(sprite.image, offset_pos)  # Draw the sprite

        # --- Player Light and Darkness Effects --- 
        if player and hasattr(player, 'get_light_effects'):
            mask_brush_surface, light_world_pos, pulsing_radius, light_surface_center_coords = player.get_light_effects()
            
            screen_light_pos = (light_world_pos[0] - self.offset.x,
                                light_world_pos[1] - self.offset.y)

            # 1. Fill darkness_surface with the current dynamic alpha
            self.darkness_surface.fill((0, 0, 0, int(current_darkness_alpha)))
            
            # 2. Blit the player's light brush onto this darkness_surface (carving out light)
            self.darkness_surface.blit(mask_brush_surface, screen_light_pos, special_flags=pygame.BLEND_RGBA_SUB)
            
            #    Blit the resulting darkness_surface (black with a soft transparent hole) onto the main display
            self.display_surface.blit(self.darkness_surface, (0,0))
