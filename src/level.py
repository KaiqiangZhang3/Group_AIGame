# Proposed content for: /Users/kaiqiangzhang/3_game/Group_AIGame/src/level.py
# Instruction: Implement checkpoint logic: setup groups, track last activated, activate on collision, provide respawn position via methods, trigger game's death screen callback, reset checkpoints. Pass game instance. (Concise version)

import pygame
import inspect
from .settings import TILE_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT, SKY_BLUE, CHECKPOINT_YELLOW
from .tile import Tile
from .player import Player
from .moving_spike import MovingSpike
from .bullet import Bullet
from .bird import Bird

class Level:
    """Manages the game level, including tiles, player, and interactions."""
    def __init__(self, level_path, surface, 
                 level_complete_callback, trigger_player_death, trigger_hidden_level_callback, 
                 level_index):
        # Basic setup
        self.display_surface = surface
        self.world_shift = 0
        self.level_index = level_index

        # Sprite group setup
        self.visible_sprites = YSortCameraGroup()
        self.obstacle_sprites = pygame.sprite.Group()
        self.exit_sprites = pygame.sprite.Group()
        self.trap_sprites = pygame.sprite.Group()
        self.checkpoint_sprites = pygame.sprite.Group()
        self.bullet_sprites = pygame.sprite.Group()
        self.bird_sprites = pygame.sprite.Group()
        self.hidden_door_sprites = pygame.sprite.Group()

        # Callbacks
        self.level_complete_callback = level_complete_callback
        self.trigger_player_death = trigger_player_death
        self.trigger_hidden_level = trigger_hidden_level_callback

        # Player spawn and checkpoint tracking
        self.initial_player_pos = None
        self.last_checkpoint_pos = None
        self.player = None

        # Load level data from file and create layout
        try:
            with open(level_path, 'r') as file:
                level_data = [line.strip('\n') for line in file.readlines()]
            print(f"DEBUG: Level data read in __init__ (first 5 lines): {level_data[:5]}") # <-- DEBUG PRINT 1 (Limited)
            self.create_layout(level_data) # Call create_layout (standardized name)
        except FileNotFoundError:
            print(f"Error: Level file not found at '{level_path}'")
            # Ensure player is None if level loading fails
            self.player = None 
        except Exception as e:
            print(f"Error during level setup: {e}")
            self.player = None

    def create_layout(self, layout):
        """Creates tiles and player based on the layout list of strings."""
        print(f"DEBUG: create_layout called with layout (first 5 lines): {layout[:5]}") # <-- DEBUG PRINT 2 (Limited)
        # Clear groups and reset state for new level load
        self.visible_sprites.empty()
        self.obstacle_sprites.empty()
        self.exit_sprites.empty()
        self.trap_sprites.empty()
        self.checkpoint_sprites.empty()
        self.bullet_sprites.empty()
        self.bird_sprites.empty()
        self.hidden_door_sprites.empty()
        self.initial_player_pos = None # Reset player position tracking
        self.last_checkpoint_pos = None
        self.player = None

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
                    print(f"DEBUG: Found 'P' at map coords ({row_index}, {col_index}) -> world pos {pos}") # <-- DEBUG PRINT 3
                    if not self.initial_player_pos:
                        self.initial_player_pos = pos
                elif cell == 'B': 
                    Bird(pos, [self.visible_sprites, self.bird_sprites], self.obstacle_sprites, self.trap_sprites)
                elif cell == 'H': 
                    Tile(pos, [self.visible_sprites, self.hidden_door_sprites], tile_type='hidden_door')

        if self.initial_player_pos:
            self.player = Player(
                 self.initial_player_pos,
                 [self.visible_sprites],
                 self.obstacle_sprites,
                 self.trap_sprites,
                 self.exit_sprites,
                 self.trigger_level_complete, 
                 self.trigger_player_death,
                 self.visible_sprites,
                 self.bullet_sprites,
                 self.bird_sprites,
                 self.hidden_door_sprites,
                 self.trigger_hidden_level
            )
        else:
            print("Error: Player start position 'P' not found in level map!")
            self.initial_player_pos = (100, 100)
            self.player = Player(self.initial_player_pos, [self.visible_sprites], self.obstacle_sprites, self.trap_sprites, self.exit_sprites, self.trigger_level_complete, self.trigger_player_death, self.visible_sprites, self.bullet_sprites, self.bird_sprites, self.hidden_door_sprites, self.trigger_hidden_level)

    def trigger_level_complete(self):
        """Callback for when the player reaches the exit. Calls game's method."""
        self.level_complete_callback()

    def trigger_player_death(self):
        """Callback for when the player hits a trap. Calls game's method."""
        self.trigger_player_death()

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
        else:
            print("Error: Attempted to reset player, but player does not exist.")

    def reset_checkpoints(self):
        """Reset all checkpoints to inactive state visually when leaving level."""
        self.last_checkpoint_pos = None 
        for checkpoint in self.checkpoint_sprites:
            if checkpoint.is_active:
                checkpoint.is_active = False
                checkpoint.image.fill(CHECKPOINT_YELLOW) 

    def run(self, dt):
        """Update and draw all sprites in the level."""
        if not self.player: return 

        # Pass dt to the sprite update methods
        self.visible_sprites.update(dt) 

        # Drawing happens after updates
        self.visible_sprites.custom_draw(self.player)

        # Checkpoints can be checked after updates/drawing
        self.check_checkpoint_collisions()

        # --- Bullet Collision Checks ---
        # Bullets vs Obstacles (kill bullet, not obstacle)
        pygame.sprite.groupcollide(self.bullet_sprites, self.obstacle_sprites, True, False)
        # Bullets vs Traps (kill bullet, not trap)
        pygame.sprite.groupcollide(self.bullet_sprites, self.trap_sprites, True, False)
        # Bullets vs Birds (kill both bullet and bird)
        pygame.sprite.groupcollide(self.bullet_sprites, self.bird_sprites, True, True)


