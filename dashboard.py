import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from datetime import datetime

st.set_page_config(page_title="Power BI Dashboard", layout="wide")

st.title("📊 Interactive Power BI Dashboard")
st.markdown("---")

# File upload
uploaded_file = st.file_uploader("📁 Upload Excel file", type=["xlsx", "xls"])

if uploaded_file is not None:
    # Load data
    @st.cache_data
    def load_excel(file):
        return pd.read_excel(file)
    
    df = load_excel(uploaded_file)
    
    st.success(f"✅ Loaded **{len(df)} rows** | **{len(df.columns)} columns**")
    
    # Data preview
    col1, col2 = st.columns([3,1])
    with col1:
        st.subheader("📋 Data Preview")
        st.dataframe(df.head(10), use_container_width=True)
    
    with col2:
        st.subheader("📈 Summary")
        st.metric("Total Records", len(df))
        st.metric("Avg Value", f"${df.select_dtypes(include=[np.number]).mean().mean():.0f}")
    
    # Filters
    st.subheader("🔧 Real-time Filters")
    col1, col2 = st.columns(2)
    
    with col1:
        # Category filter
        cat_cols = df.select_dtypes(include=['object']).columns
        if len(cat_cols) > 0:
            selected_cat = st.multiselect(
                f"Filter {cat_cols[0]}",
                options=df[cat_cols[0]].dropna().unique()
            )
            if selected_cat:
                df_filtered = df[df[cat_cols[0]].isin(selected_cat)]
            else:
                df_filtered = df
        else:
            df_filtered = df
    
    with col2:
        # Numeric filter
        num_cols = df.select_dtypes(include=[np.number]).columns
        if len(num_cols) > 0:
            num_col = num_cols[0]
            min_val, max_val = st.slider(
                f"{num_col} Range",
                float(df[num_col].min()),
                float(df[num_col].max()),
                (float(df[num_col].min()), float(df[num_col].max()))
            )
            df_filtered = df_filtered[(df_filtered[num_col] >= min_val) & (df_filtered[num_col] <= max_val)]
        else:
            df_filtered = df_filtered
    
    # Charts
    st.subheader("📊 Auto-Generated Charts")
    
    # Get columns for charts
    num_cols = df_filtered.select_dtypes(include=[np.number]).columns.tolist()
    cat_cols = df_filtered.select_dtypes(include=['object']).columns.tolist()
    
    if len(num_cols) > 0 and len(cat_cols) > 0:
        # Row 1: Bar + Pie
        col1, col2 = st.columns(2)
        
        with col1:
            fig_bar = px.bar(df_filtered, x=cat_cols[0], y=num_cols[0],
                           title="📈 Bar Chart")
            st.plotly_chart(fig_bar, use_container_width=True)
        
        with col2:
            fig_pie = px.pie(df_filtered, values=num_cols[0], names=cat_cols[0],
                           title="🥧 Pie Chart")
            st.plotly_chart(fig_pie, use_container_width=True)
        
        # Row 2: Line + Scatter
        col1, col2 = st.columns(2)
        
        with col1:
            if len(num_cols) >= 2:
                fig_line = px.line(df_filtered, x=cat_cols[0], y=num_cols[:2].tolist(),
                                 title="📉 Trend Line")
                st.plotly_chart(fig_line, use_container_width=True)
        
        with col2:
            if len(num_cols) >= 2:
                fig_scatter = px.scatter(df_filtered, x=num_cols[0], y=num_cols[1],
                                       color=cat_cols[0] if len(cat_cols)>0 else None,
                                       title="🔍 Scatter Plot")
                st.plotly_chart(fig_scatter, use_container_width=True)
    
    # Download filtered data
    csv = df_filtered.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Filtered Data",
        data=csv,
        file_name=f"dashboard_data_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
        mime='text/csv'
    )

else:
    st.info("""
    ### 🚀 **How to use:**
    1. **Upload Excel file** (.xlsx or .xls)
    2. **Apply filters** (real-time)
    3. **View auto-charts**
    4. **Download results**
    
    **💡 Sample columns:** Date, Category, Revenue, Quantity
    """)