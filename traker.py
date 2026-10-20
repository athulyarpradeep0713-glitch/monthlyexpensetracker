
import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import date
import calendar
import html

st.set_page_config(
    page_title="Daily Ledger",
    layout="wide",
    initial_sidebar_state="expanded"
)

DATA_FILE = Path(__file__).with_name("transactions.csv")
COLUMNS = [
    "ID", "Date", "Type", "Category",
    "Description", "Payment", "Amount"
]

CATEGORIES = [
    "Food & groceries", "Transport", "Shopping",
    "Bills & utilities", "Education", "Health",
    "Entertainment", "Travel", "Personal care", "Home", "Other"
]

INCOME_CATEGORIES = ["Salary", "Freelance", "Other"]

PAYMENTS = [
    "UPI", "Cash", "Debit card",
    "Credit card", "Bank transfer", "Other"
]

st.markdown("""
<style>
.stApp {
    background: #f7f6f1;
    color: #292d26;
}
[data-testid="stHeader"] {
    background: #f7f6f1;
}
[data-testid="stSidebar"] {
    background: #eeeee5 !important;
    border-right: 1px solid #deded3;
}
[data-testid="stSidebar"] > div {
    background: #eeeee5 !important;
}
[data-testid="stSidebar"] * {
    color: #292d26 !important;
}
[data-testid="stSidebar"] input,
[data-testid="stSidebar"] textarea,
[data-testid="stSidebar"] [data-baseweb="select"] > div,
[data-testid="stSidebar"] [data-baseweb="input"] > div {
    background-color: #fffefa !important;
    color: #292d26 !important;
    border-color: #d8d8cb !important;
}
[data-testid="stSidebar"] button {
    color: #292d26 !important;
}
[data-testid="stSidebar"] [data-baseweb="select"] svg {
    fill: #45483f !important;
}
[data-baseweb="popover"],
[data-baseweb="menu"],
[role="listbox"] {
    background: #fffefa !important;
}
[role="option"],
[data-baseweb="menu"] * {
    color: #292d26 !important;
}
[data-baseweb="popover"] * {
    border-color: #deded3;
}
.block-container {
    max-width: 1180px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}
h1, h2, h3 {
    color: #292d26 !important;
    letter-spacing: -0.6px;
}
label, [data-testid="stWidgetLabel"] p {
    color: #45483f !important;
}
[data-baseweb="select"] > div,
[data-baseweb="input"] > div,
[data-baseweb="textarea"] > div {
    background: #fffefa !important;
    color: #292d26 !important;
    border-color: #deded3 !important;
}
[data-baseweb="select"] input,
[data-baseweb="input"] input,
[data-baseweb="textarea"] textarea {
    color: #292d26 !important;
}
.eyebrow {
    color: #73786a;
    font-size: 11px;
    letter-spacing: 2px;
    font-weight: 600;
}
.intro {
    color: #73766d;
    font-size: 14px;
    margin-bottom: 25px;
}
.metric {
    background: #fffefa;
    border: 1px solid #e5e3d9;
    border-radius: 9px;
    padding: 19px;
    min-height: 110px;
}
.metric-label {
    color: #777a70;
    font-size: 11px;
    letter-spacing: .7px;
    margin-bottom: 12px;
}
.metric-value {
    color: #292d26;
    font-size: 25px;
    font-weight: 650;
}
.metric-note {
    color: #85877e;
    font-size: 11px;
    margin-top: 6px;
}
.section-heading {
    font-size: 18px;
    font-weight: 650;
    margin-top: 25px;
    color: #292d26;
}
.section-note {
    color: #7a7c73;
    font-size: 12px;
    margin-bottom: 15px;
}
div.stButton > button,
div.stDownloadButton > button,
div.stFormSubmitButton > button {
    border-radius: 6px;
    border: 1px solid #d2d5c7;
    background: #fffefa;
    color: #34382f;
}
div.stButton > button[kind="primary"],
div.stFormSubmitButton > button[kind="primary"] {
    background: #69765b;
    border-color: #69765b;
    color: white;
}
[data-testid="stDataFrame"] {
    border: 1px solid #e4e2d8;
    border-radius: 7px;
}
hr {
    border-color: #e3e1d8;
}
.bar-track {
    width: 100%;
    background: #e9e8df;
    border-radius: 4px;
    height: 10px;
    margin-top: 6px;
    margin-bottom: 15px;
    overflow: hidden;
}
.bar-fill {
    background: #7b8769;
    height: 10px;
    border-radius: 4px;
}
.chart-panel {
    background: #fffefa;
    border: 1px solid #e5e3d9;
    border-radius: 9px;
    padding: 18px;
}
.chart-label {
    color: #53574c;
    font-size: 13px;
}
.chart-value {
    color: #292d26;
    font-size: 13px;
    font-weight: 600;
    text-align: right;
}
</style>
""", unsafe_allow_html=True)


