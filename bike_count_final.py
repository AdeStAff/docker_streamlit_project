import streamlit as st
import pandas as pd 
import plotly.express as px
import folium
from streamlit_folium import folium_static


st.header("Paris and its cyclists")

@st.cache_data
def load_zones_map():
    m = folium.Map(location=df[["latitude", "longitude"]].mean(axis=0), zoom_start=13)

    for _, row in (
        df[["counter_name", "latitude", "longitude"]]
        .drop_duplicates("counter_name")
        .iterrows()
    ):
        folium.Marker(
            row[["latitude", "longitude"]].values.tolist(), popup=row["counter_name"]
        ).add_to(m)

    return m

@st.cache_data
def load_data():
    
    data = pd.read_parquet('train.parquet')

    return data

def plot_avg_bikes_by_weekday(df):
    df['date'] = pd.to_datetime(df['date'])
    df['day_of_week'] = df['date'].dt.day_name()
    df['month'] = df['date'].dt.month
    df['month_name'] = df['date'].dt.strftime('%B')

    # Define the correct order for days of the week (Monday to Sunday)
    days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    # List of month names in order
    month_names = df['month_name'].unique()

    selected_month = st.select_slider("Select the month", options=month_names)
    # Filter dataset by selected month
    df_filtered = df[df['month_name'] == selected_month]

    # Group by day of the week and calculate average bike count
    avg_bikes = df_filtered.groupby('day_of_week')['bike_count'].mean().reset_index()

    # Reorder days of the week
    avg_bikes['day_of_week'] = pd.Categorical(avg_bikes['day_of_week'], categories=days_order, ordered=True)
    avg_bikes = avg_bikes.sort_values('day_of_week')

    # Plot the interactive graph
    fig = px.bar(avg_bikes, x='day_of_week', y='bike_count', title=f"Avg # of cyclists per day of the week - {selected_month}")
    fig.update_layout(xaxis_title='Day of the Week', yaxis_title='Average number of cyclists')

    return fig

df = load_data()

# Introduction
st.write('Over the course of more than a year, the city of Paris tracked the number of cyclists passing through various locations using sensors strategically placed around the city. Leveraging this dataset, I created a detailed graph that analyzes the average number of cyclists per day of the week, depending on the month.')
st.write('The data was collected from September 2020 to August 2021, 24/7.')

# Display the map of sensors
st.subheader("Map of the sensors - Paris, France")
st.write("This map displays the location of the sensors that were used to collect the data.")
map = load_zones_map()
folium_static(map)


# Display the average number of cyclists per day of the week, depending on the month
st.subheader("Average number of cyclists by weekday")
st.write("The widget allows you to select the month, and to see the different distributions of cyclists by weekday depending on the month of the year")
fig = plot_avg_bikes_by_weekday(df)
st.plotly_chart(fig)