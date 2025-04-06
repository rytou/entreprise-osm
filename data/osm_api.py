import requests
import streamlit as st

@st.cache_data(show_spinner=True)
def get_osm_data(city):
    query = f"""
    [out:json][timeout:25];
    area["name"="{city}"]->.searchArea;
    (
      node["shop"](area.searchArea);
      way["shop"](area.searchArea);
      node["office"](area.searchArea);
      way["office"](area.searchArea);
      node["craft"](area.searchArea);
      way["craft"](area.searchArea);
    );
    out body;
    """
    url = "https://overpass-api.de/api/interpreter"
    response = requests.post(url, data={"data": query})
    return response.json()
