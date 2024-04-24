import pandas as pd
import altair as alt
import streamlit as st

# Load data
runs = pd.read_csv('data/processed/processed.csv')

# Set page configuration
st.set_page_config(
    page_title="Julia's Run Tracker",
    page_icon="🏃",
    layout="wide",
    initial_sidebar_state="expanded"
)
alt.themes.enable("dark")

# Sidebar
with st.sidebar:
    st.title('🏃 Julia\'s Run Tracker')
    filter_value = st.slider('Select Training Week', min_value=1, max_value=20, value=10)

# Overall summary chart
aggregate_dictionary = {'distance':['sum','max'],'moving_time':'sum',
                       'total_elevation_gain':'sum', 'average_speed':'mean',
                       'average_heartrate': 'mean', 'kudos_count':'sum'}
weekly_dash = runs.groupby(['week'], as_index=False).aggregate(aggregate_dictionary)
weekly_dash.columns = ['week','Total Distance', 'Longest Run','moving_time','total_elevation_gain','average_speed',
                       'average_heartrate', 'kudos_count']
weekly_dash = pd.melt(weekly_dash, 
                      id_vars=['week', 'moving_time','total_elevation_gain','average_speed',
                       'average_heartrate', 'kudos_count'],
                       value_vars=['Longest Run', 'Total Distance'],
                       var_name='Metric')
weekly_dash = weekly_dash[weekly_dash['week'] < 18]

click = alt.selection_single()
weekly_summary_view = alt.Chart(weekly_dash).mark_line(point=True, size=2).encode(
    alt.X('week:Q', title='Week #',axis=alt.Axis(tickCount=18)),
    alt.Y('value:Q', title='Distance [km]'),
    color=alt.condition(click, 'Metric',alt.value('lightgray')),
    tooltip = ['week', 'value']
).add_selection(
    click
).configure_axis(
    grid=False
)

st.subheader("Weekly Distance Summary")
st.altair_chart(weekly_summary_view, use_container_width=True)

# Filtered data
cols = ['name', 'start_date', 'distance', 'moving_time', 'total_elevation_gain', 'kudos_count', 'average_speed', 'average_heartrate']
filtered_data = runs[runs['week'] == filter_value][cols]
filtered_data.columns = ['Name', 'Date', 'Distance [km]', 'Moving Time [mins]', 'Elevation [m]', 'Kudos', 'Pace [min/km]', 'Heartrate']

# Display filtered data
st.subheader(f"Runs for training week #{filter_value}")
st.table(filtered_data.style.format({"Distance [km]": "{:.2f}", "Moving Time [mins]": "{:.2f}", "Elevation [m]": "{:.1f}", "Pace [min/km]": "{:.2f}", "Heartrate": "{:.0f}"}))

# Metrics
st.subheader("Weekly Metrics")
average_total_time = round(weekly_dash['moving_time'].mean(), 2)
average_total_dist = round(weekly_dash[weekly_dash['Metric']=='Total Distance']['value'].mean(), 2)
average_total_elevation = round(weekly_dash['total_elevation_gain'].mean(), 2)
average_total_speed = round(weekly_dash['average_speed'].mean(), 2)

weekly_total_time = round(filtered_data['Moving Time [mins]'].sum(), 2)
weekly_total_dist = round(filtered_data['Distance [km]'].sum(), 2)
weekly_total_elevation = round(filtered_data['Elevation [m]'].sum(), 2)
weekly_speed = round(filtered_data['Pace [min/km]'].mean(), 2)
weekly_longest_dist = round(filtered_data['Distance [km]'].max(), 2)

# Organize metrics into a 3x2 grid
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="Longest Run [km]", value=weekly_longest_dist, delta=None)

with col2:
    st.metric(label="Running Time [mins]", value=weekly_total_time, delta=round((weekly_total_time - average_total_time),2))

with col3:
    st.metric(label="Distance [km]", value=weekly_total_dist, delta=round((weekly_total_dist - average_total_dist),2))

with col1:
    st.metric(label="Elevation Gain [m]", value=weekly_total_elevation, delta=round((weekly_total_elevation - average_total_elevation),2))

with col2:
    st.metric(label="Average Speed [mins/km]", value=weekly_speed, delta=round((weekly_speed - average_total_speed),2))
