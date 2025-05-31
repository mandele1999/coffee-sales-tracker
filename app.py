import altair as alt
import pandas as pd
import streamlit as st
from tracker import process_sale, get_daily_summary, load_recipes, get_sales_summary
from export_utils import export_df_to_csv, export_df_to_excel


st.set_page_config(page_title="Coffee Sales Tracker", layout="centered")

st.title("☕ Coffee Vendor Sales Tracker")

# Sidebar navigation
page = st.sidebar.radio("Navigate to", ["Sales Entry", "Daily Summary", "Historical Summary"])

recipes = load_recipes()

if page == "Sales Entry":
    st.header("🛒 Multi-Drink Sale Entry")

    # Initialize session state
    if "cart" not in st.session_state:
        st.session_state.cart = []
    if "selected_drink" not in st.session_state:
        st.session_state.selected_drink = "-- Select a drink --"
    if "selected_qty" not in st.session_state:
        st.session_state.selected_qty = 1
    if "reset_fields" not in st.session_state:
        st.session_state.reset_fields = False

    drink_options = ["-- Select a drink --"] + list(recipes.index)

    # Handle field reset BEFORE widget instantiation
    if st.session_state.reset_fields:
        st.session_state.selected_drink = "-- Select a drink --"
        st.session_state.selected_qty = 1
        st.session_state.reset_fields = False

    with st.form("sale_form"):
        drink = st.selectbox(
            "Select Drink",
            options=drink_options,
            index=drink_options.index(st.session_state.selected_drink),
            key="selected_drink"
        )

        qty = st.number_input(
            "Quantity Sold",
            min_value=1,
            step=1,
            key="selected_qty"
        )

        add_clicked = st.form_submit_button("Add to Cart")

        if add_clicked:
            if drink == "-- Select a drink --":
                st.warning("Please select a valid drink.")
            else:
                st.session_state.cart.append({"Drink": drink, "Quantity": qty})
                st.success(f"Added {qty} x {drink} to cart.")

                # Safe field reset via flag
                st.session_state.reset_fields = True
                st.rerun()

    # Display cart
    if st.session_state.cart:
        st.markdown("### 🧾 Order Summary")
        cart_df = pd.DataFrame(st.session_state.cart)
        st.dataframe(cart_df, use_container_width=True)

        # 🔁 Modified submit logic to store confirmation
        if st.button("✅ Submit Sale"):
            try:
                total_rev, total_cost, total_profit = 0, 0, 0
                for item in st.session_state.cart:
                    d = item["Drink"]
                    q = item["Quantity"]
                    rev, cost, profit, _ = process_sale(d, q)
                    total_rev += rev
                    total_cost += cost
                    total_profit += profit

                st.session_state.cart = []
                st.session_state.sale_submitted = {
                    "rev": total_rev,
                    "cost": total_cost,
                    "profit": total_profit
                }
                st.rerun()

            except ValueError as e:
                st.error(f"Error: {e}")

        if st.button("🗑️ Clear Cart"):
            st.session_state.cart = []
            st.rerun()
    else:
        st.info("Cart is empty. Add drinks to begin.")

    # ✅ Show confirmation message if set
    if "sale_submitted" in st.session_state:
        sale = st.session_state.sale_submitted
        st.success(
            f"📦 Sale recorded! Revenue: ${sale['rev']:.2f}, Cost: ${sale['cost']:.2f}, Profit: ${sale['profit']:.2f}"
        )
        del st.session_state.sale_submitted

