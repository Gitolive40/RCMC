import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard La Civelle", layout="wide")

@st.cache_data
def load_data():
    try:
        # Lecture automatique du séparateur
        df = pd.read_csv('cleaned_data_camping.csv', sep=None, engine='python', encoding='utf-8')
    except:
        try:
            df = pd.read_csv('cleaned_data_camping.csv', sep=';', encoding='latin1')
        except:
            st.error("Impossible de lire le fichier CSV. Vérifiez qu'il est bien présent sur GitHub.")
            return pd.DataFrame()

    # --- NETTOYAGE RADICAL DES COLONNES ---
    # On supprime les espaces et on force le renommage par position pour éviter les KeyError
    df.columns = [str(c).strip().upper() for c in df.columns]
    
    # Si après nettoyage on n'a pas les bons noms, on les force par index (position)
    # On suppose l'ordre standard : 0:ANNEE, 1:MOIS, 2:TARIF, 3:NUITS, 4:NUITEES, 5:SEJOURS, 6:REVENUE
    new_names = {}
    if len(df.columns) >= 7:
        actual_cols = df.columns
        new_names = {
            actual_cols[0]: 'ANNEE',
            actual_cols[1]: 'MOIS',
            actual_cols[2]: 'TARIF',
            actual_cols[3]: 'NUITS',
            actual_cols[4]: 'NUITEES',
            actual_cols[5]: 'SEJOURS',
            actual_cols[6]: 'REVENUE_HT'
        }
        df.rename(columns=new_names, inplace=True)

    # Conversion numérique forcée
    for col in ['NUITS', 'NUITEES', 'SEJOURS', 'REVENUE_HT']:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace(',', '.').str.replace(r'[^\d.]', '', regex=True)
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    if 'ANNEE' in df.columns:
        df['ANNEE'] = pd.to_numeric(df['ANNEE'], errors='coerce').fillna(0).astype(int)
    
    if 'MOIS' in df.columns:
        df['MOIS'] = df['MOIS'].astype(str).str.strip().str.upper()

    return df

# Initialisation des données
df = load_data()

if df.empty or 'ANNEE' not in df.columns:
    st.error("Erreur de structure de données. Vérifiez votre fichier CSV.")
    if not df.empty: st.write("Colonnes détectées :", df.columns.tolist())
    st.stop()

# --- INTERFACE ---
st.title("📊 Dashboard Camping La Civelle")

# Filtre année
annees = sorted([a for a in df['ANNEE'].unique() if a > 0], reverse=True)
annee_sel = st.sidebar.selectbox("Sélectionner l'Année", annees)

# Données filtrées
mask = (df['ANNEE'] == annee_sel)
df_year = df[mask]

# --- INDICATEURS ---
c1, c2, c3, c4 = st.columns(4)
ca = df_year['REVENUE_HT'].sum()
nuitées = df_year['NUITEES'].sum()
séjours = df_year['SEJOURS'].sum()
panier = ca / séjours if séjours > 0 else 0

c1.metric("CA HT", f"{ca:,.2f} €")
c2.metric("Nuitées", f"{int(nuitées):,}")
c3.metric("Séjours", f"{int(séjours):,}")
c4.metric("Panier Moyen", f"{panier:.2f} €")

st.divider()

# --- GRAPHIQUE ---
mois_ordre = ['JANVIER', 'FÉVRIER', 'MARS', 'AVRIL', 'MAI', 'JUIN', 'JUILLET', 'AOÛT', 'SEPTEMBRE', 'OCTOBRE', 'NOVEMBRE', 'DÉCEMBRE']

st.subheader("Saisonnalité du Chiffre d'Affaires")
df_plot = df.groupby(['ANNEE', 'MOIS'])['REVENUE_HT'].sum().reset_index()
df_plot = df_plot[df_plot['MOIS'].isin(mois_ordre)]

fig = px.line(df_plot, x='MOIS', y='REVENUE_HT', color='ANNEE', markers=True,
              category_orders={"MOIS": mois_ordre},
              color_discrete_sequence=px.colors.qualitative.Bold)

st.plotly_chart(fig, use_container_width=True)

# Top Tarifs
st.subheader("Top 5 Forfaits (CA)")
top5 = df_year.groupby('TARIF')['REVENUE_HT'].sum().sort_values(ascending=False).head(5).reset_index()
fig_bar = px.bar(top5, x='REVENUE_HT', y='TARIF', orientation='h', color='REVENUE_HT')
st.plotly_chart(fig_bar, use_container_width=True)
