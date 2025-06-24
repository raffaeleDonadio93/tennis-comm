import streamlit as st
from streamlit.components.v1 import html
from library import *
from pathlib import Path
import pandas as pd

BASE_DIR = Path("operations/output/rounds")
st.set_page_config(page_title="📊 Partite & Classifica", layout="wide")

round_selected = "round_1"
turni = get_turni(BASE_DIR / round_selected)

# Carica tutti i dati fino all'ultimo turno
df_all = pd.DataFrame()
for turno in turni:
    df = load_turno_csv(round_selected, turno)
    if df is not None:
        df_all = pd.concat([df_all, df], ignore_index=True)

# Filtra partite giocate
giocate = df_all[df_all["Vincitore"].notna() & (df_all["Vincitore"] != "")]

tab1, tab2 = st.tabs(["🕹️ Tutte le Partite Giocate", "📈 Classifica Totale"])

# TAB 1: Tutte le partite giocate
with tab1:
    if giocate.empty:
        st.info("Nessuna partita giocata finora.")
    else:
        for _, row in giocate.iterrows():
            vincitore = row['Vincitore']
            p1, p2 = row['Player 1'], row['Player 2']

            style_p1 = "font-weight: 800; color: #2e7d32;" if p1 == vincitore else "font-weight: 600; color: #b71c1c;"
            style_p2 = "font-weight: 800; color: #2e7d32;" if p2 == vincitore else "font-weight: 600; color: #b71c1c;"

            sets = [estrai_punteggio(row[f'Set {i}']) for i in range(1, 4)]
            set_vinti_p1 = sum(1 for s1, s2 in sets if s1 is not None and s2 is not None and s1 > s2)
            set_vinti_p2 = sum(1 for s1, s2 in sets if s1 is not None and s2 is not None and s2 > s1)

            if set_vinti_p1 == 2 and set_vinti_p2 == 0:
                punti_p1, punti_p2 = 3, 0
            elif set_vinti_p1 == 2 and set_vinti_p2 == 1:
                punti_p1, punti_p2 = 2, 1
            elif set_vinti_p1 == 1 and set_vinti_p2 == 2:
                punti_p1, punti_p2 = 1, 2
            elif set_vinti_p1 == 0 and set_vinti_p2 == 2:
                punti_p1, punti_p2 = 0, 3
            else:
                punti_p1 = punti_p2 = "-"

            set_line_p1 = " ".join(str(s[0]) if s[0] is not None else "-" for s in sets)
            set_line_p2 = " ".join(str(s[1]) if s[1] is not None else "-" for s in sets)

            html_card = f"""
              <div style="width: 100%; display: flex; justify-content: flex-start;"> 
                  <div style="
                      border-radius: 10px;
                      padding: 16px 20px;
                      margin-bottom: 14px;
                      background: linear-gradient(135deg, #fff5b7, #fbd72b);
                      box-shadow: 0 2px 20px rgba(0, 0, 0, 0.05);
                      font-family: 'Segoe UI', sans-serif;
                      width: 100%;
                      max-width: 500px;
                  ">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 12px; font-size: 15px; color: #777;">
                      <div>📍 <strong>{row['Luogo']}</strong></div>
                      <div>{row['Data']}</div>
                      <div>{row['Superficie']}</div>
                    </div>

                    <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                      <div style="text-align: left;">
                        <div style="{style_p1} font-size: 18px; margin-bottom: 6px;">{p1}</div>
                        <div style="font-size: 16px; margin-bottom: 10px;">{set_line_p1}</div>

                        <div style="{style_p2} font-size: 18px; margin-bottom: 6px;">{p2}</div>
                        <div style="font-size: 16px;">{set_line_p2}</div>
                      </div>

                      <div style="text-align: right; font-size: 16px; font-weight: bold;">
                        <div style="margin-bottom: 26px;">{punti_p1} pt</div>
                        <div>{punti_p2} pt</div>
                      </div>
                    </div>
                  </div>
                </div>
            """
            html(html_card, height=200)

# TAB 2: Classifica
with tab2:


        # Tutti i giocatori coinvolti nel round
        tutti_giocatori = sorted(set(df_all["Player 1"]).union(df_all["Player 2"]))

        # Calcola la classifica attuale
        ultimo_turno = turni[-1]
        classifica = calcola_classifica_punti(round_selected, ultimo_turno)

        # Aggiungi i giocatori non presenti (con 0 punti e 0 partite)
        classificati = set(classifica["Giocatore"])
        mancanti = [g for g in tutti_giocatori if g not in classificati]

        for g in mancanti:
            classifica = pd.concat([
                classifica,
                pd.DataFrame([{
                    "Giocatore": g,
                    "Punti": 0,
                    "Partite Giocate": 0
                }])
            ], ignore_index=True)

        # Ordina per punti decrescenti, poi nome
        classifica = classifica.sort_values(by=["Punti", "Partite Giocate", "Giocatore"], ascending=[False, False, True]).reset_index(drop=True)


        # Stampa card per ogni giocatore
        for idx, row in classifica.iterrows():
            posizione = idx + 1
            giocatore = row["Giocatore"]
            punti = int(row["Punti"])
            partite = int(row["Partite Giocate"])

            st.markdown(f"""
                <div style="
                    border-radius: 16px;
                    padding: 16px 20px;
                    margin-bottom: 16px;
                    background: linear-gradient(135deg, #fff5b7, #fbd72b);
                    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
                    font-family: 'Segoe UI', sans-serif;
                     max-width: 420px;
                ">
                    <div style="font-size: 18px; font-weight: 700; color: #222;">🔝 {posizione}. {giocatore}</div>
                    <div style="margin-top: 6px; font-size: 15px; color: #444;">🏅 <strong>Punti:</strong> {punti}</div>
                    <div style="font-size: 15px; color: #666;">🎾 <strong>Partite:</strong> {partite}</div>
                </div>
            """, unsafe_allow_html=True)