elif page == "Daily Summary":
    st.header("📊 Daily Summary")

    summary = get_daily_summary()

    if summary:
        drink_counts, total_revenue, total_cost, total_profit = summary

        # Metrics in a single row
        col1, col2, col3 = st.columns(3)
        col1.metric("Revenue", f"${total_revenue:.2f}")
        col2.metric("Cost", f"${total_cost:.2f}")
        col3.metric("Profit", f"${total_profit:.2f}")

        st.markdown("---")

        # Sales breakdown and bar chart side-by-side
        col1, col2 = st.columns([1, 2])

        with col1:
            st.write("### Sales Breakdown")
            for d, q in drink_counts.items():
                st.write(f"- {d}: {q} sold")

        with col2:
            drink_counts_df = pd.DataFrame(list(drink_counts.items()), columns=["Drink", "Quantity"])
            st.write("### 📈 Drink Sales Chart (Today)")
            bar_chart = (
                alt.Chart(drink_counts_df)
                .mark_bar()
                .encode(
                    x=alt.X("Drink", sort="-y"),
                    y="Quantity",
                    color=alt.Color("Drink", legend=None),
                    tooltip=["Drink", "Quantity"]
                )
                .properties(height=250)
            )
            st.altair_chart(bar_chart, use_container_width=True)

        # Revenue pie chart below the above two columns but with some width control
        drink_counts_df["Price"] = drink_counts_df["Drink"].map(recipes["Price"])
        drink_counts_df["Revenue"] = drink_counts_df["Quantity"] * drink_counts_df["Price"]

        st.markdown("### 💸 Revenue Distribution (Today)")
        pie_chart = (
            alt.Chart(drink_counts_df)
            .mark_arc(innerRadius=50)
            .encode(
                theta="Revenue",
                color="Drink",
                tooltip=["Drink", "Revenue"]
            )
            .properties(width=400, height=300)
        )
        st.altair_chart(pie_chart)

    else:
        st.info("No sales recorded today.")

    st.markdown("---")

    # Revenue vs Profit over time line chart
    try:
        sales_df = pd.read_csv("data/sales_log.csv")
        sales_df["Date"] = pd.to_datetime(sales_df["Date"])

        trend_df = (
            sales_df.groupby("Date")[["Revenue", "Profit"]]
            .sum()
            .reset_index()
            .sort_values("Date")
        )

        st.markdown("### 📈 Revenue vs Profit Over Time")

        melted_df = trend_df.melt(id_vars=["Date"], value_vars=["Revenue", "Profit"],
                                  var_name="Metric", value_name="Value")

        trend_chart = (
            alt.Chart(melted_df)
            .mark_line(point=True)
            .encode(
                x=alt.X("Date:T", title="Date"),
                y=alt.Y("Value:Q", title="Amount ($)"),
                color=alt.Color("Metric:N", title="Metric"),
                tooltip=["Date:T", "Metric:N", "Value:Q"]
            )
            .properties(width=700, height=400)
        )
        st.altair_chart(trend_chart)

    except Exception as e:
        st.warning(f"Could not load trend chart: {e}")


elif page == "Historical Summary":
    
    st.header("📅 Historical Sales Summary")

    # Load recipes from drink list
    recipes = load_recipes()
    drink_options = ['All Drinks'] + list(recipes.index)

    # Filters in one row
    col1, col2 = st.columns([3, 3])
    with col1:
        selected_date = st.date_input("Select a date", value=pd.Timestamp.today())

    with col2:
        selected_drink = st.selectbox("Filter by Drink", options=drink_options)

    # Fetch and Filter data reactively
    summary, breakdown = get_sales_summary(selected_date.strftime("%Y-%m-%d"))

    if summary:

        # Convert breakdown (list of dicts) to DataFrame for filtering and export
        breakdown_df = pd.DataFrame(breakdown)

        # Filter breakdown by drink if not 'All Drinks'
        if selected_drink != 'All Drinks':
            breakdown_df = breakdown_df[breakdown_df['Drink'] == selected_drink]

        st.subheader(f"📅 Summary for {summary['Date']}")
        col1, col2, col3 = st.columns(3)
        col1.metric("💰 Total Revenue", f"${summary['Revenue']:.2f}")
        col2.metric("🧾 Total Cost", f"${summary['Cost']:.2f}")
        col3.metric("📈 Total Profit", f"${summary['Profit']:.2f}")

        st.markdown("### 🧃Drink Breakdown")
        if not breakdown_df.empty:
            st.dataframe(breakdown_df, use_container_width=True)

        # Export buttons
        col_export1, col_export2 = st.columns(2)
        with col_export1:
            if st.button("Export Breakdown CSv"):
                export_df_to_csv(breakdown_df, f"sales_breakdown_{selected_date}.csv")
                st.success("CSV Exported!")

        with col_export2:
            if st.button("Export Breakdown Excel"):
                export_df_to_excel(breakdown_df, f"sales_breakdown_{selected_date}.xlsx")
                st.success("Excel Exported!")
          
    else:
        st.info("No sales found for this drink on the selected date.")

else:
    st.warning("No sales found for that date.")