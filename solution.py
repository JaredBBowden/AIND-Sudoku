assignments = []

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
    for box in values:
        for peer in peers[box]:
            if (len(values[box]) == 2) & (values[peer] == values[box]):

                # Identify shared peers
                peer_intersection = peers[box] & peers[peer]

                # Remove values that make up these twins from all other peers
                for one_twin in values[box]:
                    for peer in peer_intersection:
                        # Only remove values if there are values to remove!
                        if (values[box] != values[peer]) & (len(values[peer]) > 1):
                            values[peer] = values[peer].replace(one_twin, "")
    return values

def cross(A, B):
    "Cross product of elements in A and elements in B."
    return [s+t for s in A for t in B]


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
    grid = dict(zip(boxes, grid))

    for value in grid:
        if grid[value] == ".":
            grid[value] = '123456789'

    return grid


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
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    for box in solved_values:
        target = values[box]
        # Move through all peers and remove
        for peer in peers[box]:
            values[peer] = values[peer].replace(target,'')
    return values


def only_choice(values):
    for unit in unitlist:
        options = '123456789'

        for option in options:
            # Wow... this is kinda dense. But the alternative is too verbose
            surviving_options = [box for box in unit if option in values[box]]
            if len(surviving_options) == 1:
                values[surviving_options[0]] = option
    return values


def reduce_puzzle(values):
    stalled = False
    while not stalled:
        # Check how many boxes have a determined value
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])

        # Use the Eliminate Strategy
        values = eliminate(values)

        # Remove naked twins
        values = naked_twins(values)

        # Use the Only Choice Strategy
        values = only_choice(values)

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
    # First, reduce the puzzle using the previous function
    reduced_values = reduce_puzzle(values)

    # Simple case control flow that determines solved/unsolved status
    if reduced_values is False:
        return False ## Failed earlier
    if all(len(reduced_values[s]) == 1 for s in boxes):
        return reduced_values ## Solved!

    # Sort to find dictionary values with the shortest length
    sorted_values = sorted(reduced_values.items(), key = lambda item : len(item[1]))

    search_candidates = []
    for value in sorted_values:
        if len(value[1]) > 1:
            search_candidates.append(value[0])

    # Now use recursion to solve each one of the resulting sudokus, and if one
    # returns a value (not False), return that answer!
    for element in reduced_values[search_candidates[0]]:
        new_sudoku = reduced_values.copy()
        new_sudoku[search_candidates[0]] = element
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
    return search(grid_values(grid))


# Define some helper values
rows = 'ABCDEFGHI'
cols = '123456789'

boxes = cross(rows, cols)

row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]

# Identify units for diagonal solution
diagonal_units = [[(row + str(i + 1)) for i, row in enumerate(rows)] ,
                    [(row + str(9 - i)) for i, row in enumerate(rows)]]

unitlist = row_units + column_units + square_units + diagonal_units
units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s],[]))-set([s])) for s in boxes)


if __name__ == '__main__':
    diag_sudoku_grid = "9.1....8.8.5.7..4.2.4....6...7......5..............83.3..6......9................"
    display(solve(diag_sudoku_grid))

    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
