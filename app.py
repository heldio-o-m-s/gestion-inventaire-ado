import streamlit as st
import pandas as pd

st.set_page_config(page_title="Gestion de Stock - QR", page_icon="📦", layout="centered")

st.title("📦 Gestion de Stock (Google Sheets)")

# Lien d'export CSV direct propre pour la feuille "Inventaire"
SPREADSHEET_ID = "1ik2XHR1hLLFZ39aZqjLnukpYVOAaPrZ1"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:csv&sheet=Inventaire"

@st.cache_data(ttl=5)
def charger_donnees():
    # Lecture directe du flux CSV généré par Google Sheets
    df = pd.read_csv(SHEET_URL)
    
    # Trouver la ligne contenant les vrais en-têtes (Code ID)
    header_idx = None
    for idx, row in df.iterrows():
        if row.astype(str).str.contains('Code ID').any():
            header_idx = idx
            break
            
    if header_idx is not None:
        # Re-formater le DataFrame avec la bonne ligne d'en-tête
        df.columns = df.iloc[header_idx]
        df = df.iloc[header_idx + 1:].reset_index(drop=True)
        
    return df

try:
    df = charger_donnees()
    
    # Supprimer les lignes où 'Code ID' n'est pas renseigné
    if 'Code ID' in df.columns:
        df = df.dropna(subset=['Code ID'])

    operation = st.radio("Opération :", ["Mouvement de Stock (Entrée/Sortie)", "Consulter le Stock"], horizontal=True)

    if operation == "Mouvement de Stock (Entrée/Sortie)":
        type_mvt = st.selectbox("Type de mouvement :", ["SORTIE 🔴", "ENTRÉE 🟢"])
        
        cat_liste = ["Toutes les zones"] + list(df['Catégorie'].dropna().unique()) if 'Catégorie' in df.columns else ["Toutes les zones"]
        cat_choisie = st.selectbox("Zone / Catégorie :", cat_liste)
        
        if cat_choisie != "Toutes les zones":
            df_dispo = df[df['Catégorie'] == cat_choisie]
        else:
            df_dispo = df

        articles_dict = dict(zip(df_dispo['Code ID'].astype(str) + " - " + df_dispo['Article / Description'].astype(str), df_dispo['Code ID']))
        article_selectionne = st.selectbox("Choisir l'article :", list(articles_dict.keys()))
        
        if article_selectionne:
            code_id = articles_dict[article_selectionne]
            ligne = df[df['Code ID'] == code_id].iloc[0]
            
            st.info(f"**Stock actuel :** {ligne['Qté en Stock']} | **Statut :** {ligne['État / Statut']}")
            
            quantite = st.number_input("Quantité :", min_value=1, step=1, value=1)
            
            if st.button("Valider la mise à jour"):
                # Simulation / Mise à jour locale
                idx = df[df['Code ID'] == code_id].index[0]
                stock_actuel = int(pd.to_numeric(df.loc[idx, 'Qté en Stock'], errors='coerce') or 0)
                
                if "SORTIE" in type_mvt:
                    nouveau_stock = max(0, stock_actuel - quantite)
                else:
                    nouveau_stock = stock_actuel + quantite
                
                st.success(f"✅ Entrée/Sortie validée pour **{ligne['Article / Description']}** ! Nouveau stock théorique : **{nouveau_stock}**")

    else:
        st.subheader("📋 Liste des articles en stock")
        recherche = st.text_input("🔍 Rechercher un article ou un code :")
        if recherche:
            df_affiche = df[
                df['Article / Description'].astype(str).str.contains(recherche, case=False, na=False) | 
                df['Code ID'].astype(str).str.contains(recherche, case=False, na=False)
            ]
        else:
            df_affiche = df
            
        cols_a_afficher = [c for c in ['Code ID', 'Article / Description', 'Catégorie', 'Qté en Stock', 'État / Statut'] if c in df.columns]
        st.dataframe(df_affiche[cols_a_afficher], use_container_width=True)

except Exception as e:
    st.error(f"❌ Erreur de chargement : {e}")
