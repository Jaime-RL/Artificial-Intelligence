def parse_sudoku_file_cells(filename):
    sudokus = []
    
    with open(filename, 'r') as f:
        lines = f.readlines()
    
    current_sudoku = []
    for line in lines:
        line = line.strip()
        
        if not line or line.startswith('NAME:') or line.startswith('TYPE:') or line.startswith('COMMENT:') or line.startswith('SUDOKU'):
            if current_sudoku and len(current_sudoku) == 9:
                sudokus.append(current_sudoku)
                current_sudoku = []
            continue
        
        if line.isdigit() and len(line) == 9:
            row = [SudokuCell(len(current_sudoku), col, int(d)) for col, d in enumerate(line)]
            current_sudoku.append(row)
    
    if current_sudoku and len(current_sudoku) == 9:
        sudokus.append(current_sudoku)
    
    return sudokus


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 


class SudokuCell:
    def __init__(self, row, col, value=0):
        self.row = row
        self.col = col
        self.value = value
        self.domain = list(range(1, 10)) if value == 0 else [value]
    


values = [1,2,3,4,5,6,7,8,9]

def is_complete(solution):
    for row in solution:
        for cell in row:
            if cell.value == 0:
                return False
    return True
    
    
def select_new_variable(solution):
    for x in range(9):
        for y in range(9):
            if solution[x][y].value == 0:
                return x, y
    return None
            


def is_consistent(value, coords_variable, solution):
    
    x, y = coords_variable

    for i in range(9):
        if solution[i][y].value == value: return False
    
    for j in range(9):
        if solution[x][j].value == value: return False
        
    block_row, block_col = x // 3, y // 3
    start_row, start_col = block_row * 3, block_col * 3
    
    for i in range(start_row, start_row + 3):
        for j in range(start_col, start_col + 3):
            if solution[i][j].value == value:
                return False

    return True
        
        
def assign_value(value, variable, solution):
    x, y = variable
    solution[x][y].value = value
    

def undo(variable, value, interferences, solution):
    x, y = variable
    solution[x][y].value = 0  
    
    for i, j, value in interferences:
        solution[i][j].domain.append(value)


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -     

    
def interference(value, variable, solution):
    x, y = variable
    interferences = []
    
    # go all over the sudoku
    for i in range(9):
        for j in range(9):
            # skip the cell we are at
            if (i, j) == (x, y):
                continue
            
            # check if we are in a relevant coordinate
            same_row = i == x
            same_col = j == y
            same_block = (i // 3 == x // 3) and (j // 3 == y // 3)
            
            # if we are in relevant coordinate get its cell            
            if same_row or same_col or same_block:
                cell = solution[i][j]
                
                # if the relevant cell is 0
                if cell.value == 0 and value in cell.domain:
                    # remove from domain the value used
                    cell.domain.remove(value)
                    # keep the interferences made
                    interferences.append((i, j, value))
                    
    return interferences
            
            
def interferences_works(solution):
    for row in solution:
        for cell in row:
            # check if for any cell without assigned number, they can place at least one
            if cell.value == 0 and len(cell.domain) == 0:
                return False
    return True
  
def apply_interferences(_interferences, _solution):
    # Interferences already applied in the interference() function
    # This function is here as a placeholder for future constraint propagation
    return
  
  
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -     


def backtracking(solution):
    if is_complete(solution):
        return solution
    
    variable = select_new_variable(solution)
    
    for value in values:
        if is_consistent(value, variable, solution):
            assign_value(value, variable, solution)
        
            interferences = interference(value, variable, solution)
        
            if interferences_works(solution):
                apply_interferences(interferences, solution) # does nothing
                
                result = backtracking(solution)
                
                if result != None:
                    return result
                
            undo(variable, value, interferences, solution)

    return None
    

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -     

        
if __name__ == "__main__":
    sudokus = parse_sudoku_file_cells('sudoku.txt')
    
    for idx, sudoku in enumerate(sudokus):
        print(f"\nSolving Sudoku {idx+1}...")
        solution = backtracking(sudoku)
        
        if solution:
            print(f"Solution found:")
            for row in solution:
                print([cell.value for cell in row])
        else:
            print("No solution found")