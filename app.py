import streamlit as st
import pandas as pd

st.set_page_config(page_title="eFootball Championship Manager", layout="wide")
st.title("🎮 eFootball Championship Manager")

# 1. Initialisation des données dans la session Streamlit
if 'players' not in st.session_state:
    st.session_state.players = ["Fallou", "Modou", "Babacar", "Djibril", "Tapha", "Elhadji", "Dame", "Papa"]

if 'matches' not in st.session_state:
    # Exemple de structure pour la Journée 1
    st.session_state.matches = [
        {"journee": 1, "p1": "Fallou", "p2": "Modou", "score1": None, "score2": None, "played": False},
        {"journee": 1, "p1": "Babacar", "p2": "Djibril", "score1": None, "score2": None, "played": False},
        {"journee": 1, "p1": "Tapha", "p2": "Elhadji", "score1": None, "score2": None, "played": False},
        {"journee": 1, "p1": "Dame", "p2": "Papa", "score1": None, "score2": None, "played": False},
    ]

# 2. Onglets de l'application
tab1, tab2, tab3 = st.tabs(["📊 Classement", "⚽ Saisie des Scores", "⚙️ Configuration"])

# --- ONGLET 1 : CLASSEMENT ---
with tab1:
    st.header("🏆 Tableau des Scores")
    
    # Calcul dynamique du classement
    stats = {p: {"Pts": 0, "MJ": 0, "G": 0, "N": 0, "P": 0, "BP": 0, "BC": 0, "DB": 0} for p in st.session_state.players}
    
    for m in st.session_state.matches:
        if m["played"]:
            p1, p2 = m["p1"], m["p2"]
            s1, s2 = m["score1"], m["score2"]
            
            stats[p1]["MJ"] += 1
            stats[p2]["MJ"] += 1
            stats[p1]["BP"] += s1
            stats[p1]["BC"] += s2
            stats[p2]["BP"] += s2
            stats[p2]["BC"] += s1
            
            if s1 > s2:
                stats[p1]["Pts"] += 3
                stats[p1]["G"] += 1
                stats[p2]["P"] += 1
            elif s2 > s1:
                stats[p2]["Pts"] += 3
                stats[p2]["G"] += 1
                stats[p1]["P"] += 1
            else:
                stats[p1]["Pts"] += 1
                stats[p2]["Pts"] += 1
                stats[p1]["N"] += 1
                stats[p2]["N"] += 1

    # Calcul de la différence de buts et conversion en DataFrame
    for p in stats:
        stats[p]["DB"] = stats[p]["BP"] - stats[p]["BC"]
        
    df_leaderboard = pd.DataFrame.from_dict(stats, orient='index')
    df_leaderboard = df_leaderboard.sort_values(by=["Pts", "DB", "BP"], ascending=False)
    
    st.dataframe(df_leaderboard, use_container_width=True)

# --- ONGLET 2 : SAISIE DES SCORES ---
with tab2:
    st.header("📝 Enregistrer les Résultats")
    
    journee_sel = st.selectbox("Choisir la journée", sorted(list(set(m["journee"] for m in st.session_state.matches))))
    
    for idx, m in enumerate(st.session_state.matches):
        if m["journee"] == journee_sel:
            col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 2])
            
            with col1:
                st.write(f"**{m['p1']}**")
            with col2:
                val1 = m["score1"] if m["score1"] is not None else 0
                score1 = st.number_input("Score 1", min_value=0, max_value=20, value=val1, key=f"s1_{idx}", label_visibility="collapsed")
            with col3:
                st.write("VS")
            with col4:
                val2 = m["score2"] if m["score2"] is not None else 0
                score2 = st.number_input("Score 2", min_value=0, max_value=20, value=val2, key=f"s2_{idx}", label_visibility="collapsed")
            with col5:
                st.write(f"**{m['p2']}**")
            
            # Bouton pour valider le match spécifique
            if st.button("Valider ce match", key=f"btn_{idx}"):
                st.session_state.matches[idx]["score1"] = score1
                st.session_state.matches[idx]["score2"] = score2
                st.session_state.matches[idx]["played"] = True
                st.success(f"Match {m['p1']} vs {m['p2']} enregistré !")
                st.rerun()

# --- ONGLET 3 : CONFIGURATION ---
with tab3:
    st.header("👥 Gestion des Joueurs")
    st.write("Joueurs actuels :", ", ".join(st.session_state.players))
    # Tu pourras ajouter ici un algorithme de génération de calendrier automatique (Round Robin)
