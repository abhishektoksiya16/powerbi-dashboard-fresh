import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime

st.set_page_config(page_title="Power BI Dashboard", layout="wide", page_icon="📊")

st.title("📊 **Universal Power BI Dashboard**")
st.markdown("**Works with ANY Excel columns automatically!**")

# File upload
uploaded_file = st.file_uploader("📁 Upload Excel", type=["xlsx", "xls"])

if uploaded_file is not None:
    try:
        df = pd.read_excel(uploaded_file)
        st.success(f"✅ Loaded **{len(df)} rows x {len(df.columns)} columns**")
        
        # Show all columns
        st.subheader("📋 **Your Data**")
        st.dataframe(df.head(10), use_container_width=True)
        
        # Column analysis
        st.subheader("🔍 **Column Types Detected**")
        col1, col2 = st.columns(2)
        with col1:
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            st.metric("📊 Numeric Columns", len(numeric_cols))
            if numeric_cols:
                st.write(numeric_cols)
        with col2:
            text_cols = df.select_dtypes(include=['object']).columns.tolist()
            st.metric("🏷️ Text Columns", len(text_cols))
            if text_cols:
                st.write(text_cols)
        
        # Filters - Dynamic based on YOUR columns
        st.subheader("🔧 **Real-time Filters**")
        filtered_df = df.copy()
        
        # Filter 1: First text column
        text_cols = df.select_dtypes(include=['object']).columns
        if len(text_cols) > 0:
            col1, col2 = st.columns(2)
            with col1:
                selected = st.multiselect(
                    f"Filter {text_cols[0]}",
                    options=sorted(df[text_cols[0]].dropna().unique()),
                    default=sorted(df[text_cols[0]].dropna().unique())
                )
                if selected:
                    filtered_df = filtered_df[filtered_df[text_cols[0]].isin(selected)]
        
        # Filter 2: First numeric column
        num_cols = df.select_dtypes(include=[np.number]).columns
        if len(num_cols) > 0:
            with col2:
                col_range = st.slider(
                    f"{num_cols[0]} Range",
                    float(df[num_cols[0]].min()),
                    float(df[num_cols[0]].max()),
                    (float(df[num_cols[0]].min()), float(df[num_cols[0]].max()))
                )
                filtered_df = filtered_df[
                    (filtered_df[num_cols[0]] >= col_range[0]) & 
                    (filtered_df[num_cols[0]] <= col_range[1])
                ]
        
        st.success(f"✅ Filtered to **{len(filtered_df)} rows**")
        
        # CHARTS - Guaranteed to work with ANY data
        st.subheader("📈 **Charts (Click to Interact)**")
        
        # Chart 1: Always works - Top categories/values
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**📊 Bar Chart**")
            if len(num_cols) > 0 and len(text_cols) > 0:
                top_data = filtered_df.groupby(text_cols[0])[num_cols[0]].sum().reset_index().head(10)
                fig_bar = px.bar(top_data, x=text_cols[0], y=num_cols[0], 
                               title=f"Top {text_cols[0]} by {num_cols[0]}")
                st.plotly_chart(fig_bar, use_container_width=True)
            else:
                st.info("Add numeric + text columns for bar chart")
        
        with col2:
            st.markdown("**🥧 Pie Chart**")
            if len(num_cols) > 0 and len(text_cols) > 0:
                pie_data = filtered_df.groupby(text_cols[0])[num_cols[0]].sum().reset_index().head(10)
                fig_pie = px.pie(pie_data, values=num_cols[0], names=text_cols[0],
                               title=f"{text_cols[0]} Distribution")
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.info("Add numeric + text columns for pie chart")
        
        with col3:
            st.markdown("**📉 Summary Stats**")
            if len(num_cols) > 0:
                fig_stats = go.Figure()
                fig_stats.add_trace(go.Indicator(
                    mode="number+gauge+delta",
                    value=filtered_df[num_cols[0]].sum(),
                    title={"text": f"Total {num_cols[0]}"},
                    gauge={
                        'axis': {'range': [None, filtered_df[num_cols[0]].max()*1.5]},
                        'bar': {'color': "darkblue"},
                    }
                ))
                st.plotly_chart(fig_stats, use_container_width=True)
            else:
                st.info("Add numeric columns")
        
        # More charts
        if len(num_cols) >= 2:
            st.markdown("**🔍 Advanced Charts**")
            col1, col2 = st.columns(2)
            
            with col1:
                fig_scatter = px.scatter(filtered_df, 
                                       x=num_cols[0], y=num_cols[1],
                                       color=text_cols[0] if len(text_cols)>0 else None,
                                       title=f"{num_cols[0]} vs {num_cols[1]}")
                st.plotly_chart(fig_scatter, use_container_width=True)
            
            with col2:
                fig_histogram = px.histogram(filtered_df, x=num_cols[0],
                                           title=f"{num_cols[0]} Distribution")
                st.plotly_chart(fig_histogram, use_container_width=True)
        
        # Table of filtered data
        st.subheader("📋 **Filtered Data**")
        st.dataframe(filtered_df, use_container_width=True)
        
        # Download
        csv = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            "📥 Download Filtered CSV",
            csv,
            f"filtered_data_{datetime.now().strftime('%Y%m%d')}.csv",
            "text/csv"
        )
        
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        st.info("💡 Upload a simple Excel with numbers and text columns")

else:
    st.info("""
    **📁 Upload ANY Excel file - Charts auto-generate!**
    
    **Works with columns like:**
    ```
    Product | Sales | Quantity | Region | Date
    Laptop  | 1000  | 10       | North  | 2024-01
    ```
    """)
    st.balloons()
