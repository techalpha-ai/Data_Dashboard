import streamlit as st
import plotly.express as px
import pandas as pd
import os
import warnings
warnings.filterwarnings("ignore")

st.set_page_config(page_title="Dashboard", page_icon=":bar_chart:", layout="wide")
st.title(" :bar_chart: Dashboard")
f1=st.file_uploader(":file_upload: Upload your file", type=["csv","txt","xlsx","xls"])
if f1 is not None:
    filename = f1.name
    st.write(f"File uploaded: {filename}")
    df=pd.read_excel(filename)
else:
    os.chdir(r"C:\Users\visha\OneDrive\Desktop\streamlit_dashboard")
    df=pd.read_excel("Sample - Superstore.xls",engine="calamine")
col1,col2=st.columns(2)
df["Order Date"]=pd.to_datetime(df["Order Date"])
#setting the max and min date 
start_date=pd.to_datetime(df["Order Date"].min())
end_date=pd.to_datetime(df["Order Date"].max())
with col1:
    date1=pd.to_datetime(st.date_input("Start Date",start_date))
with col2:
    date2=pd.to_datetime(st.date_input("End Date",end_date))
df=df[(df["Order Date"]>=date1) & (df["Order Date"]<=date2)].copy()

st.sidebar.header("Filter Here:")
#create `a multiselect for region`
region=st.sidebar.multiselect("Select Region:",options=df["Region"].unique(),default=df["Region"].unique())
if not region:
    df2=df.copy()
else:
    df2=df[df["Region"].isin(region)].copy()

#create for state
state=st.sidebar.multiselect("Select State:",options=df2["State"].unique(),default=df2["State"].unique())
if not state:
    df3=df2.copy()
else:
    df3=df2[df2["State"].isin(state)].copy() 
#create for city
city=st.sidebar.multiselect("Select City:",options=df3["City"].unique(),default=df3["City"].unique())
#filter the date based on region,state and city
if not region and not state and not city:
    filtered_df=df.copy()
elif not state and not city:
    filtered_df=df[df["Region"].isin(region)].copy()
elif not region and not city:
    filtered_df=df[df["State"].isin(state)].copy()
elif not region and not state:
    filtered_df=df[df["City"].isin(city)].copy()
elif state and city:
    filtered_df=df[(df["State"].isin(state)) & (df["City"].isin(city))].copy()
elif region and city:
    filtered_df=df[(df["Region"].isin(region)) & (df["City"].isin(city))].copy()
elif region and state:
    filtered_df=df[(df["Region"].isin(region)) & (df["State"].isin(state))].copy()
elif city:
    filtered_df=df[df["City"].isin(city)].copy()
else:
    filtered_df=df[(df["Region"].isin(region)) & (df["State"].isin(state)) & (df["City"].isin(city))].copy()
category_df=filtered_df.groupby("Category")["Sales"].sum().reset_index()
with col1:
    st.subheader("categorical wise sales")
    fig=px.bar(category_df,x="Category",y="Sales",color="Category",text_auto=True)
    st.plotly_chart(fig)
with col2:
    st.subheader("region wise sales")
    fig=px.pie(filtered_df,names="Region",values="Sales")
    st.plotly_chart(fig)
#download the data as csv
cl1,cl2=st.columns(2)
with cl1:
    with st.expander("category wise data"):
         st.dataframe(category_df)
         csv=category_df.to_csv(index=False).encode("utf-8")#encoding means converting the data into bytes
         st.download_button(label="Download data as CSV",data=csv,file_name="category_wise_sales.csv",mime="text/csv",help="Click to download the data as CSV")
with cl2:
    with st.expander("Region_wise_data"):
        region=filtered_df.groupby("Region")["Sales"].sum().reset_index()
        st.dataframe(region)
        csv=region.to_csv(index=False).encode("utf-8")#encoding means converting the data into bytes
        st.download_button(label="Download data as CSV",data=csv,file_name="region_wise_sales.csv",mime="text/csv",help="Click to download the data as CSV")
# creating a time series plot for sales over time
filtered_df["month_year"]=filtered_df["Order Date"].dt.strftime("%Y-%m") # converting the date into month and year
st.subheader("Sales over time")
time_series_df=filtered_df.groupby("month_year")["Sales"].sum().reset_index()
fig=px.line(time_series_df,x="month_year",y="Sales",title="Sales over Time")
st.plotly_chart(fig)
with st.expander("view Data of timeseries:"):
    st.write(time_series_df.T.style.background_gradient(cmap="YlGnBu",axis=0))   
    csv=time_series_df.to_csv(index=False).encode("utf-8")#encoding means converting the data into bytes
    st.download_button(label="Download data as CSV",data=csv,file_name="time_series_sales.csv",mime="text/csv",help="Click to download the data as CSV")
#creating a treemap based on region,category and sub category
st.subheader("Treemap of Sales by Region, Category and Sub-Category")
fig=px.treemap(filtered_df,path=["Region","Category","Sub-Category"],values="Sales",color="Sales",color_continuous_scale="RdBu",title="Treemap of Sales by Region, Category and Sub-Category")
st.plotly_chart(fig)
chart1,chart2=st.columns(2)
with chart1:
    st.subheader("segment wise sales")
    fig=px.pie(filtered_df,names="Segment",values="Sales",title="Segment wise sales")
    st.plotly_chart(fig)
with chart2:
    st.subheader("category wise Sales")
    fig=px.pie(filtered_df,values="Sales",names="Category",title="Category wise sales")
    st.plotly_chart(fig)

st.subheader(":point_right: Month wise sub category Sales Summary")
with st.expander("Summary_table"):
    if filtered_df.empty:
        st.info("No data matches the selected date and location filters.")
    else:
        df_summary = filtered_df.groupby(
            ["Region", "City", "Category", "Sub-Category"]
        )[["Sales", "Profit", "Quantity"]].sum().reset_index()
        st.dataframe(df_summary, use_container_width=True, height=500, hide_index=True)
        st.markdown("month wise sub category sales summary")
        filtered_df["month_year"] = filtered_df["Order Date"].dt.strftime("%b %Y")
        sub_category_year= pd.pivot_table(data=filtered_df, index=[ "Sub-Category"], values=["Sales"], aggfunc="sum",columns="month_year").reset_index()
        st.write(sub_category_year.T.style.background_gradient(cmap="YlGnBu",axis=0))
# scatter plat for sales vs profit
st.subheader("Sales vs Profit")
fig=px.scatter(filtered_df,x="Sales",y="Profit",title="Sales vs Profit")
st.plotly_chart(fig)

with st.expander("View data"):
    st.write(filtered_df.iloc[:500, 1:20:2])
#download the original data as csv
csv=df.to_csv(index=False).encode("utf-8")#encoding means converting the data into bytee
st.download_button(label="Download data as CSV",data=csv,file_name="original_data.csv",mime="text/csv",help="Click to download the original data as CSV")
