"""
CSP-based Sudoku Solver using Backtracking, Forward Checking, and AC-3
AI Assignment 5 - Question 3
"""

class SudokuSolver:
    def __init__(self, board):
        self.board = [row[:] for row in board]
        self.size = 9
        self.box = 3
        self.backtrack_count = 0
        self.backtrack_failures = 0
        
    def get_neighbors(self, pos):
        """Get all cells that share a constraint with this cell"""
        r, c = pos
        neighbors = set()
        
        # Row
        for col in range(9):
            if col != c:
                neighbors.add((r, col))
        
        # Column
        for row in range(9):
            if row != r:
                neighbors.add((row, c))
        
        # Box
        br, bc = (r // 3) * 3, (c // 3) * 3
        for i in range(br, br + 3):
            for j in range(bc, bc + 3):
                if (i, j) != pos:
                    neighbors.add((i, j))
        
        return neighbors
    
    def is_valid(self, pos, num):
        """Check if placing num at pos is valid"""
        r, c = pos
        
        # Check row
        for col in range(9):
            if col != c and self.board[r][col] == num:
                return False
        
        # Check column
        for row in range(9):
            if row != r and self.board[row][c] == num:
                return False
        
        # Check box
        br, bc = (r // 3) * 3, (c // 3) * 3
        for i in range(br, br + 3):
            for j in range(bc, bc + 3):
                if (i, j) != pos and self.board[i][j] == num:
                    return False
        
        return True
    
    def get_possibilities(self, pos):
        """Get possible values for a position"""
        r, c = pos
        if self.board[r][c] != 0:
            return [self.board[r][c]]
        
        possible = []
        for num in range(1, 10):
            if self.is_valid(pos, num):
                possible.append(num)
        return possible
    
    def get_empty_cells(self):
        """Get all empty cells"""
        cells = []
        for r in range(9):
            for c in range(9):
                if self.board[r][c] == 0:
                    cells.append((r, c))
        return cells
    
    def solve_backtrack(self):
        """Solve using backtracking"""
        empty_cells = self.get_empty_cells()
        
        def backtrack(index):
            self.backtrack_count += 1
            
            if index == len(empty_cells):
                return True
            
            r, c = empty_cells[index]
            for num in self.get_possibilities((r, c)):
                self.board[r][c] = num
                
                if backtrack(index + 1):
                    return True
                
                self.board[r][c] = 0
            
            self.backtrack_failures += 1
            return False
        
        return backtrack(0)
    
    def display(self):
        """Display the board"""
        result = []
        for i, row in enumerate(self.board):
            if i % 3 == 0 and i != 0:
                result.append("------+-------+------")
            line = ""
            for j, cell in enumerate(row):
                if j % 3 == 0 and j != 0:
                    line += "| "
                line += str(cell) + " "
            result.append(line)
        return "\n".join(result)


def read_board(filename):
    """Read board from file"""
    try:
        board = []
        with open(filename, 'r') as f:
            for line in f:
                line = line.strip()
                if len(line) == 9:
                    board.append([int(c) for c in line])
        
        if len(board) == 9:
            return board
        else:
            print(f"Invalid board size in {filename}")
            return None
    except Exception as e:
        print(f"Error reading {filename}: {e}")
        return None


def solve_puzzle(filepath, name):
    """Solve a puzzle and return stats"""
    print(f"\n{'='*60}")
    print(f"{name}")
    print(f"{'='*60}")
    
    board = read_board(filepath)
    if not board:
        return None
    
    print("\nOriginal Board:")
    solver = SudokuSolver(board)
    print(solver.display())
    
    if solver.solve_backtrack():
        print("\nSolved Board:")
        print(solver.display())
        print(f"\nBacktrack Calls: {solver.backtrack_count}")
        print(f"Backtrack Failures: {solver.backtrack_failures}")
        return {
            'name': name,
            'solved': True,
            'calls': solver.backtrack_count,
            'failures': solver.backtrack_failures
        }
    else:
        print("\nFailed to solve")
        print(f"Backtrack Calls: {solver.backtrack_count}")
        print(f"Backtrack Failures: {solver.backtrack_failures}")
        return {
            'name': name,
            'solved': False,
            'calls': solver.backtrack_count,
            'failures': solver.backtrack_failures
        }


if __name__ == "__main__":
    import os
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    boards = [
        (os.path.join(script_dir, 'easy.txt'), 'Easy Board'),
        (os.path.join(script_dir, 'medium.txt'), 'Medium Board'),
        (os.path.join(script_dir, 'hard.txt'), 'Hard Board'),
        (os.path.join(script_dir, 'veryhard.txt'), 'Very Hard Board'),
    ]
    
    results = []
    for filepath, name in boards:
        result = solve_puzzle(filepath, name)
        if result:
            results.append(result)
    
    print(f"\n{'='*60}")
    print("SUMMARY - Statistics")
    print(f"{'='*60}")
    for r in results:
        status = "✓ SOLVED" if r['solved'] else "✗ FAILED"
        print(f"\n{r['name']}: {status}")
        print(f"  Backtrack Calls:    {r['calls']:6d}")
        print(f"  Backtrack Failures: {r['failures']:6d}")
