import streamlit as st
import folium
from streamlit_folium import st_folium
import osmnx as ox
import networkx as nx

# 1. Setup ya Page
st.set_page_config(page_title="Kigali Smart Traffic", layout="wide")
st.title("🏙️ Kigali Smart Traffic & Navigation System")

@st.cache_resource
def get_graph(place_name):
    # Koresha drive network
    return ox.graph_from_place(place_name, network_type='drive')

G = get_graph("Kigali, Rwanda")

# 2. Session State yo kubika amakuru
if 'map_data' not in st.session_state:
    st.session_state.map_data = {"route": None, "distance": 0, "time": 0, "markers": []}

# 3. Sidebar - Controls
st.sidebar.header("📍 Navigation Settings")
origin = st.sidebar.text_input("Hava (Origin):", "Kigali Heights")
destination = st.sidebar.text_input("Hajya (Destination):", "Kigali City Tower")

if st.sidebar.button("CALCULATE ROUTE"):
    try:
        orig_latlon = ox.geocoder.geocode(origin)
        dest_latlon = ox.geocoder.geocode(destination)
        
        orig_node = ox.distance.nearest_nodes(G, X=orig_latlon[1], Y=orig_latlon[0])
        dest_node = ox.distance.nearest_nodes(G, X=dest_latlon[1], Y=dest_latlon[0])

        # Kubara Shortest Path
        route = nx.shortest_path(G, orig_node, dest_node, weight='length')
        
        # Kubara Distance (km) n'Igihe (minutes - 30km/h average)
        distance = nx.shortest_path_length(G, orig_node, dest_node, weight='length') / 1000
        travel_time = (distance / 30) * 60 

        # Guhindura route mo coordinates
        route_nodes = ox.graph_to_gdfs(G, edges=False).loc[route]
        st.session_state.map_data = {
            "route": list(zip(route_nodes.geometry.y, route_nodes.geometry.x)),
            "distance": round(distance, 2),
            "time": round(travel_time),
            "markers": [orig_latlon, dest_latlon]
        }
    except Exception as e:
        st.sidebar.error(f"Error finding route: {e}")

# 4. Display Info
col1, col2 = st.columns(2)
with col1:
    st.metric("Distance", f"{st.session_state.map_data['distance']} km")
with col2:
    st.metric("Estimated Time", f"{st.session_state.map_data['time']} min")

# 5. Shushanya Ikarita
m = folium.Map(location=[-1.9441, 30.0619], zoom_start=13)

if st.session_state.map_data["route"]:
    folium.PolyLine(st.session_state.map_data["route"], color="blue", weight=6).add_to(m)
    folium.Marker(st.session_state.map_data["markers"][0], popup="Start", icon=folium.Icon(color='green')).add_to(m)
    folium.Marker(st.session_state.map_data["markers"][1], popup="End", icon=folium.Icon(color='red')).add_to(m)

st_folium(m, width=1100, height=500, key="kigali_map")
