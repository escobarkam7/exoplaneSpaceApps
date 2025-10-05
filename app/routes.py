from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from app.db import get_connection  # ✅ Asegúrate que db.py existe
from app.ml import ExoplanetModel  # ✅ Importar desde ml.py
import pandas as pd
import numpy as np
from io import StringIO
import os

router = APIRouter()

# Columnas útiles por tabla
USEFUL_COLS = {
    "kepler": ["kepid", "kepoi_name", "kepler_name", "koi_disposition", "koi_period", "koi_prad", "koi_teq", "koi_steff"],
    "k2planets": ["pl_name", "hostname", "disposition", "pl_orber", "pl_rade", "pl_eqt", "st_teff", "st_rad", "st_mass", "st_logg", "sy_dist", "disc_year"],  
    "tess": ["toi", "tid", "tfopwg_disp", "pl_orbper", "pl_rade", "pl_eqt", "st_teff"]
}

# Columnas numéricas para convertir a float
NUMERIC_COLS = ["koi_period", "koi_prad", "koi_teq", "koi_steff", 
                "pl_orbper", "pl_rade", "pl_eqt", "st_teff", "st_rad", "st_mass", "st_logg", "sy_dist", "disc_year"]

# Instancia global del modelo
exoplanet_model = ExoplanetModel()

# Cargar modelo al iniciar
try:
    exoplanet_model.load_model("models/exoplanet_model.pkl")
    print("✅ Modelo de exoplanetas cargado exitosamente")
except Exception as e:
    print(f"❌ Error cargando modelo: {e}")
    # No levantamos excepción para permitir que la app inicie

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

@router.post("/classify")
async def classify_exoplanet(file: UploadFile = File(...)):
    try:
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="El archivo debe ser CSV")
        
        # Leer y procesar CSV
        contents = await file.read()
        csv_string = contents.decode('utf-8')
        df = pd.read_csv(StringIO(csv_string))
        
        print(f"📊 CSV cargado: {df.shape}")
        
        # Preprocesamiento (igual que en tu entrenamiento)
        DROP_COLS = [
            "kepid", "kepoi_name", "kepler_name", "koi_pdisposition", 
            "koi_comment", "koi_fittype", "tic_id", "toi_id", 
            "planet_name", "comments"
        ]
        
        # Detectar columna de disposición si existe
        disposition_cols = ["koi_disposition", "disposition", "tfopwg_disp"]
        for col in disposition_cols:
            if col in df.columns:
                DROP_COLS.append(col)
                break
        
        # Limpiar columnas
        keep_cols = [c for c in df.columns if c not in DROP_COLS]
        df_clean = df[keep_cols].copy()
        
        # Hacer predicción
        if exoplanet_model.model is None:
            raise HTTPException(status_code=500, detail="Modelo no disponible")
        
        predictions, probabilities = exoplanet_model.predict(df_clean)
        
        # Formatear resultados
        results = []
        for i, (pred, prob) in enumerate(zip(predictions, probabilities)):
            result = {
                "id": i + 1,
                "prediction": int(pred),
                "prediction_label": "EXOPLANET" if pred == 1 else "FALSE POSITIVE",
                "confidence": float(max(prob)),
                "probability_exoplanet": float(prob[1]),
                "probability_false_positive": float(prob[0])
            }
            results.append(result)
        
        # Estadísticas
        stats = {
            "total_samples": len(predictions),
            "exoplanets_detected": int(sum(predictions)),
            "false_positives": len(predictions) - int(sum(predictions)),
            "confidence_avg": float(np.mean([max(prob) for prob in probabilities])),
            "model_mission": exoplanet_model.mission
        }
        
        return JSONResponse({
            "success": True,
            "predictions": results,
            "statistics": stats,
            "message": f"Procesados {len(predictions)} muestras usando modelo {exoplanet_model.mission}"
        })
        
    except Exception as e:
        print(f"❌ Error en clasificación: {e}")
        raise HTTPException(status_code=500, detail=f"Error procesando archivo: {str(e)}")

@router.post("/train")
async def train_model(dataset_type: str = "KEPLER"):
    """
    Endpoint para entrenar el modelo con diferentes datasets
    """
    try:
        global exoplanet_model
        
        dataset_type = dataset_type.upper()
        valid_datasets = ["KEPLER", "K2", "TESS"]
        
        if dataset_type not in valid_datasets:
            raise HTTPException(
                status_code=400, 
                detail=f"Dataset debe ser uno de: {valid_datasets}"
            )
        
        # Entrenar nuevo modelo
        exoplanet_model = ExoplanetModel()
        results = exoplanet_model.train_model(f"data/{dataset_type}.csv")
        exoplanet_model.save_model()
        
        return {
            "success": True,
            "message": f"Modelo entrenado exitosamente con {dataset_type}",
            "results": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error entrenando modelo: {str(e)}")

@router.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "model_loaded": exoplanet_model.model is not None,
        "model_mission": exoplanet_model.mission if exoplanet_model.model else None,
        "features_count": len(exoplanet_model.feature_names) if exoplanet_model.feature_names else 0
    }

