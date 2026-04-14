"""
CSP-based Sudoku Solver with Backtracking, Forward Checking, and AC-3
AI Assignment 5 - Question 3

This solver uses:
- Constraint Satisfaction Problem (CSP) approach
- Backtracking search algorithm
- Forward Checking for constraint propagation
- AC-3 algorithm for arc consistency
- MRV (Minimum Remaining Values) heuristic for variable selection
"""

class SudokuCSP:
    """CSP-based Sudoku solver with AC-3 and Forward Checking"""
    
    def __init__(self, board):
        """Initialize CSP solver with a Sudoku board"""
        self.board = [row[:] for row in board]
        self.domains = self._create_domains()
        self.constraints = self._build_constraints()
        self.backtrack_count = 0
        self.backtrack_failures = 0
    
    def _create_domains(self):
        """Create initial domains for all variables"""
        domains = {}
        for r in range(9):
            for c in range(9):
                if self.board[r][c] != 0:
                    domains[(r, c)] = {self.board[r][c]}
                else:
                    domains[(r, c)] = set(range(1, 10))
        return domains
    
    def _build_constraints(self):
        """Build constraint graph"""
        constraints = {}
        for r in range(9):
            for c in range(9):
                neighbors = set()
                # Row neighbors
                for col in range(9):
                    if col != c:
                        neighbors.add((r, col))
                # Column neighbors
                for row in range(9):
                    if row != r:
                        neighbors.add((row, c))
                # Box neighbors
                br, bc = (r // 3) * 3, (c // 3) * 3
                for i in range(br, br + 3):
                    for j in range(bc, bc + 3):
                        if (i, j) != (r, c):
                            neighbors.add((i, j))
                constraints[(r, c)] = neighbors
        return constraints
    
    def _get_neighbors(self, var):
        """Get neighbors of a variable"""
        return self.constraints[var]
    
    def ac3(self):
        """AC-3 Algorithm: Enforce arc consistency"""
        queue = []
        
        # Initialize queue with all arcs
        for var in self.domains:
            for neighbor in self._get_neighbors(var):
                if neighbor in self.domains:
                    queue.append((var, neighbor))
        
        while queue:
            xi, xj = queue.pop(0)
            if self._revise(xi, xj):
                # Check for domain wipeout
                if len(self.domains[xi]) == 0:
                    return False
                
                # Add neighbors to queue
                for neighbor in self._get_neighbors(xi):
                    if neighbor != xj and neighbor in self.domains:
                        queue.append((neighbor, xi))
        
        return True
    
    def _revise(self, xi, xj):
        """Revise domain of xi with respect to xj"""
        revised = False
        to_remove = []
        
        for value in self.domains[xi]:
            # For Sudoku: xi and xj must have different values
            if len(self.domains[xj]) == 1:
                xj_value = list(self.domains[xj])[0]
                if value == xj_value:
                    to_remove.append(value)
                    revised = True
        
        for value in to_remove:
            self.domains[xi].discard(value)
        
        return revised
    
    def forward_check(self, var, value):
        """Forward checking: Remove value from neighbor domains"""
        removed = {}
        
        for neighbor in self._get_neighbors(var):
            if neighbor in self.domains and value in self.domains[neighbor]:
                if neighbor not in removed:
                    removed[neighbor] = []
                removed[neighbor].append(value)
                self.domains[neighbor].discard(value)
                
                # Domain wipeout
                if len(self.domains[neighbor]) == 0:
                    return False, removed
        
        return True, removed
    
    def _select_unassigned_variable(self, assigned):
        """Select unassigned variable using MRV heuristic"""
        unassigned = []
        for r in range(9):
            for c in range(9):
                if (r, c) not in assigned and len(self.domains[(r, c)]) > 1:
                    unassigned.append((r, c))
        
        if not unassigned:
            return None
        
        # MRV: Choose variable with minimum domain
        return min(unassigned, key=lambda var: len(self.domains[var]))
    
    def backtrack(self, assigned):
        """Backtracking search with constraint propagation"""
        self.backtrack_count += 1
        
        # Check if complete
        if len(assigned) == 81 - sum(1 for r in range(9) for c in range(9) if self.board[r][c] != 0):
            return assigned
        
        # Select variable
        var = self._select_unassigned_variable(assigned)
        if var is None:
            return None
        
        # Try each value
        for value in sorted(self.domains[var]):
            # Save state
            domains_backup = {k: v.copy() for k, v in self.domains.items()}
            
            # Assign
            assigned[var] = value
            self.domains[var] = {value}
            
            # Forward check
            consistent, removed = self.forward_check(var, value)
            
            if consistent:
                # AC-3
                if self.ac3():
                    # Recurse
                    result = self.backtrack(assigned)
                    if result is not None:
                        return result
            
            # Restore on failure
            del assigned[var]
            self.domains.clear()
            self.domains.update(domains_backup)
        
        self.backtrack_failures += 1
        return None
    
    def solve(self):
        """Solve the puzzle"""
        # Initial AC-3
        if not self.ac3():
            return False
        
        assigned = {}
        result = self.backtrack(assigned)
        
        if result:
            for (r, c), value in result.items():
                self.board[r][c] = value
            return True
        
        return False
    
    def display(self):
        """Display the board"""
        lines = []
        for i, row in enumerate(self.board):
            if i % 3 == 0 and i != 0:
                lines.append("------+-------+------")
            line = ""
            for j, cell in enumerate(row):
                if j % 3 == 0 and j != 0:
                    line += "| "
                line += str(cell) + " "
            lines.append(line)
        return "\n".join(lines)


def read_board(filename):
    """Read Sudoku board from file"""
    try:
        board = []
        with open(filename, 'r') as f:
            for line in f:
                line = line.strip()
                if len(line) == 9 and line.isdigit():
                    board.append([int(c) for c in line])
        
        if len(board) == 9:
            return board
        return None
    except:
        return None


def solve_puzzle(filepath, name):
    """Solve a puzzle and return statistics"""
    print(f"\n{'='*60}")
    print(f"{name}")
    print(f"{'='*60}")
    
    board = read_board(filepath)
    if not board:
        print(f"Error reading file")
        return None
    
    print("\nOriginal Board:")
    solver = SudokuCSP(board)
    print(solver.display())
    
    if solver.solve():
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
