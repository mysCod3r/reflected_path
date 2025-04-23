"""
Main entry point for the Reflected Path game.

This script imports the Game class from the game module,
instantiates it, and starts the game loop by calling its run() method.
"""
import sys
import os

# --- Add the 'src' directory to the Python path ---
# This allows us to import modules from the 'src' directory directly (e.g., from src.game import Game)
# Note: This is one way to handle imports in project structures. Alternatives exist (e.g., relative imports within the package).
try:
    # Get the absolute path of the directory containing this script (src/)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Get the parent directory (the project root)
    project_root = os.path.dirname(script_dir)
    # Add the project root to the system path if it's not already there
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
        # print(f"Added {project_root} to sys.path") # Debugging line
except NameError:
     # Handle cases where __file__ might not be defined (e.g., some interactive environments)
     print("Warning: Could not automatically determine project structure for sys.path modification.")


# --- Import the Game class ---
try:
    from src.game import Game
except ImportError as e:
    print("ERROR: Could not import the Game class from src.game.")
    print("Please ensure the file structure is correct and all dependencies are installed.")
    print(f"Import Error: {e}")
    # Check if the current working directory is the project root
    print(f"Current Working Directory: {os.getcwd()}")
    print(f"Sys Path includes: {sys.path}")
    sys.exit(1) # Exit if the core Game class cannot be imported


# --- Main execution block ---
if __name__ == '__main__':
    print("Starting Reflected Path...")
    try:
        game_instance = Game() # Create an instance of the Game class
        game_instance.run()    # Start the main game loop
    except Exception as e:
        # Catch any unexpected errors during game execution
        print("\n--- An Unexpected Error Occurred ---")
        print(f"Error Type: {type(e).__name__}")
        print(f"Error Message: {e}")
        # Optional: Include traceback for more detailed debugging
        import traceback
        traceback.print_exc()
        print("------------------------------------")
        print("Exiting due to error.")
        sys.exit(1) # Exit with an error code