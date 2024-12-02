import pandas as pd
import streamlit as st
import json
from collections import Counter

# Function to load keyword counts from a file
def load_keyword_counts():
    try:
        with open("keywords.json", "r") as f:
            data = json.load(f)  # 尝试读取 JSON 数据
            return Counter(data)  # 转换为 Counter 对象
    except (FileNotFoundError, json.JSONDecodeError):  # 文件不存在或 JSON 无效
        return Counter()  # 返回一个空的 Counter 对象

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

# Load the combined data
file_path = '_checkpoint1130.xlsx'  # 替换为您的 Excel 文件路径
excel_data = pd.ExcelFile(file_path)
all_data = pd.concat([pd.read_excel(file_path, sheet_name=sheet) for sheet in excel_data.sheet_names], ignore_index=True)

# Convert BBD to date only
all_data['bbd'] = pd.to_datetime(all_data['bbd']).dt.date

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
    # Update keyword counts and save to file
    keyword_counts[search_query] += 1
    save_keyword_counts(keyword_counts)

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

# Display results or welcome message
if search_query:
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
else:
    # Show welcome message if no search query
    st.title("Good Morning Ryota! Let's Find What You Need :)")
    st.write("Welcome! Please use the search filters on the left to find products.")
