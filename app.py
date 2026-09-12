import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import date
from dotenv import load_dotenv
from google import genai
from database import load_data, update_stock, record_sale
from users import authenticate

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="AI Business Operations Copilot", page_icon="📊", layout="wide", initial_sidebar_state="expanded")

# ---------------- GLOBAL UI STYLING ----------------
st.markdown("""
<style>
.block-container { padding-top: 1.5rem; padding-bottom: 3rem; max-width: 1500px; }
[data-testid="stSidebar"] { border-right: 1px solid #e5e7eb; background: #f8fafc; }
[data-testid="stSidebar"] .block-container { padding: 1.2rem 1rem 2rem; }
[data-testid="stSidebar"] [data-testid="stRadio"] label { padding: 0.35rem 0.45rem; border-radius: 8px; }
[data-testid="stMetric"] { background: #ffffff; border: 1px solid #e5e7eb; border-radius: 14px; padding: 16px 18px; box-shadow: 0 3px 12px rgba(15,23,42,.04); }
[data-testid="stMetricLabel"] { color: #64748b; font-weight: 600; }
[data-testid="stMetricValue"] { color: #0f172a; font-weight: 750; font-size: 1.85rem; }
.stButton > button, .stDownloadButton > button { border-radius: 9px; font-weight: 650; min-height: 42px; border: 1px solid #dbe2ea; }
.stButton > button:hover, .stDownloadButton > button:hover { border-color: #94a3b8; }
div[data-testid="stDataFrame"] { border: 1px solid #e2e8f0; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 8px rgba(15,23,42,.03); }
h1, h2, h3 { letter-spacing: -0.025em; color: #0f172a; }
.section-note { color: #64748b; font-size: 0.92rem; margin-top: -0.35rem; margin-bottom: 1rem; }
.ai-card { background: #f8fafc; border: 1px solid #dbe4ee; border-radius: 14px; padding: 18px; margin: 8px 0 18px; }
.login-card { background: #ffffff; border: 1px solid #e5e7eb; border-radius: 16px; padding: 28px; box-shadow: 0 8px 28px rgba(15,23,42,.06); }
.app-brand { padding: 4px 2px 14px; }
.app-brand-title { font-size: 1.05rem; font-weight: 750; color: #0f172a; }
.app-brand-sub { font-size: .78rem; color: #64748b; margin-top: 2px; }
.page-hero { background: #ffffff; border: 1px solid #e2e8f0; border-radius: 16px; padding: 20px 22px; margin-bottom: 20px; box-shadow: 0 4px 14px rgba(15,23,42,.04); }
.page-hero-title { font-size: 1.65rem; font-weight: 750; color: #0f172a; }
.page-hero-sub { color: #64748b; margin-top: 4px; font-size: .94rem; }
.card-title { font-weight: 700; color: #0f172a; font-size: 1rem; margin-bottom: 4px; }
.card-sub { color: #64748b; font-size: .86rem; }
div[data-testid="stFormSubmitButton"] > button {
    background: #2563eb;
    color: #ffffff;
    border: 1px solid #2563eb;
    border-radius: 9px;
    font-weight: 650;
    min-height: 44px;
}
div[data-testid="stFormSubmitButton"] > button:hover {
    background: #1d4ed8;
    border-color: #1d4ed8;
    color: #ffffff;
}
</style>
""", unsafe_allow_html=True)

def format_revenue(value):
    """Format large rupee values compactly for dashboard KPI cards."""
    value = float(value)
    if abs(value) >= 100000:
        return f"₹{value/100000:.2f}L"
    if abs(value) >= 1000:
        return f"₹{value/1000:.1f}K"
    return f"₹{value:,.0f}"

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

if "role" not in st.session_state:
    st.session_state.role = ""

# ---------------- LOGIN PAGE ----------------

