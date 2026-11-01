import streamlit as st
import plotly.express as px
import pandas as pd
import os
import warnings
from google import genai  # pip install google-genai
warnings.filterwarnings("ignore")

st.set_page_config(page_title="Dashboard", page_icon=":bar_chart:", layout="wide")
st.title(" :bar_chart: Dashboard")
f1 = st.file_uploader(":file_upload: Upload your file", type=["csv", "txt", "xlsx", "xls"])
if f1 is not None:
    filename = f1.name
    st.write(f"File uploaded: {filename}")
    # read from the uploaded object itself (not from a path on disk)
    if filename.lower().endswith((".csv", ".txt")):
        df = pd.read_csv(f1, encoding="latin-1")
    else:
        df = pd.read_excel(f1, engine="calamine")
else:
    os.chdir(r"C:\Users\visha\OneDrive\Desktop\streamlit_dashboard")
    df = pd.read_excel("Sample - Superstore.xls", engine="calamine")
col1, col2 = st.columns(2)
df["Order Date"] = pd.to_datetime(df["Order Date"])
# setting the max and min date
start_date = pd.to_datetime(df["Order Date"].min())
end_date = pd.to_datetime(df["Order Date"].max())
with col1:
    date1 = pd.to_datetime(st.date_input("Start Date", start_date))
with col2:
    date2 = pd.to_datetime(st.date_input("End Date", end_date))
df = df[(df["Order Date"] >= date1) & (df["Order Date"] <= date2)].copy()

st.sidebar.header("Filter Here:")
# create a multiselect for region
region = st.sidebar.multiselect("Select Region:", options=df["Region"].unique(), default=df["Region"].unique())
if not region:
    df2 = df.copy()
else:
    df2 = df[df["Region"].isin(region)].copy()

# create for state
state = st.sidebar.multiselect("Select State:", options=df2["State"].unique(), default=df2["State"].unique())
if not state:
    df3 = df2.copy()
else:
    df3 = df2[df2["State"].isin(state)].copy()
# create for city
city = st.sidebar.multiselect("Select City:", options=df3["City"].unique(), default=df3["City"].unique())
# filter the date based on region,state and city
if not region and not state and not city:
    filtered_df = df.copy()
elif not state and not city:
    filtered_df = df[df["Region"].isin(region)].copy()
elif not region and not city:
    filtered_df = df[df["State"].isin(state)].copy()
elif not region and not state:
    filtered_df = df[df["City"].isin(city)].copy()
elif state and city:
    filtered_df = df[(df["State"].isin(state)) & (df["City"].isin(city))].copy()
elif region and city:
    filtered_df = df[(df["Region"].isin(region)) & (df["City"].isin(city))].copy()
elif region and state:
    filtered_df = df[(df["Region"].isin(region)) & (df["State"].isin(state))].copy()
elif city:
    filtered_df = df[df["City"].isin(city)].copy()
else:
    filtered_df = df[(df["Region"].isin(region)) & (df["State"].isin(state)) & (df["City"].isin(city))].copy()

# ---------------------------------------------------------------------------
# Gemini settings (sidebar)
# ---------------------------------------------------------------------------
st.sidebar.markdown("---")
st.sidebar.header(":sparkles: Gemini AI")
# Key priority: typed in sidebar > .streamlit/secrets.toml > environment variable
default_key = ""
try:
    default_key = st.secrets.get("GEMINI_API_KEY", "")
except Exception:
    pass
default_key = default_key or os.environ.get("GEMINI_API_KEY", "")
gemini_key = st.sidebar.text_input(
    "Gemini API key",
    value=default_key,
    type="password",
    help="Get a free key at https://aistudio.google.com/apikey",
)
gemini_model = st.sidebar.text_input(
    "Model",
    value="gemini-2.5-flash",
    help="Any free-tier model, e.g. gemini-2.5-flash or gemini-2.5-flash-lite",
)

category_df = filtered_df.groupby("Category")["Sales"].sum().reset_index()
with col1:
    st.subheader("categorical wise sales")
    fig = px.bar(category_df, x="Category", y="Sales", color="Category", text_auto=True)
    st.plotly_chart(fig)
with col2:
    st.subheader("region wise sales")
    fig = px.pie(filtered_df, names="Region", values="Sales")
    st.plotly_chart(fig)
# download the data as csv
cl1, cl2 = st.columns(2)
with cl1:
    with st.expander("category wise data"):
        st.dataframe(category_df)
        csv = category_df.to_csv(index=False).encode("utf-8")  # encoding means converting the data into bytes
        st.download_button(label="Download data as CSV", data=csv, file_name="category_wise_sales.csv", mime="text/csv", help="Click to download the data as CSV")