def money(value):
    return f"₹{float(value):,.2f}"


def load_data():
    if not DATA_FILE.exists():
        return pd.DataFrame(columns=COLUMNS)

    try:
        df = pd.read_csv(DATA_FILE)

        for col in COLUMNS:
            if col not in df.columns:
                df[col] = None

        df = df[COLUMNS]
        df["ID"] = pd.to_numeric(
            df["ID"], errors="coerce"
        ).fillna(0).astype(int)

        df["Amount"] = pd.to_numeric(
            df["Amount"], errors="coerce"
        ).fillna(0.0)

        df["Date"] = pd.to_datetime(
            df["Date"], errors="coerce"
        ).dt.strftime("%Y-%m-%d")

        return df.dropna(subset=["Date"]).reset_index(drop=True)

    except (ValueError, OSError, pd.errors.ParserError):
        st.error("Could not read transactions.csv.")
        return pd.DataFrame(columns=COLUMNS)


if "transactions" not in st.session_state:
    st.session_state.transactions = load_data()

if "next_id" not in st.session_state:
    old = st.session_state.transactions
    st.session_state.next_id = (
        int(old["ID"].max()) + 1 if not old.empty else 1
    )


def save_data():
    st.session_state.transactions[COLUMNS].to_csv(
        DATA_FILE, index=False
    )


def add_transaction(tx_date, tx_type, category, description, payment, amount):
    row = {
        "ID": st.session_state.next_id,
        "Date": tx_date.isoformat(),
        "Type": tx_type,
        "Category": category,
        "Description": description.strip(),
        "Payment": payment,
        "Amount": float(amount)
    }

    st.session_state.transactions = pd.concat(
        [
            st.session_state.transactions,
            pd.DataFrame([row])
        ],
        ignore_index=True
    )

    st.session_state.next_id += 1
    save_data()


def heading(title, note=""):
    st.markdown(
        f'<div class="section-heading">{html.escape(title)}</div>',
        unsafe_allow_html=True
    )
    if note:
        st.markdown(
            f'<div class="section-note">{html.escape(note)}</div>',
            unsafe_allow_html=True
        )


def metric(label, value, note):
    st.markdown(
        f'<div class="metric">'
        f'<div class="metric-label">{html.escape(label)}</div>'
        f'<div class="metric-value">{html.escape(value)}</div>'
        f'<div class="metric-note">{html.escape(note)}</div></div>',
        unsafe_allow_html=True
    )


def draw_bars(series):
    if series.empty:
        st.caption("Nothing to display yet.")
        return

    maximum = float(series.max()) if len(series) else 0

    if maximum <= 0:
        st.caption("No values to display.")
        return

    for label, value in series.sort_values(ascending=False).items():
        safe_label = html.escape(str(label))
        width = max(0, min(100, float(value) / maximum * 100))

        st.markdown(
            f'<div class="chart-label">{safe_label}</div>'
            f'<div class="chart-value">{money(value)}</div>'
            f'<div class="bar-track"><div class="bar-fill" '
            f'style="width:{width:.2f}%"></div></div>',
            unsafe_allow_html=True
        )


# Sidebar
with st.sidebar:
    st.markdown("## Daily Ledger")
    st.caption("PERSONAL FINANCE")
    st.divider()

    st.markdown("### New transaction")
    st.caption("Record money coming in or going out.")

    with st.form("transaction_form", clear_on_submit=True):
        tx_type = st.selectbox(
            "Transaction type", ["Expense", "Income"]
        )

        # Select the date without opening a calendar popup.
        today = date.today()
        years = list(range(today.year - 10, today.year + 6))
        if today.year not in years:
            years.append(today.year)
        years = sorted(set(years))

        year = st.selectbox(
            "Year", years, index=years.index(today.year)
        )

        month = st.selectbox(
            "Month",
            list(range(1, 13)),
            index=today.month - 1,
            format_func=lambda m: calendar.month_name[m]
        )

        max_day = calendar.monthrange(year, month)[1]
        day = st.selectbox(
            "Day",
            list(range(1, max_day + 1)),
            index=min(today.day, max_day) - 1
        )

        tx_date = date(year, month, day)

        categories = (
            CATEGORIES if tx_type == "Expense"
            else INCOME_CATEGORIES
        )

        category = st.selectbox("Category", categories)

        description = st.text_input(
            "Description",
            placeholder="e.g. Weekly groceries"
        )

        payment = st.selectbox("Payment method", PAYMENTS)

        amount = st.number_input(
            "Amount (₹)",
            min_value=0.0,
            value=0.0,
            step=100.0,
            format="%.2f"
        )

        submitted = st.form_submit_button(
            "Save transaction",
            type="primary",
            use_container_width=True
        )

    if submitted:
        if amount <= 0:
            st.error("Enter an amount greater than zero.")
        elif not description.strip():
            st.error("Please enter a description.")
        else:
            add_transaction(
                tx_date, tx_type, category,
                description, payment, amount
            )
            st.success("Transaction saved.")
            st.rerun()

    st.divider()
    st.caption("Records are saved in transactions.csv.")


