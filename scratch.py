import math

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import streamlit as st
import streamlit.components.v1 as components
import networkx as nx
import plotly.express as px
import plotly.graph_objects as go
from pyvis.network import Network


APAC_COUNTRIES = [
    "Australia", "Bangladesh", "Bhutan", "Brunei", "Myanmar", "Cambodia",
    "China", "Fiji", "India", "Indonesia", "Japan", "Kiribati",
    "Laos", "Malaysia", "Maldives", "Marshall Islands", "Micronesia", "Nepal",
    "New Zealand", "North Korea", "Palau", "Papua New Guinea", "Philippines",
    "Samoa", "Singapore", "Solomon Islands", "South Korea", "Sri Lanka", "Taiwan",
    "Thailand", "Timor-Leste", "Tonga", "Tuvalu", "Vanuatu",
    "Viet Nam", "Russia", "Viet Nam"
]

# Header
st.set_page_config(layout="wide")
st.write("<h1>SIPRI Recent Data Set 1992-2023</h1>", unsafe_allow_html=True)
year_range = st.slider("Select year range for order placement dates", 1992, 2023, (1992, 2023))

# Load
original_df = pd.read_csv("data/sipri-full-rows.csv")
original_df.reset_index(inplace=True)
original_df.columns = original_df.columns.map(lambda x: x.strip())

# Source Data
with st.expander("Source data"):
    st.dataframe(original_df)

# Columns
with st.expander("Columns"):
    column_names = original_df.columns.tolist()
    filtered_columns = [col for col in column_names if not (col == '' or col.startswith('.') or col.isdigit())]
    st.write(filtered_columns)

# Clean
df = original_df[(original_df["Year of order"] >= year_range[0]) & (original_df["Year of order"] <= year_range[1])]
df = df.dropna(subset=['Recipient'])
df = df[filtered_columns]

# Filter valid APAC countries
unique_recipients = original_df["Recipient"].unique()
for country in APAC_COUNTRIES:
    if not country in unique_recipients:
        print(country)
        raise AssertionError()

with st.expander("Selected APAC countries"):
    st.write(APAC_COUNTRIES)

with st.expander("Filtered data sets to APAC region"):
    apac_df = df[(df["Recipient"].isin(APAC_COUNTRIES)) | (df["Supplier"].isin(APAC_COUNTRIES))]
    st.write("Filtered data to suppliers OR recipients in APAC region:")
    st.write(apac_df)

    apac_rec_df = df[df["Recipient"].isin(APAC_COUNTRIES)]
    st.write("Filtered data to recipients in APAC region:")
    st.write(apac_rec_df)

col1, col2 = st.columns(2)

with col1:
    # Top 8 SIPRI TIV delivered to APAC by country
    supplier_totals = apac_rec_df.groupby('Supplier')['SIPRI TIV of delivered weapons'].sum().sort_values(ascending=False)
    top_10_suppliers = supplier_totals.head(8)
    other_suppliers = supplier_totals[8:].sum()
    supplier_totals_combined = pd.concat([top_10_suppliers, pd.Series(other_suppliers, index=['Other'])])

    fig, ax = plt.subplots()
    ax.pie(supplier_totals_combined, labels=supplier_totals_combined.index, autopct='%1.0f%%', startangle=90, counterclock=False)
    ax.set_title('Top 8 Suppliers to APAC Countries by Total Weapons Value')
    st.pyplot(fig)

with col2:
    # Top 12 SIPRI TIV delivered to APAC by country
    recipient_totals = apac_rec_df.groupby('Recipient')['SIPRI TIV of delivered weapons'].sum().sort_values(ascending=False)
    top_10_recipients = recipient_totals.head(12)
    other_recipients = recipient_totals[12:].sum()
    recipient_totals_combined = pd.concat([top_10_recipients, pd.Series(other_recipients, index=['Other'])])

    fig, ax = plt.subplots()
    ax.pie(recipient_totals_combined, labels=recipient_totals_combined.index, autopct='%1.0f%%', startangle=90, counterclock=False)
    ax.set_title('Top 12 Recipients among APAC Countries by Total Weapons Value')
    st.pyplot(fig)

