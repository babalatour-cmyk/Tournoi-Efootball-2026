import streamlit as st
import pandas as pd

st.set_page_config(page_title="eFootball Championship Manager", layout="wide")
st.title("🎮 eFootball Championship Manager")

# --- 1. INITIALISATION DES DONNÉES ---
if 'players' not in st.session_state:
    st.session_state.players = ["Fallou", "Modou", "Babacar", "Djibril", "Tapha", "Elhadji", "Dame", "Papa"]

if 'matches' not in st.session_state:
    st.session_state.matches = [
        {"journee": 1, "p1": "Fallou", "p2": "Modou", "score1": None, "score2": None, "played": False},
        {"journee": 1, "p1": "Babacar", "p2": "Djibril", "score1": None, "score2": None, "played": False},
        {"journee": 1, "p1": "Tapha", "p2": "Elhadji", "score1": None, "score2": None, "played": False},
        {"journee": 1, "p1": "Dame", "p2": "Papa", "score1": None, "score2": None, "played": False},
    ]

# --- 2. SÉCURITÉ & AUTHENTIFICATION (BARRE LATÉRALE) ---
st.sidebar.header("🔒 Espace Administrateur")
# Définis ton mot de passe ici (change "guediawaye221" par ce que tu veux)
ADMIN_PASSWORD = "guediawaye221" 

if 'is_admin' not in st.session_state:
    st.session_state.is_admin = False

if not st.session_state.is_admin:
    pwd_input = st.sidebar.text_input("Mot de passe pour modifier/déverrouiller", type="password")
    if st.sidebar.button("Connexion"):
        if pwd_input == ADMIN_PASSWORD:
            st.session_state.is_admin = True
            st.sidebar.success("Mode Admin activé ! 🛠️")
            st.rerun()
        else:
            st.sidebar.error("Mot de passe incorrect.")
else:
    st.sidebar.success("🟢 Connecté en tant qu'Admin (Babacar)")
    if st.sidebar.button("Déconnexion"):
        st.session_state.is_admin = False
        st.rerun()

# --- 3. ONGLETS ---
tab1, tab2, tab3 = st.tabs(["📊 Classement", "⚽ Saisie des Scores", "⚙️ Configuration"])

# --- ONGLET 1 : CLASSEMENT ---
with tab1:
    st.header("🏆 Tableau des Scores")
    
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
            
            # Vérification : est-ce que le match est déjà validé ?
            is_locked = m["played"]
            
            with col1:
                st.write(f"**{m['p1']}**")
                
            with col2:
                val1 = m["score1"] if m["score1"] is not None else 0
                # Le champ est bloqué (disabled) si le match est joué OU si l'utilisateur n'est pas Admin
                disable_field = is_locked or not st.session_state.is_admin
                score1 = st.number_input("Score 1", min_value=0, max_value=20, value=val1, key=f"s1_{idx}", label_visibility="collapsed", disabled=disable_field)
                
            with col3:
                st.write("VS")
                
            with col4:
                val2 = m["score2"] if m["score2"] is not None else 0
                score2 = st.number_input("Score 2", min_value=0, max_value=20, value=val2, key=f"s2_{idx}", label_visibility="collapsed", disabled=disable_field)
                
            with col5:
                st.write(f"**{m['p2']}**")
            
            # Gestion des boutons selon le statut du match et les droits d'accès
            col_btn1, col_btn2 = st.columns([1, 1])
            
            # Si le match n'est pas encore joué et que tu es connecté en Admin
            if not is_locked and st.session_state.is_admin:
                if st.button("🔒 Valider et Verrouiller", key=f"btn_{idx}"):
                    st.session_state.matches[idx]["score1"] = score1
                    st.session_state.matches[idx]["score2"] = score2
                    st.session_state.matches[idx]["played"] = True
                    st.success("Match enregistré et définitivement verrouillé ! 🔐")
                    st.rerun()
            
            # Si le match est déjà verrouillé, PERSONNE ne peut le changer, SOUF toi si tu actives ton mode Admin
            elif is_locked:
                st.info(f"🔒 Match validé (Score : {m['score1']} - {m['score2']})")
                if st.session_state.is_admin:
                    if st.button("🔓 Déverrouiller (Admin)", key=f"unlock_{idx}"):
                        st.session_state.matches[idx]["played"] = False
                        st.rerun()
            
            # Si un simple visiteur regarde un match non joué
            elif not st.session_state.is_admin:
                st.warning("Seul Babacar (Admin) peut saisir le score de ce match.")
                
            st.divider()

# --- ONGLET 3 : CONFIGURATION ---
with tab3:
    st.header("👥 Gestion des Joueurs")
    st.write("Joueurs actuels :", ", ".join(st.session_state.players))
