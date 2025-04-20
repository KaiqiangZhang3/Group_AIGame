import time

class InputBuffer:
    """A class to manage input buffering for a game."""
    def __init__(self, buffer_duration=0.2):
        """
        Initialize the input buffer.
        
        :param buffer_duration: The duration (in seconds) for which inputs are buffered.
        """
        self.buffer = []  # List to store buffered inputs as (key, timestamp) tuples
        self.buffer_duration = buffer_duration  # Maximum duration to keep inputs in the buffer

    def add_input(self, key):
        """
        Add a new input to the buffer.
        
        :param key: The key code of the input to add.
        """
        self.buffer.append((key, time.time()))

    def get_and_remove_input(self, key):
        """
        Get and remove the first occurrence of a specific input from the buffer.
        
        :param key: The key code to retrieve.
        :return: True if the input was found and removed, False otherwise.
        """
        for i, (stored_key, timestamp) in enumerate(self.buffer):
            if stored_key == key:
                del self.buffer[i]
                return True
        return False

    def clear_expired_inputs(self):
        """
        Remove inputs that have expired from the buffer.
        """
        current_time = time.time()
        self.buffer = [
            (key, timestamp) for key, timestamp in self.buffer
            if current_time - timestamp <= self.buffer_duration
        ]

    def has_input(self, key):
        """
        Check if a specific input exists in the buffer.
        
        :param key: The key code to check.
        :return: True if the input exists, False otherwise.
        """
        return any(stored_key == key for stored_key, _ in self.buffer)

    def clear(self):
        """
        Clear all inputs from the buffer.
        """
        self.buffer.clear()