if not st.session_state.logged_in:

    st.markdown(
        """
        <style>
        /* ---------- Premium login page ---------- */
        .login-shell {
            min-height: 82vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 2.5rem 1rem;
        }

        .login-left {
            padding: 3.5rem 3.2rem;
            border-radius: 18px 0 0 18px;
            background: #f5f9ff;
            border: 1px solid #dbe7f5;
            min-height: 560px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }

        .login-brand {
            font-size: 2.6rem;
            line-height: 1.1;
            font-weight: 780;
            letter-spacing: -1.3px;
            color: #0f172a;
            margin: 0;
        }

        .login-accent {
            width: 54px;
            height: 4px;
            background: #2563eb;
            border-radius: 2px;
            margin: 1.15rem 0 1.1rem;
        }

        .login-description {
            font-size: 1.02rem;
            line-height: 1.65;
            color: #52627a;
            max-width: 510px;
            margin-bottom: 1.6rem;
        }

        .feature-list {
            display: grid;
            gap: .75rem;
            margin-top: .4rem;
        }

        .feature-item {
            display: flex;
            align-items: center;
            gap: .75rem;
            color: #334155;
            font-size: .96rem;
        }

        .feature-check {
            color: #2563eb;
            font-size: 16px;
            font-weight: 800;
            flex-shrink: 0;
            line-height: 1;
        }

        .login-right {
            padding: 3.4rem 3rem;
            border-radius: 18px;
            background: #ffffff;
            border: 1px solid #dbe7f5;
            min-height: 560px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            box-shadow: 0 14px 34px rgba(15, 23, 42, .06);
        }

        div[data-testid="stForm"] {
            border: 0 !important;
            padding: 0 !important;
            box-shadow: none !important;
            background: transparent !important;
        }

        .welcome-title {
            font-size: 2rem;
            font-weight: 750;
            color: #0f172a;
            margin-bottom: .35rem;
        }

        .welcome-subtitle {
            color: #64748b;
            font-size: .98rem;
            margin-bottom: 1.6rem;
        }

        .login-note {
            text-align: center;
            color: #94a3b8;
            font-size: .78rem;
            margin-top: 1.25rem;
        }

        div[data-testid="stFormSubmitButton"] > button {
            background: #2563eb;
            color: #ffffff;
            border: 1px solid #2563eb;
            border-radius: 10px;
            font-weight: 700;
            min-height: 46px;
            transition: all .15s ease;
        }

        div[data-testid="stFormSubmitButton"] > button:hover {
            background: #1d4ed8;
            border-color: #1d4ed8;
            color: #ffffff;
        }

        div[data-testid="stTextInput"] input:focus {
            border-color: #93b4f4 !important;
            box-shadow: 0 0 0 1px #93b4f4 !important;
        }

        @media (max-width: 900px) {
            .login-left {
                border-radius: 18px 18px 0 0;
                min-height: auto;
                padding: 2.5rem 2rem;
            }
            .login-right {
                border-radius: 18px;
                min-height: auto;
                padding: 2.5rem 2rem;
            }
            .login-brand {
                font-size: 2.25rem;
            }
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div style="text-align:center; margin-bottom:1.25rem;">
            <div style="font-size:.74rem; font-weight:750; letter-spacing:1.5px;
                        color:#64748b; text-transform:uppercase;">
                BUSINESS OPERATIONS PLATFORM
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    left, right = st.columns([1.08, 0.92], gap="small")

    with left:
        st.markdown(
            """
            <div class="login-left">
                <div style="font-size:.76rem; font-weight:750; letter-spacing:1.3px; color:#2563eb; text-transform:uppercase; margin-bottom:.8rem;">
                    Business Intelligence
                </div>
                <div class="login-brand">AI Business<br>Operations Copilot</div>
                <div class="login-accent"></div>
                <div class="login-description">
                    Intelligent business insights that help teams understand
                    performance, manage operations, and make faster decisions.
                </div><div class="feature-list">
                    <div class="feature-item">
                        <span class="feature-check">✓</span>
                        <span>Sales analytics and forecasting</span>
                    </div>
                    <div class="feature-item">
                        <span class="feature-check">✓</span>
                        <span>Intelligent inventory management</span>
                    </div>
                    <div class="feature-item">
                        <span class="feature-check">✓</span>
                        <span>Customer performance insights</span>
                    </div>
                    <div class="feature-item">
                        <span class="feature-check">✓</span>
                        <span>AI-powered business assistance</span>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with right:
        with st.container(border=True):
            st.markdown(
                """
                <div class="welcome-title">Welcome back</div>
                <div class="welcome-subtitle">
                    Sign in to access your business dashboard.
                </div>
                """,
                unsafe_allow_html=True
            )

            with st.form("login_form", clear_on_submit=False):
                username = st.text_input(
                    "Username",
                    placeholder="Enter your username"
                )

                password = st.text_input(
                    "Password",
                    type="password",
                    placeholder="Enter your password"
                )

                submitted = st.form_submit_button(
                    "Sign in",
                    use_container_width=True
                )

            if submitted:
                role = authenticate(username, password)

                if role:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.role = role
                    st.rerun()
                else:
                    st.error("Invalid username or password.")

            st.markdown(
                """
                <div class="login-note">
                    Secure business intelligence platform
                </div>
                """,
                unsafe_allow_html=True
            )

    st.stop()

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

sales, inventory, customers = load_data()

# ---------------- CALCULATIONS ----------------
sales["total_sales"] = sales["quantity"] * sales["unit_price"]

total_revenue = sales["total_sales"].sum()
total_orders = len(sales)

low_stock_products = inventory[
    inventory["stock"] < inventory["reorder_level"]
]

low_stock = len(low_stock_products)

customer_satisfaction = customers["satisfaction"].mean()

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.markdown(
        """<div class="app-brand"><div class="app-brand-title">📊 Business Copilot</div><div class="app-brand-sub">AI-powered business intelligence</div></div>""",
        unsafe_allow_html=True
    )
    st.success(f"👤 {st.session_state.username} · {st.session_state.role}")
    st.markdown("---")
    st.caption("WORKSPACE")
    page = st.radio(
        "Navigation",
        [
            "Dashboard",
            "Sales",
            "Inventory",
            "Customers",
            "AI Forecast",
            "AI Assistant",
            "Reports"
        ],
        label_visibility="collapsed"
    )
    st.markdown("---")
    if st.button("🚪  Sign out", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.role = ""
        st.rerun()
    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
    st.caption("Business Operations Copilot")
    st.caption("Python · Streamlit · Gemini")

# ---------------- HEADER ----------------
hero_title = "AI Business Operations Copilot" if page == "Dashboard" else page
hero_subtitle = (
    "Smarter decisions · Smoother operations · Better growth."
    if page == "Dashboard"
    else "AI Business Operations Copilot · Smarter decisions, smoother operations, better growth."
)

st.markdown(
    f"""<div class="page-hero"><div class="page-hero-title">{hero_title}</div><div class="page-hero-sub">{hero_subtitle}</div></div>""",
    unsafe_allow_html=True
)

# ---------------- KPI CARDS ----------------
if page == "Dashboard":
    col1, col2, col3, col4 = st.columns(4, gap="medium")
    with col1:
        st.metric("Revenue", format_revenue(total_revenue))
    with col2:
        st.metric("Orders", total_orders)
    with col3:
        st.metric("Low Stock", low_stock)
    with col4:
        st.metric("Customer Satisfaction", f"{customer_satisfaction:.1f}/5")

# ---------------- DASHBOARD ----------------
if page == "Dashboard":

    st.subheader("📊 Business Overview")
    st.write(
        "Real-time overview of sales, inventory, and customer performance."
    )

    # ---------------- AI / BUSINESS INSIGHTS ----------------

    st.subheader("🤖 Key Business Insights")

    insight_col1, insight_col2, insight_col3 = st.columns(3)

    # Best-selling product
    best_product = (
        sales.groupby("product")["quantity"]
        .sum()
        .sort_values(ascending=False)
        .index[0]
    )

    # Highest revenue product
    highest_revenue_product = (
        sales.groupby("product")["total_sales"]
        .sum()
        .sort_values(ascending=False)
        .index[0]
    )

    # Total units
    total_units = sales["quantity"].sum()

    with insight_col1:
        st.info(
            f"🏆 **Top Product**\n\n"
            f"{best_product}\n\n"
            f"{sales.groupby('product')['quantity'].sum().max()} units sold"
        )

    with insight_col2:
        st.success(
            f"💰 **Revenue Leader**\n\n"
            f"{highest_revenue_product}\n\n"
            "Highest revenue generated"
        )

    with insight_col3:
        st.warning(
            f"⚠️ **Inventory Risk**\n\n"
            f"{low_stock} products\n\n"
            "Require replenishment"
        )

    st.markdown("---")

        # ---------------- SALES TREND ----------------

    st.subheader("📈 Sales Trend")

    daily_sales = (
        sales.groupby("date")["total_sales"]
        .sum()
        .reset_index()
    )

    fig_sales = px.line(
        daily_sales,
        x="date",
        y="total_sales",
        markers=True,
        title="Daily Revenue"
    )

    fig_sales.update_layout(
        xaxis_title="Date",
        yaxis_title="Revenue (₹)"
    )

    st.plotly_chart(
        fig_sales,
        use_container_width=True
    )

    st.markdown("---")

    # ---------------- INVENTORY RISK ----------------

    st.subheader("📦 Inventory Risk")
    st.write("Products that may require immediate replenishment.")

    dashboard_inventory = inventory.copy()

    dashboard_inventory["Status"] = dashboard_inventory.apply(
        lambda row: "🔴 Reorder Required"
        if row["stock"] < row["reorder_level"]
        else "🟢 Healthy",
        axis=1
    )

    display_inventory = dashboard_inventory[
        [
            "product",
            "category",
            "stock",
            "reorder_level",
            "reorder_quantity",
            "Status"
        ]
    ].copy()

    st.dataframe(
        display_inventory,
        use_container_width=True,
        hide_index=True,
        height=250
    )

    st.markdown("---")

    # ---------------- TOP PRODUCTS ----------------

    st.subheader("🏆 Top Products by Sales")

    top_products = (
        sales.groupby("product")
        .agg(
            units_sold=("quantity", "sum"),
            revenue=("total_sales", "sum")
        )
        .reset_index()
        .sort_values("revenue", ascending=False)
    )

    fig_top_products = px.bar(
        top_products,
        x="product",
        y="revenue",
        title="Revenue by Product"
    )

    fig_top_products.update_layout(
        xaxis_title="Product",
        yaxis_title="Revenue (₹)"
    )

    st.plotly_chart(
        fig_top_products,
        use_container_width=True
    )

    # ---------------- BUSINESS RECOMMENDATIONS ----------------

    st.subheader("💡 Recommended Actions")

    for _, product in low_stock_products.iterrows():

        product_name = product["product"]
        current_stock = product["stock"]
        reorder_quantity = product["reorder_quantity"]

        st.warning(
            f"**{product_name}** is below the reorder level. "
            f"Current stock: {current_stock} units. "
            f"Recommended reorder: {reorder_quantity} units."
        )

    # ---------------- SALES ----------------
elif page == "Sales":

        # ---------------- RECORD NEW SALE ----------------

    if st.session_state.role == "Admin":

        st.subheader("➕ Record New Sale")

        product_prices = (
            sales.groupby("product")["unit_price"]
            .last()
            .to_dict()
        )

        sale_product = st.selectbox(
            "Select Product",
            list(product_prices.keys())
        )

        sale_quantity = st.number_input(
            "Quantity",
            min_value=1,
            value=1,
            step=1
        )

        sale_price = float(product_prices[sale_product])

        st.write(
            f"Unit Price: **₹{sale_price:,.0f}**"
        )

        st.write(
            f"Total Sale: **₹{sale_price * sale_quantity:,.0f}**"
        )

        if st.button("💾 Record Sale"):

            category = inventory.loc[
                inventory["product"] == sale_product,
                "category"
            ].iloc[0]

            try:

                record_sale(
                    product=sale_product,
                    category=category,
                    quantity=int(sale_quantity),
                    unit_price=sale_price,
                    sale_date=str(date.today())
                )

                st.success(
                    f"Sale recorded successfully: "
                    f"{sale_quantity} × {sale_product}"
                )

                st.rerun()

            except ValueError as e:

                st.error(str(e))

    else:

        st.info(
            "🔒 Only Admin users can record sales."
        )

    st.markdown("---")

    st.subheader("📈 Sales Analytics")
    st.write("Analyze revenue, sales volume, and product performance.")

    # ---------------- SALES KPIs ----------------
    sales_col1, sales_col2, sales_col3 = st.columns(3)

    total_units = sales["quantity"].sum()

    best_product = (
        sales.groupby("product")["quantity"]
        .sum()
        .sort_values(ascending=False)
        .index[0]
    )

    best_revenue_product = (
        sales.groupby("product")["total_sales"]
        .sum()
        .sort_values(ascending=False)
        .index[0]
    )

    with sales_col1:
        st.metric(
            "💰 Total Revenue",
            f"₹{total_revenue:,.0f}"
        )

    with sales_col2:
        st.metric(
            "📦 Units Sold",
            f"{total_units:,}"
        )

    with sales_col3:
        st.metric(
            "🏆 Best-Selling Product",
            best_product
        )

    st.markdown("---")

    # ---------------- DAILY SALES ----------------
    st.subheader("📊 Daily Revenue")

    daily_sales = (
        sales.groupby("date")["total_sales"]
        .sum()
        .reset_index()
    )

    fig_daily = px.line(
        daily_sales,
        x="date",
        y="total_sales",
        markers=True,
        title="Daily Revenue Trend"
    )

    fig_daily.update_layout(
        xaxis_title="Date",
        yaxis_title="Revenue (₹)"
    )

    st.plotly_chart(
        fig_daily,
        use_container_width=True
    )

    # ---------------- PRODUCT PERFORMANCE ----------------
    st.subheader("🏆 Product Performance")

    product_sales = (
        sales.groupby("product")
        .agg(
            units_sold=("quantity", "sum"),
            revenue=("total_sales", "sum")
        )
        .reset_index()
        .sort_values("revenue", ascending=False)
    )

    st.dataframe(
        product_sales,
        use_container_width=True,
        hide_index=True
    )

    # ---------------- TOP PRODUCTS CHART ----------------
    fig_products = px.bar(
        product_sales.sort_values(
            "units_sold",
            ascending=True
        ),
        x="units_sold",
        y="product",
        orientation="h",
        title="Units Sold by Product"
    )

    fig_products.update_layout(
        xaxis_title="Units Sold",
        yaxis_title="Product"
    )

    st.plotly_chart(
        fig_products,
        use_container_width=True
    )


# ---------------- INVENTORY ----------------
elif page == "Inventory":

    st.subheader("📦 Inventory Intelligence")

    st.write(
        "Monitor stock levels and identify products that require replenishment."
    )

    # ---------------- INVENTORY ANALYSIS ----------------

    inventory_analysis = inventory.copy()

    inventory_analysis["stock_deficit"] = (
        inventory_analysis["reorder_level"]
        - inventory_analysis["stock"]
    )

    inventory_analysis["status"] = inventory_analysis.apply(
        lambda row: "🔴 Reorder Required"
        if row["stock"] < row["reorder_level"]
        else "🟢 Healthy",
        axis=1
    )

    # ---------------- UPDATE INVENTORY ----------------

    st.markdown("---")

    st.subheader("✏️ Update Inventory")

    selected_product = st.selectbox(
        "Select Product",
        inventory["product"].tolist()
    )

    current_stock = int(
        inventory.loc[
            inventory["product"] == selected_product,
            "stock"
        ].iloc[0]
    )

    st.write(
        f"Current stock: **{current_stock} units**"
    )

    new_stock = st.number_input(
        "Enter New Stock",
        min_value=0,
        value=current_stock,
        step=1,
        key=f"stock_input_{selected_product}_{current_stock}"
    )

    if st.session_state.role == "Admin":

        if st.button("💾 Update Stock"):

            update_stock(
                selected_product,
                int(new_stock)
            )

            st.success(
                f"Stock updated successfully for {selected_product}."
            )

            st.rerun()

    else:

        st.info(
            "🔒 Only Admin users can update inventory."
        )

    # ---------------- AI INVENTORY RECOMMENDATIONS ----------------

    st.markdown("---")

    st.subheader("🤖 AI Inventory Recommendations")

    st.write(
        "Use AI to analyze current stock and sales history "
        "and recommend inventory actions."
    )

    if st.button("🔍 Analyze Inventory with AI"):

        inventory_data = inventory.to_string(index=False)

        sales_summary = (
            sales.groupby("product")
            .agg(
                units_sold=("quantity", "sum"),
                revenue=("total_sales", "sum")
            )
            .reset_index()
            .to_string(index=False)
        )

        with st.spinner("🤖 AI is analyzing inventory..."):

            try:

                interaction = client.interactions.create(
                    model="gemini-3.6-flash",
                    input=f"""
You are an AI inventory management assistant.

Analyze the following business data.

CURRENT INVENTORY:
{inventory_data}

SALES PERFORMANCE:
{sales_summary}

Tasks:
1. Identify products that require replenishment.
2. Identify products with healthy stock.
3. Consider sales volume when making recommendations.
4. Give a concise business recommendation.
5. Use only the provided data.
6. Do not invent numbers.

Format the response with clear headings and bullet points.
"""
                )

                st.success("🤖 AI Inventory Analysis")

                st.write(interaction.output_text)

            except Exception as e:

                if "429" in str(e) or "quota" in str(e).lower():

                    st.warning(
                        "⚠️ Gemini AI quota has been reached. "
                        "Please try again later."
                    )

                else:

                    st.error(
                        f"AI analysis failed: {e}"
                    )

    # ---------------- KPI CARDS ----------------

    st.markdown("---")

    inv_col1, inv_col2, inv_col3 = st.columns(3)

    reorder_count = len(
        inventory_analysis[
            inventory_analysis["stock"]
            < inventory_analysis["reorder_level"]
        ]
    )

    healthy_count = len(
        inventory_analysis[
            inventory_analysis["stock"]
            >= inventory_analysis["reorder_level"]
        ]
    )

    with inv_col1:
        st.metric(
            "🔴 Reorder Required",
            reorder_count
        )

    with inv_col2:
        st.metric(
            "🟢 Healthy Stock",
            healthy_count
        )

    with inv_col3:
        st.metric(
            "📦 Total Products",
            len(inventory_analysis)
        )

    st.markdown("---")

    # ---------------- INVENTORY TABLE ----------------

    st.subheader("📋 Inventory Status")

    display_inventory = inventory_analysis[
        [
            "product",
            "category",
            "stock",
            "reorder_level",
            "stock_deficit",
            "reorder_quantity",
            "status"
        ]
    ]

    st.dataframe(
        display_inventory,
        use_container_width=True,
        hide_index=True
    )

    # ---------------- STOCK CHART ----------------

    st.subheader("📊 Current Stock vs Reorder Level")

    fig_inventory = px.bar(
        inventory_analysis,
        x="product",
        y=["stock", "reorder_level"],
        barmode="group",
        title="Inventory Risk Analysis"
    )

    fig_inventory.update_layout(
        xaxis_title="Product",
        yaxis_title="Units"
    )

    st.plotly_chart(
        fig_inventory,
        use_container_width=True
    )

    # ---------------- RECOMMENDATIONS ----------------

    st.subheader("💡 Recommended Actions")

    for _, product in inventory_analysis.iterrows():

        if product["stock"] < product["reorder_level"]:

            st.warning(
                f"**{product['product']}** needs replenishment. "
                f"Current stock: {product['stock']} units. "
                f"Recommended reorder: "
                f"{product['reorder_quantity']} units."
            )


# ---------------- CUSTOMERS ----------------
elif page == "Customers":

    st.subheader("👥 Customer Analytics")
    st.write(
        "Understand customer activity, spending, and satisfaction."
    )

    # ---------------- CUSTOMER KPIs ----------------

    customer_col1, customer_col2, customer_col3, customer_col4 = st.columns(4)

    total_customers = len(customers)
    total_customer_orders = customers["orders"].sum()
    total_customer_spending = customers["total_spent"].sum()
    average_satisfaction = customers["satisfaction"].mean()

    with customer_col1:
        st.metric(
            "👥 Total Customers",
            total_customers
        )

    with customer_col2:
        st.metric(
            "🛒 Total Orders",
            total_customer_orders
        )

    with customer_col3:
        st.metric(
            "💰 Total Spending",
            f"₹{total_customer_spending:,.0f}"
        )

    with customer_col4:
        st.metric(
            "⭐ Avg Satisfaction",
            f"{average_satisfaction:.1f}/5"
        )

    st.markdown("---")

    # ---------------- TOP CUSTOMERS ----------------

    st.subheader("🏆 Top Customers")

    top_customers = customers.sort_values(
        "total_spent",
        ascending=False
    )

    st.dataframe(
        top_customers,
        use_container_width=True,
        hide_index=True
    )

    # ---------------- SPENDING CHART ----------------

    st.subheader("💰 Customer Spending")

    fig_customers = px.bar(
        top_customers.sort_values(
            "total_spent",
            ascending=True
        ),
        x="total_spent",
        y="customer_name",
        orientation="h",
        title="Customer Spending Analysis"
    )

    fig_customers.update_layout(
        xaxis_title="Total Spent (₹)",
        yaxis_title="Customer"
    )

    st.plotly_chart(
        fig_customers,
        use_container_width=True
    )

    # ---------------- SATISFACTION ----------------

    st.subheader("⭐ Customer Satisfaction")

    fig_satisfaction = px.bar(
        customers,
        x="customer_name",
        y="satisfaction",
        title="Customer Satisfaction Score"
    )

    fig_satisfaction.update_layout(
        xaxis_title="Customer",
        yaxis_title="Satisfaction (1–5)",
        yaxis_range=[0, 5]
    )

    st.plotly_chart(
        fig_satisfaction,
        use_container_width=True
    )

# ---------------- AI ASSISTANT ----------------
elif page == "AI Assistant":

    st.subheader("🤖 AI Business Assistant")

    st.write(
        "Ask questions about sales, inventory, customers, "
        "and overall business performance."
    )

    st.markdown("---")

    question = st.text_input(
        "💬 Ask a business question",
        placeholder="Example: Which products need restocking?"
    )

    if st.button("🔍 Analyze") and question:

        question_lower = question.lower()

        # ---------------- BUSINESS CALCULATIONS ----------------

        product_sales = (
            sales.groupby("product")
            .agg(
                units_sold=("quantity", "sum"),
                revenue=("total_sales", "sum")
            )
            .reset_index()
            .sort_values("revenue", ascending=False)
        )

        low_stock_products = inventory[
            inventory["stock"] < inventory["reorder_level"]
        ]

        top_product = product_sales.iloc[0]["product"]

        top_revenue = product_sales.iloc[0]["revenue"]

        total_units = sales["quantity"].sum()

        average_satisfaction = customers["satisfaction"].mean()

                # ---------------- QUESTION TYPE DETECTION ----------------

        if (
            "restock" in question_lower
            or "reorder" in question_lower
            or "low stock" in question_lower
            or "stock" in question_lower
        ):

            if len(low_stock_products) == 0:

                answer = "🟢 All products currently have healthy stock levels."

            else:

                answer = "🔴 **Products requiring replenishment:**\n\n"

                for _, row in low_stock_products.iterrows():

                    answer += (
                        f"- **{row['product']}** — "
                        f"{int(row['stock'])} units available "
                        f"(reorder level: {int(row['reorder_level'])}, "
                        f"recommended reorder: {int(row['reorder_quantity'])})\n"
                    )

                answer += (
                    "\n💡 **Recommendation:** Prioritize products "
                    "with low stock and high sales demand."
                )

            st.success("📊 Business Analysis")
            st.markdown(answer)

        elif (
            "best selling" in question_lower
            or "best-selling" in question_lower
            or "best_selling" in question_lower
            or "best-selling" in question_lower
            or "top product" in question_lower
            or "most sold" in question_lower
        ):

            st.success("📊 Business Analysis")

            st.markdown(
                f"""
                🏆 **Top-selling product:** {top_product}

                📦 **Units sold:** {int(
                    product_sales.iloc[0]["units_sold"]
                )}

                💰 **Revenue generated:** ₹{top_revenue:,.0f}
                """
            )

        elif (
            "revenue" in question_lower
            or "sales" in question_lower
            or "income" in question_lower
        ):

            st.success("📊 Business Analysis")

            st.markdown(
                f"""
                💰 **Total Revenue:** ₹{total_revenue:,.0f}

                📦 **Total Units Sold:** {int(total_units)}

                🛒 **Total Sales Transactions:** {total_orders}

                📈 **Average Transaction Value:** ₹{
                    total_revenue / total_orders:,.0f
                }
                """
            )

        elif (
            "customer" in question_lower
            or "satisfaction" in question_lower
        ):

            top_customer = customers.sort_values(
                "total_spent",
                ascending=False
            ).iloc[0]

            st.success("📊 Customer Analysis")

            st.markdown(
                f"""
                👥 **Total Customers:** {len(customers)}

                ⭐ **Average Satisfaction:** {
                    average_satisfaction:.1f
                } / 5

                🏆 **Highest-value Customer:** {
                    top_customer["customer_name"]
                }

                💰 **Customer Spending:** ₹{
                    top_customer["total_spent"]:,.0f
                }
                """
            )

        else:

            # ---------------- GEMINI FOR GENERAL QUESTIONS ----------------

            business_data = f"""
SALES SUMMARY:
{product_sales.to_string(index=False)}

INVENTORY:
{inventory.to_string(index=False)}

CUSTOMERS:
{customers.to_string(index=False)}

TOTAL REVENUE: ₹{total_revenue:,.0f}
TOTAL ORDERS: {total_orders}
TOTAL UNITS SOLD: {total_units}
AVERAGE CUSTOMER SATISFACTION: {average_satisfaction:.1f}/5
"""

            with st.spinner("🤖 AI is analyzing your question..."):

                try:

                    interaction = client.interactions.create(
                        model="gemini-3.6-flash",
                        input=f"""
You are an AI Business Operations Copilot.

Answer the user's question using only the
provided business information.

BUSINESS DATA:
{business_data}

USER QUESTION:
{question}

Rules:
- Answer directly.
- Be concise and professional.
- Do not invent numbers.
- Give a useful recommendation when appropriate.
- Keep the response under 150 words.
"""
                    )

                    st.success("🤖 AI Business Insight")
                    st.write(interaction.output_text)

                except Exception as e:

                    if "429" in str(e) or "quota" in str(e).lower():

                        st.warning(
                            "⚠️ Gemini AI quota has been reached. "
                            "Please try again later."
                        )

                    else:

                        st.error(
                            f"AI request failed: {e}"
                        )

# ---------------- REPORTS ----------------
elif page == "Reports":

    st.subheader("📑 Business Reports")

    st.write(
        "Generate a summary of sales, inventory, and customer performance."
    )

    # ---------------- REPORT SUMMARY ----------------

    st.subheader("📊 Business Summary")

    report_col1, report_col2, report_col3, report_col4 = st.columns(4)

    total_units = sales["quantity"].sum()
    average_order_value = total_revenue / total_orders

    with report_col1:
        st.metric(
            "💰 Total Revenue",
            f"₹{total_revenue:,.0f}"
        )

    with report_col2:
        st.metric(
            "📦 Units Sold",
            f"{total_units:,}"
        )

    with report_col3:
        st.metric(
            "⚠️ Low Stock Products",
            low_stock
        )

    with report_col4:
        st.metric(
            "🛒 Average Order Value",
            f"₹{average_order_value:,.0f}"
        )

    st.markdown("---")

    # ---------------- PRODUCT PERFORMANCE ----------------

    st.subheader("🏆 Product Performance")

    product_report = (
        sales.groupby("product")
        .agg(
            units_sold=("quantity", "sum"),
            revenue=("total_sales", "sum")
        )
        .reset_index()
        .sort_values("revenue", ascending=False)
    )

    st.dataframe(
        product_report,
        use_container_width=True,
        hide_index=True
    )

    st.markdown("---")

    # ---------------- INVENTORY REPORT ----------------

    st.subheader("📦 Inventory Report")

    report_inventory = inventory.copy()

    report_inventory["Status"] = report_inventory.apply(
        lambda row: "🔴 Reorder Required"
        if row["stock"] < row["reorder_level"]
        else "🟢 Healthy",
        axis=1
    )

    st.dataframe(
        report_inventory,
        use_container_width=True,
        hide_index=True
    )

    st.markdown("---")

    # ---------------- CUSTOMER REPORT ----------------

    st.subheader("👥 Customer Report")

    customer_report = customers.sort_values(
        "total_spent",
        ascending=False
    )

    st.dataframe(
        customer_report,
        use_container_width=True,
        hide_index=True
    )

    st.markdown("---")

    # ---------------- DOWNLOAD REPORT ----------------

    st.subheader("⬇️ Download Reports")

    report_csv = product_report.to_csv(index=False)

    st.download_button(
        label="📥 Download Sales Report",
        data=report_csv,
        file_name="business_sales_report.csv",
        mime="text/csv"
    )

# ---------------- AI FORECAST ----------------
elif page == "AI Forecast":

    st.subheader("📈 AI Sales Forecast")

    st.write(
        "Analyze historical sales and estimate future business performance."
    )

    # Product performance
    product_summary = (
        sales.groupby("product")
        .agg(
            units_sold=("quantity", "sum"),
            revenue=("total_sales", "sum")
        )
        .reset_index()
        .sort_values("revenue", ascending=False)
    )

    st.subheader("📊 Historical Performance")

    st.dataframe(
        product_summary,
        use_container_width=True,
        hide_index=True
    )

    st.markdown("---")

    # Daily sales
    daily_sales = (
        sales.groupby("date")["total_sales"]
        .sum()
        .reset_index()
    )

    average_daily_sales = daily_sales["total_sales"].mean()

    recent_average = (
        daily_sales.tail(5)["total_sales"].mean()
    )

    # Determine trend
    if recent_average > average_daily_sales:
        trend = "📈 Increasing"
    elif recent_average < average_daily_sales:
        trend = "📉 Decreasing"
    else:
        trend = "➡️ Stable"

    # Estimate next 7 days
    estimated_next_7_days = recent_average * 7

    st.subheader("🔮 Forecast")

    forecast_col1, forecast_col2, forecast_col3 = st.columns(3)

    with forecast_col1:
        st.metric(
            "Average Daily Revenue",
            f"₹{average_daily_sales:,.0f}"
        )

    with forecast_col2:
        st.metric(
            "Recent Daily Average",
            f"₹{recent_average:,.0f}"
        )

    with forecast_col3:
        st.metric(
            "Sales Trend",
            trend
        )

    st.markdown("---")

    st.subheader("🔮 Estimated Next 7 Days Revenue")

    st.metric(
        "Expected Revenue",
        f"₹{estimated_next_7_days:,.0f}"
    )

    st.info(
        "This forecast is based on recent historical sales trends. "
        "Actual future sales may vary."
    )

    st.subheader("📈 Historical Sales Trend")

    fig_forecast = px.line(
        daily_sales,
        x="date",
        y="total_sales",
        markers=True,
        title="Historical Daily Revenue"
    )

    fig_forecast.update_layout(
        xaxis_title="Date",
        yaxis_title="Revenue (₹)"
    )

    st.plotly_chart(
        fig_forecast,
        use_container_width=True
    )

    # ---------------- FORECAST BUTTON ----------------

    if st.button("🤖 Generate AI Forecast"):

        forecast_data = product_summary.to_string(index=False)

        with st.spinner("🤖 Analyzing sales trends..."):

            interaction = client.interactions.create(
                model="gemini-3.6-flash",
                input=f"""
You are an AI Business Operations Copilot.

Analyze the following historical sales data:

{forecast_data}

Provide a concise business forecast.

Include:
1. Top performing product.
2. Products showing strong sales performance.
3. Expected sales trend.
4. Inventory recommendation.
5. One useful business recommendation.

Rules:
- Use only the provided data.
- Do not invent exact future revenue numbers.
- Clearly state that this is a trend-based forecast.
- Keep the answer under 200 words.
"""
            )

        st.success("🤖 AI Forecast Generated")

        st.write(interaction.output_text)