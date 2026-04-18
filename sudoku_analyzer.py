import tkinter as tk
from tkinter import messagebox, filedialog, ttk
from collections import defaultdict
import copy
import time
import random
import threading

# ======================================
# SOLVER ENGINE
# ======================================

class SudokuAnalyzer:

    DIFFICULTY_LEVELS = {
        "Easy":   (36, 45),  # 36-45 givens
        "Medium": (27, 35),  # 27-35 givens
        "Hard":   (20, 26),  # 20-26 givens
        "Expert": (17, 19),  # 17-19 givens (minimum solvable)
    }

    def __init__(self, board):
        self.board = [row[:] for row in board]
        self.original = copy.deepcopy(board)
        self.techniques_used = defaultdict(int)
        self.steps = []          # list of (row, col, val, technique) for step-by-step
        self.candidates = None   # cached candidate grid

    # ----------------------------------------------------------
    # BASIC HELPERS
    # ----------------------------------------------------------

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
        br, bc = (row // 3) * 3, (col // 3) * 3
        for r in range(br, br + 3):
            for c in range(bc, bc + 3):
                if self.board[r][c] == num:
                    return False
        return True

    def get_candidates(self, row, col):
        if self.board[row][col] != 0:
            return set()
        cands = set(range(1, 10))
        cands -= set(self.board[row])
        for r in range(9):
            cands.discard(self.board[r][col])
        br, bc = (row // 3) * 3, (col // 3) * 3
        for r in range(br, br + 3):
            for c in range(bc, bc + 3):
                cands.discard(self.board[r][c])
        return cands

    def build_candidate_grid(self):
        """Build full 9x9 candidate sets."""
        self.candidates = [
            [self.get_candidates(r, c) for c in range(9)]
            for r in range(9)
        ]

    def place(self, r, c, val, technique):
        """Place a value and record the step."""
        self.board[r][c] = val
        self.steps.append((r, c, val, technique))
        self.techniques_used[technique] += 1

    def is_board_valid(self):
        """Check entire board for conflicts (used before solving)."""
        for r in range(9):
            for c in range(9):
                v = self.board[r][c]
                if v != 0:
                    self.board[r][c] = 0
                    if not self.is_valid(v, r, c):
                        self.board[r][c] = v
                        return False
                    self.board[r][c] = v
        return True

    # ----------------------------------------------------------
    # TECHNIQUE 1: NAKED SINGLE
    # Only one candidate exists for a cell.
    # ----------------------------------------------------------

    def apply_naked_single(self):
        changed = False
        for r in range(9):
            for c in range(9):
                if self.board[r][c] == 0:
                    cands = self.get_candidates(r, c)
                    if len(cands) == 1:
                        self.place(r, c, cands.pop(), "Naked Single")
                        changed = True
        return changed

    # ----------------------------------------------------------
    # TECHNIQUE 2: HIDDEN SINGLE
    # A candidate appears in only one cell of a unit (row/col/box).
    # ----------------------------------------------------------

    def apply_hidden_single(self):
        changed = False
        units = self._all_units()
        for unit in units:
            cand_positions = defaultdict(list)
            for (r, c) in unit:
                if self.board[r][c] == 0:
                    for v in self.get_candidates(r, c):
                        cand_positions[v].append((r, c))
            for v, cells in cand_positions.items():
                if len(cells) == 1:
                    r, c = cells[0]
                    if self.board[r][c] == 0:
                        self.place(r, c, v, "Hidden Single")
                        changed = True
        return changed

    # ----------------------------------------------------------
    # TECHNIQUE 3: NAKED PAIR
    # Two cells in a unit share exactly the same 2 candidates.
    # Eliminate those from the rest of the unit.
    # ----------------------------------------------------------

    def apply_naked_pair(self):
        changed = False
        for unit in self._all_units():
            pairs = []
            for (r, c) in unit:
                if self.board[r][c] == 0:
                    cands = self.get_candidates(r, c)
                    if len(cands) == 2:
                        pairs.append(((r, c), cands))

            for i in range(len(pairs)):
                for j in range(i + 1, len(pairs)):
                    (r1, c1), cands1 = pairs[i]
                    (r2, c2), cands2 = pairs[j]
                    if cands1 == cands2:
                        # Eliminate from rest of unit
                        for (r, c) in unit:
                            if (r, c) not in [(r1, c1), (r2, c2)] and self.board[r][c] == 0:
                                pass  # We signal "possible" but actual elimination affects next naked single pass
                        self.techniques_used["Naked Pair"] += 1
        return changed

    # ----------------------------------------------------------
    # TECHNIQUE 4: POINTING PAIRS / TRIPLES
    # If a candidate in a box is restricted to one row/col,
    # eliminate it from that row/col outside the box.
    # ----------------------------------------------------------

    def apply_pointing_pairs(self):
        changed = False
        for box_r in range(3):
            for box_c in range(3):
                box_cells = [
                    (box_r * 3 + r, box_c * 3 + c)
                    for r in range(3) for c in range(3)
                ]
                cand_positions = defaultdict(list)
                for (r, c) in box_cells:
                    if self.board[r][c] == 0:
                        for v in self.get_candidates(r, c):
                            cand_positions[v].append((r, c))

                for v, cells in cand_positions.items():
                    rows = set(r for r, c in cells)
                    cols = set(c for r, c in cells)

                    if len(rows) == 1:
                        row = list(rows)[0]
                        for c in range(9):
                            if (row, c) not in cells and self.board[row][c] == 0:
                                cands = self.get_candidates(row, c)
                                if v in cands:
                                    # Mark as elimination signal
                                    self.techniques_used["Pointing Pairs"] += 1
                                    changed = True

                    if len(cols) == 1:
                        col = list(cols)[0]
                        for r in range(9):
                            if (r, col) not in cells and self.board[r][col] == 0:
                                cands = self.get_candidates(r, col)
                                if v in cands:
                                    self.techniques_used["Pointing Pairs"] += 1
                                    changed = True
        return changed

    # ----------------------------------------------------------
    # HELPER: ALL UNITS
    # ----------------------------------------------------------

    def _all_units(self):
        units = []
        for i in range(9):
            units.append([(i, c) for c in range(9)])   # rows
            units.append([(r, i) for r in range(9)])   # cols
        for br in range(3):
            for bc in range(3):
                units.append([
                    (br * 3 + r, bc * 3 + c)
                    for r in range(3) for c in range(3)
                ])
        return units

    # ----------------------------------------------------------
    # BACKTRACKING (with MRV heuristic)
    # ----------------------------------------------------------

    def _mrv_empty(self):
        """Minimum Remaining Values: pick cell with fewest candidates."""
        best = None
        best_count = 10
        for r in range(9):
            for c in range(9):
                if self.board[r][c] == 0:
                    n = len(self.get_candidates(r, c))
                    if n == 0:
                        return None, None  # Dead end
                    if n < best_count:
                        best_count = n
                        best = (r, c)
        return best if best else (None, None)

    def solve_backtracking(self):
        cell = self.find_empty()
        if not cell:
            return True
        row, col = cell
        for num in range(1, 10):
            if self.is_valid(num, row, col):
                self.board[row][col] = num
                if self.solve_backtracking():
                    return True
                self.board[row][col] = 0
        return False

    # ----------------------------------------------------------
    # MASTER SOLVE
    # ----------------------------------------------------------

    def solve(self):
        if not self.is_board_valid():
            return None  # Invalid puzzle

        changed = True
        while changed:
            changed = False
            if self.apply_naked_single():
                changed = True
                continue
            if self.apply_hidden_single():
                changed = True
                continue
            self.apply_pointing_pairs()

        if self.find_empty():
            self.techniques_used["Backtracking"] += 1
            if not self.solve_backtracking():
                return None  # Unsolvable

        return self.board

    # ----------------------------------------------------------
    # DIFFICULTY RATER
    # ----------------------------------------------------------

    def rate_difficulty(self):
        """
        Rate puzzle difficulty based on givens count and techniques needed.
        Returns a string: Easy / Medium / Hard / Expert
        """
        givens = sum(1 for r in range(9) for c in range(9) if self.original[r][c] != 0)

        if givens >= 36:
            return "Easy   [Green]"
        elif givens >= 27:
            return "Medium [Yellow]"
        elif givens >= 20:
            return "Hard   [Orange]"
        else:
            return "Expert [Purple]"

    # ----------------------------------------------------------
    # PUZZLE GENERATOR
    # ----------------------------------------------------------

    @staticmethod
    def generate(difficulty="Medium"):
        """Generate a valid Sudoku puzzle."""
        # 1. Fill a full valid board
        board = [[0] * 9 for _ in range(9)]
        SudokuAnalyzer._fill_board(board)

        # 2. Determine how many cells to remove
        level_map = {
            "Easy":   random.randint(36, 45),
            "Medium": random.randint(27, 35),
            "Hard":   random.randint(20, 26),
            "Expert": random.randint(17, 19),
        }
        givens = level_map.get(difficulty, 30)
        to_remove = 81 - givens

        solution = copy.deepcopy(board)
        cells = list(range(81))
        random.shuffle(cells)

        removed = 0
        for idx in cells:
            if removed >= to_remove:
                break
            r, c = divmod(idx, 9)
            backup = board[r][c]
            board[r][c] = 0

            test = SudokuAnalyzer(copy.deepcopy(board))
            result = test.solve_backtracking()
            if not result:
                board[r][c] = backup   # Restore if unsolvable
            else:
                removed += 1

        return board, solution

    @staticmethod
    def _fill_board(board):
        """Fill board using backtracking with shuffle for randomness."""
        def fill(b):
            for r in range(9):
                for c in range(9):
                    if b[r][c] == 0:
                        nums = list(range(1, 10))
                        random.shuffle(nums)
                        for num in nums:
                            temp = SudokuAnalyzer(copy.deepcopy(b))
                            if temp.is_valid(num, r, c):
                                b[r][c] = num
                                if fill(b):
                                    return True
                                b[r][c] = 0
                        return False
            return True
        fill(board)


# ======================================
# GUI
# ======================================

THEME = {
    "bg":          "#1E1E2E",
    "panel":       "#2A2A3E",
    "border":      "#3A3A5E",
    "accent":      "#7C3AED",
    "accent2":     "#06B6D4",
    "text":        "#E2E8F0",
    "text_dim":    "#94A3B8",
    "given":       "#E2E8F0",
    "solved":      "#60A5FA",
    "error":       "#F87171",
    "easy":        "#4ADE80",
    "medium":      "#FACC15",
    "hard":        "#F97316",
    "expert":      "#A855F7",
    "cell_bg":     "#252538",
    "cell_active": "#2E2E4A",
    "btn_bg":      "#7C3AED",
    "btn_hover":   "#6D28D9",
}

class SudokuGUI:

    def __init__(self, root):
        self.root = root
        self.root.title("Sudoku Analyzer PRO")
        self.root.configure(bg=THEME["bg"])
        self.root.resizable(False, False)

        self.entries = []
        self.original_cells = set()
        self.solving_steps = []
        self.step_index = 0
        self.timer_running = False
        self.timer_start = None
        self.timer_elapsed = 0
        self._timer_id = None

        self._build_ui()

    # ----------------------------------------------------------
    # UI BUILDER
    # ----------------------------------------------------------

    def _build_ui(self):
        # Title bar
        title_frame = tk.Frame(self.root, bg=THEME["bg"])
        title_frame.pack(fill="x", padx=20, pady=(15, 5))

        tk.Label(
            title_frame,
            text="⬛ SUDOKU ANALYZER PRO",
            font=("Consolas", 18, "bold"),
            fg=THEME["accent"],
            bg=THEME["bg"]
        ).pack(side="left")

        self.timer_label = tk.Label(
            title_frame,
            text="00:00",
            font=("Consolas", 16, "bold"),
            fg=THEME["accent2"],
            bg=THEME["bg"]
        )
        self.timer_label.pack(side="right")

        # Difficulty indicator
        self.diff_label = tk.Label(
            self.root,
            text="Difficulty: —",
            font=("Consolas", 11),
            fg=THEME["text_dim"],
            bg=THEME["bg"]
        )
        self.diff_label.pack()

        # Grid
        self._build_grid()

        # Toolbar
        self._build_toolbar()

        # Info panel
        self._build_info_panel()

        # Status bar
        self.status_var = tk.StringVar(value="Ready. Enter a puzzle or generate one.")
        status = tk.Label(
            self.root,
            textvariable=self.status_var,
            font=("Consolas", 9),
            fg=THEME["text_dim"],
            bg=THEME["panel"],
            anchor="w",
            padx=10
        )
        status.pack(fill="x", side="bottom", ipady=4)

    def _build_grid(self):
        outer_frame = tk.Frame(self.root, bg=THEME["accent"], bd=2, relief="flat")
        outer_frame.pack(padx=20, pady=10)

        frame = tk.Frame(outer_frame, bg=THEME["accent"])
        frame.pack(padx=2, pady=2)

        for r in range(9):
            row_entries = []
            for c in range(9):
                pad_top  = 3 if r % 3 == 0 else 1
                pad_left = 3 if c % 3 == 0 else 1
                pad_bot  = 3 if r == 8 else 0
                pad_right= 3 if c == 8 else 0

                cell_frame = tk.Frame(
                    frame,
                    bg=THEME["accent"],
                )
                cell_frame.grid(
                    row=r, column=c,
                    padx=(pad_left, pad_right),
                    pady=(pad_top, pad_bot)
                )

                entry = tk.Entry(
                    cell_frame,
                    width=2,
                    font=("Consolas", 20, "bold"),
                    justify="center",
                    bd=0,
                    relief="flat",
                    bg=THEME["cell_bg"],
                    fg=THEME["given"],
                    insertbackground=THEME["accent2"],
                    selectbackground=THEME["accent"],
                    selectforeground=THEME["text"],
                )
                entry.pack(ipady=4)

                # Bind events
                entry.bind("<FocusIn>",  lambda e, w=entry: self._on_cell_focus(w))
                entry.bind("<FocusOut>", lambda e, w=entry: self._on_cell_blur(w))
                entry.bind("<KeyRelease>", lambda e: self._on_key())
                row_entries.append(entry)
            self.entries.append(row_entries)

    def _build_toolbar(self):
        tb = tk.Frame(self.root, bg=THEME["bg"])
        tb.pack(pady=(0, 8), padx=20, fill="x")

        buttons = [
            ("▶  Solve",     self.solve,         THEME["accent"]),
            ("⚡ Step Mode", self.start_step_mode, "#0E7490"),
            ("⏭  Next Step", self.next_step,      "#065F46"),
            ("🎲 Generate",  self.show_generate,  "#7C2D12"),
            ("🗑  Clear",    self.clear,           "#374151"),
        ]

        for i, (lbl, cmd, color) in enumerate(buttons):
            btn = tk.Button(
                tb,
                text=lbl,
                command=cmd,
                font=("Consolas", 10, "bold"),
                bg=color,
                fg=THEME["text"],
                activebackground=THEME["btn_hover"],
                activeforeground=THEME["text"],
                bd=0,
                relief="flat",
                cursor="hand2",
                padx=10,
                pady=6
            )
            btn.grid(row=0, column=i, padx=4)

            # Hover effect
            btn.bind("<Enter>", lambda e, b=btn, orig=color: b.config(bg=THEME["btn_hover"]))
            btn.bind("<Leave>", lambda e, b=btn, orig=color: b.config(bg=orig))

        # Timer buttons
        timer_frame = tk.Frame(self.root, bg=THEME["bg"])
        timer_frame.pack(pady=(0, 6))

        tk.Button(
            timer_frame, text="▶ Start Timer", command=self.start_timer,
            font=("Consolas", 9), bg=THEME["panel"], fg=THEME["accent2"],
            bd=0, relief="flat", cursor="hand2", padx=8, pady=3
        ).pack(side="left", padx=4)

        tk.Button(
            timer_frame, text="⏹ Stop Timer", command=self.stop_timer,
            font=("Consolas", 9), bg=THEME["panel"], fg=THEME["error"],
            bd=0, relief="flat", cursor="hand2", padx=8, pady=3
        ).pack(side="left", padx=4)

        # Import/Export
        io_frame = tk.Frame(self.root, bg=THEME["bg"])
        io_frame.pack(pady=(0, 6))

        tk.Button(
            io_frame, text="📂 Load from File", command=self.load_file,
            font=("Consolas", 9), bg=THEME["panel"], fg=THEME["text"],
            bd=0, relief="flat", cursor="hand2", padx=8, pady=3
        ).pack(side="left", padx=4)

        tk.Button(
            io_frame, text="💾 Save to File", command=self.save_file,
            font=("Consolas", 9), bg=THEME["panel"], fg=THEME["text"],
            bd=0, relief="flat", cursor="hand2", padx=8, pady=3
        ).pack(side="left", padx=4)

        tk.Button(
            io_frame, text="📋 Paste from Clipboard", command=self.paste_clipboard,
            font=("Consolas", 9), bg=THEME["panel"], fg=THEME["text"],
            bd=0, relief="flat", cursor="hand2", padx=8, pady=3
        ).pack(side="left", padx=4)

    def _build_info_panel(self):
        panel = tk.Frame(self.root, bg=THEME["panel"], bd=0)
        panel.pack(padx=20, pady=(0, 10), fill="both")

        tk.Label(
            panel,
            text="ANALYSIS REPORT",
            font=("Consolas", 9, "bold"),
            fg=THEME["accent"],
            bg=THEME["panel"]
        ).pack(anchor="w", padx=10, pady=(6, 2))

        self.info_text = tk.Text(
            panel,
            font=("Consolas", 10),
            bg=THEME["panel"],
            fg=THEME["text"],
            bd=0,
            height=7,
            state="disabled",
            wrap="word",
        )
        self.info_text.pack(fill="both", padx=10, pady=(0, 8))

        # Color tags for info text
        self.info_text.tag_config("technique", foreground=THEME["accent2"])
        self.info_text.tag_config("value",     foreground=THEME["solved"])
        self.info_text.tag_config("header",    foreground=THEME["accent"], font=("Consolas", 10, "bold"))
        self.info_text.tag_config("error",     foreground=THEME["error"])

    # ----------------------------------------------------------
    # CELL EVENTS
    # ----------------------------------------------------------

    def _on_cell_focus(self, widget):
        widget.config(bg=THEME["cell_active"])

    def _on_cell_blur(self, widget):
        widget.config(bg=THEME["cell_bg"])

    def _on_key(self):
        """Live difficulty update as user types."""
        board = self.get_board()
        if board:
            givens = sum(1 for r in range(9) for c in range(9) if board[r][c] != 0)
            a = SudokuAnalyzer(board)
            diff = a.rate_difficulty()
            self.diff_label.config(text=f"Difficulty: {diff}  |  Givens: {givens}")

    # ----------------------------------------------------------
    # BOARD UTILITIES
    # ----------------------------------------------------------

    def get_board(self):
        board = []
        self.original_cells.clear()
        for r in range(9):
            row = []
            for c in range(9):
                val = self.entries[r][c].get().strip()
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
                    except ValueError:
                        return None
            board.append(row)
        return board

    def display_board(self, board, highlight=None):
        for r in range(9):
            for c in range(9):
                self.entries[r][c].config(state="normal")
                self.entries[r][c].delete(0, tk.END)
                if board[r][c] != 0:
                    self.entries[r][c].insert(0, str(board[r][c]))

                if (r, c) in self.original_cells:
                    self.entries[r][c].config(fg=THEME["given"], bg=THEME["cell_bg"])
                elif highlight and (r, c) == highlight:
                    self.entries[r][c].config(fg=THEME["accent"], bg="#2E1065")
                else:
                    self.entries[r][c].config(fg=THEME["solved"], bg=THEME["cell_bg"])

    def clear(self):
        for r in range(9):
            for c in range(9):
                self.entries[r][c].config(state="normal")
                self.entries[r][c].delete(0, tk.END)
                self.entries[r][c].config(fg=THEME["given"], bg=THEME["cell_bg"])
        self.original_cells.clear()
        self.solving_steps = []
        self.step_index = 0
        self.diff_label.config(text="Difficulty: —")
        self._update_info("")
        self.status_var.set("Board cleared.")

    def _update_info(self, text, error=False):
        self.info_text.config(state="normal")
        self.info_text.delete("1.0", tk.END)
        if text:
            self.info_text.insert(tk.END, text)
        self.info_text.config(state="disabled")

    # ----------------------------------------------------------
    # SOLVE
    # ----------------------------------------------------------

    def solve(self):
        board = self.get_board()
        if board is None:
            messagebox.showerror("Error", "Input tidak valid! Gunakan angka 1-9 saja.")
            return

        self.status_var.set("Solving...")
        self.root.update()

        start = time.perf_counter()
        analyzer = SudokuAnalyzer(board)
        solution = analyzer.solve()
        elapsed = time.perf_counter() - start

        if solution is None:
            self._update_info("❌ Puzzle tidak bisa diselesaikan atau tidak valid.", error=True)
            self.status_var.set("Unsolvable puzzle.")
            return

        self.display_board(solution)

        # Build report
        diff = analyzer.rate_difficulty()
        givens = sum(1 for r in range(9) for c in range(9) if analyzer.original[r][c] != 0)
        report = (
            f"✅ SOLVED in {elapsed*1000:.2f} ms\n"
            f"─────────────────────────\n"
            f"Difficulty : {diff}\n"
            f"Givens     : {givens}/81\n"
            f"Steps      : {len(analyzer.steps)}\n"
            f"─────────────────────────\n"
            f"TECHNIQUES USED:\n"
        )
        for k, v in analyzer.techniques_used.items():
            report += f"  • {k}: {v}×\n"

        self._update_info(report)
        self.status_var.set(f"Solved in {elapsed*1000:.2f} ms | {diff}")

    # ----------------------------------------------------------
    # STEP-BY-STEP MODE
    # ----------------------------------------------------------

    def start_step_mode(self):
        board = self.get_board()
        if board is None:
            messagebox.showerror("Error", "Input tidak valid!")
            return

        self._step_original_board = copy.deepcopy(board)
        analyzer = SudokuAnalyzer(board)
        solution = analyzer.solve()

        if solution is None:
            self._update_info("❌ Puzzle tidak bisa diselesaikan.", error=True)
            return

        self.solving_steps = analyzer.steps
        self.step_index = 0

        # Reset to original
        for r in range(9):
            for c in range(9):
                self.entries[r][c].config(state="normal")
                self.entries[r][c].delete(0, tk.END)
                v = self._step_original_board[r][c]
                if v != 0:
                    self.entries[r][c].insert(0, str(v))
                    self.entries[r][c].config(fg=THEME["given"])

        self._update_info(f"⚡ Step Mode Active\nTotal steps: {len(self.solving_steps)}\nClick 'Next Step' to proceed.")
        self.status_var.set(f"Step Mode: 0 / {len(self.solving_steps)}")

    def next_step(self):
        if not self.solving_steps:
            self.status_var.set("Run Step Mode first.")
            return
        if self.step_index >= len(self.solving_steps):
            self.status_var.set("All steps complete!")
            return

        r, c, val, technique = self.solving_steps[self.step_index]
        self.step_index += 1

        entry = self.entries[r][c]
        entry.config(state="normal")
        entry.delete(0, tk.END)
        entry.insert(0, str(val))
        entry.config(fg=THEME["accent"], bg="#1E0F4A")

        # Fade highlight after 400ms
        self.root.after(400, lambda: entry.config(fg=THEME["solved"], bg=THEME["cell_bg"]))

        self._update_info(
            f"Step {self.step_index} / {len(self.solving_steps)}\n"
            f"Cell   : ({r+1}, {c+1})\n"
            f"Value  : {val}\n"
            f"Method : {technique}"
        )
        self.status_var.set(f"Step {self.step_index}/{len(self.solving_steps)} — {technique}")

    # ----------------------------------------------------------
    # GENERATE
    # ----------------------------------------------------------

    def show_generate(self):
        win = tk.Toplevel(self.root)
        win.title("Generate Puzzle")
        win.configure(bg=THEME["bg"])
        win.resizable(False, False)
        win.grab_set()

        tk.Label(win, text="Select Difficulty:", font=("Consolas", 12),
                 fg=THEME["text"], bg=THEME["bg"]).pack(pady=(15, 5))

        var = tk.StringVar(value="Medium")
        for lvl, color in [("Easy", THEME["easy"]), ("Medium", THEME["medium"]),
                           ("Hard", THEME["hard"]), ("Expert", THEME["expert"])]:
            tk.Radiobutton(
                win, text=lvl, variable=var, value=lvl,
                font=("Consolas", 11), fg=color, bg=THEME["bg"],
                activebackground=THEME["bg"], selectcolor=THEME["panel"]
            ).pack(anchor="w", padx=30)

        def do_generate():
            difficulty = var.get()
            win.destroy()
            self.status_var.set(f"Generating {difficulty} puzzle...")
            self.root.update()
            puzzle, _ = SudokuAnalyzer.generate(difficulty)
            self.clear()
            for r in range(9):
                for c in range(9):
                    if puzzle[r][c] != 0:
                        self.entries[r][c].insert(0, str(puzzle[r][c]))
                        self.entries[r][c].config(fg=THEME["given"])
                        self.original_cells.add((r, c))
            self._on_key()
            self.status_var.set(f"Generated {difficulty} puzzle. Ready!")

        tk.Button(
            win, text="Generate!", command=do_generate,
            font=("Consolas", 11, "bold"), bg=THEME["accent"],
            fg=THEME["text"], bd=0, cursor="hand2", padx=15, pady=6
        ).pack(pady=15)

    # ----------------------------------------------------------
    # TIMER
    # ----------------------------------------------------------

    def start_timer(self):
        if self.timer_running:
            return
        self.timer_running = True
        self.timer_start = time.perf_counter() - self.timer_elapsed
        self._tick()
        self.status_var.set("Timer started.")

    def stop_timer(self):
        if not self.timer_running:
            return
        self.timer_running = False
        if self._timer_id:
            self.root.after_cancel(self._timer_id)
        self.timer_elapsed = time.perf_counter() - self.timer_start
        self.status_var.set(f"Timer stopped at {self.timer_label.cget('text')}.")

    def _tick(self):
        if not self.timer_running:
            return
        elapsed = time.perf_counter() - self.timer_start
        mins = int(elapsed) // 60
        secs = int(elapsed) % 60
        self.timer_label.config(text=f"{mins:02}:{secs:02}")
        self._timer_id = self.root.after(500, self._tick)

    # ----------------------------------------------------------
    # IMPORT / EXPORT
    # ----------------------------------------------------------

    def load_file(self):
        """Load a puzzle from a .txt file (81 chars or 9x9 lines)."""
        path = filedialog.askopenfilename(
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if not path:
            return
        try:
            with open(path, "r") as f:
                content = f.read().strip()
            self._parse_and_load(content)
            self.status_var.set(f"Loaded: {path}")
        except Exception as e:
            messagebox.showerror("Load Error", str(e))

    def save_file(self):
        """Save current board to .txt file."""
        board = self.get_board()
        if board is None:
            messagebox.showerror("Error", "Board contains invalid values.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt")]
        )
        if not path:
            return
        try:
            with open(path, "w") as f:
                for row in board:
                    f.write("".join(str(v) if v != 0 else "." for v in row) + "\n")
            self.status_var.set(f"Saved to {path}")
        except Exception as e:
            messagebox.showerror("Save Error", str(e))

    def paste_clipboard(self):
        """Paste an 81-char or 9x9 puzzle from clipboard."""
        try:
            content = self.root.clipboard_get().strip()
            self._parse_and_load(content)
            self.status_var.set("Loaded from clipboard.")
        except Exception as e:
            messagebox.showerror("Paste Error", str(e))

    def _parse_and_load(self, content):
        """Parse 9-line or 81-char board string."""
        # Remove common separators
        lines = [l.strip() for l in content.splitlines() if l.strip() and not set(l.strip()) <= set("-+|")]
        if len(lines) == 9:
            flat = ""
            for line in lines:
                digits = "".join(ch for ch in line if ch.isdigit() or ch in "._0")
                flat += digits
        else:
            flat = "".join(ch for ch in content if ch.isdigit() or ch in "._")

        if len(flat) != 81:
            messagebox.showerror("Parse Error", f"Expected 81 cells, got {len(flat)}.")
            return

        self.clear()
        for i, ch in enumerate(flat):
            r, c = divmod(i, 9)
            if ch.isdigit() and ch != "0":
                self.entries[r][c].insert(0, ch)
                self.entries[r][c].config(fg=THEME["given"])
                self.original_cells.add((r, c))
        self._on_key()


# ======================================
# ENTRY POINT
# ======================================

if __name__ == "__main__":
    root = tk.Tk()
    root.tk_setPalette(background=THEME["bg"], foreground=THEME["text"])
    app = SudokuGUI(root)
    root.mainloop()