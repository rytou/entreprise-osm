import streamlit as st
import requests
import plotly.graph_objects as go
from collections import defaultdict

st.set_page_config(page_title="Entreprises OSM", layout="wide")
st.title("Répartition des entreprises par secteur d’activité")

villes = st.multiselect("Choisir une ou plusieurs villes", ["Toronto", "Ottawa"], default=["Toronto"])

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

secteurs_valides = {
    "bakery", "butcher", "clothes", "shoes", "hairdresser", "beauty",
    "supermarket", "convenience", "florist", "chemist", "pharmacy",
    "optician", "books", "stationery", "gift", "furniture", "electronics",
    "mobile_phone", "computer", "jewelry", "watch", "sports", "toys",
    "dry_cleaning", "laundry", "tailor", "restaurant", "cafe", "fast_food",
    "bar", "pub", "dentist", "doctor", "veterinary", "insurance", "lawyer",
    "bank", "real_estate", "travel_agency", "accountant", "car_repair",
    "car_rental", "bicycle", "garage", "hardware", "doityourself",
    "variety_store", "greengrocer", "ice_cream"
}

ville_secteurs = defaultdict(lambda: defaultdict(int))

for ville in villes:
    data = get_osm_data(ville)
    for el in data["elements"]:
        tags = el.get("tags", {})
        for k in ["shop", "office", "craft"]:
            if k in tags:
                secteur = tags[k]
                ville_secteurs[ville][secteur] += 1

tous_les_secteurs = set()
for secteurs in ville_secteurs.values():
    tous_les_secteurs.update(secteurs.keys())

secteurs_affichables = sorted(s for s in tous_les_secteurs if s in secteurs_valides)
defaut = [s for s in secteurs_affichables if s in secteurs_valides]

st.write("Filtrer par secteur")
col1, col2 = st.columns([1, 5])
with col1:
    if st.button("Tout sélectionner"):
        st.session_state["secteurs_choisis"] = secteurs_affichables

secteurs_choisis = st.multiselect(
    label="",
    options=secteurs_affichables,
    default=st.session_state.get("secteurs_choisis", defaut if defaut else secteurs_affichables),
    key="secteurs_choisis"
)

fig = go.Figure()
for ville in villes:
    data = ville_secteurs[ville]
    filtres = {s: data.get(s, 0) for s in secteurs_choisis}
    fig.add_bar(
        x=list(filtres.keys()),
        y=list(filtres.values()),
        name=ville
    )

fig.update_layout(
    barmode='group',
    title=f"Entreprises par secteur d'activité ({', '.join(villes)})",
    xaxis_title="Secteur",
    yaxis_title="Nombre",
    xaxis_tickangle=-45,
    template="plotly_dark",
    height=600,
    margin=dict(t=60, l=40, r=40, b=120)
)

if villes:
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Veuillez sélectionner au moins une ville.")
