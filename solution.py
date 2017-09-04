rows = 'ABCDEFGHI'
cols = '123456789'

assignments = []

def cross(A, B):
    "Cross product of elements in A and elements in B."
    # Associate LETTERs side with NUMBERs side, creating A1,A1...
    return [s + t for s in A for t in B]

# initializing
grid_dict = {} ## grid as dictionary
boxes = cross(rows, cols) ## boxes "names", like: A1,A2... (list)
row_units = [cross(r, cols) for r in rows] ## rows: [[A1..A9],[B1...B9]] (list of lists)
column_units = [cross(rows, c) for c in cols] ## columns: [[A1...I1],[A2...I2]] (list of lists)
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')] ## square (3x3): [[A1...C3],[A4..C6]] (list of lists)
unitlist = row_units + column_units + square_units ## list of all lists perspectives
units = dict((s, [u for u in unitlist if s in u]) for s in boxes) ## referencing boxes per unit (square), as dict of lists of lists {[[]]}
peers = dict((s, set(sum(units[s],[]))-set([s])) for s in boxes) ## peers per box as dict of dict {{}}

def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """

    # Don't waste memory appending actions that don't actually change any values
    if values[box] == value:
        return values

    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values

def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """

    # Find all instances of naked twins
    for box in values:
        value_box = values[box]

        # Check if current box has the naked twins candidate length
        if len(value_box) == 2:
            # search on it twin peer
            for peer in peers[box]:
                # If it true, so FOUND it naked peer
                if value_box == values[peer]:
                    twin_peer = peer
                    for deep_peer in peers[box]:
                        if len(values[deep_peer]) > len(value_box) and (deep_peer[0]==box[0] or deep_peer[1]==box[1]) and (twin_peer in peers[deep_peer]):
                            for digit in value_box:
                                if digit in values[deep_peer]:
                                    assign_value(values, deep_peer, values[deep_peer].replace(digit, ''))

    return values

def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    # iterate each box (A1,A2...) & each value (char index element at received grid/sudoku)
    for box, grid_v in zip(boxes, grid):
        if grid_v == '.':
            # if . it means an empty box, so receive all numbers
            grid_dict[box] = cols
        elif grid_v in cols:
            # if cols (string of all numbers) contains it grid_value, so store it as it is
            grid_dict[box] = grid_v
    # return it filled dictionary
    return grid_dict

def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    """
    width = 1+max(len(values[s]) for s in boxes)
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF': print(line)
    return

def eliminate(values):
    # boxes keys "constant"
    boxes = [box for box in values.keys() if len(values[box]) == 1]
    # iterate each box
    for box in boxes:
        # retrieve it box value digit
        digit = values[box]
        # iterate peers (columns/units/lines)
        for peer in peers[box]:
            # eliminate it current iteration digit from it peer boxes
            # peers is a dict of boxes which are another dictionaries with associated boxes relation
            # values[peer] = values[peer].replace(digit,'')
            assign_value(values, peer, values[peer].replace(digit,''))
    return values

def only_choice(values):
    # iterate each unit (3x3) as array, better than iterate it list
    for unit in unitlist:
        # iterate numbers values to find it "chars" on each box
        for digit in '123456789':
            # iterate unit's boxes & create a "digit_places" map array containing the places where it number repeats
            dplaces = [box for box in unit if digit in values[box]]
            # if it doesn't repeat, so there is a only choice place
            if len(dplaces) == 1:
                # values[dplaces[0]] = digit
                assign_value(values, dplaces[0], digit)
    return values

def reduce_puzzle(values):
    stalled = False
    while not stalled:
        # Check how many boxes have a determined value
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])

        # Eliminate Strategy
        eliminated_grid = eliminate(values)

        # Only Choice Strategy
        only_choice_grid = only_choice(eliminated_grid)

        # Check how many boxes have a determined value, to compare
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        # If no new values were added, stop the loop.
        stalled = solved_values_before == solved_values_after
        # Sanity check, return False if there is a box with zero available values:
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values

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
    n, s = min((len(reduced[s]), s) for s in boxes if len(reduced[s]) > 1)
    # Now use recurrence to solve each one of the resulting sudokus, and
    for value in values[s]:
        # Create the next entry (like forward propagation)
        new_sudoku = values.copy()
        new_sudoku[s] = value
        # Propagating to the next search
        attempt = search(new_sudoku)
        if attempt:
            return attempt

def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    solved = True
    searched_grid = search(grid)
    solved = [False for sg in searched_grid if len(searched_grid[sg]) > 1]
    if solved: return searched_grid


if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    display(solve(diag_sudoku_grid))

    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')