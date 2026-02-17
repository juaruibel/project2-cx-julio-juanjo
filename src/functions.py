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
    df = df.drop_duplicates()
    df.to_csv(out_path, index=False)
    print(f"Guardado: {out_path}")
    return "ok"

def load_data_merge(file_merge):
    """
    Carga el .csv limpio del merge para analizar pero manteniendo el tipo:
    c.p como string dado que pandas lo convierte automáticamente a int
    :param file_merge: nombre del archivo para cargar
    """
    path = DATA_CLEAN_DIR / file_merge
    return pd.read_csv(path)

def tasa_finalizacion(df):
    """
    Toma un dataframe y devuelve tasa de finalización.
    """
    # Usuarios únicos que llegan a confirm 
    usuarios_confirm = df[df["process_step"] == "confirm"]
    usuarios_confirm = (df[df["process_step"] == "confirm"][["client_id"]].drop_duplicates())
    num_usuarios_confirm = usuarios_confirm.shape[0]
    # Client id únicos
    num_client_id_unique = df["client_id"].nunique()
    output = round((num_usuarios_confirm/num_client_id_unique)*100, 2)
    return output

def num_usuarios_total_y_confirm(df):
    """
    Toma un dataframe y devuelve tasa de finalización.
    """
    # Usuarios únicos que llegan a confirm 
    usuarios_confirm = df[df["process_step"] == "confirm"]
    usuarios_confirm = (df[df["process_step"] == "confirm"][["client_id"]].drop_duplicates())
    num_usuarios_confirm = usuarios_confirm.shape[0]
    # Client id únicos
    num_client_id_unique = df["client_id"].nunique()
    print(f"Número de usuarios: {num_client_id_unique}")
    print(f"Número de usuarios que finalizan: {num_usuarios_confirm}")
    return num_client_id_unique, num_usuarios_confirm

def tiempo_dedicado(df):
    """
    Toma un dataframe y devuelve el tiempo dedicado de los pasos.
    """
    df["date_time"] = pd.to_datetime(df["date_time"])
    df = df.sort_values(["visitor_id", "visit_id", "date_time"])

    # Fechas y diferencia
    
    df["next_time"] = df.groupby(["client_id","visit_id"])["date_time"].shift(-1)
    df["next_step"] = df.groupby(["client_id","visit_id"])["process_step"].shift(-1)
    df["duration"] = df["next_time"] - df["date_time"]

    # Filtros por step

    start_s1 = df[(df["process_step"] == "start") & (df["next_step"] == "step_1")]
    s1_s2 = df[(df["process_step"] == "step_1") & (df["next_step"] == "step_2")]
    s2_s3 = df[(df["process_step"] == "step_2") & (df["next_step"] == "step_3")]
    s3_confirm = df[(df["process_step"] == "step_3") & (df["next_step"] == "confirm")]
    
    # Medias
    
    media_paso1 = start_s1["duration"].mean()
    media_paso2 = s1_s2["duration"].mean()
    media_paso3 = s2_s3["duration"].mean()
    media_paso4 = s3_confirm["duration"].mean()
    print(f"El tiempo dedicado de start a paso 1 es: {media_paso1}")
    print(f"El tiempo dedicado del paso 1 al paso 2 es: {media_paso2}")
    print(f"El tiempo dedicado del paso 2 al paso 3 es: {media_paso3}")
    print(f"El tiempo dedicado del paso 3 a confirm es: {media_paso1}")
    return media_paso1, media_paso2, media_paso3, media_paso4

def tasa_error(df):
    """
    Toma un df y devuelve la tasa de error:
    Consideramos como tasa de error lo que en la metodología del proyecto es señalado como tal
    sin embargo cabe la posibilidad de considerar como error que next_step sea el mismo paso
    pero sí se contabiliza como transición.
    """

    df["date_time"] = pd.to_datetime(df["date_time"])
    df = df.sort_values(["visitor_id", "visit_id", "date_time"])

    # Fechas y diferencia
    
    df["next_time"] = df.groupby(["client_id","visit_id"])["date_time"].shift(-1)
    df["next_step"] = df.groupby(["client_id","visit_id"])["process_step"].shift(-1)
    df["duration"] = df["next_time"] - df["date_time"]

    # Error

    error1 = df[(df["process_step"] == "step_1") & (df["next_step"] == "start")].shape[0]
    error2 = df[(df["process_step"] == "step_2") & (df["next_step"] == "start")].shape[0]
    error3 = df[(df["process_step"] == "step_2") & (df["next_step"] == "step_1")].shape[0]
    error4 = df[(df["process_step"] == "step_3") & (df["next_step"] == "start")].shape[0]
    error5 = df[(df["process_step"] == "step_3") & (df["next_step"] == "step_1")].shape[0]
    error6 = df[(df["process_step"] == "step_3") & (df["next_step"] == "step_2")].shape[0]
    error_total = error1 + error2 + error3 + error4 + error5 + error6
    total_transiciones = df["next_step"].notna().sum()
    tasa_error = round((error_total / total_transiciones) * 100, 2)
    return tasa_error

