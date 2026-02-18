# Importamos librerías

from pathlib import Path
from datetime import datetime
import pandas as pd
import numpy as np
from IPython.display import display
import matplotlib.pyplot as plt
import seaborn as sns

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
    print(f"El tiempo dedicado del paso 3 a confirm es: {media_paso4}")
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

def save_data_clean_excel(df, nombre):
    """
    Guarda un dataframe desde notebooks/ y lo guarda en data/cleaned/, 
    si no existe, crea el directorio.

    :param df: dataframe que se quiere guardar como .xlsx
    :param nombre: nombre que tomará el archivo
    """
    out_dir = DATA_CLEAN_DIR
    out_dir.mkdir(parents=True, exist_ok=True)

    ts = datetime.now().strftime("%Y%m%d_%H%M")
    out_path = out_dir / f"{ts}_{nombre}.xlsx"
    df = df.drop_duplicates()
    df.to_excel(out_path, index=False, engine="openpyxl")
    print(f"Guardado: {out_path}")
    return "ok"

def informe(x):
    print("Información del DataFrame:")
    print(x.info())
    print("Descripción estadística:")
    print(x.describe())
    print("Valores nulos:")
    print(x.isnull().sum())
    print("Tipos de datos:")
    print(x.dtypes)
    print("Primeras 5 filas:")
    print(x.head())
    print("Últimas 5 filas:")
    print(x.tail())
    print("Forma del DataFrame:")
    print(x.shape)
    print("columnas")
    print(x.columns)

def datos(x):
    print("datos nulos")
    print(x.isnull().sum())
    print("datos totales")
    print(x.count())   
    print("porcentaje de nulos")
    print(x.isnull().sum() / x.shape[0]*100)
    print("datos duplicados")
    print(x.duplicated().sum())


def eliminar_na(df):
    """
    Toma un dataframe y elimina NaN
    """
    cols = ["clnt_tenure_yr","clnt_tenure_mnth","gendr","num_accts","bal","calls_6_mnth","logons_6_mnth"]
    df = df.dropna(subset=cols)
    return df

def cliente_principal(df):
    """
    Discretiza clnt_age, define el cliente principal para análisis demográfico.
    """
    mode_calls = df["calls_6_mnth"].mode()[0]
    mode_logons = df["logons_6_mnth"].mode()[0]
    # Nota: usamos >= moda (no ==) para mantener la logica usada en Tableau.
    df_client_mode = df[
        (df["logons_6_mnth"] >= mode_logons) & (df["calls_6_mnth"] >= mode_calls)
    ].copy()

    # Bins fijos (no dependen del min/max del subset) para evitar cortes raros
    age_bins = [0.0, 30.0, 50.0, np.inf]
    age_labels = ["Young", "Medium", "Old"]
    df_client_mode.loc[:, "Age_category"] = pd.cut(
        df_client_mode["clnt_age"],
        bins=age_bins,
        labels=age_labels,
        include_lowest=True,
    )

    tenure_bins = [0.0, 15.0, 35.0, np.inf]
    tenure_labels = ["New", "Established", "Loyal"]
    df_client_mode.loc[:, "Years_category"] = pd.cut(
        df_client_mode["clnt_tenure_yr"],
        bins=tenure_bins,
        labels=tenure_labels,
        include_lowest=True,
    )

    q1 = df_client_mode["bal"].quantile(0.25)
    high_value_client = df_client_mode[df_client_mode["bal"] > q1].copy()
    high_value_client.loc[:, "Age_category"] = high_value_client["Age_category"].astype(
        str
    )
    high_value_client.loc[:, "Years_category"] = high_value_client[
        "Years_category"
    ].astype(str)
    return high_value_client

def visual_pie_chart_age(df, show=True):
    """
    Toma df de high_value_client y devuelve fig, ax para visualización.
    Por defecto visualiza; show=False si se quiere fig, ax solo.
    """
    freq = df["Age_category"].value_counts()
    colors = sns.color_palette("Set3", n_colors=len(freq))

    fig, ax = plt.subplots(figsize=(6, 6))
    freq.plot.pie(autopct="%1.1f%%", startangle=45, colors=colors, ax=ax)
    ax.set_ylabel("")

    if show:
        plt.show()

    return fig, ax

def visual_pie_chart_tenure_yr(df, show=True):
    """
    Toma df de high_value_client y devuelve fig, ax para visualización.
    Por defecto visualiza; show=False si se quiere fig, ax solo.
    """
    freq= df["Years_category"].value_counts()
    colors = sns.color_palette("Set3", n_colors=len(freq))

    fig, ax = plt.subplots(figsize=(6, 6))
    freq.plot.pie(autopct="%1.1f%%", startangle=45, colors=colors, ax=ax)
    ax.set_ylabel("")

    if show:
        plt.show()
    
    return fig, ax

