"""
Stock Portfolio Performance Tracker
-----------------------------------
- User enters ticker symbols, buy prices and share quantities
- Tickers are validated against the S&P 500 dataset (sp500.csv), which also
  supplies the company name and sector for each holding
- Current price: taken from a price column in the CSV if one exists, else from
  a small built-in sample price list, else entered manually by the user
- Calculates invested capital, current value and % gain/loss per holding
- Writes the results to portfolio_summary.csv using the csv module
"""

import csv
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_FILE = os.path.join(BASE_DIR, "sp500.csv")
SUMMARY_FILE = os.path.join(BASE_DIR, "portfolio_summary.csv")

# Sample prices (illustrative only, not live market data)
SAMPLE_PRICES = {
    "AAPL": 190.50, "MSFT": 410.20, "GOOGL": 140.75, "AMZN": 175.30,
    "TSLA": 245.60, "NVDA": 880.10, "META": 485.40, "JPM": 195.25,
    "NFLX": 610.00, "INTC": 31.20, "AMD": 165.80, "TXN": 170.40,
}

TICKER_COLUMNS = ("symbol", "ticker")
NAME_COLUMNS = ("security", "name", "company")
SECTOR_COLUMNS = ("gics sector", "sector")
PRICE_COLUMNS = ("price", "current price", "current_price", "close", "last", "last price")


def find_column(columns, options):
    """Return the real column name matching any option (case-insensitive)."""
    return next((columns[o] for o in options if o in columns), None)


