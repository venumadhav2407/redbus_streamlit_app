# streamlit app 
# create a virtual environment
# python -m venv myenv
# myenv\Scripts\activate

from sqlite3 import connect
import streamlit as st
import pandas as pd
from datetime import datetime

# db connection
conn = connect("redbus_db.db")
curr = conn.cursor()
data = curr.execute('select * from redbus_details;').fetchall()

# fetch data
def fetch_data(from_, to_):
    sql = f"SELECT * from redbus_details where route_name = '{from_} to {to_}' order by route_name;"
    
    details = pd.read_sql(sql, conn)
    return details



# creata dataframe
df = pd.DataFrame(data, columns=['id','Bus_Name', 'Route_Name',  'Bus_Type',
       'Departing_Time', 'Duration', 'Reaching_Time', 'Star_Rating', 'Price',
       'Seat_Availability', 'Route_Link'])

st.set_page_config(layout="centered",page_icon=":material/directions_bus:",page_title="Online Bus Ticket Booking Project", initial_sidebar_state="expanded",
                   menu_items={'About': "# Online bus ticket booking app!"})

# header
st.markdown("# :red[Online Bus Tickets Booking]")
st.info("Ride with Pride, Anywhere, Anytime!", icon=':material/directions_bus:')
st.divider()


    

# sidebar 
with st.sidebar.form("user"):
    
    # define state
    if "_from_" not in st.session_state:
        st.session_state._from_ = None

    if "_to_" not in st.session_state:
        st.session_state._to_ = None
            
            
    
    # from
    route_name = df['Route_Name'].unique()
    from_ = list(set(i.split(" to ")[0] for i in route_name))
    from_.sort()
    user_source = st.selectbox(":red[ :material/directions_bus: **From**]", from_, key='_from_', index=None)
    
   

    # to
    to_ = list(set(i.split(" to ")[1] for i in route_name))
    to_.sort()
    user_destination = st.selectbox(":red[ :material/directions_bus:  **To**]", to_, key='_to_', index=None)
    
   
    
    submitted = st.form_submit_button(" :material/search:  Search buses", type="primary", use_container_width=True)
 


# check the condition 
if (st.session_state._from_ is not None) and ( st.session_state._to_ is not None):
    
    
    bus_data = fetch_data(st.session_state._from_, st.session_state._to_)
    
    with st.sidebar.container(height=300):

        tab1, tab2, tab3  = st.tabs(["Rating", "Price", "Bus Type"])

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
        
        
    
    # Display route and total buses information
    col1, col2 = st.columns([3,1])
    col1.write(f"Route : {st.session_state._from_} --> {st.session_state._to_}")
    col2.write(f"Total Buses : {len(bus_data)}")   
    
    
    # load the data is bus_data is not empty
    if not bus_data.empty: 

    
        with st.container():
                        
            for index, row in bus_data.iterrows():
                            
                with st.expander(f"{row['bus_name']}", expanded=True, icon=":material/directions_bus:"):
                    st.link_button(f" {row['bus_name']} :material/link:", row['route_link'])
                    
                    # split the two half
                    col1, col2 = st.columns([3,1])
                    
                    col1.write(f" **{row['departing_time']}** :grey[--->] {row['reaching_time']} ")
                    col1.write(f" **{row['duration']}** ")
                    col1.write(f"{row['bus_type']}")
                    
                    col2.write(f" ### :green[:material/currency_rupee:]  {row['price']}")
                    col2.write(f" :red[:material/star_rate:] {row['star_rating']}")
                    col2.write(f"{row['seat_availability']} Seats")
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
    


    
    





            


    


