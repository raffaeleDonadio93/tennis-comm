import streamlit as st
import pandas as pd
import os
import plotly.express as px
from pathlib import Path
from streamlit.components.v1 import html

BASE_DIR = Path("operations/output/elo")

def get_rounds():
    rounds = sorted([d.name for d in BASE_DIR.iterdir() if d.is_dir() and d.name.startswith("round")])
    return rounds

def get_turni(round_dir):
    turni = sorted([f.stem for f in round_dir.glob("turno_*.csv")])
    return turni


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
st.title("🎾 Dashboard")

rounds = get_rounds()
round_selected = st.selectbox("Seleziona Round", rounds)

turni = get_turni(BASE_DIR / round_selected)
turno_selected = st.selectbox("Seleziona Turno", turni)

df_turno = load_turno_csv(round_selected, turno_selected)

if df_turno is None:
    st.error("Dati turno non trovati.")
    st.stop()

# Dividi partite già giocate da quelle future
df_giocate = df_turno[df_turno["Vincitore"].notna() & (df_turno["Vincitore"] != "")]
df_future = df_turno[df_turno["Vincitore"].isna() | (df_turno["Vincitore"] == "")]

tab1, tab2, tab3 = st.tabs(["Partite Giocate", "Prossime Partite", "Classifica Elo"])

with tab1:

    st.subheader(f"🎾 Partite già giocate al round: {round_selected.split('_')[1]} - turno: {turno_selected.split('_')[1]}")

    if df_giocate.empty:
        st.info("Nessuna partita giocata ancora in questo turno.")
    else:
        for _, row in df_giocate.iterrows():
            vincitore = row['Vincitore']
            p1, p2 = row['Player 1'], row['Player 2']

            # Evidenzia il vincitore
            style_p1 = "font-weight: 600; color: #222;" if p1 == vincitore else "color: #999;"
            style_p2 = "font-weight: 600; color: #222;" if p2 == vincitore else "color: #999;"

            # Set
            s1 = row['Set 1'] if pd.notna(row['Set 1']) else "-"
            s2 = row['Set 2'] if pd.notna(row['Set 2']) else "-"
            s3 = row['Set 3'] if pd.notna(row['Set 3']) else "-"

            html_card = f"""
            <div style="width: 100%; display: flex; justify-content: flex-start;">
              <div style="
                  border-radius: 22px;
                  padding: 16px 20px;
                  margin-bottom: 14px;
                  background: linear-gradient(135deg, #f9f9f9, #ffffff);
                  box-shadow: 0 2px 20px rgba(0, 0, 0, 0.05);
                  font-family: 'Segoe UI', sans-serif;
                  width: 100%;
                  max-width: 620px;
                  max-height: 620px;
              ">
                <div style="display: flex; justify-content: space-between; margin-bottom: 12px; font-size: 15px; color: #777;">
                  <div>📍 <strong>{row['Luogo']}</strong></div>
                  <div>{row['Data']} • {row['Orario']}</div>
                  <div>{row['Superficie']}</div>
                </div>
            
                <div style="display: flex; justify-content: space-between; align-items: center;">
                  <!-- Giocatori con Elo sotto il nome -->
                  <div style="width: 40%; display: flex; flex-direction: column; justify-content: space-between;">
                    <div style="{style_p1} font-size: 15px;">
                      {p1}
                      <div style="font-size: 12px; color: #555; margin-top: 4px;">
                        Elo: {int(row['Elo iniziale 1'])} → <strong>{int(row['Elo 1 Finale'])}</strong>
                      </div>
                    </div>
            
                    <div style="{style_p2} font-size: 15px; margin-top: 10px;">
                      {p2}
                      <div style="font-size: 12px; color: #555; margin-top: 4px;">
                        Elo: {int(row['Elo iniziale 2'])} → <strong>{int(row['Elo 2 Finale'])}</strong>
                      </div>
                    </div>
                  </div>
            
                  <!-- Set -->
                  <div style="width: 30%; text-align: center;">
                    <div style="font-size: 16px;"><strong>{s1}</strong></div>
                    <div style="font-size: 16px;"><strong>{s2}</strong></div>
                    <div style="font-size: 16px;"><strong>{s3}</strong></div>
                  </div>
            
                  <!-- Spazio vuoto per bilanciare layout (rimuoviamo Elo qui) -->
                  <div style="width: 30%;"></div>
                </div>
              </div>
            </div>

            """
            html(html_card, height=200)
with tab2:
    st.subheader(f"Prossime partite da giocare al round: {round_selected.split('_')[1]} - turno: {turno_selected.split('_')[1]}")
    if df_future.empty:
        st.info("Non ci sono altre partite in programma per questo turno.")
    else:
        cols = st.columns(len(df_future))

        for idx, (i, row) in enumerate(df_future.iterrows()):
            with cols[idx]:
                st.markdown(
                    f"""
                    <div style="border:1px solid #ccc; padding:15px; border-radius:10px; text-align:center;">
                        <p style="font-weight:bold; font-size:26px;">
                            {row['Player 1']}<br>
                            <span style="font-size:18px; color:#555;">vs</span><br>
                            {row['Player 2']}
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )



with tab3:
    st.subheader(f"Classifica Elo Aggregata fino al round {round_selected.split('_')[1]} - turno: {turno_selected.split('_')[1]}")
    df_classifica = calcola_classifica_aggregata(round_selected, turno_selected)


    cols = st.columns(len(df_classifica))

    for idx, row in df_classifica.iterrows():
        with cols[idx]:
            st.markdown(
                f"""
                <div style="
                    border: 1px solid #ccc;
                    border-radius: 12px;
                    padding: 16px;
                    margin: 5px;
                    background: linear-gradient(135deg, #f0f4f8, #d9e2ec);
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    text-align: center;
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                ">
                    <div style="font-weight: 700; font-size: 18px; margin-bottom: 8px;">{row['Giocatore']}</div>
                    <div style="font-size: 14px; color: #333;">Elo finale: <strong>{row['Elo finale']}</strong></div>
                    <div style="font-size: 14px; color: #555;">Partite giocate: {row['Partite Giocate']}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

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


