import streamlit as st
import pandas as pd

# Load the data
df = pd.read_csv("data/trade-register.csv", skiprows=11)

# Since the dataframe has a MultiIndex and only one column, we need to reset the index and rename the columns appropriately
df.reset_index(inplace=True)
df.columns = df.columns.map(lambda x: x.strip())
df['YO'] = pd.to_datetime(df['Year of order'], format='%Y')

st.write("Fields:")
st.text(str(df.columns))
print(df.info())

st.write("Filter by date range:")
start_date = st.date_input("Start date", df['YO'].min().date())
end_date = st.date_input("End date", df['YO'].max().date())

# Display the dataframe
st.write("Dataframe:")
st.dataframe(df)

# Example plot: Number of Orders by Year
st.write("Number of Orders by Year:")
if 'Year of order' in df.columns:
    orders_by_year = df.groupby('Year of order').size()
    st.line_chart(orders_by_year)

st.write("Number of Orders by Supplier:")
orders_by_year = df.groupby('Supplier').size()
st.line_chart(orders_by_year)

st.write("Number of Orders by Weapon designation:")
orders_by_year = df.groupby('Weapon designation').size()
st.line_chart(orders_by_year)
