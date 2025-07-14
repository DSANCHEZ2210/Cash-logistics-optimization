import pandas as pd
from modelo_dia import ejecutar_modelo_dia  # Devuelve: costo_total, viajes_realizados, dinero_final

# Cargar datos
flujo = pd.read_csv("flujo_efectivo_semanal.csv")
flujo.columns = flujo.columns.str.strip().str.lower()
resumen_lunes = pd.read_csv("resumen_tiendas_lunes.csv")
tipos = pd.read_csv("tipo_tiendas.csv")  # Contiene columna "tienda" y "tipo_tienda"

# Asegurar índices correctos
flujo.set_index("tienda", inplace=True)
resumen_lunes.set_index("tienda", inplace=True)
# Asegurar nombres correctos
tipos.rename(columns={"TiendaCodigo": "tienda", "TipoTienda": "tipo_tienda"}, inplace=True)
tipos.set_index("tienda", inplace=True)


# Días a simular
dias = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday"]

# Dinero inicial del lunes
dinero_final = resumen_lunes["dinero_inicial"].copy()
MINIMO_OPERACION = 8800

# Acumulador de resultados
resultados = []

for dia in dias:
    print(f"\n===== Día: {dia.capitalize()} =====")
    print("Dinero final (previo al día):")
    print(dinero_final.sort_values(ascending=False))

    entradas = flujo[f"entrada_{dia}"]
    salidas = flujo[f"salida_{dia}"]

    dinero_inicial = (dinero_final * 0.7) + entradas - salidas
    dinero_inicial = dinero_inicial.clip(lower=0)

    total_efectivo = dinero_inicial.sum()
    print(f"Total efectivo circulando al inicio del día {dia.capitalize()}: ${total_efectivo:,.2f}")

    for tienda, valor in dinero_inicial.items():
        if valor < MINIMO_OPERACION:
            print(f"Tienda {tienda} tiene solo ${round(valor, 2)} (por debajo del mínimo operativo)")

    # Crear resumen diario
    # Crear resumen diario correctamente
    # Crear resumen diario correctamente
    resumen_dia = dinero_inicial.reset_index()
    resumen_dia.columns = ["tienda", "dinero_inicial"]

    # Convertir claves a int para evitar errores de tipo
    resumen_dia["tienda"] = resumen_dia["tienda"].astype(int)
    resumen_lunes.index = resumen_lunes.index.astype(int)

    # Añadir ROP y PO
    resumen_dia["rop"] = resumen_dia["tienda"].map(resumen_lunes["rop"])
    resumen_dia["po"] = resumen_dia["tienda"].map(resumen_lunes["po"])

    # Asegurar tipo_tienda correcto
    tipo_tienda_path = "tipo_tiendas.csv"
    tipos = pd.read_csv(tipo_tienda_path)
    tipos.columns = tipos.columns.str.strip().str.lower()
    tipos = tipos.rename(columns={"tiendacodigo": "tienda"})
    tipos = tipos.reset_index(drop=True)  # 🔧 Solución clave
    resumen = resumen.merge(tipos, on="tienda", how="left")


    # Eliminar columna duplicada que causa error ('Tienda' con mayúscula)
    resumen_dia = resumen_dia.drop(columns=["Tienda"])

    # Guardar CSV del día
    resumen_dia.to_csv(f"resumen_tiendas_{dia}.csv", index=False)



    try:
        costo_total, viajes_realizados, dinero_final = ejecutar_modelo_dia(f"resumen_tiendas_{dia}.csv", tipo_tienda_path="tipo_tiendas.csv")
        print(f"Costo total: ${round(costo_total, 2)}")

        resultados.append({
            "día": dia,
            "costo_total": costo_total,
            "viajes_realizados": viajes_realizados,
            "efectivo_total_post_modelo": dinero_final.sum()
        })

    except Exception as e:
        print(f"Error en {dia.capitalize()}: {e}")
        break

# Guardar resultados agregados
pd.DataFrame(resultados).to_csv("resultados_semanales.csv", index=False)
