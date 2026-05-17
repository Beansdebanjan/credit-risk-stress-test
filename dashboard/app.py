import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

st.set_page_config(layout="wide", page_title="Credit Risk Dashboard")
st.title("Credit Risk Stress Testing Dashboard")

try:
    df = pd.read_parquet('outputs/dashboard_data.parquet')
except FileNotFoundError:
    st.error("Data not found. Please run the stress testing pipeline first.")
    st.stop()

# KPIs
st.subheader("Key Portfolio Metrics")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Customers", f"{len(df):,}")
col2.metric("Mean Stress Score", f"{df['StressScore'].mean():.1f}")
col3.metric("High Stress Level %", f"{(df['StressLevel'] == 'High').mean() * 100:.1f}%")
col4.metric("Default Risk %", f"{(df['Default_Risk'] == 'Yes').mean() * 100:.1f}%")

col5, col6, col7, col8 = st.columns(4)
avg_base_savings = df['Monthly_Savings'].mean()
avg_stressed_savings = df['StressedMonthlySavings'].mean()
savings_diff = avg_stressed_savings - avg_base_savings

col5.metric("Avg Stressed Savings", f"₹{avg_stressed_savings:,.0f}", f"₹{savings_diff:,.0f}")
col6.metric("Avg Stressed Utilization", f"{df['StressedCreditUtilization'].mean():.1f}%", f"+{df['StressedCreditUtilization'].mean() - df['Credit_Utilization_%'].mean():.1f}%")
col7.metric("Avg Stressed DTI", f"{df['StressedDTI'].mean():.1f}%")
col8.metric("Negative Savings %", f"{(df['StressedMonthlySavings'] <= 0).mean() * 100:.1f}%")

st.divider()

st.subheader("Visualizations")
# Row 1: Stress Level Dist and Stress Score Hist
c1, c2 = st.columns(2)
with c1:
    fig1 = px.pie(df, names='StressLevel', title='Distribution of Stress Levels', color='StressLevel',
                  color_discrete_map={'Low': 'green', 'Medium': 'orange', 'High': 'red'})
    st.plotly_chart(fig1, use_container_width=True)

with c2:
    fig2 = px.histogram(df, x='StressScore', nbins=50, title='Distribution of Stress Scores')
    st.plotly_chart(fig2, use_container_width=True)

# Row 2: Age Variations & Income Barrier
c3, c4 = st.columns(2)

# Prepare Age Group data
conditions = [
    (df['Age'] < 30),
    (df['Age'] >= 30) & (df['Age'] <= 40),
    (df['Age'] > 40) & (df['Age'] <= 50),
    (df['Age'] > 50)
]
choices = ['<30', '30-40', '40-50', '>50']
df['Age_Group'] = np.select(conditions, choices, default='>50')

age_util = df.groupby('Age_Group')[['Credit_Utilization_%', 'StressedCreditUtilization']].mean().reset_index()

with c3:
    fig3 = go.Figure()
    fig3.add_trace(go.Bar(x=age_util['Age_Group'], y=age_util['Credit_Utilization_%'], name='Baseline Utilization'))
    fig3.add_trace(go.Bar(x=age_util['Age_Group'], y=age_util['StressedCreditUtilization'], name='Stressed Utilization'))
    fig3.update_layout(title='Credit Utilization Shift by Age Group', barmode='group', yaxis_title='Utilization %')
    st.plotly_chart(fig3, use_container_width=True)

# Prepare Income Group data
inc_cond = [
    (df['Monthly_Income'] < 60000),
    (df['Monthly_Income'] >= 60000) & (df['Monthly_Income'] <= 100000),
    (df['Monthly_Income'] > 100000)
]
inc_choices = ['<60k', '60k-100k', '>100k']
df['Income_Bracket'] = np.select(inc_cond, inc_choices, default='>100k')

df['Is_Default'] = (df['Default_Risk'] == 'Yes').astype(int)
inc_def = df.groupby('Income_Bracket')['Is_Default'].mean().reset_index()
inc_def['Is_Default'] *= 100  # Convert to percentage

with c4:
    fig4 = px.bar(inc_def, x='Income_Bracket', y='Is_Default', title='Default Risk % by Income Bracket', text_auto='.1f', labels={'Is_Default': 'Default Risk (%)'})
    fig4.update_traces(textposition='outside')
    st.plotly_chart(fig4, use_container_width=True)

st.divider()

st.subheader("Top Riskiest Customers")
top_customers = df.sort_values(by='StressScore', ascending=False).head(20)
st.dataframe(top_customers[['Customer_ID', 'Age', 'Monthly_Income', 'StressScore', 'StressLevel', 'Default_Risk', 'StressedMonthlySavings', 'StressedDTI', 'StressedCreditUtilization']], use_container_width=True)

st.download_button("Download Full Stressed Data", data=df.to_csv(index=False).encode('utf-8'), file_name="stressed_full.csv", mime="text/csv")
try:
    memos = pd.read_csv('outputs/top20_memos.csv')
    st.download_button("Download Top 20 Memos", data=memos.to_csv(index=False).encode('utf-8'), file_name="top20_memos.csv", mime="text/csv")
except:
    pass
