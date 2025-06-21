import streamlit as st
import pandas as pd
import os
import plotly.express as px
from pathlib import Path

BASE_DIR = Path("operations/output/elo")

def get_rounds():
    rounds = sorted([d.name for d in BASE_DIR.iterdir() if d.is_dir() and d.name.startswith("round")])
    return rounds

def get_turni(round_dir):
    turni = sorted([f.stem for f in round_dir.glob("turno_*.csv")])
    return turni

@st.cache_data
def load_turno_csv(round_name, turno_name):
    filepath = BASE_DIR / round_name / f"{turno_name}.csv"
    if not filepath.exists():
        return None
    df = pd.read_csv(filepath)
    for col in ["Elo iniziale 1", "Elo iniziale 2", "Elo 1 Finale", "Elo 2 Finale"]:
        if col not in df.columns:
            if "iniziale" in col:
                df[col] = 1500.0
            else:
                df[col] = pd.NA
    return df

def estrai_giocatori(df):
    return sorted(set(df["Player 1"]).union(df["Player 2"]))

def calcola_classifica_aggregata(round_name, turno_name):
    round_num = int(round_name.split("_")[1])
    turno_num = int(turno_name.split("_")[1])

    rounds = get_rounds()
    df_all = pd.DataFrame()

    for r in rounds:
        r_num = int(r.split("_")[1])
        if r_num > round_num:
            break
        round_path = BASE_DIR / r
        turni = get_turni(round_path)

        for t in turni:
            t_num = int(t.split("_")[1])
            if r_num == round_num and t_num > turno_num:
                break
            df_turno = load_turno_csv(r, t)
            if df_turno is not None:
                df_all = pd.concat([df_all, df_turno], ignore_index=True)

    # Solo partite giocate (con vincitore)
    df_giocate = df_all[df_all["Vincitore"].notna() & (df_all["Vincitore"] != "")]

    elo_finali = {}
    partite_giocate = {}

    for player in pd.unique(df_all[["Player 1", "Player 2"]].values.ravel()):
        elo1 = df_all.loc[df_all["Player 1"] == player, "Elo 1 Finale"]
        elo2 = df_all.loc[df_all["Player 2"] == player, "Elo 2 Finale"]
        elo_finale = pd.concat([elo1, elo2]).max()
        elo_finali[player] = elo_finale if pd.notnull(elo_finale) else 1500

        # Conta partite giocate come Player 1 o Player 2
        count1 = df_giocate[df_giocate["Player 1"] == player].shape[0]
        count2 = df_giocate[df_giocate["Player 2"] == player].shape[0]
        partite_giocate[player] = count1 + count2

    df_classifica = pd.DataFrame({
        "Giocatore": list(elo_finali.keys()),
        "Elo finale": list(elo_finali.values()),
        "Partite Giocate": [partite_giocate[p] for p in elo_finali.keys()]
    })
    df_classifica = df_classifica.sort_values(by="Elo finale", ascending=False).reset_index(drop=True)
    return df_classifica

# -- Streamlit app --

st.set_page_config(page_title="🎾 Tennis Elo Dashboard", layout="wide")
st.title("🎾 Tennis Elo Dashboard")

rounds = get_rounds()
round_selected = st.sidebar.selectbox("Seleziona Round", rounds)

turni = get_turni(BASE_DIR / round_selected)
turno_selected = st.sidebar.selectbox("Seleziona Turno", turni)

df_turno = load_turno_csv(round_selected, turno_selected)

if df_turno is None:
    st.error("Dati turno non trovati.")
    st.stop()

# Dividi partite già giocate da quelle future
df_giocate = df_turno[df_turno["Vincitore"].notna() & (df_turno["Vincitore"] != "")]
df_future = df_turno[df_turno["Vincitore"].isna() | (df_turno["Vincitore"] == "")]

tab1, tab2, tab3 = st.tabs(["Partite Giocate", "Prossime Partite", "Classifica Elo"])

with tab1:
    st.subheader(f"Partite già giocate - {round_selected} {turno_selected}")
    st.dataframe(df_giocate[[
        "Data", "Orario", "Luogo", "Player 1", "Player 2",
        "Set 1", "Set 2", "Set 3", "Vincitore", "Superficie",
        "Elo iniziale 1", "Elo iniziale 2", "Elo 1 Finale", "Elo 2 Finale"
    ]], use_container_width=True)

    if not df_giocate.empty:
        df_plot = pd.DataFrame({
            "Giocatore": list(df_giocate["Player 1"]) + list(df_giocate["Player 2"]),
            "Elo Iniziale": list(df_giocate["Elo iniziale 1"]) + list(df_giocate["Elo iniziale 2"]),
            "Elo Finale": list(df_giocate["Elo 1 Finale"]) + list(df_giocate["Elo 2 Finale"])
        }).drop_duplicates(subset=["Giocatore"])

        df_melted = df_plot.melt(id_vars="Giocatore", value_vars=["Elo Iniziale", "Elo Finale"],
                                 var_name="Tipo Elo", value_name="Punteggio Elo")

        fig = px.line(df_melted, x="Tipo Elo", y="Punteggio Elo", color="Giocatore",
                      markers=True,
                      title=f"Andamento Elo - {round_selected} {turno_selected}",
                      labels={"Tipo Elo": "Fase", "Punteggio Elo": "Elo"})
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Nessuna partita giocata ancora in questo turno.")

with tab2:
    st.subheader(f"Prossime partite da giocare - {round_selected} {turno_selected}")
    st.dataframe(df_future[[
        "Data", "Orario", "Luogo", "Player 1", "Player 2",
        "Set 1", "Set 2", "Set 3", "Vincitore", "Superficie"
    ]], use_container_width=True)
    st.info("Le partite senza vincitore sono da giocare.")

with tab3:
    st.subheader(f"Classifica Elo Aggregata fino a {round_selected} {turno_selected}")
    df_classifica = calcola_classifica_aggregata(round_selected, turno_selected)

    fig2 = px.bar(
        df_classifica,
        x="Giocatore",
        y="Elo finale",
        color="Giocatore",
        title="Classifica Elo Cumulativa",
        text="Elo finale"
    )
    fig2.update_traces(textposition='outside')
    fig2.update_layout(yaxis=dict(range=[min(df_classifica["Elo finale"]) - 10, max(df_classifica["Elo finale"]) + 10]))

    st.plotly_chart(fig2, use_container_width=True)

    st.dataframe(df_classifica[["Giocatore", "Elo finale", "Partite Giocate"]], use_container_width=True)