with cl2:
    with st.expander("Region_wise_data"):
        region_df = filtered_df.groupby("Region")["Sales"].sum().reset_index()
        st.dataframe(region_df)
        csv = region_df.to_csv(index=False).encode("utf-8")  # encoding means converting the data into bytes
        st.download_button(label="Download data as CSV", data=csv, file_name="region_wise_sales.csv", mime="text/csv", help="Click to download the data as CSV")
# creating a time series plot for sales over time
filtered_df["month_year"] = filtered_df["Order Date"].dt.strftime("%Y-%m")  # converting the date into month and year
st.subheader("Sales over time")
time_series_df = filtered_df.groupby("month_year")["Sales"].sum().reset_index()
fig = px.line(time_series_df, x="month_year", y="Sales", title="Sales over Time")
st.plotly_chart(fig)
with st.expander("view Data of timeseries:"):
    st.write(time_series_df.T.style.background_gradient(cmap="YlGnBu", axis=0))
    csv = time_series_df.to_csv(index=False).encode("utf-8")  # encoding means converting the data into bytes
    st.download_button(label="Download data as CSV", data=csv, file_name="time_series_sales.csv", mime="text/csv", help="Click to download the data as CSV")
# creating a treemap based on region,category and sub category
st.subheader("Treemap of Sales by Region, Category and Sub-Category")
fig = px.treemap(filtered_df, path=["Region", "Category", "Sub-Category"], values="Sales", color="Sales", color_continuous_scale="RdBu", title="Treemap of Sales by Region, Category and Sub-Category")
st.plotly_chart(fig)
chart1, chart2 = st.columns(2)
with chart1:
    st.subheader("segment wise sales")
    fig = px.pie(filtered_df, names="Segment", values="Sales", title="Segment wise sales")
    st.plotly_chart(fig)
with chart2:
    st.subheader("category wise Sales")
    fig = px.pie(filtered_df, values="Sales", names="Category", title="Category wise sales")
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
        sub_category_year = pd.pivot_table(data=filtered_df, index=["Sub-Category"], values=["Sales"], aggfunc="sum", columns="month_year").reset_index()
        st.write(sub_category_year.T.style.background_gradient(cmap="YlGnBu", axis=0))
# scatter plat for sales vs profit
st.subheader("Sales vs Profit")
fig = px.scatter(filtered_df, x="Sales", y="Profit", title="Sales vs Profit")
st.plotly_chart(fig)

with st.expander("View data"):
    st.write(filtered_df.iloc[:500, 1:20:2])
# download the original data as csv
csv = df.to_csv(index=False).encode("utf-8")  # encoding means converting the data into bytee
st.download_button(label="Download data as CSV", data=csv, file_name="original_data.csv", mime="text/csv", help="Click to download the original data as CSV")


# ---------------------------------------------------------------------------
# AI analysis with Gemini
# ---------------------------------------------------------------------------
def build_data_summary(d: pd.DataFrame) -> str:
    """Compress the filtered data into a compact text summary.
    We send aggregates (not raw rows) so the prompt stays small and fits the free-tier limits."""
    parts = []
    parts.append(
        f"Date range: {d['Order Date'].min().date()} to {d['Order Date'].max().date()}\n"
        f"Rows: {len(d)}"
    )
    total_sales = d["Sales"].sum()
    total_profit = d["Profit"].sum()
    margin = (total_profit / total_sales * 100) if total_sales else 0
    kpis = (
        f"Total Sales: {total_sales:,.2f}\n"
        f"Total Profit: {total_profit:,.2f}\n"
        f"Profit Margin: {margin:.2f}%\n"
        f"Total Quantity: {d['Quantity'].sum():,}"
    )
    if "Order ID" in d.columns:
        kpis += f"\nUnique Orders: {d['Order ID'].nunique():,}"
    if "Discount" in d.columns:
        kpis += f"\nAverage Discount: {d['Discount'].mean():.2%}"
    parts.append("KEY METRICS\n" + kpis)

    def agg(cols, top=None, sort_by="Sales"):
        g = d.groupby(cols)[["Sales", "Profit", "Quantity"]].sum().round(2)
        g["Margin %"] = (g["Profit"] / g["Sales"] * 100).round(2)
        g = g.sort_values(sort_by, ascending=False)
        return (g.head(top) if top else g).to_string()

    parts.append("BY CATEGORY\n" + agg("Category"))
    parts.append("BY SEGMENT\n" + agg("Segment"))
    parts.append("BY REGION\n" + agg("Region"))
    parts.append("BY SUB-CATEGORY\n" + agg("Sub-Category"))
    parts.append("TOP 10 STATES BY SALES\n" + agg("State", top=10))
    parts.append("TOP 10 CITIES BY SALES\n" + agg("City", top=10))
    worst = (d.groupby(["Sub-Category", "Region"])[["Sales", "Profit"]].sum().round(2)
             .sort_values("Profit").head(10))
    parts.append("10 LEAST PROFITABLE SUB-CATEGORY/REGION COMBOS\n" + worst.to_string())

    monthly = (
        d.assign(month=d["Order Date"].dt.to_period("M").astype(str))
        .groupby("month")[["Sales", "Profit"]].sum().round(2)
    )
    parts.append("MONTHLY SALES & PROFIT\n" + monthly.to_string())

    if "Discount" in d.columns:
        disc = d.assign(discount_band=pd.cut(
            d["Discount"], bins=[-0.01, 0, 0.1, 0.2, 0.3, 0.5, 1.0],
            labels=["0%", "0-10%", "10-20%", "20-30%", "30-50%", "50%+"]))
        disc = disc.groupby("discount_band", observed=True)[["Sales", "Profit"]].sum().round(2)
        parts.append("PROFIT BY DISCOUNT BAND\n" + disc.to_string())

    return "\n\n".join(parts)


