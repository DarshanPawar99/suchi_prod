import streamlit as st
import pandas as pd

st.title("3M → Cromwell Category Matching by Cromwell Level")

uploaded_file = st.file_uploader("Upload your Excel file", type="xlsx")
if not uploaded_file:
    st.info("Awaiting Excel file upload…")
    st.stop()

# Load sheets
xl = pd.ExcelFile(uploaded_file)
if not {"cromwell", "3m_master_sheet"}.issubset(xl.sheet_names):
    st.error("Workbook must contain sheets named 'cromwell' and '3m_master_sheet'.")
    st.stop()

df_crom   = xl.parse("cromwell")
df_master = xl.parse("3m_master_sheet")

# Validate columns
if not {"cromwell_category", "cromwell_cat_level"}.issubset(df_crom.columns):
    st.error("Sheet 'cromwell' needs 'cromwell_category' & 'cromwell_cat_level'.")
    st.stop()
if "Product Category Tree" not in df_master.columns:
    st.error("Sheet '3m_master_sheet' needs 'Product Category Tree'.")
    st.stop()

# Normalize helper (case & space insensitive)
def normalize(txt: str) -> str:
    return "".join(txt.lower().split())

# Build lookup: normalized name → (original name, cromwell level)
crom_map = {
    normalize(name): (name, lvl)
    for name, lvl in zip(df_crom["cromwell_category"], df_crom["cromwell_cat_level"])
}

# Determine how many cromwell levels we want to show.
# If you know max level is 4, set max_level = 4; otherwise:
max_level = int(df_crom["cromwell_cat_level"].max())

# Build results
rows = []
for tree in df_master["Product Category Tree"].fillna(""):
    parts = [p.strip() for p in tree.split(",") if p.strip()]
    # initialize with no match
    row = {"Product Category Tree": tree}
    for lvl in range(1, max_level + 1):
        row[f"Category Level {lvl}"] = "no match"
    # try each part
    for part in parts:
        key = normalize(part)
        if key in crom_map:
            orig_name, lvl = crom_map[key]
            # place in the column for that cromwell level
            row[f"Category Level {lvl}"] = orig_name
    rows.append(row)

result_df = pd.DataFrame(rows)

st.subheader("Matching by Cromwell Levels")
st.dataframe(result_df)
