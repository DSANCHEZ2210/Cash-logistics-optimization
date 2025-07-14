import pandas as pd
import matplotlib.pyplot as plt

# --- Cargar archivo Excel ---
file_path = "resumen_costos_semanales_V2.xlsx"
df = pd.read_excel(file_path)

# --- Eliminar fila de totales si existe ---
df = df[df["tienda"] != "Costos_Columna"]
df.reset_index(drop=True, inplace=True)

# --- Seleccionar columnas de costos de viaje ---
cols_costos_viaje = [col for col in df.columns if "costo_viaje_" in col]

# --- Calcular el total de costos de viaje por tienda ---
df["costo_total_viaje"] = df[cols_costos_viaje].sum(axis=1)

# --- Graficar ---
plt.figure(figsize=(14, 6))
plt.bar(df["tienda"].astype(str), df["costo_total_viaje"], color='darkorange')
plt.title("Costo total de viaje semanal por tienda")
plt.xlabel("Tienda")
plt.ylabel("Costo total ($)")
plt.xticks(rotation=90)
plt.tight_layout()
plt.grid(axis='y')
plt.show()
