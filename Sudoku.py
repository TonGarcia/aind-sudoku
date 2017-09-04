
# coding: utf-8

# In[3]:

project_sudoku_grid_example = '..3.2.6..9..3.5..1..18.64....81.29..7.......8..67.82....26.95..8..2.3..9..5.1.3..'


# # Utils Functions & Variables
# 
# utils.py

# In[4]:

rows = 'ABCDEFGHI'
cols = '123456789'

def cross(a, b):
    # Associate LETTERs side with NUMBERs side, creating A1,A1...
    return [s+t for s in a for t in b]

boxes = cross(rows, cols)

row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]
unitlist = row_units + column_units + square_units
units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s],[]))-set([s])) for s in boxes)

def display(values):
    """
    Display the values as a 2-D grid.
    Input: The sudoku in dictionary form
    Output: None
    """
    width = 1+max(len(values[s]) for s in boxes)
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF': print(line)
    return


# # Main Execution Functions
# 
# function.py

# In[5]:

def grid_values(grid):
    """Convert grid string into {<box>: <value>} dict with '123456789' value for empties.

    Args:
        grid: Sudoku grid in string form, 81 characters long
    Returns:
        Sudoku grid in dictionary form:
        - keys: Box labels, e.g. 'A1'
        - values: Value in corresponding box, e.g. '8', or '123456789' if it is empty.
    """
    grid_dict = {}
    all_numbers = '123456789'
    boxes = cross(rows, cols)
    for box, grid_v in zip(boxes, grid):
        if grid_v == '.':
            grid_dict[box] = all_numbers
        elif grid_v in all_numbers:
         grid_dict[box] = grid_v
    return grid_dict


# In[6]:

print(grid_values(project_sudoku_grid_example))


# In[7]:

# eliminate strategy
def eliminate(values):
    """Eliminate values from peers of each box with a single value.

    Go through all the boxes, and whenever there is a box with a single value,
    eliminate this value from the set of values of all its peers.
    peers = a dictionary of boxes with it peers (columns, rows & square(3x3))

    Args:
        values: Sudoku in dictionary form. --> Populated Grid
    Returns:
        Resulting Sudoku in dictionary form after eliminating values.
    """

    boxes = [box for box in values.keys() if len(values[box]) == 1]
    for box in boxes:
        digit = values[box]
        for peer in peers[box]:
            values[peer] = values[peer].replace(digit,'')
    return values


# In[8]:

eliminated_sudoku_grid = eliminate(grid_values(project_sudoku_grid_example))


# In[9]:

def only_choice(values):
    """Finalize all values that are the only choice for a unit.

    Go through all the units, and whenever there is a unit with a value
    that only fits in one box, assign the value to this box.

    Input: Sudoku in dictionary form.
    Output: Resulting Sudoku in dictionary form after filling in only choices.
    """
    # TODO: Implement only choice strategy here
    for unit in unitlist:
        # iterate numbers values to find it on boxes
        for digit in '123456789':
            # iterate unit's boxes & create a "digit_places" map array containing the places where it number repeats 
            dplaces = [box for box in unit if digit in values[box]]
            # if it doesn't repeat, so there is a only choice place 
            if len(dplaces) == 1:
                values[dplaces[0]] = digit
    return values


# In[11]:

only_choice(eliminated_sudoku_grid)


# In[12]:

def reduce_puzzle(values):
    stalled = False
    while not stalled:
        # Check how many boxes have a determined value
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])

        # Your code here: Use the Eliminate Strategy
        eliminated_grid = eliminate(values)

        # Your code here: Use the Only Choice Strategy
        only_choice_grid = only_choice(eliminated_grid)

        # Check how many boxes have a determined value, to compare
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        # If no new values were added, stop the loop.
        stalled = solved_values_before == solved_values_after
        # Sanity check, return False if there is a box with zero available values:
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values


# In[13]:

harder_grid = '4.....8.5.3..........7......2.....6.....8.4......1.......6.3.7.5..2.....1.4......'


# In[51]:

def search(values):
    "Using depth-first search and propagation, create a search tree and solve the sudoku."
    # Prevent Type Error
    values_type = type(values)
    values = grid_values(values) if values_type == str else values
    if values == False:
        return 'wrong values type (not a String neither a Dict)'

    # First, reduce the puzzle using the previous function
    reduced = reduce_puzzle(values)
    if reduced is False:
        return False  ## Failed earlier
    if all(len(values[s]) == 1 for s in boxes):
        return values  ## Solved!

    # Choose one of the unfilled squares with the fewest possibilities
    # Loop on boxes to find the fewest length
    # s is the space (dict grid key), like: F3
    n, s = min((len(reduced[s]), s) for s in boxes if len(reduced[s]) > 1) # == 2 or len(reduced[s]) == 3
    # Now use recurrence to solve each one of the resulting sudokus, and 
    for value in values[s]:
        # Create the next entry (like forward propagation)
        new_sudoku = values.copy()
        new_sudoku[s] = value
        # Propagating to the next search
        attempt = search(new_sudoku)
        if attempt:
            return attempt


# In[52]:

search(harder_grid)


# In[ ]:



