# Coffee Vendor Sales Tracker

A simple, lightweight Streamlit app for coffee vendors to **record daily sales, track revenue, costs, and profit**, and review sales summaries — all with zero fuss.

---

## Features

* **Multi-drink sale entry:** Add multiple drinks with quantities to a cart before submitting.
* **Live cart management:** Review, submit, or clear your sales cart.
* **Daily sales summary:** View real-time revenue, cost, profit, and sales breakdowns with charts.
* **Historical sales summary:** Filter sales by date and drink with export options (CSV, Excel).
* **Simple CSV-based storage:** Keeps data easy to manage and portable.
* **Minimal dependencies:** Built with Streamlit and Pandas.

---

## Getting Started

### Prerequisites

* Python 3.8+
* Recommended: create and activate a virtual environment

### Installation

```bash
git clone https://github.com/yourusername/coffee-sales-tracker.git
cd coffee-sales-tracker
pip install -r requirements.txt
```

### Running the App

```bash
streamlit run app.py
```

Open your browser at the URL provided (usually [http://localhost:8501](http://localhost:8501)).

---

## Usage

1. Navigate to **Sales Entry** to add drinks sold.
2. Add multiple items to the cart and submit sales when ready.
3. Use **Daily Summary** to monitor today’s sales and revenue trends.
4. Explore **Historical Summary** for past sales data with export options.

---

## Project Structure

* `app.py` — Main Streamlit application.
* `tracker.py` — Core sales processing and data utilities.
* `export_utils.py` — Helpers for exporting data.
* `data/` — Folder containing sales log CSV files.
* `recipes.csv` — Drink recipes and prices.

---

## Notes

* This is a vendor-focused MVP designed for **single-user, local use**.
* Data is stored in CSV files for simplicity; no database required.
* No authentication or multi-user support currently implemented.
* Designed for easy extension or integration.

---

## Contributing

Contributions welcome. Open issues or submit pull requests with improvements.

---

## License

[MIT License](MIT License)
