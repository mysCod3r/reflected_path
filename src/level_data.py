"""
Contains the path data and potentially level-specific settings for Reflected Path.

LEVELS: A list where each element is a level's path.
        Each path is a list of (row, col) tuples on the left side.
LEVEL_SETTINGS: A list of dictionaries, one per level, containing overrides
                for default time, ink, and the new 'mistake_limit'.
                If a level doesn't have an entry here, defaults from config.py are used.
"""

# --- Level Path Data ---
LEVELS = [
    # --- Original 10 Levels ---
    # 1: Simple L shape (3x3)
    [ (2, 1), (3, 1), (4, 1), (4, 2), (4, 3) ],
    # 2: Diagonal line (4 tiles)
    [ (1, 1), (2, 2), (3, 3), (4, 4) ],
    # 3: U shape (7 tiles)
    [ (6, 2), (5, 2), (4, 2), (4, 3), (4, 4), (5, 4), (6, 4) ],
    # 4: Simple Cross (5 tiles)
    [ (3, 2), (4, 2), (5, 2), (4, 1), (4, 3) ],
    # 5: Zig Zag (6 tiles)
    [ (1, 1), (1, 2), (2, 2), (2, 3), (3, 3), (3, 4) ],
    # 6: Frame like (12 tiles)
    [ (2, 1), (2, 2), (2, 3), (2, 4), (3, 4), (4, 4), (5, 4), (5, 3), (5, 2), (5, 1), (4, 1), (3, 1)],
    # 7: Stairs (7 tiles)
    [ (7, 1), (6, 1), (6, 2), (5, 2), (5, 3), (4, 3), (4, 4) ],
    # 8: T shape (5 tiles)
    [ (2, 1), (2, 2), (2, 3), (3, 2), (4, 2) ],
    # 9: S shape (7 tiles)
    [ (1, 3), (1, 2), (2, 2), (3, 2), (3, 3), (4, 3), (4, 4) ],
    # 10: More complex path (10 tiles)
    [ (3, 1), (4, 1), (5, 1), (5, 2), (5, 3), (4, 3), (3, 3), (3, 4), (3, 5), (4, 5) ],

    # --- New Levels (11-25) ---
    # 11: Small Spiral (9 tiles)
    [ (3, 3), (3, 4), (4, 4), (5, 4), (5, 3), (5, 2), (4, 2), (3, 2), (3, 1) ],
    # 12: Arrow pointing down-right (7 tiles)
    [ (1, 1), (2, 2), (3, 3), (4, 4), (3, 4), (5, 4) , (4,5)],
    # 13: Interlocking L's (tricky reflection) (10 tiles)
    [ (1, 1), (2, 1), (3, 1), (3, 2), (3, 3), (4, 3), (5, 3), (5, 4), (5, 5) , (6,5)],
    # 14: Thin Frame (16 tiles)
    [ (1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (2, 5), (3, 5), (4, 5), (5, 5), (6, 5), (6, 4), (6, 3), (6, 2), (6, 1), (5, 1), (4,1), (3,1), (2,1)],
    # 15: Checkerboard Fragment (9 tiles - sparse)
    [ (2, 1), (2, 3), (2, 5), (4, 1), (4, 3), (4, 5), (6, 1), (6, 3), (6, 5) ],
    # 16: Long Snake (13 tiles)
    [ (1, 6), (1, 5), (1, 4), (2, 4), (3, 4), (3, 3), (3, 2), (4, 2), (5, 2), (5, 1), (6, 1), (7, 1), (8, 1) ],
    # 17: Castle Top (11 tiles)
    [ (4, 1), (4, 2), (3, 2), (3, 3), (2, 3), (2, 4), (3, 4), (3, 5), (4, 5), (4, 6), (5,6) ],
    # 18: Symmetric-ish Shape (reflection is key) (9 tiles)
    [ (2, 2), (3, 1), (4, 2), (5, 1), (6, 2), (5, 3), (4, 4), (3, 3) ], # Missing center (4,3) to break perfect symmetry
    # 19: Double U (14 tiles)
    [ (2, 1), (3, 1), (4, 1), (4, 2), (3, 2), (2, 2), (2, 4), (3, 4), (4, 4), (4, 5), (3, 5), (2, 5) , (5,1), (5,5)],
    # 20: Maze like start (15 tiles)
    [ (1, 1), (1, 2), (1, 3), (2, 3), (3, 3), (3, 2), (3, 1), (4, 1), (5, 1), (5, 2), (5, 3), (5, 4), (4, 4), (3, 4), (2, 4) ],
    # 21: Almost Full Column (10 tiles)
    [ (1, 3), (2, 3), (3, 3), (4, 3), (5, 3), (6, 3), (7, 3), (8, 3), (9, 3), (10, 3) ],
    # 22: Scattered Dots (6 tiles)
    [ (1, 1), (3, 5), (5, 2), (7, 6), (9, 3), (11, 1) ],
    # 23: H Shape (7 tiles)
    [ (2, 1), (3, 1), (4, 1), (5, 1), (6, 1), (4, 2), (4, 3) ],
    # 24: Plus Sign variations (13 tiles)
    [ (3, 3), (4, 3), (5, 3), (6, 3), (7, 3), (5, 1), (5, 2), (5, 4), (5, 5), (1,3), (2,3), (8,3), (9,3)],
    # 25: Final Challenge - Complex Weave (18 tiles)
    [ (1, 1), (2, 1), (2, 2), (1, 2), (1, 3), (1, 4), (2, 4), (3, 4), (3, 3), (3, 2), (4, 2), (5, 2), (5, 3), (5, 4), (5, 5), (4, 5), (3,5), (2,5) ]
]

# --- Level Specific Settings ---
# Index corresponds to level index (Level 1 is index 0)
# Add entries only for levels where you want to OVERRIDE the defaults from config.py
LEVEL_SETTINGS = [
    # Level 1-5: Use defaults (maybe slightly more ink for frame?)
    {}, # Level 1
    {}, # Level 2
    {}, # Level 3
    {}, # Level 4
    {}, # Level 5
    {'ink': 30, 'mistakes': 7}, # Level 6 (Frame - needs more ink, allow some mistakes)
    {}, # Level 7
    {}, # Level 8
    {'time': 20000}, # Level 9 (S shape - less time?)
    {'ink': 25, 'mistakes': 5}, # Level 10 (Complex - more ink, fewer mistakes)

    # Settings for new levels (Adjust as needed for difficulty)
    {}, # Level 11 (Spiral)
    {'mistakes': 4}, # Level 12 (Arrow - precise clicks needed)
    {'time': 35000, 'ink': 30, 'mistakes': 6}, # Level 13 (Interlocking - more time/ink)
    {'ink': 40, 'mistakes': 8}, # Level 14 (Thin Frame - lots of ink needed)
    {'time': 20000, 'mistakes': 3}, # Level 15 (Checkerboard - less time, few mistakes)
    {'ink': 35, 'mistakes': 5}, # Level 16 (Long Snake)
    {'time': 30000}, # Level 17 (Castle Top)
    {'mistakes': 4}, # Level 18 (Symmetric-ish)
    {'ink': 35, 'mistakes': 6}, # Level 19 (Double U)
    {'time': 40000, 'ink': 40, 'mistakes': 7}, # Level 20 (Maze like)
    {'time': 15000, 'mistakes': 4}, # Level 21 (Full Column - less time)
    {'mistakes': 2}, # Level 22 (Scattered Dots - very few mistakes allowed)
    {}, # Level 23 (H Shape)
    {'ink': 30, 'mistakes': 5}, # Level 24 (Plus variations)
    {'time': 45000, 'ink': 45, 'mistakes': 5}, # Level 25 (Final - more time/ink, strict mistakes)
]