def load_dataset(path=DATASET_FILE):
    """Read the S&P 500 CSV. Returns {ticker: {name, sector, price}}."""
    companies = {}
    if not os.path.exists(path):
        return companies
    try:
        with open(path, "r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            if not reader.fieldnames:
                return companies
            cols = {n.strip().lower(): n for n in reader.fieldnames}
            t_col = find_column(cols, TICKER_COLUMNS)
            n_col = find_column(cols, NAME_COLUMNS)
            s_col = find_column(cols, SECTOR_COLUMNS)
            p_col = find_column(cols, PRICE_COLUMNS)
            if not t_col:
                return companies
            for row in reader:
                ticker = (row.get(t_col) or "").strip().upper()
                if not ticker:
                    continue
                price = None
                if p_col:
                    try:
                        price = float(row[p_col])
                    except (ValueError, TypeError):
                        price = None
                companies[ticker] = {
                    "name": (row.get(n_col) or "").strip() if n_col else "",
                    "sector": (row.get(s_col) or "").strip() if s_col else "",
                    "price": price,
                }
    except OSError:
        pass
    return companies


def read_positive_float(prompt):
    while True:
        try:
            value = float(input(prompt).strip())
            if value > 0:
                return value
            print("  Please enter a number greater than 0.")
        except ValueError:
            print("  Invalid number. Try again.")


def read_positive_int(prompt):
    while True:
        try:
            value = int(input(prompt).strip())
            if value > 0:
                return value
            print("  Please enter a whole number greater than 0.")
        except ValueError:
            print("  Invalid number. Try again.")


def add_position(portfolio, ticker, buy_price, shares):
    """Add a holding; if the ticker already exists, average the buy price."""
    if ticker in portfolio:
        old = portfolio[ticker]
        total = old["shares"] + shares
        avg = (old["buy_price"] * old["shares"] + buy_price * shares) / total
        portfolio[ticker] = {"buy_price": avg, "shares": total}
    else:
        portfolio[ticker] = {"buy_price": buy_price, "shares": shares}


def collect_portfolio(companies):
    portfolio = {}
    print("Enter your stock holdings. Type 'done' as the ticker to finish.\n")
    while True:
        ticker = input("Ticker symbol (or 'done'): ").strip().upper()
        if ticker == "DONE":
            if portfolio:
                return portfolio
            print("  Add at least one stock first.")
            continue
        if not ticker.replace(".", "").isalpha():
            print("  Ticker should contain letters only (e.g. AAPL).")
            continue
        if companies and ticker not in companies:
            print(f"  Note: {ticker} is not in the S&P 500 dataset.")
        elif ticker in companies and companies[ticker]["name"]:
            print(f"  {companies[ticker]['name']}")
        buy_price = read_positive_float("  Buy price per share: ")
        shares = read_positive_int("  Number of shares: ")
        add_position(portfolio, ticker, buy_price, shares)
        print(f"  Added {shares} x {ticker} @ {buy_price:.2f}\n")


def get_current_price(ticker, companies):
    info = companies.get(ticker)
    if info and info["price"] is not None:
        return info["price"]
    if ticker in SAMPLE_PRICES:
        return SAMPLE_PRICES[ticker]
    print(f"  No stored price for {ticker}.")
    return read_positive_float(f"  Enter current price for {ticker}: ")


def build_rows(portfolio, companies):
    rows = []
    for ticker, pos in portfolio.items():
        current = get_current_price(ticker, companies)
        invested = pos["buy_price"] * pos["shares"]
        value = current * pos["shares"]
        gain = value - invested
        info = companies.get(ticker, {})
        rows.append({
            "Ticker": ticker,
            "Company": info.get("name", ""),
            "Sector": info.get("sector", ""),
            "Shares": pos["shares"],
            "Buy Price": round(pos["buy_price"], 2),
            "Current Price": round(current, 2),
            "Invested": round(invested, 2),
            "Current Value": round(value, 2),
            "Gain/Loss": round(gain, 2),
            "Gain/Loss %": round(gain / invested * 100, 2),
        })
    return rows


def print_report(rows):
    header = (f"{'Ticker':<8}{'Shares':>7}{'Buy':>10}{'Now':>10}"
              f"{'Invested':>12}{'Value':>12}{'Gain/Loss':>12}{'%':>9}")
    print("\n" + "=" * len(header))
    print(header)
    print("-" * len(header))
    for r in rows:
        print(f"{r['Ticker']:<8}{r['Shares']:>7}{r['Buy Price']:>10.2f}{r['Current Price']:>10.2f}"
              f"{r['Invested']:>12.2f}{r['Current Value']:>12.2f}"
              f"{r['Gain/Loss']:>12.2f}{r['Gain/Loss %']:>8.2f}%")
    invested = sum(r["Invested"] for r in rows)
    value = sum(r["Current Value"] for r in rows)
    gain = value - invested
    pct = gain / invested * 100
    print("-" * len(header))
    print(f"{'TOTAL':<8}{'':>7}{'':>10}{'':>10}{invested:>12.2f}{value:>12.2f}{gain:>12.2f}{pct:>8.2f}%")
    print("=" * len(header))
    status = "PROFIT" if gain >= 0 else "LOSS"
    print(f"Overall portfolio result: {status} of {abs(gain):.2f} ({pct:+.2f}%)")
    return invested, value, gain, pct


def save_summary(rows, totals, path=SUMMARY_FILE):
    invested, value, gain, pct = totals
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
        writer.writerow({
            "Ticker": "TOTAL", "Invested": round(invested, 2),
            "Current Value": round(value, 2), "Gain/Loss": round(gain, 2),
            "Gain/Loss %": round(pct, 2),
        })
    print(f"\nSummary saved to {os.path.basename(path)} "
          f"({datetime.now().strftime('%Y-%m-%d %H:%M')})")


def main():
    print("=== STOCK PORTFOLIO PERFORMANCE TRACKER ===\n")
    companies = load_dataset()
    if companies:
        print(f"Loaded {len(companies)} S&P 500 companies from {os.path.basename(DATASET_FILE)}\n")
    else:
        print("sp500.csv not found; skipping ticker validation.\n")

    portfolio = collect_portfolio(companies)
    rows = build_rows(portfolio, companies)
    totals = print_report(rows)
    save_summary(rows, totals)


if __name__ == "__main__":
    main()
