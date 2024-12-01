import pandas as pd
import streamlit as st

# Load the combined data
file_path = '_checkpoint1130.xlsx'  # 请将此处替换为Excel文件的名称
excel_data = pd.ExcelFile(file_path)
all_data = pd.concat([pd.read_excel(file_path, sheet_name=sheet) for sheet in excel_data.sheet_names], ignore_index=True)

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

# Apply search query filter
if search_query:
    filtered_data = filtered_data[
        filtered_data['product_title'].str.contains(search_query, case=False, na=False) |
        filtered_data['brand'].str.contains(search_query, case=False, na=False)
    ]

# Apply brand filter
if selected_brand != "All":
    filtered_data = filtered_data[filtered_data['brand'] == selected_brand]

# Apply price range filter
filtered_data = filtered_data[(filtered_data['price'] >= min_price) & (filtered_data['price'] <= max_price)]

# Apply discount filter
if discount_only:
    filtered_data = filtered_data[filtered_data['Korting'].notna()]

# Display results
st.header("Search Results")
if not filtered_data.empty:
    for _, row in filtered_data.iterrows():
        st.image(row['image'], width=150)
        st.write(f"**Product Name:** {row['product_title']}")
        st.write(f"**Brand:** {row['brand']}")
        st.write(f"**Price:** ${row['price']}")
        st.write(f"**After Sale Price:** ${row['after_sale']}")
        st.write(f"**Discount Info:** {row['Korting']}")
        st.write(f"**Best Before Date:** {row['bbd']}")
        st.write(f"[View Details]({row['link']})")
        st.write("---")
else:
    st.write("No products found matching the selected filters.")
