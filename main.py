import random
import os

class Sudoku:
    def __init__(self, difficulty='medium'):
        self.board = [[0]*9 for _ in range(9)]
        self.solution = [[0]*9 for _ in range(9)]
        self.fixed = [[False]*9 for _ in range(9)]
        self.cursor = [0, 0]
        self.generate_puzzle(difficulty)
    
    def generate_puzzle(self, difficulty):
        # Generate a complete valid sudoku board
        self.fill_board()
        # Copy solution
        for i in range(9):
            for j in range(9):
                self.solution[i][j] = self.board[i][j]
        
        # Remove numbers based on difficulty
        cells_to_remove = {'easy': 30, 'medium': 40, 'hard': 50}
        remove_count = cells_to_remove.get(difficulty, 40)
        
        cells = [(i, j) for i in range(9) for j in range(9)]
        random.shuffle(cells)
        
        for i, j in cells[:remove_count]:
            self.board[i][j] = 0
        
        # Mark fixed cells
        for i in range(9):
            for j in range(9):
                if self.board[i][j] != 0:
                    self.fixed[i][j] = True
    
    def fill_board(self):
        # Simple backtracking to fill the board
        nums = list(range(1, 10))
        random.shuffle(nums)
        return self.fill_cell(0, 0, nums)
    
    def fill_cell(self, row, col, nums):
        if row == 9:
            return True
        
        next_row, next_col = (row, col + 1) if col < 8 else (row + 1, 0)
        
        random.shuffle(nums)
        for num in nums:
            if self.is_valid(row, col, num):
                self.board[row][col] = num
                if self.fill_cell(next_row, next_col, nums):
                    return True
                self.board[row][col] = 0
        
        return False
    
    def is_valid(self, row, col, num):
        # Check row
        if num in self.board[row]:
            return False
        
        # Check column
        if num in [self.board[i][col] for i in range(9)]:
            return False
        
        # Check 3x3 box
        box_row, box_col = 3 * (row // 3), 3 * (col // 3)
        for i in range(box_row, box_row + 3):
            for j in range(box_col, box_col + 3):
                if self.board[i][j] == num:
                    return False
        
        return True
    
    def clear_screen(self):
        os.system('clear' if os.name != 'nt' else 'cls')
    
    def display(self):
        self.clear_screen()
        print("\n" + "═" * 50)
        print(" " * 18 + "SUDOKU GAME")
        print("═" * 50 + "\n")
        
        for i in range(9):
            if i % 3 == 0 and i != 0:
                print("    " + "─" * 41)
            
            row_str = "    "
            for j in range(9):
                if j % 3 == 0 and j != 0:
                    row_str += "│ "
                
                # Highlight cursor position
                if self.cursor[0] == i and self.cursor[1] == j:
                    if self.board[i][j] == 0:
                        row_str += "[_]"
                    else:
                        color = "\033[96m" if self.fixed[i][j] else "\033[93m"
                        row_str += f"[{color}{self.board[i][j]}\033[0m]"
                else:
                    if self.board[i][j] == 0:
                        row_str += " _ "
                    else:
                        color = "\033[96m" if self.fixed[i][j] else "\033[92m"
                        row_str += f" {color}{self.board[i][j]}\033[0m "
            
            print(row_str)
        
        print("\n" + "═" * 50)
        print("\n  Controls:")
        print("  Arrow keys: wasd | Numbers: 1-9 | Clear: 0 | Check: c | Quit: q")
        print("  \033[96mBlue\033[0m = Given | \033[92mGreen\033[0m = Your input | \033[93mYellow\033[0m = Selected")
        print("═" * 50)
    
    def move_cursor(self, direction):
        if direction == 'up' and self.cursor[0] > 0:
            self.cursor[0] -= 1
        elif direction == 'down' and self.cursor[0] < 8:
            self.cursor[0] += 1
        elif direction == 'left' and self.cursor[1] > 0:
            self.cursor[1] -= 1
        elif direction == 'right' and self.cursor[1] < 8:
            self.cursor[1] += 1
    
    def set_value(self, value):
        row, col = self.cursor
        if not self.fixed[row][col]:
            if value == 0:
                self.board[row][col] = 0
            elif self.is_valid(row, col, value) or self.board[row][col] == value:
                self.board[row][col] = value
    
    def check_solution(self):
        for i in range(9):
            for j in range(9):
                if self.board[i][j] != self.solution[i][j]:
                    return False
        return True
    
    def play(self):
        self.display()
        
        while True:
            try:
                command = input("\n  Enter command: ").lower().strip()
                
                if command == 'q':
                    print("\n  Thanks for playing!")
                    break
                elif command == 'w':
                    self.move_cursor('up')
                elif command == 's':
                    self.move_cursor('down')
                elif command == 'a':
                    self.move_cursor('left')
                elif command == 'd':
                    self.move_cursor('right')
                elif command in '123456789':
                    self.set_value(int(command))
                elif command == '0':
                    self.set_value(0)
                elif command == 'c':
                    if self.check_solution():
                        self.display()
                        print("\n  🎉 Congratulations! You solved it! 🎉\n")
                        break
                    else:
                        self.display()
                        print("\n  ❌ Not quite right yet. Keep trying!")
                        continue
                
                self.display()
                
            except KeyboardInterrupt:
                print("\n\n  Thanks for playing!")
                break

if __name__ == "__main__":
    print("\n" + "═" * 50)
    print(" " * 15 + "WELCOME TO SUDOKU!")
    print("═" * 50)
    print("\n  Select difficulty:")
    print("  1. Easy")
    print("  2. Medium")
    print("  3. Hard")
    
    while True:
        choice = input("\n  Enter choice (1-3): ").strip()
        if choice in ['1', '2', '3']:
            difficulty = ['easy', 'medium', 'hard'][int(choice) - 1]
            break
        print("  Invalid choice. Please enter 1, 2, or 3.")
    
    game = Sudoku(difficulty)
    game.play()