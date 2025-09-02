import streamlit as st
import pandas as pd
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime, time
from bson.objectid import ObjectId

# --- Page Configuration ---
st.set_page_config(
    page_title="OanTrack Expense Dashboard",
    page_icon="💸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Database Connection ---
@st.cache_resource
def get_database_connection():
    """Connects to MongoDB and returns the database collection."""
    try:
        uri = st.secrets["MONGO_URI"]
    except KeyError:
        st.error("MongoDB URI not found in `.streamlit/secrets.toml`. Please add it to deploy to Streamlit Cloud.")
        st.stop()

    try:
        client = MongoClient(uri, server_api=ServerApi('1'))
        db = client["oantracker"]
        collection = db["expense"]
        # Ping the database to check the connection
        client.admin.command('ping')
        st.sidebar.success("✅ Database connection successful!")
        return collection

    except Exception as e:
        st.error("Failed to connect to MongoDB. Please check your URI in `.streamlit/secrets.toml`")
        st.exception(e)
        st.stop()

# Get the database collection
collection = get_database_connection()

# --- Data Loading and Caching ---
# We use st.cache_data to avoid reloading data every time the script reruns
@st.cache_data(ttl=60)
def load_data(collection):
    """Loads all data from the MongoDB collection into a Pandas DataFrame."""
    try:
        raw_data = list(collection.find())
        if not raw_data:
            return pd.DataFrame()
        data = pd.DataFrame(raw_data)
        
        # Ensure essential columns exist and are of the correct type
        data["amount"] = data["amount"].astype(float)
        if "category" not in data.columns:
            data["category"] = "Uncategorized"
        
        # Convert 'date' to datetime and clean invalid entries
        if "date" in data.columns:
            data["date"] = pd.to_datetime(data["date"], errors="coerce")
            data = data[data["date"].notna()]
        else:
            st.warning("No 'date' field found in your data.")
            data["date"] = pd.NaT

        return data
    except Exception as e:
        st.error("An error occurred while loading data.")
        st.exception(e)
        return pd.DataFrame()

# Load the data once at the start
with st.spinner("Loading data..."):
    df = load_data(collection)

# --- Main Application Logic ---
def show_add_expense_form():
    """Displays the form for adding a new expense."""
    st.subheader("➕ Add New Expense")
    with st.form("add_receipt"):
        merchant = st.text_input("Merchant", placeholder="e.g., Tim Hortons")
        category = st.selectbox("Category", [
            "Groceries", "Food & Beverage", "Transport", "Utilities", "Rent", 
            "Subscriptions", "Shopping", "Parking", "App Purchases", "Other"
        ])
        amount = st.number_input("Amount", min_value=0.0, format="%.2f")
        date = st.date_input("Date")
        payment_method = st.selectbox("Payment Method", ["Credit Card", "Debit", "Cash", "Other"])
        notes = st.text_area("Notes", placeholder="e.g., Coffee with Sarah")
        submitted = st.form_submit_button("Add Expense")

        if submitted:
            if not merchant or amount <= 0:
                st.error("Please fill in a merchant name and a valid amount.")
                return

            new_receipt = {
                "user_id": "bentley001",  # Hardcoded for a single user, but could be dynamic
                "date": datetime.combine(date, time()),
                "merchant": merchant,
                "category": category,
                "amount": amount,
                "currency": "CAD",
                "payment_method": payment_method,
                "items": [],
                "receipt_image": "",
                "notes": notes,
            }
            collection.insert_one(new_receipt)
            # Clear the cache and rerun the app to show the new data
            st.cache_data.clear()
            st.success("Expense added successfully!")
            st.rerun()

def show_dashboard(filtered_df):
    """Displays the main dashboard with metrics and charts."""
    st.title("OanTrack Expense Dashboard 💸")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_spent = filtered_df["amount"].sum() if not filtered_df.empty else 0
        st.metric("Total Spent", f"${total_spent:,.2f}")
    
    with col2:
        num_transactions = len(filtered_df)
        st.metric("Transactions", num_transactions)
        
    with col3:
        if not filtered_df.empty:
            average_spent = total_spent / num_transactions if num_transactions > 0 else 0
            st.metric("Average per Transaction", f"${average_spent:,.2f}")
        else:
            st.metric("Average per Transaction", "$0.00")

    st.markdown("---")
    
    st.subheader("Spending by Category")
    if not filtered_df.empty:
        category_totals = filtered_df.groupby("category")["amount"].sum().sort_values(ascending=False)
        st.bar_chart(category_totals)
    else:
        st.info("No data available for selected filters.")

    st.subheader("Monthly Spending Trend")
    if "date" in filtered_df.columns and not filtered_df.empty:
        # Group data by month to plot a trend
        monthly_totals = filtered_df.set_index("date").resample("MS")["amount"].sum()
        st.line_chart(monthly_totals)
    else:
        st.info("No valid date entries available for monthly trend.")
        
    st.markdown("---")

def show_receipt_details(filtered_df):
    """Displays the expense details in a table and shows receipt images."""
    st.subheader("Receipt Details")
    display_df = filtered_df.drop(columns=["_id"], errors="ignore")
    st.dataframe(display_df, use_container_width=True)

    # Show images if the column exists and has data
    if "receipt_image" in filtered_df.columns:
        for _, row in filtered_df.iterrows():
            if row["receipt_image"]:
                st.image(row["receipt_image"], caption=f"{row.get('merchant', 'Unknown')} - ${row['amount']}", width=300)

def show_remove_expense_form(df):
    """Displays the form to remove an expense by its ID."""
    st.subheader("🗑️ Remove an Expense")
    if not df.empty:
        # Sort by date and get the top 10 for convenience
        recent_expenses = df.sort_values(by="date", ascending=False).head(10)
        
        # Use a more descriptive format for the selectbox
        def format_func(doc_id):
            row = recent_expenses[recent_expenses["_id"] == doc_id].iloc[0]
            date_str = row["date"].strftime("%Y-%m-%d")
            return f"{date_str} - {row['merchant']} (${row['amount']})"
            
        selected_id = st.selectbox(
            "Select an expense to remove",
            options=recent_expenses["_id"],
            format_func=format_func
        )

        if st.button("Remove Selected Expense"):
            # Ensure the selected ID is a valid ObjectId
            doc_to_delete = {"_id": selected_id}
            collection.delete_one(doc_to_delete)
            st.cache_data.clear()
            st.success("Expense removed successfully!")
            st.rerun()
    else:
        st.info("No expenses available to remove.")

# --- Main App Execution ---
if df.empty:
    st.info("No expense data found. Please add a new expense below.")
    show_add_expense_form()
else:
    # Sidebar filters
    st.sidebar.title("🔍 Filters")
    df['month'] = df['date'].dt.strftime('%Y-%m')
    
    # Use a sorted list for consistent filter options
    sorted_categories = sorted(df["category"].dropna().unique())
    selected_category = st.sidebar.selectbox("Category", ["All"] + sorted_categories)
    
    sorted_months = sorted(df["month"].dropna().astype(str).unique())
    selected_month = st.sidebar.selectbox("Month", ["All"] + sorted_months)

    # Apply filters
    filtered_df = df.copy()
    if selected_category != "All":
        filtered_df = filtered_df[filtered_df["category"] == selected_category]
    if selected_month != "All":
        filtered_df = filtered_df[filtered_df["month"].astype(str) == selected_month]

    # Display the different sections of the app
    show_dashboard(filtered_df)
    show_receipt_details(filtered_df)
    
    st.markdown("---")
    
    show_add_expense_form()
    show_remove_expense_form(df)
