import tkinter as tk
from tkinter import messagebox
from collections import defaultdict
import copy

# ======================================
# SOLVER ENGINE
# ======================================

class SudokuAnalyzer:

    def __init__(self, board):
        self.board = board
        self.original = copy.deepcopy(board)
        self.techniques_used = defaultdict(int)

    def find_empty(self):
        for r in range(9):
            for c in range(9):
                if self.board[r][c] == 0:
                    return r, c
        return None

    def is_valid(self, num, row, col):
        if num in self.board[row]:
            return False

        for r in range(9):
            if self.board[r][col] == num:
                return False

        box_row = (row // 3) * 3
        box_col = (col // 3) * 3
        for r in range(box_row, box_row + 3):
            for c in range(box_col, box_col + 3):
                if self.board[r][c] == num:
                    return False
        return True

    def get_candidates(self, row, col):
        candidates = set(range(1, 10))
        candidates -= set(self.board[row])

        for r in range(9):
            candidates.discard(self.board[r][col])

        box_row = (row // 3) * 3
        box_col = (col // 3) * 3
        for r in range(box_row, box_row + 3):
            for c in range(box_col, box_col + 3):
                candidates.discard(self.board[r][c])
        return candidates

    def apply_naked_single(self):
        changed = False
        for r in range(9):
            for c in range(9):
                if self.board[r][c] == 0:
                    candidates = self.get_candidates(r, c)
                    if len(candidates) == 1:
                        self.board[r][c] = candidates.pop()
                        self.techniques_used["Naked Single"] += 1
                        changed = True
        return changed

    def solve_backtracking(self):
        empty = self.find_empty()
        if not empty:
            return True

        row, col = empty
        for num in range(1, 10):
            if self.is_valid(num, row, col):
                self.board[row][col] = num
                if self.solve_backtracking():
                    return True
                self.board[row][col] = 0
        return False

    def solve(self):
        while self.apply_naked_single():
            pass

        if self.find_empty():
            self.techniques_used["Backtracking"] += 1
            self.solve_backtracking()

        return self.board


# ======================================
# GUI
# ======================================

class SudokuGUI:

    def __init__(self, root):
        self.root = root
        self.root.title("Sudoku Solver Analyzer PRO")

        self.entries = []
        self.original_cells = set()

        self.create_grid()
        self.create_buttons()
        self.create_info_label()

    # ==============================
    # GRID WITH 3x3 BLACK BORDERS
    # ==============================

    def create_grid(self):
        frame = tk.Frame(self.root, bg="black")
        frame.pack(padx=10, pady=10)

        for r in range(9):
            row_entries = []
            for c in range(9):

                border_width = 1

                if r % 3 == 0:
                    top = 3
                else:
                    top = 1

                if c % 3 == 0:
                    left = 3
                else:
                    left = 1

                entry = tk.Entry(
                    frame,
                    width=2,
                    font=("Arial", 20),
                    justify="center",
                    bd=1,
                    relief="solid"
                )

                entry.grid(row=r, column=c, padx=(left, 1), pady=(top, 1))
                row_entries.append(entry)

            self.entries.append(row_entries)

    # ==============================
    # BUTTONS
    # ==============================

    def create_buttons(self):
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)

        solve_button = tk.Button(button_frame, text="Start Analyzer", command=self.solve)
        solve_button.grid(row=0, column=0, padx=5)

        clear_button = tk.Button(button_frame, text="Clear", command=self.clear)
        clear_button.grid(row=0, column=1, padx=5)

    def create_info_label(self):
        self.info_label = tk.Label(self.root, text="", justify="left")
        self.info_label.pack()

    # ==============================
    # UTILITIES
    # ==============================

    def get_board(self):
        board = []
        self.original_cells.clear()

        for r in range(9):
            row = []
            for c in range(9):
                val = self.entries[r][c].get()

                if val == "":
                    row.append(0)
                else:
                    try:
                        num = int(val)
                        if 1 <= num <= 9:
                            row.append(num)
                            self.original_cells.add((r, c))
                        else:
                            return None
                    except:
                        return None
            board.append(row)
        return board

    def display_board(self, board):
        for r in range(9):
            for c in range(9):
                self.entries[r][c].delete(0, tk.END)
                self.entries[r][c].insert(0, str(board[r][c]))

                if (r, c) in self.original_cells:
                    self.entries[r][c].config(fg="black")
                else:
                    self.entries[r][c].config(fg="blue")

    def clear(self):
        for r in range(9):
            for c in range(9):
                self.entries[r][c].delete(0, tk.END)
                self.entries[r][c].config(fg="black")
        self.info_label.config(text="")

    # ==============================
    # SOLVE
    # ==============================

    def solve(self):
        board = self.get_board()
        if board is None:
            messagebox.showerror("Error", "Input tidak valid!")
            return

        analyzer = SudokuAnalyzer(board)
        solution = analyzer.solve()

        self.display_board(solution)

        text = "Techniques Used:\n"
        for k, v in analyzer.techniques_used.items():
            text += f"{k}: {v}\n"

        self.info_label.config(text=text)


# ======================================
# RUN
# ======================================

if __name__ == "__main__":
    root = tk.Tk()
    app = SudokuGUI(root)
    root.mainloop()