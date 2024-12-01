import pandas as pd
import streamlit as st
from collections import Counter

# Hide Streamlit default headers and footers
hide_streamlit_style = """
    <style>
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Load the combined data
file_path = '_checkpoint1130.xlsx'  # 替换为 Excel 文件路径
excel_data = pd.ExcelFile(file_path)
all_data = pd.concat([pd.read_excel(file_path, sheet_name=sheet) for sheet in excel_data.sheet_names], ignore_index=True)

# Convert BBD to date only
all_data['bbd'] = pd.to_datetime(all_data['bbd']).dt.date

# Initialize a Counter to track search keyword counts
if "keyword_counts" not in st.session_state:
    st.session_state["keyword_counts"] = Counter()

# Page title
st.title("Supermarket Product Search Tool")

# Sidebar for multi-condition filters
st.sidebar.header("Search Filters")

# Keyword search
search_query = st.sidebar.text_input("Search by Product Name or Keyword:")

# Brand filter
unique_brands = all_data['brand'].dropna().unique()
selected_brand = st.sidebar.selectbox("Filter by Brand:", options=["All"] + list(unique_brands))

# Price range filter
min_price, max_price = st.sidebar.slider(
    "Filter by Price Range:",
    min_value=float(all_data['price'].min()),
    max_value=float(all_data['price'].max()),
    value=(float(all_data['price'].min()), float(all_data['price'].max()))
)

# Discount filter
discount_only = st.sidebar.checkbox("Show Discounted Items Only")

# Apply filters to the dataset
filtered_data = all_data.copy()

if search_query:
    # Record the search query in the Counter
    st.session_state["keyword_counts"][search_query] += 1

    # Apply search query filter
    filtered_data = filtered_data[
        filtered_data['product_title'].str.contains(search_query, case=False, na=False) |
        filtered_data['brand'].str.contains(search_query, case=False, na=False)
    ]

if selected_brand != "All":
    filtered_data = filtered_data[filtered_data['brand'] == selected_brand]

filtered_data = filtered_data[(filtered_data['price'] >= min_price) & (filtered_data['price'] <= max_price)]

if discount_only:
    filtered_data = filtered_data[filtered_data['Korting'].notna()]

# Display results
st.header("Search Results")
if not filtered_data.empty:
    for _, row in filtered_data.iterrows():
        st.image(row['image'], width=150)
        st.write(f"**Product Name:** {row['product_title']}")
        st.write(f"**Brand:** {row['brand']}")
        st.write(f"**Price:** €{row['price']}")
        st.write(f"**After Sale Price:** €{row['after_sale']}")
        st.write(f"**Discount Info:** {row['Korting']}")
        st.write(f"**Best Before Date:** {row['bbd']}")
        st.write(f"[View Details]({row['link']})")
        st.write("---")
else:
    st.write("No products found matching the selected filters.")

# Show the top 10 most searched keywords
st.header("Top 10 Searched Keywords")
if st.session_state["keyword_counts"]:
    top_keywords = st.session_state["keyword_counts"].most_common(10)
    for i, (keyword, count) in enumerate(top_keywords, start=1):
        st.write(f"{i}. {keyword}: {count} times")
else:
    st.write("No keywords searched yet.")