def finish(df):
    """
    Toma un dataframe y devuelve el dataframe convirtiendo la columna process_step en bool/int.
    """
    finish = (
        df.groupby("client_id")["process_step"]
        .apply(lambda s: (s == "confirm").any())
        .astype(int)
    )
    return finish

def to_datetime(df):
    """
    Convierte columna en datetime y lo ordena por client_id,
    visit_id, date_time.
    """
    df["date_time"] = pd.to_datetime(df["date_time"])
    df = df.sort_values(["client_id", "visit_id", "date_time"])
    return df

def calcular_tiempo_para_test(df, df2):
    """
    Calcula el tiempo hasta `confirm` por usuario (client_id) para poder
    comparar control vs test.

    Regla usada (A):
    - Se calcula `time_to_confirm` por sesion (client_id, visit_id).
    - Si un client_id confirma en varias sesiones, se toma la PRIMERA sesion
      que confirma (menor `t_confirm`).

    Devuelve dos Series numéricas (segundos) listas para `ttest_ind` y,
    adicionalmente, un dataframe `first_confirm` (una fila por client_id)
    útil para graficar y auditar.

    :param df: dataframe de eventos (debe incluir client_id, visit_id, process_step, date_time)
    :param df2: dataframe de asignacion al experimento (debe incluir client_id, Variation)
    """
    df_events = df.copy()
    df_events["date_time"] = pd.to_datetime(df_events["date_time"])
    df_events = df_events.sort_values(["client_id", "visit_id", "date_time"])

    # t0 por sesion
    t0 = (
        df_events.groupby(["client_id", "visit_id"], as_index=False)["date_time"]
        .min()
        .rename(columns={"date_time": "t0"})
    )

    # t_confirm por sesion (si no hay confirm, quedara NaT tras el merge)
    df_confirm = df_events[df_events["process_step"] == "confirm"]
    t_confirm = (
        df_confirm.groupby(["client_id", "visit_id"], as_index=False)["date_time"]
        .min()
        .rename(columns={"date_time": "t_confirm"})
    )

    sessions = t0.merge(t_confirm, on=["client_id", "visit_id"], how="left")
    sessions["time_to_confirm"] = sessions["t_confirm"] - sessions["t0"]

    # Nos quedamos solo con sesiones que confirman
    sessions_confirm = sessions.dropna(subset=["t_confirm"]).copy()

    # Regla A: primera sesion que confirma por client_id
    first_confirm = (
        sessions_confirm.sort_values(["client_id", "t_confirm"])
        .drop_duplicates(subset=["client_id"], keep="first")
    )

    # Asignacion a control/test
    assignment = df2[["client_id", "Variation"]].drop_duplicates()
    first_confirm = first_confirm.merge(assignment, on="client_id", how="inner")

    # Para t-test: pasar a segundos (float)
    first_confirm["time_to_confirm_seconds"] = (
        first_confirm["time_to_confirm"].dt.total_seconds()
    )

    control_times = first_confirm.loc[
        first_confirm["Variation"] == "Control", "time_to_confirm_seconds"
    ]
    test_times = first_confirm.loc[
        first_confirm["Variation"] == "Test", "time_to_confirm_seconds"
    ]

    return control_times, test_times, first_confirm

def preparar_grupos_experimento(df_exp, df_demo, columna_valor):
    """
    Une los datos del experimento y demografía, y separa los valores por grupo.
    """
    # 1. Merge de los DataFrames
    df_merged = pd.merge(df_exp, df_demo, on='client_id', how='inner')
    
    # 2. Filtrado por grupos para la columna deseada
    test_vals = df_merged[df_merged["Variation"] == "Test"][columna_valor]
    control_vals = df_merged[df_merged["Variation"] == "Control"][columna_valor]
    
    return test_vals, control_vals, df_merged
