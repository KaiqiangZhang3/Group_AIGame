import pygame
from src.settings import *
from src.levels.tile import Tile
from src.player.player import Player
from src.entities.moving_spike import MovingSpike
from src.entities.coin import Coin

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
        self.exit_sprites = pygame.sprite.Group() # Group for exit points
        self.checkpoint_sprites = pygame.sprite.Group() # Group for checkpoints
        self.moving_spike_sprites = pygame.sprite.Group() # Group for moving spikes
        self.trap_sprites = pygame.sprite.Group() # Group for traps
        self.coin_sprites = pygame.sprite.Group() # Group for coins
        self.all_coins_in_level = [] # Keep track of all coins for reset
        self.temp_platforms = [] # Keep track of all temporary platforms for reset
        self.periodic_platforms = [] # Keep track of all periodic platforms
        self.initial_player_pos = None
        self.last_checkpoint_pos = None
        self.player = None

        self.setup_level(level_data)

    def setup_level(self, layout):
        """Creates tiles and player based on the layout."""
        # Clear groups and reset state for new level load
        self.visible_sprites.empty()
        self.obstacle_sprites.empty()
        self.exit_sprites.empty()
        self.checkpoint_sprites.empty()
        self.moving_spike_sprites.empty()
        self.trap_sprites.empty()
        self.coin_sprites.empty()
        self.all_coins_in_level.clear() # Reset coins
        self.temp_platforms.clear() # Reset temporary platforms list
        self.periodic_platforms.clear() # Reset periodic platforms list
        self.initial_player_pos = None
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
                elif cell == TEMP_PLATFORM_CHAR:
                    tile = Tile(pos, [self.visible_sprites, self.obstacle_sprites], tile_type='temp_platform')
                    self.temp_platforms.append(tile)
                elif cell == PERIODIC_PLATFORM_CHAR:
                    tile = Tile(pos, [self.visible_sprites], tile_type='periodic_platform') # Only add to visible initially
                    self.periodic_platforms.append(tile)
                    if tile.is_currently_visible: # Add to obstacles if starting visible
                        self.obstacle_sprites.add(tile)
                elif cell == 'P': 
                    if not self.initial_player_pos:
                        self.initial_player_pos = pos
                elif cell == COIN_CHAR:
                    coin = Coin(pos, [self.visible_sprites, self.coin_sprites])
                    self.all_coins_in_level.append(coin)

        self.initial_player_pos = self.initial_player_pos if self.initial_player_pos else (100, 100) # Fallback position
        self.player = Player(
            self.initial_player_pos,
            [self.visible_sprites],
            self.obstacle_sprites,
            self.trap_sprites,
            self.exit_sprites,
            self.coin_sprites, # Added coin_sprites group for player to interact with
            self.trigger_level_complete, 
            self.trigger_player_death
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
            print("[DEBUG] Level.reset_player_to_respawn called.") # DEBUG
            self.player.reset_state(respawn_pos)
            self.game.current_state = GameState.PLAYING

            # Reset coins so they reappear
            for coin in self.all_coins_in_level:
                coin.reset() # This resets the coin's internal 'is_collected' state
                # If coin.collect() uses self.kill(), it's removed from all groups.
                # We need to add it back to the relevant groups to make it visible and interactive again.
                if not coin.alive(): # check if it's not part of any group
                    self.visible_sprites.add(coin)
                self.coin_sprites.add(coin)

            # Reset temporary platforms
            print(f"[DEBUG] Resetting {len(self.temp_platforms)} temporary platforms.") # DEBUG
            for i, platform in enumerate(self.temp_platforms):
                print(f"[DEBUG] TempPlatform {i}: Initial alive state: {platform.alive()}") # DEBUG
                platform.reset_timer()
                print(f"[DEBUG] TempPlatform {i}: State after reset_timer. Alive: {platform.alive()}, Groups: {platform.groups()}") # DEBUG
                if not platform.alive():
                    print(f"[DEBUG] TempPlatform {i}: Re-adding to visible and obstacle sprites.") # DEBUG
                    self.visible_sprites.add(platform)
                    self.obstacle_sprites.add(platform)
                    print(f"[DEBUG] TempPlatform {i}: State after re-adding. Alive: {platform.alive()}, Groups: {platform.groups()}") # DEBUG
                else:
                    print(f"[DEBUG] TempPlatform {i}: Was already alive. Groups: {platform.groups()}") # DEBUG
                    # Ensure it's in obstacle_sprites if it somehow got removed but stayed alive
                    if platform not in self.obstacle_sprites:
                        print(f"[DEBUG] TempPlatform {i}: Was alive but not in obstacle_sprites. Re-adding to obstacle_sprites.") # DEBUG
                        self.obstacle_sprites.add(platform)
                        print(f"[DEBUG] TempPlatform {i}: Groups after ensuring obstacle: {platform.groups()}") # DEBUG

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
        """Update and draw all sprites in the level, using delta time."""
        if not self.player: return 

        self.visible_sprites.custom_draw(self.player) # Draw based on previous frame's state, before updates

        self.visible_sprites.update(dt) # Update all sprites (player, tiles, entities)

        # Update periodic platform collision status AFTER their state has been updated by visible_sprites.update()
        # This ensures collision status matches visual status for the current frame.
        for platform in self.periodic_platforms:
            if platform.is_currently_visible:
                if platform not in self.obstacle_sprites:
                    self.obstacle_sprites.add(platform)
            else: # It's invisible
                if platform in self.obstacle_sprites:
                    self.obstacle_sprites.remove(platform)

        self.check_checkpoint_collisions() # Checkpoint logic can run after player has moved


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

    def custom_draw(self, player):
        """Draw layers, centering the camera on the player."""
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

        # --- Draw Default Background ---
        self.display_surface.blit(self.default_bg_surf, (0, 0))

        # --- Draw Map Background ---
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
