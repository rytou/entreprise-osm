import streamlit as st
import requests
import plotly.graph_objects as go

st.set_page_config(page_title="Entreprises OSM", layout="wide")
st.title("Répartition des entreprises par secteur d’activité")

ville = st.selectbox("Choisir une ville", ["Toronto", "Ottawa"])

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

data = get_osm_data(ville)

secteurs = {}
for el in data["elements"]:
    tags = el.get("tags", {})
    for k in ["shop", "office", "craft"]:
        if k in tags:
            secteur = tags[k]
            secteurs[secteur] = secteurs.get(secteur, 0) + 1

# Liste des secteurs "pertinents" à afficher par défaut
secteurs_valides = {
    "bakery", "hairdresser", "florist", "supermarket", "pharmacy", "butcher",
    "optician", "clothes", "restaurant", "books", "lawyer", "car_repair",
    "dry_cleaning", "dentist", "insurance", "bank", "electronics", "tailor",
    "beauty", "cafe", "variety_store", "furniture", "chemist", "doctor"
}

if secteurs:
    defaut = [s for s in secteurs if s in secteurs_valides]

    secteurs_choisis = st.multiselect(
        "Filtrer par secteur",
        options=list(secteurs.keys()),
        default=defaut if defaut else list(secteurs.keys())
    )

    data_filtrée = {k: v for k, v in secteurs.items() if k in secteurs_choisis}

    fig = go.Figure(data=[
        go.Bar(
            x=list(data_filtrée.keys()),
            y=list(data_filtrée.values()),
            text=list(data_filtrée.values()),
            textposition='outside',
            marker_color='lightskyblue'
        )
    ])

    fig.update_layout(
        title=f"Entreprises à {ville} (secteurs filtrés)",
        xaxis_title="Secteur",
        yaxis_title="Nombre",
        xaxis_tickangle=-45,
        template="plotly_dark",
        height=600,
        margin=dict(t=60, l=40, r=40, b=120)
    )

    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Aucune entreprise trouvée.")
