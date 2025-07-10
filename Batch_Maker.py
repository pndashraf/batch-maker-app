import streamlit as st
import pandas as pd
from datetime import datetime
import os

st.title("🗂️ Batch Maker")

SUPPLIER_FILE = "suppliers.csv"
BATCH_FOLDER = "batches"
os.makedirs(BATCH_FOLDER, exist_ok=True)

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

# ✅ EDIT BATCH SECTION
st.subheader("✏️ Edit Saved Batch")

selected_edit_supplier = st.selectbox("Select Supplier to Edit Batches", suppliers, key="edit")
edit_file = os.path.join(BATCH_FOLDER, f"{selected_edit_supplier}.csv")
if os.path.exists(edit_file):
    edit_df = pd.read_csv(edit_file)

    if not edit_df.empty:
        edit_code = st.selectbox("Select Final Code to Edit", edit_df["Final Code"].tolist())
        row_to_edit = edit_df[edit_df["Final Code"] == edit_code].iloc[0]

        new_date = st.date_input("Edit Date", datetime.strptime(row_to_edit["Date"], "%Y-%m-%d"))
        new_load_no = st.number_input("Edit Load No", value=int(row_to_edit["Load No"]), min_value=1)

        new_fy_code = int(f"{new_date.year % 100}{(new_date.year + 1) % 100}")
        new_date_code = new_date.strftime("%d%m")
        new_final_code = f"{selected_edit_supplier[:3].upper()}{new_fy_code}/{new_date_code}/{new_load_no}"

        st.write(f"New FY Code: {new_fy_code}")
        st.write(f"New Date Code: {new_date_code}")
        st.code(new_final_code)

        if st.button("Update Batch"):
            if new_final_code != edit_code and new_final_code in edit_df["Final Code"].values:
                st.error("❌ Updated Final Code would duplicate an existing one!")
            else:
                edit_df.loc[edit_df["Final Code"] == edit_code, ["Date", "Load No", "FY Code", "Date Code", "Final Code"]] = [
                    new_date.strftime("%Y-%m-%d"), new_load_no, new_fy_code, new_date_code, new_final_code
                ]
                edit_df.to_csv(edit_file, index=False)
                st.success("✅ Batch updated successfully!")
                st.dataframe(edit_df)
    else:
        st.info("No batches to edit for this supplier.")
else:
    st.info("No batches to edit for this supplier.")
