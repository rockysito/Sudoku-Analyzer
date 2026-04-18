<div align="center">

# ⬛ Sudoku Analyzer PRO

**A powerful Sudoku solver and analyzer built with Python & Tkinter**

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![Tkinter](https://img.shields.io/badge/GUI-Tkinter-green?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-purple?style=for-the-badge)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-orange?style=for-the-badge)

> Analyze, solve, generate, and learn Sudoku step-by-step — with technique identification and difficulty rating.

</div>

---

## ✨ Features

| Feature | Description |
|---|---|
| 🧠 **Multi-Technique Solver** | Naked Single, Hidden Single, Pointing Pairs, Backtracking (MRV) |
| 📊 **Difficulty Rater** | Auto-rates puzzle as Easy / Medium / Hard / Expert |
| ⚡ **Step-by-Step Mode** | Watch the solver work cell by cell with highlight animations |
| 🎲 **Puzzle Generator** | Generate random valid puzzles by difficulty level |
| ⏱️ **Built-in Timer** | Track how long you take to solve manually |
| 📂 **Import / Export** | Load/save puzzles from `.txt` files or paste from clipboard |
| 🌙 **Dark Theme UI** | Premium dark interface with smooth hover effects |
| ✅ **Puzzle Validator** | Detects invalid or unsolvable puzzles before solving |
| 📋 **Analysis Report** | Shows techniques used, timing, givens count |

---

## 📸 Preview

> _Screenshot will appear here after first run_

```
┌───────┬───────┬───────┐
│ 5 3 . │ . 7 . │ . . . │
│ 6 . . │ 1 9 5 │ . . . │
│ . 9 8 │ . . . │ . 6 . │
├───────┼───────┼───────┤
│ 8 . . │ . 6 . │ . . 3 │
│ 4 . . │ 8 . 3 │ . . 1 │
│ 7 . . │ . 2 . │ . . 6 │
├───────┼───────┼───────┤
│ . 6 . │ . . . │ 2 8 . │
│ . . . │ 4 1 9 │ . . 5 │
│ . . . │ . 8 . │ . 7 9 │
└───────┴───────┴───────┘
```

---

## 🚀 Getting Started

### Prerequisites

- Python **3.8 or higher**
- `tkinter` (bundled with Python — no extra install needed)

> **Windows**: Download Python from [python.org](https://www.python.org/downloads/) and make sure to check **"Add Python to PATH"** during installation.

---

### 📥 Installation

#### 1. Clone the repository

```bash
git clone https://github.com/rockysito/Sudoku-Analyzer.git
cd Sudoku-Analyzer
```

#### 2. (Optional) Create a virtual environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

#### 3. Install dependencies

```bash
pip install -r requirements.txt
```

> This project uses only the Python standard library, so no external packages are required.

---

### ▶️ Running the App

```bash
python sudoku_analyzer.py
```

Or on some systems:

```bash
python3 sudoku_analyzer.py
```

The GUI window will open immediately.

---

## 🎮 How to Use

### Manual Input

1. Click on any cell in the 9×9 grid
2. Type a digit (1–9) for each given clue
3. Leave cells empty for unknown squares
4. Click **▶ Solve** to solve the puzzle

---

### Step-by-Step Mode

Learn *how* the solver thinks:

1. Enter a puzzle manually or generate one
2. Click **⚡ Step Mode** — the board resets to show only the givens
3. Click **⏭ Next Step** repeatedly to watch each cell being filled
4. The **Analysis Report** shows which technique was used at each step

---

### Generate a Puzzle

1. Click **🎲 Generate**
2. Select difficulty: `Easy`, `Medium`, `Hard`, or `Expert`
3. Click **Generate!** — a random valid puzzle appears instantly

---

### Timer (Manual Solving)

1. Enter or generate a puzzle
2. Click **▶ Start Timer** to begin counting
3. Solve it yourself by typing values
4. Click **⏹ Stop Timer** when done

---

### Import a Puzzle from File

Supported file formats:

**Format A — 9 lines of 9 digits (`.` or `0` for unknowns):**
```
530070000
600195000
098000060
800060003
400803001
700020006
060000280
000419005
000080079
```

**Format B — 81 characters on one line:**
```
530070000600195000098000060800060003400803001700020006060000280000419005000080079
```

**Steps:**
1. Click **📂 Load from File**
2. Browse to your `.txt` file and open it
3. The puzzle loads automatically

---

### Paste from Clipboard

1. Copy an 81-character or 9-line puzzle string
2. Click **📋 Paste from Clipboard**
3. The grid fills in automatically

---

### Save a Puzzle

1. Click **💾 Save to File**
2. Choose a filename and location
3. The puzzle is saved as a 9-line `.txt` file

---

## 🧠 Solver Techniques Explained

| Technique | Description | Difficulty |
|---|---|---|
| **Naked Single** | A cell has only one valid candidate | Easy |
| **Hidden Single** | A candidate exists in only one cell of a row/column/box | Easy–Medium |
| **Pointing Pairs** | A candidate in a box is restricted to one row/column; eliminate it elsewhere | Medium |
| **Backtracking** | Brute-force with MRV (Minimum Remaining Values) heuristic | Hard/Expert |

The solver applies techniques in order of complexity and only falls back to backtracking when logic fails.

---

## 📁 Project Structure

```
Sudoku-Analyzer/
│
├── sudoku_analyzer.py     ← Main application (solver + GUI)
├── requirements.txt       ← Dependency list
├── README.md              ← This documentation
│
└── samples/               ← Example puzzle files
    ├── easy_puzzle.txt
    └── hard_puzzle.txt
```

---

## 🔧 Running Sample Puzzles

```bash
# After launching the app:
# 1. Click "📂 Load from File"
# 2. Navigate to the samples/ folder
# 3. Open easy_puzzle.txt or hard_puzzle.txt
```

Or paste this directly into the app (Easy puzzle):
```
530070000600195000098000060800060003400803001700020006060000280000419005000080079
```

---

## 🧪 Testing the Solver (Command Line)

You can run the solver without the GUI for quick testing:

```python
from sudoku_analyzer import SudokuAnalyzer

board = [
    [5,3,0,0,7,0,0,0,0],
    [6,0,0,1,9,5,0,0,0],
    [0,9,8,0,0,0,0,6,0],
    [8,0,0,0,6,0,0,0,3],
    [4,0,0,8,0,3,0,0,1],
    [7,0,0,0,2,0,0,0,6],
    [0,6,0,0,0,0,2,8,0],
    [0,0,0,4,1,9,0,0,5],
    [0,0,0,0,8,0,0,7,9],
]

analyzer = SudokuAnalyzer(board)
solution = analyzer.solve()

for row in solution:
    print(row)

print("\nTechniques used:")
for k, v in analyzer.techniques_used.items():
    print(f"  {k}: {v}")

print(f"\nDifficulty: {analyzer.rate_difficulty()}")
```

---

## ❓ FAQ

**Q: "Puzzle tidak bisa diselesaikan" appears even though my puzzle looks correct.**  
A: Check for duplicate numbers in the same row, column, or 3×3 box. The validator will catch conflicts.

**Q: The app is slow on Expert puzzles.**  
A: Expert puzzles (17–19 givens) require heavy backtracking. Generation may take 5–30 seconds — this is normal.

**Q: Can I add my own puzzles?**  
A: Yes! Save any 9×9 puzzle as `.txt` (dots for empty cells) and use **📂 Load from File**.

---

## 🤝 Contributing

Contributions are welcome! Here's how:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-technique`
3. Commit your changes: `git commit -m "Add: X-Wing elimination technique"`
4. Push to the branch: `git push origin feature/new-technique`
5. Open a Pull Request

### Ideas for contribution:
- [ ] Add X-Wing technique
- [ ] Add Swordfish technique
- [ ] CLI mode (`python sudoku_analyzer.py --solve puzzle.txt`)
- [ ] Export as image/PDF
- [ ] Web interface (Flask / Streamlit)
- [ ] Candidate preview tooltips on hover

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## 👤 Author

Made with ❤️ by **[Godless1405]**

[![GitHub](https://img.shields.io/badge/GitHub-rockysito-181717?style=flat&logo=github)](https://github.com/rockysito)

---

<div align="center">

**⭐ Star this repo if you found it useful!**

</div>
