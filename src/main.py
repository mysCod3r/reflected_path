"""
Main entry point for the Reflected Path game.

This script imports the Game class from the game module,
instantiates it, and starts the game loop by calling its run() method.
"""
import sys
import os

try:
    # Get the absolute path of the directory containing this script (src/)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Get the parent directory (the project root)
    project_root = os.path.dirname(script_dir)
    # Add the project root to the system path if it's not already there
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
except NameError:
     print("Warning: Could not automatically determine project structure for sys.path modification.")


# --- Import the Game class ---
try:
    from src.game import Game
except ImportError as e:
    print("ERROR: Could not import the Game class from src.game.")
    print("Please ensure the file structure is correct and all dependencies are installed.")
    print(f"Import Error: {e}")
    print(f"Current Working Directory: {os.getcwd()}")
    print(f"Sys Path includes: {sys.path}")
    sys.exit(1)


# --- Main execution block ---
if __name__ == '__main__':
    print("Starting Reflected Path...")
    try:
        game_instance = Game()
        game_instance.run()
    except Exception as e:
        print("\n--- An Unexpected Error Occurred ---")
        print(f"Error Type: {type(e).__name__}")
        print(f"Error Message: {e}")
        import traceback
        traceback.print_exc()
        print("------------------------------------")
        print("Exiting due to error.")
        sys.exit(1)