def ask_gemini(api_key: str, model: str, prompt: str) -> str:
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(model=model, contents=prompt)
    return response.text or "(Gemini returned an empty response.)"


st.markdown("---")
st.subheader(":sparkles: AI Analysis (Gemini)")
st.caption("The analysis is based on the data currently shown (after your date/region/state/city filters).")

if filtered_df.empty:
    st.info("No data matches the selected filters, so there is nothing to analyse.")
elif not gemini_key:
    st.info("Enter your Gemini API key in the sidebar to enable AI analysis. "
            "You can get a free key from https://aistudio.google.com/apikey")
else:
    SYSTEM_PROMPT = (
        "You are a senior business data analyst. You are given aggregated sales data from a "
        "retail 'Superstore' dataset (already filtered by the user). Base every statement on the "
        "numbers provided and do not invent figures. Be concise and specific, quote actual numbers, "
        "and use markdown."
    )
    data_summary = build_data_summary(filtered_df)

    tab1, tab2 = st.tabs(["Auto insights", "Ask a question"])

    with tab1:
        if st.button("Generate insights", key="gen_insights"):
            prompt = (
                f"{SYSTEM_PROMPT}\n\nDATA SUMMARY:\n{data_summary}\n\n"
                "Write an analysis with these sections:\n"
                "1. **Executive summary** (3-4 sentences)\n"
                "2. **Key trends** (sales/profit over time, seasonality, growth or decline)\n"
                "3. **Top performers** (categories, regions, states, cities)\n"
                "4. **Problem areas** (loss-making or low-margin segments, effect of discounts)\n"
                "5. **Recommendations** (4-5 concrete, actionable steps)"
            )
            with st.spinner("Gemini is analysing your data..."):
                try:
                    st.session_state["ai_insights"] = ask_gemini(gemini_key, gemini_model, prompt)
                except Exception as e:
                    st.session_state["ai_insights"] = None
                    st.error(f"Gemini request failed: {e}")
        if st.session_state.get("ai_insights"):
            st.markdown(st.session_state["ai_insights"])
            st.download_button(
                "Download analysis (.md)",
                data=st.session_state["ai_insights"].encode("utf-8"),
                file_name="ai_analysis.md",
                mime="text/markdown",
            )

    with tab2:
        question = st.text_input("Ask something about this data",
                                 placeholder="e.g. Why is Tables sub-category losing money?")
        if st.button("Ask Gemini", key="ask_q") and question.strip():
            prompt = (
                f"{SYSTEM_PROMPT}\n\nDATA SUMMARY:\n{data_summary}\n\n"
                f"USER QUESTION: {question}\n\n"
                "Answer using only the data above. If the data is not enough to answer, say so."
            )
            with st.spinner("Thinking..."):
                try:
                    st.session_state["ai_answer"] = ask_gemini(gemini_key, gemini_model, prompt)
                except Exception as e:
                    st.session_state["ai_answer"] = None
                    st.error(f"Gemini request failed: {e}")
        if st.session_state.get("ai_answer"):
            st.markdown(st.session_state["ai_answer"])
