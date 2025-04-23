"""
Contains the path data for each level of Reflected Path.

Each level's path is represented as a list of (row, col) tuples.
These coordinates define the tiles that make up the original path,
which is assumed to be on the left side of the symmetry line.

Grid coordinates are 0-indexed (top-left is 0, 0).
Ensure coordinates stay within the grid boundaries defined in config.py
(specifically, column index should be less than SYMMETRY_LINE_TILE_INDEX).
"""

# You can easily add, remove, or modify levels here.
LEVELS = [
    # Level 1: Simple L shape (3x3)
    [ (2, 1), (3, 1), (4, 1), (4, 2), (4, 3) ],

    # Level 2: Diagonal line (4 tiles)
    [ (1, 1), (2, 2), (3, 3), (4, 4) ],

    # Level 3: U shape (7 tiles)
    [ (6, 2), (5, 2), (4, 2), (4, 3), (4, 4), (5, 4), (6, 4) ],

    # Level 4: Simple Cross (5 tiles)
    [ (3, 2), (4, 2), (5, 2), (4, 1), (4, 3) ],

    # Level 5: Zig Zag (6 tiles)
    [ (1, 1), (1, 2), (2, 2), (2, 3), (3, 3), (3, 4) ],

    # Level 6: Frame like (12 tiles)
    [ (2, 1), (2, 2), (2, 3), (2, 4),
      (3, 4), (4, 4), (5, 4),
      (5, 3), (5, 2), (5, 1),
      (4, 1), (3, 1) ],

    # Level 7: Stairs (7 tiles)
    [ (7, 1), (6, 1), (6, 2), (5, 2), (5, 3), (4, 3), (4, 4) ],

    # Level 8: T shape (5 tiles)
    [ (2, 1), (2, 2), (2, 3), (3, 2), (4, 2) ],

    # Level 9: S shape (7 tiles)
    [ (1, 3), (1, 2), (2, 2), (3, 2), (3, 3), (4, 3), (4, 4) ],

    # Level 10: More complex path (10 tiles)
    [ (3, 1), (4, 1), (5, 1), (5, 2), (5, 3), (4, 3), (3, 3), (3, 4), (3, 5), (4, 5) ],
]
