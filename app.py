import streamlit as st
import pandas as pd
import plotly.express as px

# 1. CONFIGURATION DE LA PAGE
st.set_page_config(
    page_title="Dashboard Camping La Civelle",
    page_icon="⛺",
    layout="wide"
)

# 2. FONCTION DE CHARGEMENT ET NETTOYAGE
@st.cache_data
def load_data():
    file_path = 'cleaned_data_camping.csv'
    
    # Test de lecture avec différents séparateurs (virgule puis point-virgule)
    try:
        df = pd.read_csv(file_path, sep=',')
        if len(df.columns) < 2: # Si pandas ne voit qu'une seule colonne, le séparateur est faux
            df = pd.read_csv(file_path, sep=';')
    except:
        df = pd.read_csv(file_path, sep=';')

    # Nettoyage des noms de colonnes (enlève les espaces et sauts de ligne)
    df.columns = df.columns.str.replace('\n', ' ').str.strip()

    # Mappage forcé des noms de colonnes si nécessaire
    # On s'assure que 'Revenue_HT' existe même si le CSV a gardé l'ancien nom
    rename_dict = {
        'Montant Séjours HT': 'Revenue_HT',
        'Montant\nSéjours HT': 'Revenue_HT',
        'Montant_HT': 'Revenue_HT'
    }
    df.rename(columns=rename_dict, inplace=True)

    # Conversion des données numériques et gestion des vides
    numeric_cols = ['Nuits', 'Nuitées', 'Séjours', 'Revenue_HT']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    if 'ANNEE' in df.columns:
        df['ANNEE'] = pd.to_numeric(df['ANNEE'], errors='coerce').fillna(0).astype(int)

    return df

# Chargement effectif
df = load_data()

# 3. TITRE ET STYLE
st.title("⛺ Dashboard de Pilotage - Camping La Civelle")
st.markdown("---")

# 4. BARRE LATÉRALE (FILTRES)
st.sidebar.header("⚙️ Paramètres d'affichage")

if 'ANNEE' in df.columns:
    annees_dispos = sorted(df['ANNEE'].unique(), reverse=True)
    annee_selected = st.sidebar.selectbox("Année à analyser", annees_dispos)
else:
    st.error("La colonne 'ANNEE' est introuvable dans le fichier.")
    st.stop()

mois_order = ['JANVIER', 'FÉVRIER', 'MARS', 'AVRIL', 'MAI', 'JUIN', 
              'JUILLET', 'AOÛT', 'SEPTEMBRE', 'OCTOBRE', 'NOVEMBRE', 'DÉCEMBRE']

# 5. CALCUL DES INDICATEURS (KPI)
data_annee = df[df['ANNEE'] == annee_selected]
total_ca = data_annee['Revenue_HT'].sum()
total_nuitees = data_annee['Nuitées'].sum()
total_sejours = data_annee['Séjours'].sum()

# Comparaison N-1
data_n_1 = df[df['ANNEE'] == annee_selected - 1]
ca_n_1 = data_n_1['Revenue_HT'].sum()
evol_ca = ((total_ca - ca_n_1) / ca_n_1 * 100) if ca_n_1 > 0 else 0

# 6. AFFICHAGE DES MÉTRIQUES EN COLONNES
col1, col2, col3, col4 = st.columns(4)
col1.metric("Chiffre d'Affaires HT", f"{total_ca:,.2f} €", f"{evol_ca:+.1f}% vs N-1")
col2.metric("Nuitées", f"{int(total_nuitees):,}")
col3.metric("Séjours", f"{int(total_sejours):,}")
col4.metric("Panier Moyen", f"{ (total_ca/total_sejours if total_sejours > 0 else 0):.2f} €")

st.markdown("### 📈 Analyses Graphiques")

# 7. GRAPHIQUES
row2_col1, row2_col2 = st.columns(2)

with row2_col1:
    st.write("**Saisonnalité du Chiffre d'Affaires (€)**")
    # On prépare les données pour que tous les mois s'affichent dans l'ordre
    df_saison = df.groupby(['ANNEE', 'MOIS'], observed=True)['Revenue_HT'].sum().reset_index()
    fig_ca = px.line(df_saison, x='MOIS', y='Revenue_HT', color='ANNEE',
                     category_orders={"MOIS": mois_order}, markers=True,
                     labels={'Revenue_HT': 'CA HT (€)', 'MOIS': 'Mois'})
    st.plotly_chart(fig_ca, use_container_width=True)

with row2_col2:
    st.write("**Répartition du CA par Type de Forfait**")
    top_tarifs = data_annee.groupby('Tarif')['Revenue_HT'].sum().sort_values(ascending=False).head(8).reset_index()
    fig_pie = px.pie(top_tarifs, values='Revenue_HT', names='Tarif', hole=0.4,
                     color_discrete_sequence=px.colors.sequential.RdBu)
    st.plotly_chart(fig_pie, use_container_width=True)

# 8. TABLEAU DE DONNÉES
with st.expander("🔍 Voir le détail des données brutes"):
    st.dataframe(data_annee, use_container_width=True)

st.sidebar.info(f"Données chargées : {len(df)} lignes.")
