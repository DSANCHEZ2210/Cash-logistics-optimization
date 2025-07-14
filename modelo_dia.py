import pandas as pd
import numpy as np
from pulp import LpMinimize, LpProblem, LpVariable, lpSum, LpBinary, LpStatus, PULP_CBC_CMD

def ejecutar_modelo_dia(path="resumen_tiendas_dia.csv", tipo_tienda_path="tipo_tiendas.csv"):

    # =====================
    # Cargar datos
    # =====================
    resumen = pd.read_csv(path)
    resumen.columns = resumen.columns.str.strip().str.lower()

    tipos = pd.read_csv(tipo_tienda_path)
    tipos.columns = tipos.columns.str.strip().str.lower()

    tipos = tipos.rename(columns={"tiendacodigo": "tienda"})  # asegurar nombre clave
    resumen = resumen.merge(tipos, on="tienda", how="left")

    tiendas_unicas = resumen["tienda"].tolist()
    tienda_to_idx = {tienda: idx for idx, tienda in enumerate(tiendas_unicas)}
    idx_to_tienda = {idx: tienda for tienda, idx in tienda_to_idx.items()}
    n_tiendas = len(tiendas_unicas)

    D0 = resumen["dinero_inicial"].values
    ROP = resumen["rop"].values
    PO = resumen["po"].values
    tipo_tienda = resumen["tipo_tienda"].values
    tiene_bancoppel = [1 if str(tipo).lower() == "coppel" else 0 for tipo in tipo_tienda]

    MINIMO_OPERACION = 8800
    MAX_ENVIO = 100000
    margen_exceso = 10000

    # =====================
    # Modelo
    # =====================
    model = LpProblem("Minimizar_Costo_Transporte", LpMinimize)

    np.random.seed(0)
    distancia = np.random.randint(1, 30, size=(n_tiendas, n_tiendas))
    np.fill_diagonal(distancia, 0)

    x = [[LpVariable(f"x_{i}_{j}", lowBound=0) for j in range(n_tiendas)] for i in range(n_tiendas)]
    y = [[LpVariable(f"y_{i}_{j}", cat=LpBinary) for j in range(n_tiendas)] for i in range(n_tiendas)]
    D = [LpVariable(f"D_{i}", lowBound=0) for i in range(n_tiendas)]
    e = [LpVariable(f"exceso_{i}", lowBound=0) for i in range(n_tiendas)]
    f = [LpVariable(f"falta_{i}", lowBound=0) for i in range(n_tiendas)]
    exceso_bancoppel = [LpVariable(f"exceso_local_{i}", lowBound=0) for i in range(n_tiendas)]

    # ---------------------
    # Función objetivo
    # ---------------------
    model += (
        lpSum((3 * x[i][j] / 1000) + (25 * distancia[i][j] * y[i][j])
            for i in range(n_tiendas) for j in range(n_tiendas) if i != j) +
        lpSum(0.00001 * e[i] for i in range(n_tiendas)) +
        lpSum(1 * f[i] for i in range(n_tiendas)) +
        lpSum(0.001 * exceso_bancoppel[i] for i in range(n_tiendas))
    )

    # ---------------------
    # Restricciones
    # ---------------------
    for i in range(n_tiendas):
        model += D[i] == D0[i] - lpSum(x[i][j] for j in range(n_tiendas) if j != i) + lpSum(x[j][i] for j in range(n_tiendas) if j != i)
        model += D[i] >= MINIMO_OPERACION
        model += D[i] + f[i] >= PO[i]
        model += e[i] >= D[i] - PO[i] - margen_exceso

        model += D[i] <= 250000 + exceso_bancoppel[i]

        if tiene_bancoppel[i]:
            model += exceso_bancoppel[i] >= D[i] - 250000
        else:
            model += exceso_bancoppel[i] == 0

    for i in range(n_tiendas):
        for j in range(n_tiendas):
            if i != j:
                model += x[i][j] <= MAX_ENVIO * y[i][j]
                model += x[i][j] >= MINIMO_OPERACION * y[i][j]

    # =====================
    # Resolver
    # =====================
    model.solve(PULP_CBC_CMD(msg=False))
    print("Estado del modelo:", LpStatus[model.status])
    print(f"Costo total del modelo: ${round(model.objective.value(), 2)}")

    dinero_final_series = pd.Series({idx_to_tienda[i]: D[i].varValue for i in range(n_tiendas)}, name="dinero_final")
    return model.objective.value(), sum(1 for i in range(n_tiendas) for j in range(n_tiendas) if i != j and x[i][j].varValue and x[i][j].varValue > 0), dinero_final_series