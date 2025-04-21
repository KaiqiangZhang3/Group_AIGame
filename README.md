# I Wanna Study Computer Science

A 2D platform jumping game developed with Pygame, combining precise jumping, trap avoidance, and puzzle elements.

## Game Introduction

"I Wanna Study Computer Science" is a challenging 2D platform game where players need to navigate through various levels using precise jumps, dodges, and timing. The game combines classic platform game elements while incorporating modern game mechanics such as dashing and double jumping.

## Features

- Carefully designed level system
- Smooth player controls, including jumping, double jumping, and dashing abilities
- Various obstacles and traps, including moving spikes
- Checkpoint system to reduce game difficulty
- Clean and intuitive menu interface

## Installation and Running

### Prerequisites

- Python 3.6+
- Pygame 2.0+

### Installation Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/Group_AIGame.git
   cd Group_AIGame
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the game:
   ```bash
   python main.py
   ```

## Game Controls

- **Arrow Keys**: Move character (left/right)
- **Space**: Jump/Double Jump
- **Z Key**: Dash
- **SHIFT Key**: Dash
- **R Key**: Reset current level
- **ESC Key**: Return to main menu

## Project Structure

```
Group_AIGame/
├── assets/             # Game resources (images, etc.)
├── src/                # Source code
│   ├── core/           # Core game logic
│   ├── entities/       # Game entities (like moving spikes)
│   ├── levels/         # Level design and management
│   ├── player/         # Player character related
│   ├── ui/             # User interface components
│   └── settings.py     # Game settings and constants
├── main.py             # Game entry point
└── requirements.txt    # Project dependencies
```

## Game Mechanics

### Player Abilities
- **Basic Movement**: Move left and right, basic jumping
- **Double Jump**: Perform a second jump while in the air
- **Dash**: Move quickly for a short time, useful for crossing large gaps or avoiding danger

### Level Elements
- **Platforms**: Surfaces where the player can stand
- **Spikes**: Contact leads to player death
- **Moving Spikes**: Dangerous objects that move along specific paths
- **Checkpoints**: Locations that save player progress
- **Exit**: Location to complete the level

## Developer Information

This game is a team project, completed by multiple developers.

## License

[Add appropriate license information here]