def visual_tabla_cruzada_age_years(df, normalize="row", show=True):
    """
    Tabla cruzada (Years_category x Age_category) para analizar combinaciones tipo:
    - Dentro de `New`, cuantos son `Old`.

    Params:
    - normalize: "row" (por defecto) para % por Years_category, o None para conteos.
    - show: muestra el plot si True.

    Returns:
    - counts: DataFrame de conteos.
    - row_pct: DataFrame de % por fila (0-100).
    - fig, ax: figura y ejes del heatmap.
    """
    required_cols = {"Age_category", "Years_category"}
    missing = required_cols - set(df.columns)
    if missing:
        raise KeyError(f"Faltan columnas requeridas: {sorted(missing)}")

    counts = pd.crosstab(df["Years_category"], df["Age_category"])
    row_pct = counts.div(counts.sum(axis=1), axis=0).mul(100).round(1)

    if normalize == "row":
        heatmap_data = row_pct
        fmt = ".1f"
        title = "Years_category x Age_category (% por Years_category)"
    elif normalize is None:
        heatmap_data = counts
        fmt = "d"
        title = "Years_category x Age_category (conteos)"
    else:
        raise ValueError('normalize debe ser "row" o None')

    fig, ax = plt.subplots(figsize=(7, 4))
    sns.heatmap(heatmap_data, annot=True, fmt=fmt, cmap="Oranges", ax=ax)
    ax.set_title(title)
    ax.set_xlabel("Age_category")
    ax.set_ylabel("Years_category")

    if show:
        plt.show()

    return counts, row_pct, fig, ax

def visualizacion_test_1(finish_control, finish_test, show=True):
    """
    Visualiza el numero de usuarios que finalizan (confirm) por grupo.

    `finish_control` y `finish_test` deben ser Series/arrays de 0/1 (por client_id).
    """
    labels = ["Control", "Test"]
    valores = [int(finish_control.sum()), int(finish_test.sum())]

    fig, ax = plt.subplots(figsize=(5, 4))
    bars = ax.bar(labels, valores, color=["gray", "blue"])
    ax.set_ylabel("Num usuarios que finalizan")
    ax.set_title("Usuarios que finalizan por grupo")
    ax.bar_label(bars, padding=3)

    if show:
        plt.show()

    return fig, ax


def filtro_y_tasa(df1, df2):
    """
    Filtra dos dfs y devuelve tasa de finalización llamando a la función tasa_finalizacion.
    También devuelve los df para experimento: df_control y df_test
    :param df1: dataframe con variation
    :param df2: dataframe con client_id
    """
    test = df1[df1["Variation"]=="Test"]
    control = df1[df1["Variation"]=="Control"]
    # Filtramos grupo de control
    
    df_control = df2[df2["client_id"].isin(control["client_id"])]
    df_test = df2[df2["client_id"].isin(test["client_id"])]

    # Tasa finalización

    tasa_finalizacion_control = tasa_finalizacion(df_control)
    tasa_finalizacion_test = tasa_finalizacion(df_test)

    return tasa_finalizacion_control, tasa_finalizacion_test, df_control, df_test

def visualizacion_test_2(df, show=True):
    """
    Histograma de `time_to_confirm_seconds` por `Variation`.
    Devuelve (fig, ax).
    """
    fig, ax = plt.subplots(figsize=(7, 4))

    sns.histplot(
        data=df,
        x="time_to_confirm_seconds",
        hue="Variation",
        kde=True,
        stat="density",
        common_norm=False,
        bins=30,
        ax=ax,
    )

    ax.set_title("Time to confirm (seconds)")

    if show:
        plt.show()

    return fig, ax

def visualizacion_test_3(df, show=True):
    
    fig, ax = plt.subplots(figsize=(7, 4))
    sns.histplot(data=df, x="clnt_age", hue="Variation", kde=True, element="step", ax=ax)
    ax.set_title(f"Distribución de Edad")

    if show:
        plt.show()

    return fig, ax

def visualizacion_test_4(df, show=True):
    fig, ax = plt.subplots(figsize=(7, 4))
    sns.boxplot(data=df, x="Variation", y="clnt_tenure_yr", palette="Set2")
    ax.set_title("Comparación de Permanencia en Años")
    if show:
        plt.show()
    return fig, ax
