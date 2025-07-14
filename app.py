# app.py

import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
import os

# --- Page Configuration ---
st.set_page_config(
    page_title="Airbnb Dashboard",
    layout="wide",
    page_icon="🏡"
)

# --- Custom CSS Styling ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    h1 {
        font-size: 40px;
        color: #2C3E50;
    }
    .stMetric {
        background-color: #f5f7fa;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# --- Load Data ---
@st.cache_data
def load_data():
    return pd.read_csv("cleaned_listings.csv")

df = load_data()

# --- Header with Branding ---
col_logo, col_title = st.columns([1, 5])
with col_title:
    st.markdown("## 🏡 Airbnb Seattle - Interactive Dashboard")
    st.caption("Analyze listings, explore prices, and discover hidden patterns in Airbnb data.")

st.markdown("---")

# --- Sidebar Filters ---
st.sidebar.header("🎛️ Filter Listings")
neighborhoods = st.sidebar.multiselect("Neighborhood", sorted(df['neighbourhood_cleansed'].unique()))
room_types = st.sidebar.multiselect("Room Type", sorted(df['room_type'].unique()))
min_price, max_price = st.sidebar.slider("Price Range ($)", 0, int(df['price'].max()), (50, 500))
superhost_filter = st.sidebar.checkbox("Only Superhosts")

filtered_df = df.copy()
if neighborhoods:
    filtered_df = filtered_df[filtered_df['neighbourhood_cleansed'].isin(neighborhoods)]
if room_types:
    filtered_df = filtered_df[filtered_df['room_type'].isin(room_types)]
filtered_df = filtered_df[(filtered_df['price'] >= min_price) & (filtered_df['price'] <= max_price)]
if superhost_filter:
    filtered_df = filtered_df[filtered_df['host_is_superhost'] == True]

# --- Export Filtered CSV ---
st.sidebar.markdown("📥 Export Data")
csv = filtered_df.to_csv(index=False).encode('utf-8')
st.sidebar.download_button("Download CSV", csv, "filtered_listings.csv", "text/csv")

# --- KPI Cards ---
st.markdown("### 📊 Summary Metrics")
col1, col2, col3 = st.columns(3)
col1.metric("Listings", f"{len(filtered_df):,}")
col2.metric("Avg. Price", f"${filtered_df['price'].mean():.2f}")
col3.metric("Avg. Rating", f"{filtered_df['review_score_avg'].mean():.2f}")

st.markdown("---")

# --- Visuals ---

# 1. Avg Price by Neighborhood (Line Chart)
st.subheader("📈 Avg Price by Neighborhood")
top_neigh = filtered_df.groupby("neighbourhood_cleansed")["price"].mean().sort_values(ascending=False).head(10)
fig1 = px.line(x=top_neigh.index, y=top_neigh.values, markers=True,
               labels={"x": "Neighborhood", "y": "Avg Price ($)"})
fig1.update_traces(line_color="crimson", hovertemplate="%{x}<br>$%{y:.2f}")
st.plotly_chart(fig1, use_container_width=True)

# 2. Room Type Distribution (Pie)
st.subheader("🛏️ Room Type Distribution")
fig2 = px.pie(filtered_df, names="room_type", hole=0.3, title=None)
fig2.update_traces(textinfo="percent+label", pull=[0.05]*len(filtered_df["room_type"].unique()))
st.plotly_chart(fig2, use_container_width=True)

# 3. Price vs Review Score (Scatter)
st.subheader("⭐ Price vs Review Score")
fig3 = px.scatter(filtered_df, x="review_score_avg", y="price", color="room_type",
                  hover_data=["name", "neighbourhood_cleansed"], opacity=0.5)
st.plotly_chart(fig3, use_container_width=True)

# 4. Availability by Neighborhood (Area Chart)
st.subheader("📆 Availability by Neighborhood")
top_avail = filtered_df.groupby('neighbourhood_cleansed')['availability_365'].mean().sort_values(ascending=False).head(10)
fig4 = px.area(x=top_avail.index, y=top_avail.values, labels={"x": "Neighborhood", "y": "Avg Days Available"},
               color_discrete_sequence=["skyblue"])
fig4.update_traces(hovertemplate="%{x}: %{y} days")
st.plotly_chart(fig4, use_container_width=True)

# 5. Price by Cancellation Policy (Violin Plot)
st.subheader("🎻 Price by Cancellation Policy")
fig5 = px.violin(filtered_df, x="cancellation_policy", y="price", box=True, points="all",
                 color="cancellation_policy", color_discrete_sequence=px.colors.qualitative.Set2)
st.plotly_chart(fig5, use_container_width=True)

# 6. Avg Reviews per Month by Room Type (Line Chart)
st.subheader("📈 Avg Reviews per Month by Room Type")
avg_reviews = filtered_df.groupby('room_type')['reviews_per_month'].mean().sort_values()
fig = px.line(x=avg_reviews.index, y=avg_reviews.values, markers=True,
              labels={"x": "Room Type", "y": "Avg Reviews/Month"}, color_discrete_sequence=["teal"])
fig.update_traces(hovertemplate="%{x}: %{y:.2f} reviews/month")
st.plotly_chart(fig, use_container_width=True)

# --- Footer ---
st.markdown("---")
st.caption("📍 Data: Airbnb Seattle – Built with ❤️ using Streamlit · Designed by Anuj Mangukiya")