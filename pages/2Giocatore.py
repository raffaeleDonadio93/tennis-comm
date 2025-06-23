import streamlit as st
from streamlit.components.v1 import html
from library import *

BASE_DIR = Path("operations/output/rounds")

st.set_page_config(page_title="📋 Dettaglio Giocatore", layout="wide")

round_selected = "round_1"  # Fisso per ora, puoi renderlo dinamico
turni = get_turni(BASE_DIR / round_selected)

# Carica tutti i dati fino all'ultimo turno
df_all = pd.DataFrame()
for turno in turni:
    df = load_turno_csv(round_selected, turno)
    if df is not None:
        df_all = pd.concat([df_all, df], ignore_index=True)

# Estrai giocatori
giocatori = sorted(set(df_all["Player 1"]).union(df_all["Player 2"]))
giocatore = st.selectbox("Seleziona un giocatore", giocatori)

# Partite giocate
giocate = df_all[df_all["Vincitore"].notna() & (df_all["Vincitore"] != "")]
giocate_player = giocate[(giocate["Player 1"] == giocatore) | (giocate["Player 2"] == giocatore)]

# Partite future
future = df_all[df_all["Vincitore"].isna() | (df_all["Vincitore"] == "")]
future_player = future[(future["Player 1"] == giocatore) | (future["Player 2"] == giocatore)]

tab1, tab2, tab3 = st.tabs(["🕹️ Partite Giocate", "📅 Partite Future", "📈 Statistiche"])

with tab1:
    if giocate_player.empty:
        st.info("Nessuna partita giocata finora.")
    else:
        for _, row in giocate_player.iterrows():
            vincitore = row['Vincitore']
            p1, p2 = row['Player 1'], row['Player 2']

            # Evidenzia il vincitore
            style_p1 = (
                "font-weight: 800; color: #2e7d32;" if p1 == vincitore else
                "font-weight: 600; color: #b71c1c;"
            )
            style_p2 = (
                "font-weight: 800; color: #2e7d32;" if p2 == vincitore else
                "font-weight: 600; color: #b71c1c;"
            )

            # Estrai set
            sets = [estrai_punteggio(row[f'Set {i}']) for i in range(1, 4)]

            # Conta set vinti
            set_vinti_p1 = sum(1 for s1, s2 in sets if s1 is not None and s2 is not None and s1 > s2)
            set_vinti_p2 = sum(1 for s1, s2 in sets if s1 is not None and s2 is not None and s2 > s1)

            # Calcola punti
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

            # Format set lines
            set_line_p1 = " ".join(str(s[0]) if s[0] is not None else "-" for s in sets)
            set_line_p2 = " ".join(str(s[1]) if s[1] is not None else "-" for s in sets)

            # HTML rendering
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
                      <div>{row['Data']} • {row['Orario']}</div>
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

with tab2:
    if future_player.empty:
        st.info("Nessuna partita futura trovata.")
    else:
        for _, row in future_player.iterrows():
            avversario = row["Player 2"] if row["Player 1"] == giocatore else row["Player 1"]
            turno = row.get("Turno", "Turno sconosciuto")  # Recupera il turno

            st.markdown(f"""
                <div style="background: #fffbe6; padding: 14px 18px; border-radius: 12px; margin-bottom: 12px;">
                    <strong>{giocatore}</strong> vs <strong>{avversario}</strong><br>
                    🔁 <strong>Turno: {turno}</strong><br>
                   
                </div>
            """, unsafe_allow_html=True)

with tab3:
    # Classifica generale
    ultimo_turno = turni[-1]
    classifica = calcola_classifica_punti(round_selected, ultimo_turno)

    if giocatore in classifica["Giocatore"].values:
        stats = classifica[classifica["Giocatore"] == giocatore].iloc[0]
        st.success(f"🏆 **Posizione in classifica:** {classifica[classifica['Giocatore'] == giocatore].index[0] + 1}")
        st.metric("🎯 Punti Totali", stats["Punti"])
        st.metric("🎾 Partite Giocate", stats["Partite Giocate"])
    else:
        st.warning("Il giocatore non ha ancora punti registrati.")
