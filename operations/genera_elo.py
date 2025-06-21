import pandas as pd
import os
from glob import glob

# Configurazioni
rounds_folder = "output/rounds"  # cartella con i CSV originali (round_X/turno_Y.csv)
output_folder = "output/elo"    # cartella dove salvare i file con Elo aggiornati
elo_iniziale = 1500
k_elo = 32

# Funzione aggiornamento Elo
def elo_update(rating_a, rating_b, score_a, k=k_elo):
    expected_a = 1 / (1 + 10 ** ((rating_b - rating_a) / 400))
    return rating_a + k * (score_a - expected_a)

# Carica e ordina file csv per round e turno
def ordina_file(rounds_folder):
    files = []
    for round_path in sorted(glob(os.path.join(rounds_folder, "round_*"))):
        for file in sorted(glob(os.path.join(round_path, "turno_*.csv"))):
            files.append(file)
    return files

# Inizializza Elo di tutti i giocatori
def init_elo(df_all_matches):
    players = pd.unique(df_all_matches[["Player 1", "Player 2"]].values.ravel())
    elo_dict = {player: elo_iniziale for player in players}
    return elo_dict

# Legge tutti i csv in un unico DataFrame per inizializzare i giocatori
def carica_tutti_i_matches(files):
    dfs = []
    for f in files:
        dfs.append(pd.read_csv(f))
    return pd.concat(dfs, ignore_index=True)

# Calcola Elo progressivamente e riscrive i csv aggiornati
def calcola_elo(files):
    df_all = carica_tutti_i_matches(files)
    elo_dict = init_elo(df_all)

    os.makedirs(output_folder, exist_ok=True)

    for file in files:
        df = pd.read_csv(file)
        df_updated = df.copy()

        for i, row in df.iterrows():
            p1 = row["Player 1"]
            p2 = row["Player 2"]
            vincitore = str(row["Vincitore"]).strip()

            # Se vincitore mancante, salta partita
            if vincitore == "" or vincitore.lower() == "nan":
                continue

            # Salva Elo iniziale prima della partita
            df_updated.loc[i, "Elo iniziale 1"] = round(elo_dict[p1], 2)
            df_updated.loc[i, "Elo iniziale 2"] = round(elo_dict[p2], 2)

            # Calcola punteggi risultati per aggiornamento Elo
            if vincitore == p1:
                score_p1 = 1
                score_p2 = 0
            elif vincitore == p2:
                score_p1 = 0
                score_p2 = 1
            else:
                score_p1 = 0.5
                score_p2 = 0.5

            # Aggiorna Elo
            elo_p1_new = elo_update(elo_dict[p1], elo_dict[p2], score_p1)
            elo_p2_new = elo_update(elo_dict[p2], elo_dict[p1], score_p2)

            elo_dict[p1] = elo_p1_new
            elo_dict[p2] = elo_p2_new

            # Salva Elo finale dopo la partita
            df_updated.loc[i, "Elo 1 Finale"] = round(elo_p1_new, 2)
            df_updated.loc[i, "Elo 2 Finale"] = round(elo_p2_new, 2)

        # Costruisci percorso output simile al percorso input
        rel_path = os.path.relpath(file, rounds_folder)
        output_path = os.path.join(output_folder, rel_path)

        # Assicurati che la cartella esista
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Salva il CSV aggiornato
        df_updated.to_csv(output_path, index=False)
        print(f"Aggiornato e salvato: {output_path}")

# Esecuzione
files_ordinati = ordina_file(rounds_folder)
calcola_elo(files_ordinati)
