import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns
import plotly.express as px
import streamlit as st

# Titre de l'app
st.title("Analyse des émissions de CO2 par pays")

# Charger le DataFrame (caché pour performance)
@st.cache_data
def load_df():
    return pd.read_csv('CO2_per_capita_cleaned.csv')
    #return pd.read_csv('../student-challenges/curriculum/03-Data-Analysis/05-Dashboards-with-Plotly-Dash-Streamlit/01-Challenges/01-Plotly-CO2-emissions/data/CO2_per_capita_cleaned.csv')

df = load_df()
st.success(f"DataFrame chargé : {df.shape[0]:,} lignes, {df.shape[1]} colonnes")
st.dataframe(df.head())  # Aperçu des données

# Sidebar pour interactions (exemples avec vos fonctions précédentes)
st.sidebar.header("Options")
start_year = st.sidebar.slider("Année de début", 1960, 2011, 2008)
end_year = st.sidebar.slider("Année de fin", 1960, 2011, 2011)
nb_countries = st.sidebar.slider("Top pays", 5, 20, 10)

# Appel de votre fonction top_n_emitters
if 'top_n_emitters' not in st.session_state:
    def top_n_emitters(df, start_year=2008, end_year=2011, nb_displayed=10):
        # Filtrer par années
        df_filtered = df[(df['Year'] >= start_year) & (df['Year'] <= end_year)]
        
        # Calculer la moyenne des émissions de CO2 par pays
        df_mean = df_filtered.groupby('Country Name')['CO2 Per Capita (metric tons)'].mean().reset_index()
        df_mean.columns = ['Country Name', 'CO2 Per Capita (metric tons)']  # Renommer pour cohérence
        
        # Trier décroissant et garder les top N
        df_top = df_mean.nlargest(nb_displayed, 'CO2 Per Capita (metric tons)')
        
        # Créer le bar plot
        fig = px.bar(df_top, x='CO2 Per Capita (metric tons)', y='Country Name',
                    orientation='h',  # Horizontal pour lisibilité
                    title=f'Top {nb_displayed} émetteurs de CO2 par habitant ({start_year}-{end_year})',
                    labels={'CO2 Per Capita (metric tons)': 'Émissions CO2 par habitant (tonnes métriques)'})
        
        fig.update_layout(yaxis={'categoryorder':'total ascending'})  # Tri par valeur décroissante
        return fig
    pass

if st.sidebar.button("Top émetteurs (Bar plot)"):
    fig_bar = top_n_emitters(df, start_year, end_year, nb_countries)
    st.plotly_chart(fig_bar, width='stretch') #use_container_width=True

# Agréger les émissions totales par pays et par année (population implicite via per capita, mais somme pour taille)
df_plot = df.groupby(['Country Code', 'Year', 'Country Name'])['CO2 Per Capita (metric tons)'].sum().reset_index()
df_plot.rename(columns={'CO2 Per Capita (metric tons)': 'Total CO2 Emissions'}, inplace=True)

# Bouton Carte animée
if st.sidebar.button("Carte animée"):
    with st.spinner("Préparation de la carte..."):
        # Agréger UNIQUEMENT quand bouton cliqué (optimisé)
        df_plot = df.groupby(['Country Code', 'Year', 'Country Name'])['CO2 Per Capita (metric tons)'].sum().reset_index()
        df_plot.rename(columns={'CO2 Per Capita (metric tons)': 'Total CO2 Emissions'}, inplace=True)
        
        fig = px.scatter_geo(df_plot,
                             locations='Country Code',
                             size='Total CO2 Emissions',
                             animation_frame='Year',
                             hover_name='Country Name',
                             size_max=40,
                             projection='natural earth',
                             title='Émissions de CO2 par pays (animé par année)',
                             labels={'Total CO2 Emissions': 'Émissions totales CO2 (tonnes)',
                                     'Year': 'Année'})
        
        st.plotly_chart(fig, width='stretch') #use_container_width=True
    pass
