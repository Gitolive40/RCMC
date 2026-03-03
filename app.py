import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard La Civelle", layout="wide")

@st.cache_data
def load_data():
    try:
        df = pd.read_csv('cleaned_data_camping.csv', sep=None, engine='python')
    except:
        # En cas d'erreur de lecture, on crée un DataFrame vide avec les bonnes colonnes
        return pd.DataFrame(columns=['ANNEE', 'MOIS', 'Tarif', 'Nuits', 'Nuitées', 'Séjours', 'Revenue_HT'])

    # 1. Nettoyage noms de colonnes
    df.columns = df.columns.str.replace('\n', ' ').str.strip()

    # 2. Identification CA
    for col in df.columns:
        if any(key in col for key in ['Montant', 'Revenue', 'CA', 'HT']):
            df.rename(columns={col: 'Revenue_HT'}, inplace=True)
            break

    # 3. Conversion numérique (Gestion virgules et espaces)
    cols = ['Nuits', 'Nuitées', 'Séjours', 'Revenue_HT']
    for col in cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace(',', '.').str.replace(r'[^\d.]', '', regex=True)
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # 4. Nettoyage des MOIS (Enlève les espaces invisibles et force les majuscules)
    if 'MOIS' in df.columns:
        df['MOIS'] = df['MOIS'].astype(str).str.strip().str.upper()

    if 'ANNEE' in df.columns:
        df['ANNEE'] = pd.to_numeric(df['ANNEE'], errors='coerce').fillna(0).astype(int)

    return df

df = load_data()

# --- FILTRES ---
annees = sorted(df['ANNEE'].unique(), reverse=True)
annee_sel = st.sidebar.selectbox("Sélectionner l'Année", annees)
data_filtree = df[df['ANNEE'] == annee_sel]

# --- AFFICHAGE ---
st.title(f"📊 Dashboard {annee_sel} - Camping La Civelle")

c1, c2, c3 = st.columns(3)
ca = data_filtree['Revenue_HT'].sum()
nuitees = data_filtree['Nuitées'].sum()
sejours = data_filtree['Séjours'].sum()

c1.metric("Chiffre d'Affaires HT", f"{ca:,.2f} €")
c2.metric("Total Nuitées", f"{int(nuitees):,}")
c3.metric("Total Séjours", f"{int(sejours):,}")

st.divider()

# --- GRAPHIQUE SAISONNALITÉ ---
st.subheader("Saisonnalité : Chiffre d'Affaires Mensuel")

mois_ordre = ['JANVIER', 'FÉVRIER', 'MARS', 'AVRIL', 'MAI', 'JUIN', 'JUILLET', 'AOÛT', 'SEPTEMBRE', 'OCTOBRE', 'NOVEMBRE', 'DÉCEMBRE']

# Préparation des données du graphique
df_graph = df.groupby(['ANNEE', 'MOIS'])['Revenue_HT'].sum().reset_index()
# On s'assure que seuls les mois connus sont présents pour éviter les erreurs de tri
df_graph = df_graph[df_graph['MOIS'].isin(mois_ordre)]

if not df_graph.empty:
    fig = px.line(df_graph, 
                  x='MOIS', 
                  y='Revenue_HT', 
                  color='ANNEE', 
                  markers=True,
                  category_orders={"MOIS": mois_ordre},
                  labels={'Revenue_HT': 'CA HT (€)', 'MOIS': 'Mois'})
    
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("⚠️ Pas assez de données pour générer le graphique de saisonnalité.")

# --- TOP FORFAITS ---
st.subheader("Répartition du CA par Type de Forfait")
top_df = data_filtree.groupby('Tarif')['Revenue_HT'].sum().sort_values(ascending=False).head(10).reset_index()
if not top_df.empty:
    fig_bar = px.bar(top_df, x='Revenue_HT', y='Tarif', orientation='h', 
                     color='Revenue_HT', color_continuous_scale='Viridis')
    st.plotly_chart(fig_bar, use_container_width=True)
