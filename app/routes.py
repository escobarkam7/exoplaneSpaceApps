from fastapi import APIRouter
from .db import get_connection

router = APIRouter()

# Columnas útiles por tabla
USEFUL_COLS = {
    "kepler": ["kepid", "kepoi_name", "kepler_name", "koi_disposition", "koi_period", "koi_prad", "koi_teq", "koi_steff"],
    "k2planets": ["k2_name", "k2_disposition", "k2_period", "k2_prad", "k2_teq", "k2_steff"],
    "tess": ["toi", "tid", "tfopwg_disp", "pl_orbper", "pl_rade", "pl_eqt", "st_teff"]
}

# Columnas numéricas para convertir a float
NUMERIC_COLS = ["koi_period", "koi_prad", "koi_teq", "koi_steff", 
                "k2_period", "k2_prad", "k2_teq", "k2_steff",
                "pl_orbper", "pl_rade", "pl_eqt", "st_teff"]

@router.get("/planets/{dataset}")
def read_planets(dataset: str, limit: int = 50):
    """
    Devuelve las primeras 'limit' filas de la tabla seleccionada
    """
    if dataset not in USEFUL_COLS:
        return {"error": "Dataset no válido. Usa: kepler, k2planets o tess"}
    
    conn = get_connection()
    cur = conn.cursor()
    
    # Ejecuta la consulta
    cur.execute(f"SELECT * FROM {dataset}_raw LIMIT %s;", (limit,))
    rows = cur.fetchall()
    
    # Nombres de columnas en la tabla
    colnames = [desc[0] for desc in cur.description]
    conn.close()

    results = []
    for row in rows:
        row_dict = {}
        for i, value in enumerate(row):
            col = colnames[i]
            if col not in USEFUL_COLS[dataset]:
                continue  # saltar columnas que no queremos
            if col in NUMERIC_COLS and value is not None and value != '':
                try:
                    row_dict[col] = float(value)
                except ValueError:
                    row_dict[col] = value
            else:
                row_dict[col] = value
        results.append(row_dict)

    return {
        "dataset": dataset,
        "limit": limit,
        "total": len(results),
        "data": results
    }

@router.get("/datasets")
def list_datasets():
    """Devuelve la lista de datasets disponibles"""
    return {"datasets": list(USEFUL_COLS.keys())}