# Datheon Python Programming Internship

Python projects completed as part of the Datheon Python Programming Internship.

## Tasks Completed

| Task | Project | Folder |
|------|---------|--------|
| 1 | Hangman Word Guessing Game (Console) | `Task1_Hangman/` |
| 2 | Stock Portfolio Performance Tracker | `Task2_Portfolio/` |
| 3 | Automated File Organizer & Cleanup Utility | `Task3_Organizer/` |

## Task 1: Hangman Word Guessing Game

A terminal-based Hangman game.

**Features**
- Random secret word selection (from `words.txt` if present, otherwise a built-in list)
- Masked word display (e.g. `_ A _ H E O N`)
- ASCII gallows art that updates with each wrong guess
- 6 attempts; repeated guesses do not cost an attempt
- Victory and defeat screens, with a play-again option

**Run**
```
cd Task1_Hangman
python hangman.py
```

## Task 2: Stock Portfolio Performance Tracker

A console utility to track an investment portfolio.

**Features**
- Enter ticker symbols, buy prices and share quantities
- Tickers are validated against the S&P 500 dataset (`sp500.csv`), which also provides company name and sector
- Calculates invested capital, current value and percentage gain/loss per holding, plus portfolio totals
- Saves results to `portfolio_summary.csv` using Python's `csv` module

**Note:** The dataset has no price column, so current prices come from a small built-in sample list (illustrative values, not live market data). For other tickers, the user enters the current price.

**Run**
```
cd Task2_Portfolio
python portfolio.py
```

## Task 3: Automated File Organizer & Cleanup Utility

A script that sorts a cluttered folder (e.g. Downloads) into category subfolders.

**Features**
- Checks each file's extension and moves it into `Documents`, `Images`, `Videos`, `Archives` or `Code` using `os.scandir()` and `shutil.move()`
- Previews the changes (dry run) and asks for confirmation before moving anything
- Handles naming collisions by renaming (e.g. `report_1.pdf`) and handles permission errors
- Leaves unknown file types and existing subfolders untouched
- Logs every action to `organizer.log` and prints an execution summary

**Run**
```
cd Task3_Organizer
python organizer.py
```

## Requirements

- Python 3 (standard library only, no extra packages needed)

## Author

Swathi R  
GitHub: https://github.com/swathi010907

## License

This project is licensed under the MIT License.