# Main dashboard
st.markdown(
    '<div class="eyebrow">PERSONAL FINANCE / OVERVIEW</div>',
    unsafe_allow_html=True
)

st.title("Your money, at a glance.")

st.markdown(
    '<div class="intro">A simple record of what comes in and what goes out.</div>',
    unsafe_allow_html=True
)

transactions = st.session_state.transactions.copy()

if not transactions.empty:
    transactions["Date"] = pd.to_datetime(
        transactions["Date"], errors="coerce"
    )
    months = sorted(
        transactions["Date"].dropna().dt.strftime("%Y-%m").unique(),
        reverse=True
    )
else:
    months = []

current_month = date.today().strftime("%Y-%m")
if current_month not in months:
    months.insert(0, current_month)

month_names = {
    m: pd.to_datetime(m + "-01").strftime("%B %Y")
    for m in months
}

period = st.selectbox(
    "View period",
    ["All months"] + months,
    format_func=lambda m: (
        m if m == "All months" else month_names.get(m, m)
    )
)

if period == "All months":
    filtered = transactions.copy()
else:
    filtered = transactions[
        transactions["Date"].dt.strftime("%Y-%m") == period
    ].copy()

income = filtered.loc[
    filtered["Type"] == "Income", "Amount"
].sum()

expenses = filtered.loc[
    filtered["Type"] == "Expense", "Amount"
].sum()

balance = income - expenses

a, b, c = st.columns(3)

with a:
    metric("TOTAL INCOME", money(income), "Money received this period")

with b:
    metric("TOTAL EXPENSES", money(expenses), "Money spent this period")

with c:
    metric("NET BALANCE", money(balance), "Income minus expenses")


left, right = st.columns(2)

with left:
    heading("Spending by category", "Where your expenses are going.")

    expense_data = filtered[filtered["Type"] == "Expense"]

    if expense_data.empty:
        st.info("Your spending chart will appear here after you add expenses.")
    else:
        totals = expense_data.groupby("Category")["Amount"].sum()
        draw_bars(totals)

with right:
    heading("Income vs expenses", "A comparison for the selected period.")

    comparison = pd.Series(
        {"Income": income, "Expenses": expenses}
    )
    draw_bars(comparison)

    if income > 0:
        st.caption(
            f"Net balance is {(balance / income) * 100:.1f}% of income."
        )
    else:
        st.caption("Add income to see your balance percentage.")


# Transactions
heading("Transactions", "Your recorded financial activity.")

if filtered.empty:
    st.info("No transactions for this period yet. Add one from the sidebar.")
else:
    display = filtered.copy()

    display["Date"] = display["Date"].dt.strftime("%d %b %Y")

    display["Amount"] = display.apply(
        lambda row: (
            "+ " if row["Type"] == "Income" else "− "
        ) + money(row["Amount"]),
        axis=1
    )

    display = display.sort_values("Date", ascending=False)

    st.dataframe(
        display[
            [
                "Date", "Description", "Category",
                "Type", "Payment", "Amount"
            ]
        ],
        use_container_width=True,
        hide_index=True
    )

    st.download_button(
        "Export transactions as CSV",
        data=filtered.to_csv(index=False).encode("utf-8"),
        file_name="my_transactions.csv",
        mime="text/csv"
    )


# Delete records
with st.expander("Manage transactions"):
    all_data = st.session_state.transactions.copy()

    if all_data.empty:
        st.caption("There are no transactions to manage yet.")
    else:
        ids = all_data["ID"].astype(int).tolist()

        def transaction_label(tx_id):
            row = all_data[all_data["ID"] == tx_id].iloc[0]
            return (
                f'{row["Date"]} · {row["Description"]} · '
                f'{row["Type"]} · {money(row["Amount"])}'
            )

        chosen_id = st.selectbox(
            "Choose a transaction to delete",
            ids,
            format_func=transaction_label
        )

        if st.button("Delete selected transaction"):
            st.session_state.transactions = (
                st.session_state.transactions[
                    st.session_state.transactions["ID"] != chosen_id
                ].reset_index(drop=True)
            )
            save_data()
            st.success("Transaction deleted.")
            st.rerun()

st.divider()
st.caption("Daily Ledger · Keep it simple. Know where it goes.")
