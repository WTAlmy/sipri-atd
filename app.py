import math
import tempfile

import geopandas as gpd
import networkx as nx
import pandas as pd
import plotly.express as px
import streamlit as st
import streamlit.components.v1 as components
from pyvis.network import Network

APAC_COUNTRIES = [
    "Australia",
    "Bangladesh",
    "Bhutan",
    "Brunei",
    "Myanmar",
    "Cambodia",
    "China",
    "Fiji",
    "India",
    "Indonesia",
    "Japan",
    "Kiribati",
    "Laos",
    "Malaysia",
    "Maldives",
    "Marshall Islands",
    "Micronesia",
    "Nepal",
    "New Zealand",
    "North Korea",
    "Palau",
    "Papua New Guinea",
    "Philippines",
    "Samoa",
    "Singapore",
    "Solomon Islands",
    "South Korea",
    "Sri Lanka",
    "Taiwan",
    "Thailand",
    "Timor-Leste",
    "Tonga",
    "Tuvalu",
    "Vanuatu",
    "Viet Nam",
    "Russia",
    "Viet Nam",
]

# Load
original_df = pd.read_csv("data/sipri-full-rows.csv")
original_df.reset_index(inplace=True)
original_df.columns = original_df.columns.map(lambda x: x.strip())

# Validate valid APAC countries
unique_recipients = original_df["Recipient"].unique()
for country in APAC_COUNTRIES:
    if country not in unique_recipients:
        print(country)
        raise AssertionError()

# Process columns
column_names = original_df.columns.tolist()
filtered_columns = [
    col
    for col in column_names
    if not (col == "" or col.startswith(".") or col.isdigit())
]

# Set up, clean, filter pre-sidebar
apac_rec_df = original_df.dropna(subset=["Recipient"])
apac_rec_df = apac_rec_df[apac_rec_df["Recipient"].isin(APAC_COUNTRIES)]
apac_rec_df = apac_rec_df[filtered_columns]

# Header
st.set_page_config(layout="wide")
st.write("<h1>SIPRI Recent Data Set 1992-2023</h1>", unsafe_allow_html=True)

# Source dataframe
with st.expander("Source data"):
    st.dataframe(original_df)

# Columns
with st.expander("Available columns"):
    st.write(filtered_columns)

# APAC countries
with st.expander("Selected APAC countries"):
    world = gpd.read_file(gpd.datasets.get_path("naturalearth_lowres"))
    apac_map = world[world["name"].isin(APAC_COUNTRIES + ["Vietnam"])]
    fig = px.choropleth(
        apac_map,
        geojson=world.__geo_interface__,
        locations=apac_map.index,
        color="name",
        hover_name="name",
        title="Selected APAC Countries",
    )
    fig.update_geos(projection_type="equirectangular")
    st.plotly_chart(fig)
    st.write(APAC_COUNTRIES)

# Dataframe of APAC recipients
with st.expander("Source data filtered on APAC countries"):
    st.write(apac_rec_df)

# Sidebar
with st.sidebar:
    st.header("Filters")
    global_year_range = st.slider("Order Placement Year", 1992, 2023, (1992, 2023))
    global_recipient_filter = st.multiselect(
        "Filter by Recipient Countries", apac_rec_df["Recipient"].unique()
    )
    global_supplier_filter = st.multiselect(
        "Filter by Supplier Countries", apac_rec_df["Supplier"].unique()
    )
    global_description_filter = st.multiselect(
        "Filter by Weapon Categories", apac_rec_df["Weapon description"].unique()
    )

# Create filtered dataframes
year_filter_df = apac_rec_df[
    (apac_rec_df["Year of order"] >= global_year_range[0])
    & (apac_rec_df["Year of order"] <= global_year_range[1])
]
each_filter_df = year_filter_df
year_text = f"{global_year_range[0]}-{global_year_range[1]}"
rcp_base = "Recipients: "
rcp_text = "APAC"
sup_base = "Suppliers: "
sup_text = "APAC"
cat_base = "Weapon categories: "
cat_text = "All"
if global_recipient_filter:
    each_filter_df = each_filter_df[
        each_filter_df["Recipient"].isin(global_recipient_filter)
    ]
    rcp_text = ", ".join(global_recipient_filter)
if global_supplier_filter:
    each_filter_df = each_filter_df[
        each_filter_df["Supplier"].isin(global_supplier_filter)
    ]
    sup_text = ", ".join(global_supplier_filter)
if global_description_filter:
    each_filter_df = each_filter_df[
        each_filter_df["Weapon description"].isin(global_description_filter)
    ]
    cat_text = ", ".join(global_description_filter)
rcp_full = rcp_base + rcp_text
sup_full = sup_base + sup_text
cat_full = cat_base + cat_text
full_subtitle_text = f"<br><sup>{year_text}; {rcp_full}; {sup_full}; {cat_full}</sup>"


# General overview
st.write(
    f"<h3>General Overview: {global_year_range[0]}-{global_year_range[1]} </h3>",
    unsafe_allow_html=True,
)
col1, col2 = st.columns(2)

