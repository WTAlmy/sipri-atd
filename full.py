import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Header
st.write("<h1>SIPRI Full Data Set 1950-2023</h1>", unsafe_allow_html=True)

# Load
df = pd.read_csv("data/sipri-full-rows.csv")
df.reset_index(inplace=True)
df.columns = df.columns.map(lambda x: x.strip())

# Source Data
st.write("Source data:")
st.dataframe(df)

# Columns
column_names = df.columns.tolist()
filtered_columns = [col for col in column_names if not (col == '' or col.startswith('.') or col.isdigit())]
st.write("Columns:")
st.write(filtered_columns)

# Clean 1
df = df[filtered_columns]
st.write("Clean 1:")
st.dataframe(df)

# Clean 2
df = df.dropna(subset=['Recipient'])
df['OrderYear'] = pd.to_datetime(df['Year of order'], format='%Y')
st.write("Clean 2:")
st.dataframe(df)

# Total value by country
supplier_totals = df.groupby('Supplier')['SIPRI TIV of delivered weapons'].sum().sort_values(ascending=False).head(10)
fig, ax = plt.subplots()
ax.pie(supplier_totals, labels=supplier_totals.index, autopct='%1.1f%%', startangle=90, counterclock=False)
ax.set_title('Top 10 Supplier Countries by Total Weapons Value')
st.pyplot(fig)

# Total value by year
yearly_totals = df.groupby(df['OrderYear'].dt.year)['SIPRI TIV of delivered weapons'].sum()
fig, ax = plt.subplots()
yearly_totals.plot(kind='line', ax=ax)
ax.set_title('Total Weapons Value by Year (1950-2023)')
ax.set_xlabel('Year')
ax.set_ylabel('Total Weapons Value (in millions)')
st.pyplot(fig)

# Dropdown for recipient country selection
recipient_country = st.selectbox("Select a Recipient Country", df['Recipient'].unique())
df_filtered = df[df['Recipient'] == recipient_country]

# Total value by country for selected recipient
supplier_totals_filtered = df_filtered.groupby('Supplier')['SIPRI TIV of delivered weapons'].sum().sort_values(ascending=False).head(10)
fig, ax = plt.subplots()
ax.pie(supplier_totals_filtered, labels=supplier_totals_filtered.index, autopct='%1.1f%%', startangle=90, counterclock=False)
ax.set_title(f'Top 10 Supplier Countries by Total Weapons Value for {recipient_country}')
st.pyplot(fig)

# Total value by year for selected recipient
yearly_totals_filtered = df_filtered.groupby(df_filtered['OrderYear'].dt.year)['SIPRI TIV of delivered weapons'].sum()
fig, ax = plt.subplots()
yearly_totals_filtered.plot(kind='line', ax=ax)
ax.set_title(f'Total Weapons Value by Year (1950-2023) for {recipient_country}')
ax.set_xlabel('Year')
ax.set_ylabel('Total Weapons Value (in millions)')
st.pyplot(fig)

## Filter data for the heatmap and limit to top 20 weapon types by volume
df_heatmap_filtered = df_filtered[(df_filtered['OrderYear'].dt.year >= 2010) & (df_filtered['OrderYear'].dt.year <= 2023)]
top_20_weapons = df_heatmap_filtered.groupby('Weapon description')['Number delivered'].sum().sort_values(ascending=False).head(20).index
df_heatmap_filtered = df_heatmap_filtered[df_heatmap_filtered['Weapon description'].isin(top_20_weapons)]

df_heatmap = df_heatmap_filtered.pivot_table(values='SIPRI TIV of delivered weapons', index='Weapon description', columns=df_heatmap_filtered['OrderYear'].dt.year, aggfunc='sum', fill_value=0)
df_heatmap_log = np.log1p(df_heatmap)

# Plot heatmap
fig, ax = plt.subplots(figsize=(12, 8))
sns.heatmap(df_heatmap_log, ax=ax, cmap='viridis', annot=True, fmt=".1f")
ax.set_title(f'Heatmap of Total Weapons Value by Weapon Type and Year (2010-2023) for {recipient_country}')
ax.set_xlabel('Year')
ax.set_ylabel('Weapon Type')
st.pyplot(fig)