import pandas as pd
import streamlit as st
import json
from collections import Counter
import random


# Function to load keyword counts from a file
def load_keyword_counts():
    try:
        with open("keywords.json", "r") as f:
            data = json.load(f)  
            return Counter(data)  
    except (FileNotFoundError, json.JSONDecodeError): 
        return Counter()  

# Function to save keyword counts to a file
def save_keyword_counts(counter):
    with open("keywords.json", "w") as f:
        json.dump(counter, f)

# Hide Streamlit default headers and footers
hide_streamlit_style = """
    <style>
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Load the combined data with caching
@st.cache_data
def load_data(file_path):
    excel_data = pd.ExcelFile(file_path)
    return pd.concat([pd.read_excel(file_path, sheet_name=sheet) for sheet in excel_data.sheet_names], ignore_index=True)


# load data
file_path = '_checkpoint1203.xlsx'  # 每次更新记得替换
all_data = load_data(file_path)

# Convert BBD to date only
all_data['bbd'] = pd.to_datetime(all_data['bbd']).dt.date

# Format prices to 2 decimal places
all_data['price'] = all_data['price'].map(lambda x: f"{x:.2f}")
all_data['after_sale'] = all_data['after_sale'].map(lambda x: f"{x:.2f}")

# Load keyword counts at the start
keyword_counts = load_keyword_counts()

# Page title
st.title("Shilla Product Search DEMO")

# Show the top 10 most searched keywords at the top of the page
st.header("Top 10 Searched Keywords")
if keyword_counts:
    top_keywords = keyword_counts.most_common(10)
    for i, (keyword, count) in enumerate(top_keywords, start=1):
        st.write(f"{i}. {keyword}: {count} times")
else:
    st.write("No keywords searched yet.")

# Welcome message
st.title("Good Morning Ryota! Let's Find What You Need :)")
st.write("Welcome! Please use the search filters on the left to find products.")

# Sidebar for multi-condition filters
st.sidebar.header("Search Filters")

# Sidebar option to view supermarket layout
if st.sidebar.checkbox("Show Shelf Position"):
    st.header("Shilla Layout")
    st.image("shelf position.jpg", caption="Shilla Layout", use_column_width=True)

# Keyword search
search_query = st.sidebar.text_input("Search by Product Name or Keyword:")

# Brand filter
unique_brands = all_data['brand'].dropna().unique()
selected_brand = st.sidebar.selectbox("Filter by Brand:", options=["All"] + list(unique_brands))

# Price range filter
min_price, max_price = st.sidebar.slider(
    "Filter by Price Range:",
    min_value=float(all_data['price'].astype(float).min()),
    max_value=float(all_data['price'].astype(float).max()),
    value=(float(all_data['price'].astype(float).min()), float(all_data['price'].astype(float).max()))
)

# Discount filter
discount_only = st.sidebar.checkbox("Show Discounted Items Only")

# Shelf location filter
shelf_query = st.sidebar.text_input("Search by Shelf (e.g., a6):")

# Initialize filtered_data as the full dataset
filtered_data = all_data.copy()

# Apply filters only if search_query or any filter is set
if search_query or selected_brand != "All" or discount_only or shelf_query or (min_price != float(all_data['price'].astype(float).min()) or max_price != float(all_data['price'].astype(float).max())):
    # Update keyword counts and save to file
    if search_query:
        keyword_counts[search_query] += 1
        save_keyword_counts(keyword_counts)

    # Apply Search by Product Name or Keyword filter (if provided)
    if search_query:
        filtered_data = filtered_data[
            filtered_data['product_title'].str.contains(search_query, case=False, na=False) |
            filtered_data['brand'].str.contains(search_query, case=False, na=False)
        ]

    # Apply Brand filter
    if selected_brand != "All":
        filtered_data = filtered_data[filtered_data['brand'] == selected_brand]

    # Apply Price range filter
    filtered_data = filtered_data[
        (filtered_data['price'].astype(float) >= min_price) & (filtered_data['price'].astype(float) <= max_price)
    ]

    # Apply Discount filter
    if discount_only:
        filtered_data = filtered_data[filtered_data['Korting'].notna()]

    # Apply Shelf Location filter
    if shelf_query:
        filtered_data = filtered_data[
            filtered_data['Place'].str.contains(shelf_query, case=False, na=False)
        ]

    # Display filtered results
    st.header("Search Results")
    if not filtered_data.empty:
        for _, row in filtered_data.iterrows():
            st.image(row['image'], width=150)
            st.write(f"**Product Name:** {row['product_title']}")
            st.write(f"**Shelf Location:** {row.get('Place', 'N/A')}")
            st.write(f"**Brand:** {row['brand']}")
            st.write(f"**Price:** €{row['price']}")
            st.write(f"**After Sale Price:** €{row['after_sale']}")  
            st.write(f"**Discount Info:** {row['Korting']}")  
            st.write(f"**Best Before Date:** {row['bbd']}")
            st.write(f"[View Details]({row['link']})")
            st.write("---")
    else:
        st.write("No products found matching the selected filters.")
