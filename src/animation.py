import pygame
import os

class AnimationClip:
    """Manages a single animation sequence."""
    def __init__(self, frames, fps=12, loop=True):
        self.frames = frames
        self.fps = fps if fps > 0 else 12
        self.loop = loop
        self.frame_duration = 1.0 / self.fps
        self.current_frame_index = 0
        self.time_since_last_frame = 0.0
        self.is_playing = True
        self.finished_one_cycle = False # For non-looping animations to signal completion

        if not self.frames:
            # Create a small placeholder surface if no frames are provided
            self.image = pygame.Surface((32, 32))
            self.image.fill((255, 0, 255)) # Bright pink placeholder
            pygame.draw.rect(self.image, (0,0,0), self.image.get_rect(), 1) # Black border
            self.is_playing = False # Nothing to play
        else:
            self.image = self.frames[self.current_frame_index]

    def update(self, dt):
        """Update the animation frame based on delta time."""
        if not self.is_playing or not self.frames:
            return

        self.time_since_last_frame += dt
        if self.time_since_last_frame >= self.frame_duration:
            self.time_since_last_frame -= self.frame_duration # Use remainder for smoother animation
            self.current_frame_index += 1
            if self.current_frame_index >= len(self.frames):
                if self.loop:
                    self.current_frame_index = 0
                    self.finished_one_cycle = True # Completed a loop
                else:
                    self.current_frame_index = len(self.frames) - 1 # Stay on last frame
                    self.is_playing = False # Stop playing if not looping
                    self.finished_one_cycle = True
            self.image = self.frames[self.current_frame_index]

    def reset(self):
        """Resets the animation to the first frame."""
        self.current_frame_index = 0
        self.time_since_last_frame = 0.0
        self.is_playing = True
        self.finished_one_cycle = False
        if self.frames:
            self.image = self.frames[self.current_frame_index]

    def get_current_image(self):
        """Returns the current frame's surface."""
        return self.image

    def is_finished(self):
        """Returns True if a non-looping animation has completed its cycle."""
        return not self.loop and self.finished_one_cycle

class Animator:
    """Manages multiple AnimationClips for a character or object."""
    NON_LOOPING_ACTIONS = [
        'attack_1', 'attack_2', 'attack_3', 'air_attack', 'special_attack',
        'hurt', 'death', 'dash', 'jump_start', 'throw', 'defend', 
        'healing', 'healing_no_effect', 'wall_jump'
        # 'jump_transition' could be non-looping or short-looping depending on design
    ]

    def __init__(self, base_sprites_path, default_fps=12):
        self.animations = {}
        self.current_action_name = None
        self.default_fps = default_fps
        self.placeholder_image = pygame.Surface((32, 32))
        self.placeholder_image.fill((255, 105, 180)) # Hot pink
        pygame.draw.line(self.placeholder_image, (0,0,0), (0,0), (31,31), 1)
        pygame.draw.line(self.placeholder_image, (0,0,0), (0,31), (31,0), 1)

        if base_sprites_path:
            self.load_animations_from_directory(base_sprites_path)
        else:
            print(f"Warning: Animator initialized with no base_sprites_path.")

    def trim_surface(self, surface):
        rect = surface.get_bounding_rect()
        return surface.subsurface(rect).copy()

    def load_animations_from_directory(self, base_path):
        """Loads all animation sequences from subdirectories of base_path."""
        if not os.path.isdir(base_path):
            print(f"Error: Animator base path '{base_path}' not found or not a directory.")
            return

        for action_name in os.listdir(base_path):
            action_path = os.path.join(base_path, action_name)
            if os.path.isdir(action_path):
                frames = []
                try:
                    # Sort files numerically if possible, otherwise alphabetically
                    # Assumes filenames like frame_001.png, frame_002.png or action_0.png, action_1.png
                    raw_files = [f for f in os.listdir(action_path) if f.lower().endswith('.png')]
                    
                    # Attempt to sort numerically based on numbers in filename
                    def sort_key(filename):
                        parts = filename.split('_') # or other delimiter
                        try:
                            # Try to extract number from last part before .png
                            return int(parts[-1].split('.')[0]) 
                        except (ValueError, IndexError):
                            return filename # Fallback to string sort if no number
                    
                    sorted_files = sorted(raw_files, key=sort_key)
                    
                    for frame_file in sorted_files:
                        frame_path = os.path.join(action_path, frame_file)
                        try:
                            image = self.trim_surface(pygame.image.load(frame_path).convert_alpha())
                            frames.append(image)
                        except pygame.error as e:
                            print(f"Warning: Could not load image '{frame_path}': {e}")
                    
                    if frames:
                        is_looping = action_name not in self.NON_LOOPING_ACTIONS
                        clip = AnimationClip(frames, fps=self.default_fps, loop=is_looping)
                        self.animations[action_name] = clip
                        print(f"Animator: Loaded action '{action_name}' with {len(frames)} frames (looping: {is_looping}).")
                    else:
                        print(f"Warning: No valid PNG frames found in '{action_path}' for action '{action_name}'.")
                except Exception as e:
                    print(f"Error processing directory '{action_path}': {e}")
        
        if not self.animations:
            print(f"Warning: Animator loaded no animations from '{base_path}'.")
        elif not self.current_action_name and 'idle' in self.animations:
            self.set_action('idle') # Default to idle if available

    def set_action(self, action_name):
        """Sets the current animation action."""
        if action_name == self.current_action_name and self.animations.get(action_name) and self.animations[action_name].is_playing:
            # If trying to set the same action and it's already playing (and not finished if non-looping), do nothing
            # unless it's a looping animation, in which case it's fine to just let it continue.
            # For non-looping, if it's finished, we want to allow resetting it by calling set_action again.
            current_clip = self.animations[action_name]
            if not current_clip.loop and current_clip.is_finished(): 
                current_clip.reset()
            return

        if action_name in self.animations:
            if self.current_action_name and self.current_action_name in self.animations:
                # Optional: Stop the previous animation if needed, though reset handles start
                pass 
            self.current_action_name = action_name
            self.animations[self.current_action_name].reset()
            # print(f"Animator: Set action to '{action_name}'") # For debugging
        else:
            # print(f"Warning: Animator action '{action_name}' not found. Current action: {self.current_action_name}")
            pass # Keep current animation or do nothing if no current_action_name

    def update(self, dt):
        """Updates the current animation clip."""
        if self.current_action_name and self.current_action_name in self.animations:
            self.animations[self.current_action_name].update(dt)

    def get_current_image(self):
        """Returns the surface of the current animation's active frame."""
        if self.current_action_name and self.current_action_name in self.animations:
            return self.animations[self.current_action_name].get_current_image()
        return self.placeholder_image # Return a placeholder if no valid action is set
    
    def is_current_action_finished(self):
        """Checks if the current non-looping animation has finished."""
        if self.current_action_name and self.current_action_name in self.animations:
            clip = self.animations[self.current_action_name]
            return clip.is_finished()
        return True # If no action, consider it 'finished'
