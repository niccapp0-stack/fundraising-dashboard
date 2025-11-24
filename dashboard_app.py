import streamlit as st
import pandas as pd
import numpy as np

# Australian benchmark values for attrition rates
AU_BENCHMARKS = {
    "New": 72,
    "General": 32,
    "Regular": 18,
    "Middle": 12,
    "Major": 10
}

st.set_page_config(page_title="Fundraising Dashboard", layout="wide")
st.title("Fundraising Dashboard (Starter Version)")

st.sidebar.header("Step 1: Upload Your Donor CSV")
uploaded_file = st.sidebar.file_uploader("Select a CSV file...", type="csv")

# Example template
if st.sidebar.button("Download CSV Template"):
    template_df = pd.DataFrame({
        "donor_id":["D0001"],
        "donor_name":["Fake Donor Example"],
        "segment":["Middle"],
        "gift_2023":[220],
        "gift_2024":[230],
        "gift_2025":[255]
    })
    template_df.to_csv("donor_template.csv", index=False)
    st.sidebar.success("Template downloaded (donor_template.csv).")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.success("Donor data loaded!")
    st.write(df.head())

    segs = ["New", "General", "Regular", "Middle", "Major"]
    segStats = {}
    for s in segs:
        sub = df[df["segment"]==s]
        n = len(sub)
        gifts_2023 = sub["gift_2023"].sum()
        gifts_2024 = sub["gift_2024"].sum()
        retained = sub[(sub["gift_2023"]>0) & (sub["gift_2024"]>0)]
        lapsed = sub[(sub["gift_2023"]>0) & (sub["gift_2024"]==0)]
        attr_rate = round(len(lapsed)/(len(retained)+len(lapsed)+1e-9)*100) if n > 0 else 0
        avg_value_change = round((retained["gift_2024"]-retained["gift_2023"]).mean()) if len(retained)>0 else 0
        segStats[s] = {
            "Count": n,
            "Attrition": attr_rate,
            "Benchmark": AU_BENCHMARKS[s],
            "Avg_Value_Change": avg_value_change,
        }

    st.markdown("### Segment Metrics & Benchmarks")
    metrics_tbl = pd.DataFrame(segStats).T
    metrics_tbl = metrics_tbl[["Count", "Attrition", "Benchmark", "Avg_Value_Change"]]
    st.dataframe(metrics_tbl)

    st.markdown("### Donor List (Log Actions)")
    action_col, table_col = st.columns([1,5])
    with table_col:
        act_log = []
        for idx, row in df.iterrows():
            action = st.text_input(f"Log Action for {row['donor_name']}", key=f"act{idx}")
            act_log.append(action)
        df["action_log"] = act_log
        st.write(df)

    st.markdown("### Value Lost To Attrition (Chart)")
    value_lost = 0
    for s in segs:
        sub = df[df["segment"]==s]
        lapsed = sub[(sub["gift_2023"]>0) & (sub["gift_2024"]==0)]
        lost = lapsed["gift_2023"].sum()
        value_lost += lost
    st.metric(label="Total Value Lost to Attrition", value=f"${value_lost}")
    st.bar_chart(df.groupby("segment")["gift_2023"].sum() - df.groupby("segment")["gift_2024"].sum())

    if st.button("Export Donor List (CSV)"):
        csvout = df.to_csv(index=False).encode()
        st.download_button("Download Log Data", csvout, "donor_dashboard_logs.csv", "text/csv")

else:
    st.info("Use the sidebar to upload your donor CSV file.")
    st.markdown("""
    **Required columns:**  
    - donor_id  
    - donor_name  
    - segment (New/General/Regular/Middle/Major)  
    - gift_2023  
    - gift_2024  
    - gift_2025
    """)
