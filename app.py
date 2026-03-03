import streamlit as st
import pandas as pd
import plotly.express as px

# Configuration de la page
st.set_page_config(page_title="Dashboard Camping La Civelle", layout="wide")

# Chargement des données
@st.cache_data
def load_data():
    df = pd.read_csv('cleaned_data_camping.csv')
    return df

df = load_data()

st.title("📊 Reporting d'Activité - Camping La Civelle")

# --- BARRE LATÉRALE (Filtres) ---
st.sidebar.header("Filtres")
annee_selected = st.sidebar.selectbox("Sélectionner une année", sorted(df['ANNEE'].unique(), reverse=True))
mois_order = ['JANVIER', 'FÉVRIER', 'MARS', 'AVRIL', 'MAI', 'JUIN', 'JUILLET', 'AOÛT', 'SEPTEMBRE', 'OCTOBRE', 'NOVEMBRE', 'DÉCEMBRE']

# --- CALCUL DES MÉTRIQUES ---
data_annee = df[df['ANNEE'] == annee_selected]
total_ca = data_annee['Revenue_HT'].sum()
total_nuitees = data_annee['Nuitées'].sum()
total_sejours = data_annee['Séjours'].sum()

# Comparaison avec Année N-1 (si disponible)
data_n_minus_1 = df[df['ANNEE'] == annee_selected - 1]
ca_n_1 = data_n_minus_1['Revenue_HT'].sum()
evol_ca = ((total_ca - ca_n_1) / ca_n_1 * 100) if ca_n_1 > 0 else 0

# --- AFFICHAGE DES KPI ---
col1, col2, col3 = st.columns(3)
col1.metric("Chiffre d'Affaires HT", f"{total_ca:,.2f} €", f"{evol_ca:+.1f}% vs N-1")
col2.metric("Total Nuitées", f"{int(total_nuitees)}")
col3.metric("Total Séjours", f"{int(total_sejours)}")

st.divider()

# --- GRAPHIQUES ---
c1, c2 = st.columns(2)

with c1:
    st.subheader("Saisonnalité du Chiffre d'Affaires")
    fig_ca = px.line(df, x='MOIS', y='Revenue_HT', color='ANNEE', 
                     category_orders={"MOIS": mois_order}, markers=True)
    st.plotly_chart(fig_ca, use_container_width=True)

with c2:
    st.subheader("Top 5 des Forfaits (CA)")
    top_tarifs = data_annee.groupby('Tarif')['Revenue_HT'].sum().sort_values(ascending=False).head(5).reset_index()
    fig_pie = px.pie(top_tarifs, values='Revenue_HT', names='Tarif', hole=0.4)
    st.plotly_chart(fig_pie, use_container_width=True)

# --- TABLEAU DE DÉTAILS ---
if st.checkbox("Afficher les données brutes"):
    st.write(data_annee)