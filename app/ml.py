# =========================
# Exoplanets - Logistic Regression (Kepler, K2, TESS unificado)
# =========================

# --- Importación de librerías ---
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    classification_report, confusion_matrix, ConfusionMatrixDisplay,
    roc_auc_score, roc_curve, auc
)
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import warnings
import os

warnings.filterwarnings("ignore")

class ExoplanetModel:
    def __init__(self):
        self.model = None
        self.preprocessor = None
        self.mission = None
        self.feature_names = None
    
    def train_model(self, csv_path):
        """
        Entrena el modelo con un archivo CSV
        """
        # =========================
        # CARGA Y CONFIGURACIÓN DEL DATASET
        # =========================
        df = pd.read_csv(csv_path, comment="#", low_memory=False)
        print(f"\nArchivo cargado: {csv_path}")
        print("Shape:", df.shape)
        print("Columnas:", df.columns[:10].tolist())

        # --- Detección automática de columna de disposición según archivo
        if "koi_disposition" in df.columns:
            disposition_col = "koi_disposition"
            self.mission = "Kepler"
        elif "disposition" in df.columns:
            disposition_col = "disposition"
            self.mission = "K2"
        elif "tfopwg_disp" in df.columns:
            disposition_col = "tfopwg_disp"
            self.mission = "TESS"
        else:
            raise ValueError("No se encontró ninguna columna de disposición conocida (koi_disposition, disposition, tfopwg_disp).")

        print(f"Misión detectada: {self.mission} (columna '{disposition_col}')")

        # --- Crear target binario desde la columna de disposición ---
        pos = {"CONFIRMED", "CANDIDATE"}
        neg = {"FALSE POSITIVE"}

        mask = df[disposition_col].isin(pos.union(neg))
        df = df[mask].copy()  # nos quedamos con filas etiquetables
        df["is_confirmed"] = np.where(df[disposition_col].isin(pos), 1, 0)

        print("\nDistribución de estados:")
        print(df[disposition_col].value_counts())
        print("\nObjetivo is_confirmed (1=Confirmed/Candidate, 0=False Positive):")
        print(df["is_confirmed"].value_counts())

        TARGET_COLUMN = "is_confirmed"

        # --- Descartar columnas de fuga o identificadores ---
        DROP_COLS = [
            disposition_col, "kepid", "kepoi_name", "kepler_name",
            "koi_pdisposition", "koi_comment", "koi_fittype",
            "tic_id", "toi_id", "planet_name", "comments"
        ]

        # --- Limpiar columnas casi vacías ---
        max_missing_pct = 0.95
        keep_cols = [c for c in df.columns if df[c].isna().mean() <= max_missing_pct]
        df = df[keep_cols]

        # --- Separar X, y ---
        y = df[TARGET_COLUMN].astype(int)
        X = df.drop(columns=[TARGET_COLUMN] + [c for c in DROP_COLS if c in df.columns], errors="ignore")
        
        # Guardar nombres de características para referencia futura
        self.feature_names = X.columns.tolist()

        # --- Tipos ---
        numeric_cols = [c for c in X.columns if pd.api.types.is_numeric_dtype(X[c])]
        categorical_cols = [c for c in X.columns if c not in numeric_cols]

        print(f"\nCaracterísticas numéricas: {len(numeric_cols)}")
        print(f"Características categóricas: {len(categorical_cols)}")

        # --- Pipelines ---
        numeric_pipe = Pipeline(steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler(with_mean=False))
        ])

        categorical_pipe = Pipeline(steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=True))
        ])

        # --- Preprocesamiento combinado ---
        self.preprocessor = ColumnTransformer(
            transformers=[
                ("num", numeric_pipe, numeric_cols),
                ("cat", categorical_pipe, categorical_cols)
            ]
        )

        # --- Modelo de Regresión Logística ---
        log_reg = LogisticRegression(
            max_iter=400,
            class_weight="balanced",
            multi_class="ovr",
            solver="lbfgs",
            n_jobs=-1
        )

        # --- Pipeline completo ---
        self.model = Pipeline(steps=[
            ("preprocess", self.preprocessor),
            ("model", log_reg)
        ])

        # =========================
        # ENTRENAMIENTO Y EVALUACIÓN
        # =========================
        # --- Split (Particiones) estratificado ---
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.20, random_state=42, stratify=y
        )

        # --- Entrenamiento ---
        print("\nEntrenando modelo...")
        self.model.fit(X_train, y_train)

        # --- Evaluación ---
        y_pred = self.model.predict(X_test)
        print("\n== Classification report ==")
        print(classification_report(y_test, y_pred, digits=4, zero_division=0))

        # --- Métricas adicionales ---
        y_probs = self.model.predict_proba(X_test)[:, 1]
        roc_auc = roc_auc_score(y_test, y_probs)
        print(f"AUC-ROC Score: {roc_auc:.2f}")

        print(f"\n✅ Entrenamiento completado correctamente para la misión {self.mission}.")
        
        return {
            "mission": self.mission,
            "accuracy": (y_pred == y_test).mean(),
            "roc_auc": roc_auc,
            "features_used": len(self.feature_names)
        }

    def predict(self, X_new):
        """
        Hacer predicciones con nuevos datos
        """
        if self.model is None:
            raise ValueError("Modelo no entrenado. Llama a train_model primero.")
        
        predictions = self.model.predict(X_new)
        probabilities = self.model.predict_proba(X_new)
        
        return predictions, probabilities

    def save_model(self, filepath="models/exoplanet_model.pkl"):
        """
        Guardar el modelo entrenado
        """
        if self.model is None:
            raise ValueError("No hay modelo para guardar")
        
        # Crear directorio si no existe
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        model_data = {
            'pipeline': self.model,
            'mission': self.mission,
            'feature_names': self.feature_names
        }
        
        joblib.dump(model_data, filepath)
        print(f"✅ Modelo guardado en: {filepath}")

    def load_model(self, filepath="models/exoplanet_model.pkl"):
        """
        Cargar modelo entrenado
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Modelo no encontrado en: {filepath}")
        
        model_data = joblib.load(filepath)
        self.model = model_data['pipeline']
        self.mission = model_data['mission']
        self.feature_names = model_data['feature_names']
        
        print(f"✅ Modelo cargado: {self.mission}")
        print(f"Características: {len(self.feature_names)}")

# Función para entrenar fácilmente
def train_exoplanet_model(dataset_type="KEPLER"):
    """
    Función conveniente para entrenar el modelo
    """
    dataset_map = {
        "KEPLER": "data/KEPLER.csv",
        "K2": "data/K2.csv", 
        "TESS": "data/TESS.csv"
    }
    
    if dataset_type not in dataset_map:
        raise ValueError(f"Dataset debe ser: {list(dataset_map.keys())}")
    
    csv_path = dataset_map[dataset_type]
    
    # Verificar que el archivo existe
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Archivo no encontrado: {csv_path}")
    
    # Entrenar modelo
    model = ExoplanetModel()
    results = model.train_model(csv_path)
    
    # Guardar modelo
    model.save_model()
    
    return model, results

# Ejemplo de uso
if __name__ == "__main__":
    # Entrenar con Kepler
    model, results = train_exoplanet_model("KEPLER")
    print(f"Resultados: {results}")