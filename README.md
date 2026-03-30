# GoBang

A small GoBang game built with Python and Pygame.

## Setup

Create the project virtual environment:

```bash
python3 -m venv .venv
```

Activate it:

```bash
source .venv/bin/activate
```

When you are done working, you can leave the virtual environment with:

```bash
deactivate
```

Then install the dependencies:

```bash
python3 -m pip install -r requirements.txt
```

If you use Anaconda or a virtual environment, run the command inside that environment first.

## Run

```bash
python3 main.py
```

## Project Structure

- `main.py`: tiny entrypoint
- `assets/`: images and audio used by the game
- `gobang/app.py`: game loop, page flow, rendering, and event handling
- `gobang/logic.py`: board state, win detection, draw detection, undo, and AI move selection
- `gobang/ui.py`: reusable UI widgets
- `gobang/assets.py`: asset loading
- `gobang/constants.py`: shared layout and rule constants

## Features

- Player vs Player mode
- Player vs AI mode
- Undo support
- Draw detection
