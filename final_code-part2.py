import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Used Car Price Dashboard", layout="wide")

# Load data

@st.cache_data  # cache so it doesn't reload on every interaction
def load_data():
    return pd.read_excel("used_car_price_dataset_extended.xlsx", engine="openpyxl")

df = load_data()

# Title & description

st.title("Used Car Price Explorer")
st.write(
    """
    This interactive dashboard uses a dataset of used cars. 
    Use the filters in the sidebar to explore how price varies by brand, 
    model year, mileage, fuel type, transmission, and more. 
    All charts and the data table update automatically as you change the filters.
    """
)

# Sidebar filters

st.sidebar.header("Filters")

# Year range slider
year_min = int(df["make_year"].min())
year_max = int(df["make_year"].max())
year_range = st.sidebar.slider(
    "Model year range",
    min_value=year_min,
    max_value=year_max,
    value=(year_min, year_max),
    step=1,
)

# Brand multiselect
brand_options = sorted(df["brand"].dropna().unique())
selected_brands = st.sidebar.multiselect(
    "Brand",
    options=brand_options,
    default=brand_options,
)

# Fuel type dropdown (selectbox)
fuel_options = ["All"] + sorted(df["fuel_type"].dropna().unique())
selected_fuel = st.sidebar.selectbox("Fuel type", options=fuel_options)

# Transmission multiselect
trans_options = sorted(df["transmission"].dropna().unique())
selected_trans = st.sidebar.multiselect(
    "Transmission",
    options=trans_options,
    default=trans_options,
)

# Price slider
price_min = float(df["price_usd"].min())
price_max = float(df["price_usd"].max())
price_range = st.sidebar.slider(
    "Price range (USD)",
    min_value=float(round(price_min, 2)),
    max_value=float(round(price_max, 2)),
    value=(float(round(price_min, 2)), float(round(price_max, 2))),
)

# Max owners slider
owner_max = int(df["owner_count"].max())
max_owners = st.sidebar.slider(
    "Maximum number of previous owners",
    min_value=1,
    max_value=owner_max,
    value=owner_max,
)

# Service history dropdown
service_options = ["All"] + sorted(df["service_history"].dropna().unique())
service_choice = st.sidebar.selectbox("Service history", options=service_options)

# Apply filters

mask = (
    df["make_year"].between(year_range[0], year_range[1])
    & df["brand"].isin(selected_brands)
    & df["transmission"].isin(selected_trans)
    & df["price_usd"].between(price_range[0], price_range[1])
    & (df["owner_count"] <= max_owners)
)

if selected_fuel != "All":
    mask = mask & (df["fuel_type"] == selected_fuel)

if service_choice != "All":
    mask = mask & (df["service_history"] == service_choice)

filtered_df = df[mask]

if filtered_df.empty:
    st.warning("No cars match the current filter selection. Try relaxing some filters.")
    st.stop()

# Metrics section

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Number of cars", f"{len(filtered_df):,}")
with col2:
    st.metric("Average price (USD)", f"${filtered_df['price_usd'].mean():,.0f}")
with col3:
    st.metric("Average mileage (km per liter)", f"{filtered_df['mileage_kmpl'].mean():.1f}")

# Chart 1: Price vs. Mileage

st.subheader("Price vs. Mileage (colored by fuel type)")
fig_scatter = px.scatter(
    filtered_df,
    x="mileage_kmpl",
    y="price_usd",
    color="fuel_type",
    hover_data=["brand", "make_year", "engine_cc", "owner_count"],
    labels={
        "mileage_kmpl": "Mileage (km per liter)",
        "price_usd": "Price (USD)",
        "fuel_type": "Fuel type",
    },
)
fig_scatter.update_traces(marker=dict(size=6, opacity=0.7))
st.plotly_chart(fig_scatter, use_container_width=True)

# Chart 2: Average Price by Brand

st.subheader("Average Price by Brand (Filtered)")
avg_price_by_brand = (
    filtered_df.groupby("brand")["price_usd"]
    .mean()
    .sort_values(ascending=False)
    .reset_index()
)
fig_bar = px.bar(
    avg_price_by_brand.head(15),
    x="brand",
    y="price_usd",
    labels={"brand": "Brand", "price_usd": "Average price (USD)"},
)
st.plotly_chart(fig_bar, use_container_width=True)

# Chart 3: Average Price by Model Year

st.subheader("Average Price by Model Year (Filtered)")
avg_price_by_year = (
    filtered_df.groupby("make_year")["price_usd"]
    .mean()
    .reset_index()
    .sort_values("make_year")
)
fig_line = px.line(
    avg_price_by_year,
    x="make_year",
    y="price_usd",
    labels={"make_year": "Model year", "price_usd": "Average price (USD)"},
)
st.plotly_chart(fig_line, use_container_width=True)

# Data table

st.subheader("Filtered Data (first 100 rows)")
st.dataframe(filtered_df.head(100))