with col1:
    # Top 10 SIPRI TIV delivered to APAC by country
    supplier_totals = (
        year_filter_df.groupby("Supplier")["SIPRI TIV of delivered weapons"]
        .sum()
        .sort_values(ascending=False)
    )
    top_10_suppliers = supplier_totals.head(10)
    other_suppliers = supplier_totals[10:].sum()
    supplier_totals_combined = pd.concat(
        [top_10_suppliers, pd.Series(other_suppliers, index=["Other"])]
    )
    fig = px.pie(
        supplier_totals_combined,
        values=supplier_totals_combined,
        names=supplier_totals_combined.index,
        title="Top 10 Suppliers to APAC Countries by Total Weapons Value",
    )
    st.plotly_chart(fig)

with col2:
    # Top 10 SIPRI TIV delivered to APAC by country
    recipient_totals = (
        year_filter_df.groupby("Recipient")["SIPRI TIV of delivered weapons"]
        .sum()
        .sort_values(ascending=False)
    )
    top_10_recipients = recipient_totals.head(10)
    other_recipients = recipient_totals[10:].sum()
    recipient_totals_combined = pd.concat(
        [top_10_recipients, pd.Series(other_recipients, index=["Other"])]
    )
    fig = px.pie(
        recipient_totals_combined,
        values=recipient_totals_combined,
        names=recipient_totals_combined.index,
        title="Top 10 Recipients among APAC Countries by Total Weapons Value",
    )
    st.plotly_chart(fig)

# Filtered Widgets
st.write(
    f"<h3>Filtered Widgets: {global_year_range[0]}-{global_year_range[1]} </h3>",
    unsafe_allow_html=True,
)

# Bar graph of total value ordered by year
yearly_totals = each_filter_df.groupby(year_filter_df["Year of order"])[
    "SIPRI TIV of delivered weapons"
].sum()
fig = px.bar(
    yearly_totals,
    title=f"Total Weapons Ordered by Year from {global_year_range[0]}-{global_year_range[1]}{full_subtitle_text}",
)
fig.update_layout(xaxis_title="Year", yaxis_title="Total Weapons Value (millions TIV)")
st.plotly_chart(fig)

col1, col2 = st.columns(2)

with col1:
    # Breakdown of total value by supplier country for the selected recipient country
    rec_supplier_totals = (
        each_filter_df.groupby("Supplier")["SIPRI TIV of delivered weapons"]
        .sum()
        .sort_values(ascending=False)
    )
    top_rec_suppliers = rec_supplier_totals.head(5)
    other_rec_suppliers = rec_supplier_totals[5:].sum()
    rec_supplier_totals_combined = pd.concat(
        [top_rec_suppliers, pd.Series(other_rec_suppliers, index=["Other"])]
    )
    fig = px.pie(
        rec_supplier_totals_combined,
        values=rec_supplier_totals_combined,
        names=rec_supplier_totals_combined.index,
        title="Weapons Value Breakdown by Supplier",
    )
    st.plotly_chart(fig)

with col2:
    # Breakdown of total value by recipient country for the selected supplier country
    sup_recipient_totals = (
        each_filter_df.groupby("Recipient")["SIPRI TIV of delivered weapons"]
        .sum()
        .sort_values(ascending=False)
    )
    top_sup_recipients = sup_recipient_totals.head(5)
    other_sup_recipients = sup_recipient_totals[5:].sum()
    sup_recipient_totals_combined = pd.concat(
        [top_sup_recipients, pd.Series(other_sup_recipients, index=["Other"])]
    )
    fig = px.pie(
        sup_recipient_totals_combined,
        values=sup_recipient_totals_combined,
        names=sup_recipient_totals_combined.index,
        title="Weapons Value Breakdown by Recipient",
    )
    st.plotly_chart(fig)


# Cache generated graph based on filtered dataframe
@st.cache_data
def build_graph(each_filter_df):
    G = nx.DiGraph()
    for index, row in each_filter_df.iterrows():
        if not G.has_edge(row["Supplier"], row["Recipient"]):
            G.add_edge(
                row["Supplier"],
                row["Recipient"],
                weight=row["SIPRI TIV of delivered weapons"],
            )
        else:
            G[row["Supplier"]][row["Recipient"]]["weight"] += row[
                "SIPRI TIV of delivered weapons"
            ]
    net = Network(height="700px", width="100%", directed=True)
    net.from_nx(G)
    net.repulsion()
    for edge in net.edges:
        edge["title"] = f"log(TIV): {round(math.log(edge['width']+1, 6), 2)}"
        edge["value"] = math.log(edge["width"] + 1, 6)
    return net


# Graph
net = build_graph(each_filter_df)
with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp_file:
    net.save_graph(tmp_file.name)
    tmp_file.seek(0)
    graph_html = tmp_file.read().decode("utf-8")

st.write(
    "<h4>Directed Graph of Total Weapons Value Ordered</h4>", unsafe_allow_html=True
)
components.html(graph_html, height=750)

# Globally Filtered Dataframe
with st.expander("Source data filtered on global configuration options"):
    st.write(each_filter_df)
