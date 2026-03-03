import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard Camping La Civelle", layout="wide")

@st.cache_data
def load_data():
    # Lecture flexible (détection séparateur , ou ;)
    try:
        df = pd.read_csv('cleaned_data_camping.csv', sep=',')
        if len(df.columns) < 2: df = pd.read_csv('cleaned_data_camping.csv', sep=';')
    except:
        df = pd.read_csv('cleaned_data_camping.csv', sep=';')

    # 1. Nettoyage des noms de colonnes
    df.columns = df.columns.str.replace('\n', ' ').str.strip()

    # 2. Identification de la colonne Revenue (même si le nom change)
    # On cherche une colonne qui contient "Montant", "Revenue", "CA" ou "Prix"
    for col in df.columns:
        if any(key in col for key in ['Montant', 'Revenue', 'CA', 'HT', 'Prix']):
            df.rename(columns={col: 'Revenue_HT'}, inplace=True)
            break

    # 3. Traitement des nombres (Gestion des virgules françaises "1200,50")
    cols_numeriques = ['Nuits', 'Nuitées', 'Séjours', 'Revenue_HT']
    for col in cols_numeriques:
        if col in df.columns:
            # On convertit en texte, on remplace la virgule par un point, puis en nombre
            df[col] = df[col].astype(str).str.replace(',', '.').str.replace(' ', '')
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # 4. Forcer l'année en entier
    if 'ANNEE' in df.columns:
        df['ANNEE'] = pd.to_numeric(df['ANNEE'], errors='coerce').fillna(0).astype(int)

    return df

df = load_data()

st.title("📊 Reporting - Camping La Civelle")

# --- FILTRES ---
st.sidebar.header("Filtres")
annees = sorted(df['ANNEE'].unique(), reverse=True)
annee_sel = st.sidebar.selectbox("Année", annees)

# --- CALCULS ---
data = df[df['ANNEE'] == annee_sel]
ca = data['Revenue_HT'].sum()
nuitees = data['Nuitées'].sum()
sejours = data['Séjours'].sum()
panier = ca / sejours if sejours > 0 else 0

# --- AFFICHAGE ---
c1, c2, c3, c4 = st.columns(4)
c1.metric("CA HT Total", f"{ca:,.2f} €")
c2.metric("Nuitées", f"{int(nuitees):,}")
c3.metric("Séjours", f"{int(sejours):,}")
c4.metric("Panier Moyen", f"{panier:.2f} €")

st.divider()

# Graphique Saisonnalité
mois_ordre = ['JANVIER', 'FÉVRIER', 'MARS', 'AVRIL', 'MAI', 'JUIN', 'JUILLET', 'AOÛT', 'SEPTEMBRE', 'OCTOBRE', 'NOVEMBRE', 'DÉCEMBRE']
st.subheader("Évolution Mensuelle du Chiffre d'Affaires")
fig = px.line(df.groupby(['ANNEE', 'MOIS'])['Revenue_HT'].sum().reset_index(), 
             x='MOIS', y='Revenue_HT', color='ANNEE', markers=True,
             category_orders={"MOIS": mois_ordre})
st.plotly_chart(fig, use_container_width=True)

# Affichage des erreurs de colonnes pour debug si besoin
if ca == 0:
    st.warning("⚠️ Le chiffre d'affaires est à 0. Vérifiez que votre fichier contient bien une colonne nommée 'Revenue_HT' ou 'Montant Séjours HT'.")
    if st.checkbox("Voir les colonnes détectées"):
        st.write(df.columns.tolist())
        st.write(df.head())