col1, col2, col3 = st.columns([3, 4, 3])

with col2:
    yearly_totals = apac_rec_df.groupby(apac_rec_df['Year of order'])['SIPRI TIV of delivered weapons'].sum()
    fig, ax = plt.subplots()
    yearly_totals.plot(kind='line', ax=ax)
    ax.set_title(f'Total APAC Weapons Value by Year {year_range[0]}-{year_range[1]}')
    ax.set_xlabel('Year')
    ax.set_ylabel('Total Weapons Value (millions TIV)')
    st.pyplot(fig)

col1, col2 = st.columns(2)

with col1:
    recipient_country = st.selectbox("Select a Recipient Country", apac_rec_df['Recipient'].unique())
    df_filter_rec = apac_rec_df[apac_rec_df['Recipient'] == recipient_country]

    # Breakdown of total value by supplier country for the selected recipient country
    rec_supplier_totals = df_filter_rec.groupby('Supplier')['SIPRI TIV of delivered weapons'].sum().sort_values(ascending=False)
    top_rec_suppliers = rec_supplier_totals.head(5)
    other_rec_suppliers = rec_supplier_totals[5:].sum()
    rec_supplier_totals_combined = pd.concat([top_rec_suppliers, pd.Series(other_rec_suppliers, index=['Other'])])

    fig, ax = plt.subplots()
    ax.pie(rec_supplier_totals_combined, labels=rec_supplier_totals_combined.index, autopct='%1.0f%%', startangle=90, counterclock=False)
    ax.set_title(f'Weapons Value Breakdown by Supplier for {recipient_country}')
    st.pyplot(fig)

with col2:
    supplier_country = st.selectbox("Select a Supplier Country", apac_rec_df["Supplier"].unique())
    df_filter_sup = apac_rec_df[apac_rec_df['Supplier'] == supplier_country]

    # Breakdown of total value by recipient country for the selected supplier country
    sup_recipient_totals = df_filter_sup.groupby('Recipient')['SIPRI TIV of delivered weapons'].sum().sort_values(ascending=False)
    top_sup_recipients = sup_recipient_totals.head(5)
    other_sup_recipients = sup_recipient_totals[5:].sum()
    sup_recipient_totals_combined = pd.concat([top_sup_recipients, pd.Series(other_sup_recipients, index=['Other'])])

    fig, ax = plt.subplots()
    ax.pie(sup_recipient_totals_combined, labels=sup_recipient_totals_combined.index, autopct='%1.0f%%', startangle=90, counterclock=False)
    ax.set_title(f'Weapons Value Breakdown by Recipient for {supplier_country}')
    st.pyplot(fig)

# Network graph
col1, col2, col3 = st.columns([2, 6, 2])
with col2:
    st.write("Directed Graph of Total Weapons Value Ordered")
    select_all = st.checkbox("Show All Weapon Descriptions")
    if select_all:
        weapon_description_filter = apac_rec_df["Weapon description"].unique().tolist()
    else:
        weapon_description_filter = st.multiselect("Select Weapon Descriptions to include in the network graph", apac_rec_df["Weapon description"].unique())
    weapon_apac_rec_df = apac_rec_df[apac_rec_df["Weapon description"].isin(weapon_description_filter)]

G = nx.DiGraph()
for index, row in weapon_apac_rec_df.iterrows():
    if not G.has_edge(row['Supplier'], row['Recipient']):
        G.add_edge(row['Supplier'], row['Recipient'], weight=row['SIPRI TIV of delivered weapons'])
    else:
        G[row['Supplier']][row['Recipient']]['weight'] += row['SIPRI TIV of delivered weapons']

net = Network(height='700px', width='100%', directed=True)
net.from_nx(G)
net.repulsion()
import math
for edge in net.edges:
    edge['title'] = f"log(TIV): {round(math.log(edge["width"]+1, 10), 2)}"
    edge['value'] = math.log(edge["width"]+1, 10)

net.save_graph('graph.html')
with open('graph.html', 'r', encoding='utf-8') as f:
    graph_html = f.read()

with col2:
    components.html(graph_html, height=750)