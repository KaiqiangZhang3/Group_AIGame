import time

class InputBuffer:
    """A class to manage input buffering for a game, storing events with timestamps."""
    def __init__(self, buffer_duration_seconds=1.5):
        """
        Initialize the input buffer.
        
        :param buffer_duration_seconds: The duration (in seconds) for which inputs are generally kept if not processed.
        """
        self.buffer = []  # List to store buffered inputs as (event_key, timestamp_seconds) tuples
        self.buffer_duration_seconds = buffer_duration_seconds

    def add_input(self, event_key):
        """
        Add a new input event to the buffer with a current timestamp.
        
        :param event_key: The identifier of the input event (e.g., KEY_JUMP, VOICE_JUMP).
        """
        self.buffer.append((event_key, time.time()))

    def get_recent_events(self, event_keys=None, time_window_seconds=None):
        """
        Retrieve recent events from the buffer, optionally filtered by type and time window.
        Does NOT remove events from the buffer.
        
        :param event_keys: A list of event keys to filter by. If None, all event types are considered.
        :param time_window_seconds: The lookback period in seconds from the current time.
                                   If None, all events in the buffer are considered (respecting buffer_duration_seconds).
        :return: A list of (event_key, timestamp_seconds) tuples, sorted by timestamp ascending.
        """
        current_time = time.time()
        candidate_events = []

        for event_k, timestamp_s in self.buffer:
            # Filter by time window if specified
            if time_window_seconds is not None and (current_time - timestamp_s > time_window_seconds):
                continue  # Event is older than the specified window
            
            # Filter by event type if specified
            if event_keys is not None and event_k not in event_keys:
                continue
                
            candidate_events.append((event_k, timestamp_s))
            
        # Sort by timestamp to ensure chronological order for processing, though append usually maintains this.
        candidate_events.sort(key=lambda x: x[1])
        return candidate_events

    def remove_specific_events(self, events_to_remove):
        """
        Remove specific events from the buffer.
        
        :param events_to_remove: A list of (event_key, timestamp_seconds) tuples to remove.
                                 These should be exact matches to items in the buffer.
        """
        for event_to_remove in events_to_remove:
            try:
                self.buffer.remove(event_to_remove)
            except ValueError:
                # Event might have already been removed (e.g., by clear_expired_inputs or another call)
                # or was never in the buffer. This is generally not an error for this operation.
                pass 

    def clear_expired_inputs(self):
        """
        Remove inputs that have expired based on self.buffer_duration_seconds.
        This should be called periodically (e.g., once per game loop).
        """
        current_time = time.time()
        self.buffer = [
            (key, timestamp) for key, timestamp in self.buffer
            if current_time - timestamp <= self.buffer_duration_seconds
        ]

    def has_input(self, event_key):
        """
        Check if a specific input event type exists in the buffer (and is not expired).
        Note: For precise timing checks for coordinated actions, use get_recent_events.
        
        :param event_key: The event key to check.
        :return: True if the input exists and is relatively recent, False otherwise.
        """
        # It's good practice to clear expired inputs before checking, 
        # ensuring 'has_input' reflects reasonably current state.
        self.clear_expired_inputs() 
        return any(stored_key == event_key for stored_key, _ in self.buffer)

    def clear(self):
        """
        Clear all inputs from the buffer.
        """
        self.buffer.clear()