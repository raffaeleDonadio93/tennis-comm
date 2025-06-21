import pandas as pd
import os

# Leggi il CSV delle partite generate
df_matches = pd.read_csv("output/calendario.csv")

# Valori di default che puoi modificare
default_data = "01/07/2025"
default_orario = "15:00"
default_luogo = "Stadio Centrale"
default_set1 = ""
default_set2 = ""
default_set3 = ""
default_vincitore = ""
default_superficie = "Terra Rossa"

def crea_csv_per_turni_e_round(df, base_folder="output/rounds"):
    # Prendi tutti i round unici
    rounds = df["Round"].unique()

    for round_num in rounds:
        # Cartella per il round
        round_folder = os.path.join(base_folder, f"round_{round_num}")
        os.makedirs(round_folder, exist_ok=True)

        # Filtra le partite di questo round
        df_round = df[df["Round"] == round_num]

        # Prendi tutti i turni di questo round
        turni = df_round["Turno"].unique()

        for turno in turni:
            df_turno = df_round[df_round["Turno"] == turno].copy()

            # Aggiungi colonne con valori di default
            df_turno["Data"] = default_data
            df_turno["Orario"] = default_orario
            df_turno["Luogo"] = default_luogo
            df_turno["Set 1"] = default_set1
            df_turno["Set 2"] = default_set2
            df_turno["Set 3"] = default_set3
            df_turno["Vincitore"] = default_vincitore
            df_turno["Superficie"] = default_superficie

            # Seleziona colonne nell'ordine richiesto
            df_out = df_turno[["Data", "Orario", "Luogo", "Player 1", "Player 2",
                               "Set 1", "Set 2", "Set 3", "Vincitore", "Superficie"]]

            # Salva CSV nel path corretto
            output_path = os.path.join(round_folder, f"turno_{turno}.csv")
            df_out.to_csv(output_path, index=False)
            print(f"CSV generato: {output_path}")

# Esegui la funzione
crea_csv_per_turni_e_round(df_matches)