# Custom sprite group for drawing with camera offset and Y-sorting
class YSortCameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        # Get display surface and dimensions for camera calculations
        self.display_surface = pygame.display.get_surface()
        self.half_width = self.display_surface.get_size()[0] // 2 if self.display_surface else SCREEN_WIDTH // 2
        self.half_height = self.display_surface.get_size()[1] // 2 if self.display_surface else SCREEN_HEIGHT // 2
        self.offset = pygame.math.Vector2()

        # Optional: Background surface (can be expanded if needed)
        bg_width = SCREEN_WIDTH * 2 # Example: larger than screen
        bg_height = SCREEN_HEIGHT * 2
        self.floor_surf = pygame.Surface((bg_width, bg_height))
        self.floor_surf.fill(SKY_BLUE)
        self.floor_rect = self.floor_surf.get_rect(topleft = (0,0))

    def update(self, dt):
        # Overriding default group update to pass dt
        for sprite in self.sprites():
            # Check if sprite has an update method that accepts dt
            if hasattr(sprite, 'update'):
                try:
                    # Get the signature of the update method
                    sig = inspect.signature(sprite.update)
                    # Check if 'dt' is a parameter
                    if 'dt' in sig.parameters:
                        sprite.update(dt) # Call update with dt
                    else:
                        sprite.update() # Call update without dt
                except (ValueError, TypeError): # Handle built-ins or other non-inspectable callables
                    sprite.update()

    def custom_draw(self, player):
        """Draw layers, centering the camera on the player."""
        if not self.display_surface: self.display_surface = pygame.display.get_surface() # Try to get surface again
        if not self.display_surface: return # Cannot draw

        # Calculate camera offset based on player center
        self.offset.x = player.rect.centerx - self.half_width
        self.offset.y = player.rect.centery - self.half_height

        # --- Clamp Camera Offset --- 
        # Prevent camera showing area left of the world start (x=0)
        self.offset.x = max(0, self.offset.x)
        # Prevent camera showing area above the world start (y=0) - adjust if needed
        self.offset.y = max(0, self.offset.y) 
        # Note: We might later need to add clamping for the right/bottom edges too,
        # based on the actual size of the level map.

        # Draw background first, applying the clamped offset
        floor_offset_pos = self.floor_rect.topleft - self.offset
        self.display_surface.blit(self.floor_surf, floor_offset_pos)

        # Draw sprites sorted by Y (optional sort, depends on visuals)
        for sprite in sorted(self.sprites(), key=lambda sprite: sprite.rect.centery):
             offset_pos = sprite.rect.topleft - self.offset # Calculate position relative to camera
             # self.display_surface.blit(sprite.image, offset_pos) # Old way: Draw the sprite image

             # New way: Draw player specifically, otherwise blit image
             if isinstance(sprite, Player):
                 sprite.draw(self.display_surface, offset_pos) # Call Player's custom draw
             elif hasattr(sprite, 'image'): # Check if sprite has an image before blitting
                 self.display_surface.blit(sprite.image, offset_pos)
             # Else: Sprite has no image and isn't the player (shouldn't happen with current setup)
