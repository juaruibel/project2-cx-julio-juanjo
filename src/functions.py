# Importamos librerías

from pathlib import Path
from datetime import datetime
import pandas as pd
import numpy as np
from IPython.display import display

# Encuentra la raíz del proyecto usando __file__

BASE_DIR = Path(__file__).resolve().parent.parent

# Define la carpeta data_clean/

DATA_CLEAN_DIR = BASE_DIR / "data" / "cleaned"



# Guardar dataframe final como csv en data/cleaned/

def save_data_clean(df, nombre):
    """
    Guarda un dataframe desde notebooks/ y lo guarda en data/cleaned/, 
    si no existe, crea el directorio.

    :param df: dataframe que se quiere guardar como .csv
    :param nombre: nombre que tomará el archivo
    """
    out_dir = DATA_CLEAN_DIR
    out_dir.mkdir(parents=True, exist_ok=True)

    ts = datetime.now().strftime("%Y%m%d_%H%M")
    out_path = out_dir / f"{ts}_{nombre}.csv"
    df.to_csv(out_path, index=False)
    print(f"Guardado: {out_path}")
    return "ok"