# streamlit app 
from sqlite3 import connect
import streamlit as st
import pandas as pd
from datetime import datetime

# db connection
conn = connect("redbus_db.db")
curr = conn.cursor()
data = pd.read_sql('select * from redbus_details;', conn)

# fetch data
def fetch_data(from_, to_):
    sql = f"SELECT * from redbus_details where route_name = '{from_} to {to_}' order by route_name;"
    
    details = pd.read_sql(sql, conn)
    return details


    

st.set_page_config(layout="centered",page_icon=":material/directions_bus:",page_title="Online Bus Ticket Booking Project", initial_sidebar_state="expanded",
                   menu_items={'About': "# Online bus ticket booking app!"})

# header
st.markdown("# :red[Online Bus Tickets Booking]")
st.info("Ride with Pride, Anywhere, Anytime!", icon=':material/directions_bus:')
st.divider()

# initialize the state variable
if "source" not in st.session_state:
    st.session_state._from_ = []

if "destination" not in st.session_state:
    st.session_state._to_ = []
    
if "state" not in st.session_state:
    st.session_state.state = None
    
if "from_city" not in st.session_state:
    st.session_state.from_city = None
  
    
if "to_city" not in st.session_state:
    st.session_state.to_city = None  
    
    

def update_routes():
    """Callback to update 'From' and 'To' routes based on selected state."""
    if st.session_state.state:
        route_name = data[data['state'] == st.session_state.state]['route_name'].unique()
        source = sorted(list(set(i.split(" to ")[0] for i in route_name)))
        destination = sorted(list(set(i.split(" to ")[1] for i in route_name)))
        st.session_state.source = source
        st.session_state.destination = destination
    else:
        st.session_state.source = []
        st.session_state.destination = []

# states list
list_of_states = data['state'].unique()
state_li = st.sidebar.selectbox("**Select the State**", list_of_states, index=None, key="state", on_change=update_routes)
# sidebar 
with st.sidebar.form("form"):
      

    user_source = st.selectbox(":red[ :material/directions_bus: **From**]", st.session_state.source, key='from_city', index=None)
    
    user_destination = st.selectbox(":red[ :material/directions_bus:  **To**]", st.session_state.destination, key='to_city', index=None)
    
   
    submitted = st.form_submit_button(" :material/search:  Search buses", type="secondary", use_container_width=True)
 

# check the condition 
if (st.session_state.from_city is not None) and (st.session_state.to_city is not None):
    
    
    bus_data = fetch_data(st.session_state.from_city, st.session_state.to_city)
    
    with st.sidebar.container(height=300):

        tab1, tab2, tab3, tab4  = st.tabs(["Rating", "Price", "Bus Type", "Time"])

        # rating_options = {
        #     1: tab1.checkbox("⭐ 1", key="rating_1"),
        #     2: tab1.checkbox("⭐⭐ 2", key="rating_2"),
        #     3: tab1.checkbox("⭐⭐⭐ 3", key="rating_3"),
        #     4: tab1.checkbox("⭐⭐⭐⭐ 4", key="rating_4"),
        #     5: tab1.checkbox("⭐⭐⭐⭐⭐ 5", key="rating_5")
        # }
        # # Get selected ratings
        # selected_ratings = [rating for rating, checked in rating_options.items() if checked]
        
    
        rating = tab1.radio(":red[ :material/star_rate:]  **Rating**", ["⭐ 1", "⭐⭐ 2", "⭐⭐⭐ 3", "⭐⭐⭐⭐ 4", "⭐⭐⭐⭐⭐ 5"],index=None   ,  horizontal=False)
        if rating:
            rating = int(rating.split()[1])
            bus_data = bus_data[bus_data['star_rating'] <= rating].sort_values(by='star_rating', ascending=False)

        # --------------- tab2-------------
        # filter the bus details by price
        price_range = tab2.slider(" :green[:material/currency_rupee:] **Price Range**", min_value=100, max_value=5000,
                                  value=(),step=100)
        
        
        # Filter the bus data by the selected price range
        filtered_data  = bus_data[(bus_data['price'] >= price_range[0]) & (bus_data['price'] <= price_range[1])]

        # Dropdown for sorting order
        sort_order = tab2.selectbox("Sort By",["Low to High", "High to Low"])
        
        
        # Sort the filtered data based on the user's selection
        if sort_order == "Low to High":
            bus_data = filtered_data.sort_values(by='price', ascending=True)
        else:
            bus_data = filtered_data.sort_values(by='price', ascending=False)
            
        # ----------------- tab3 --------------
        # bus type
        bus_type = tab3.radio("Select Bus Type", options=["SEATER", "SLEEPER", "AC", "NONAC"],index=None)
        
        # Filtering based on the selected bus type
        if bus_type == "SEATER":
            bus_data = bus_data[bus_data['bus_type'].str.contains('Seater', case=False)]
        elif bus_type == "SLEEPER":
            bus_data = bus_data[bus_data['bus_type'].str.contains('Sleeper', case=False)]
        elif bus_type == "AC":
            bus_data = bus_data[bus_data['bus_type'].str.contains('AC|A/C', case=False)]
        elif bus_type == "NONAC":
            bus_data = bus_data[bus_data['bus_type'].str.contains('Non AC|NON A/C', case=False)]
        
        
        # ------------------- tab4 -------------------
        # Time filter
        time_filter = tab4.radio("Select Time", options=["Morning", "Afternoon ", "Evening", "Night"],
                               captions=["06:00 - 12:00","12:00 - 18:00", "18:00 - 24:00", "00:00 - 06:00"]  , index=None, horizontal=True)
        
        if time_filter == "Morning":
            bus_data = bus_data[(bus_data['departing_time'] >= '06:00') & (bus_data['departing_time'] <= '12:00')]
        elif time_filter == "Afternoon":
            bus_data = bus_data[(bus_data['departing_time'] >= '12:00') & (bus_data['departing_time'] <= '18:00')]
        elif time_filter == "Evening":
            bus_data = bus_data[(bus_data['departing_time'] >= '18:00') & (bus_data['departing_time'] <= '24:00')]
        elif time_filter == "Night":
            bus_data = bus_data[(bus_data['departing_time'] >= '00:00') & (bus_data['departing_time'] <= '06:00')]

        



    # Display route and total buses information
    col1, col2 = st.columns([3,1])
    col1.write(f"Route : {st.session_state.from_city} --> {st.session_state.to_city}")
    col2.write(f"Total Buses : {len(bus_data)}")   
    
    
    # load the data is bus_data is not empty
    if not bus_data.empty: 

    
        st.dataframe(bus_data.drop(columns=['id','state'], axis=1), hide_index=True, column_config={
            "route_link" : st.column_config.LinkColumn("route_link"),
            "price" : st.column_config.NumberColumn("price", format="₹ %d")
        })            
     
    else:
        st.markdown(
            """
            <div style="text-align: center;">
                <h1>Oops!!</h1>
                <p style="font-size:50px">No Buses Found</p>
            </div>
            """,
            unsafe_allow_html=True
            )

                      
else:
    st.warning("""  # Select the routes to find the buses.... """)
    


    
    





            


    


