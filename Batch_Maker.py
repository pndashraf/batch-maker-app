import streamlit as st
import pandas as pd
from datetime import datetime
import os

# ✅ Always use absolute app directory
APP_DIR = os.path.dirname(os.path.abspath(__file__))
SUPPLIER_FILE = os.path.join(APP_DIR, "suppliers.csv")
BATCH_FOLDER = os.path.join(APP_DIR, "batches")
os.makedirs(BATCH_FOLDER, exist_ok=True)

st.title("🗂️ Batch Maker")

# Load suppliers
if os.path.exists(SUPPLIER_FILE):
    suppliers = pd.read_csv(SUPPLIER_FILE)["Supplier"].tolist()
else:
    suppliers = []

# Add Supplier
st.subheader("Manage Suppliers")
new_supplier = st.text_input("Add New Supplier")
if st.button("Add Supplier") and new_supplier:
    if new_supplier not in suppliers:
        suppliers.append(new_supplier)
        pd.DataFrame({"Supplier": suppliers}).to_csv(SUPPLIER_FILE, index=False)
        st.success(f"Supplier '{new_supplier}' added.")
    else:
        st.warning("Supplier already exists.")

# Batch creation
farmer_name = st.selectbox("Select Supplier", suppliers)
selected_date = st.date_input("Select Date", datetime.today())

batch_file = os.path.join(BATCH_FOLDER, f"{farmer_name}.csv")

# Show exact file path for debugging
st.write(f"🔍 Batch file path: `{batch_file}`")

if os.path.exists(batch_file):
    df = pd.read_csv(batch_file)
else:
    df = pd.DataFrame(columns=["Farmer Name", "Date", "Load No", "FY Code", "Date Code", "Final Code"])

last_load_no = df["Load No"].max() if not df.empty else 0
next_load_no = int(last_load_no) + 1

load_no = st.number_input("Load No", value=next_load_no, min_value=1)

fy_code = int(f"{selected_date.year % 100}{(selected_date.year + 1) % 100}")
st.write(f"FY Code: {fy_code}")

date_code = selected_date.strftime("%d%m")
final_code = f"{farmer_name[:3].upper()}{fy_code}/{date_code}/{load_no}"

st.write(f"Date Code: {date_code}")
st.code(final_code)
st.text_input("Copy Final Code", value=final_code)

if st.button("Add to Batch"):
    if final_code in df["Final Code"].values:
        st.error("❌ Duplicate Final Code detected! Entry not allowed.")
    else:
        new_row = pd.DataFrame({
            "Farmer Name": [farmer_name],
            "Date": [selected_date],
            "Load No": [load_no],
            "FY Code": [fy_code],
            "Date Code": [date_code],
            "Final Code": [final_code]
        })
        df = pd.concat([df, new_row], ignore_index=True)
        df.to_csv(batch_file, index=False)
        st.success(f"✅ Batch entry added to {farmer_name}!")
    st.dataframe(df)

# View batches
st.subheader("📚 View Saved Batches")
selected_view_supplier = st.selectbox("Select Supplier to View Batches", suppliers, key="view")
view_file = os.path.join(BATCH_FOLDER, f"{selected_view_supplier}.csv")
if os.path.exists(view_file):
    view_df = pd.read_csv(view_file)
    st.dataframe(view_df)
else:
    st.info("No batches saved for this supplier yet.")
