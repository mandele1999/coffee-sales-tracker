# Core logic for tracking the state of the application (Backend logic)
# This module handles inventory management, recipe processing, and sales logging.
import pandas as pd
from datetime import date

# === File Paths ===
INVENTORY_PATH = "data/inventory.csv"
RECIPES_PATH = "data/recipes.csv"
SALES_LOG_PATH = "data/sales_log.csv"

# === Loaders ===
def load_inventory():
    return pd.read_csv(INVENTORY_PATH, index_col="Ingredient")

def load_recipes():
    return pd.read_csv(RECIPES_PATH, index_col="Drink")

# === Savers ===
def save_inventory(df):
    df.to_csv(INVENTORY_PATH)

def log_sale(drink, quantity, revenue, cost, profit):
    try:
        log_df = pd.read_csv(SALES_LOG_PATH)
    except FileNotFoundError:
        log_df = pd.DataFrame(columns=["Date", "Drink", "Quantity", "Revenue", "Cost", "Profit"])

    today = date.today().isoformat()
    log_df.loc[len(log_df)] = [today, drink, quantity, revenue, cost, profit]
    log_df.to_csv(SALES_LOG_PATH, index=False)

# === Core Logic ===
def process_sale(drink, quantity):
    """
    Process a drink sale: update inventory, log sale, and return financials.
    """
    inventory = load_inventory()
    recipes = load_recipes()

    if drink not in recipes.index:
        raise ValueError(f"No recipe found for {drink}")

    recipe = recipes.loc[drink]
    cost = 0

    for ingredient in inventory.index:
        used = recipe.get(ingredient, 0) * quantity
        if used > inventory.at[ingredient, "Stock"]:
            raise ValueError(f"Not enough {ingredient} in stock!")
        inventory.at[ingredient, "Stock"] -= used
        cost += used * inventory.at[ingredient, "CostPerUnit"]

    revenue = recipe["Price"] * quantity
    profit = revenue - cost

    save_inventory(inventory)
    log_sale(drink, quantity, revenue, cost, profit)

    return revenue, cost, profit, inventory

def get_daily_summary():
    """
    Return today's summary: drink counts, total revenue, cost, profit.
    """
    df = pd.read_csv(SALES_LOG_PATH)
    today = date.today().isoformat()
    today_df = df[df["Date"] == today]

    if today_df.empty:
        return None

    drink_summary = today_df.groupby("Drink")["Quantity"].sum().to_dict()
    total_revenue = today_df["Revenue"].sum()
    total_cost = today_df["Cost"].sum()
    total_profit = today_df["Profit"].sum()

    return drink_summary, total_revenue, total_cost, total_profit

def get_sales_summary(date_str):
    """
    Return summary and breakdown of sales for a specific date.
    """
    try:
        df = pd.read_csv(SALES_LOG_PATH)
        df = df[df["Date"] == date_str]

        if df.empty:
            return None, pd.DataFrame()  # return empty DataFrame, NOT empty list

        total_revenue = df["Revenue"].sum()
        total_cost = df["Cost"].sum()
        total_profit = df["Profit"].sum()

        drink_summary = (
            df.groupby("Drink")[["Quantity", "Revenue", "Cost", "Profit"]]
            .sum()
            .reset_index()
        )

        summary = {
            "Date": date_str,
            "Revenue": total_revenue,
            "Cost": total_cost,
            "Profit": total_profit,
        }

        return summary, drink_summary  # Return DataFrame directly

    except Exception as e:
        return None, pd.DataFrame()  # Return empty DataFrame on error