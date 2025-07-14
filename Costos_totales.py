import pandas as pd
from glob import glob

# --- Configuración ---
dias = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
archivo_costos = lambda d: f"costos_transporte_{d}.csv"
archivo_resultados = lambda d: f"resultado_{d}.csv"

# --- Diccionario para almacenar datos por tienda ---
datos_tienda = {}

# --- Procesamiento por día ---
for dia in dias:
    # Cargar archivos
    try:
        df_costos = pd.read_csv(archivo_costos(dia))
        df_resultados = pd.read_csv(archivo_resultados(dia))
    except FileNotFoundError:
        print(f"Archivo faltante para {dia}, se omite...")
        continue

    # Agrupar costo de viajes por tienda origen
    costos_por_tienda = df_costos.groupby("origen")["costo_viaje"].sum()

    # Extraer cobros_operaciones por tienda
    cobros_operaciones = df_resultados.set_index("tienda")["cobros_operaciones"]

    # Guardar en diccionario
    for tienda in set(costos_por_tienda.index).union(cobros_operaciones.index):
        if tienda not in datos_tienda:
            datos_tienda[tienda] = []
        datos_tienda[tienda].append(costos_por_tienda.get(tienda, 0))
        datos_tienda[tienda].append(cobros_operaciones.get(tienda, 0))

# --- Construir DataFrame final ---
columnas = []
for dia in dias:
    columnas.append(f"costo_viaje_{dia}")
    columnas.append(f"cobros_operaciones_{dia}")

df_final = pd.DataFrame.from_dict(datos_tienda, orient="index", columns=columnas)
df_final.index.name = "tienda"

# Calcular columna final de suma de gastos
df_final["suma_total"] = df_final.sum(axis=1)

# --- Exportar ---
df_final.to_csv("resumen_costos_semanales.csv")
print("✅ Archivo 'resumen_costos_semanales.csv' generado correctamente.")
