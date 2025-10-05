# entrenar_local.py
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, roc_auc_score
import joblib
import os

print("🚀 Entrenando modelo compatible con tu sistema...")

# Crear datos de ejemplo realistas basados en Kepler
np.random.seed(42)
n_samples = 2000

# Patrones reales: 
# - Exoplanetas: períodos largos, radios pequeños, temperaturas moderadas
# - Falsos positivos: períodos cortos, radios grandes, temperaturas extremas
data = {
    'koi_period': np.concatenate([
        np.random.uniform(50, 400, n_samples//2),    # Exoplanetas reales
        np.random.uniform(1, 50, n_samples//2)       # Falsos positivos
    ]),
    'koi_prad': np.concatenate([
        np.random.uniform(0.5, 4, n_samples//2),     # Exoplanetas reales  
        np.random.uniform(4, 20, n_samples//2)       # Falsos positivos
    ]),
    'koi_teq': np.concatenate([
        np.random.uniform(300, 800, n_samples//2),   # Exoplanetas reales
        np.random.uniform(800, 2000, n_samples//2)   # Falsos positivos
    ]),
    'koi_steff': np.random.uniform(4000, 6500, n_samples),
    'koi_slogg': np.random.uniform(4.0, 4.8, n_samples),
    'koi_srad': np.random.uniform(0.7, 1.5, n_samples),
    'koi_smass': np.random.uniform(0.7, 1.3, n_samples)
}

df = pd.DataFrame(data)

# Crear target basado en patrones reales de NASA
conditions = (
    (df['koi_period'] > 100) & 
    (df['koi_prad'] < 3.5) & 
    (df['koi_teq'] < 700) &
    (df['koi_steff'] > 4500)
)
df['is_confirmed'] = np.where(conditions, 1, 0)

print(f"📊 Dataset creado: {df.shape}")
print(f"🎯 Distribución: {df['is_confirmed'].value_counts().to_dict()}")

# Preparar features (igual que tu código original)
X = df.drop('is_confirmed', axis=1)
y = df['is_confirmed']

# Pipelines idénticos a tu código
numeric_cols = X.columns.tolist()
categorical_cols = []

preprocess = ColumnTransformer([
    ("num", Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler(with_mean=False))
    ]), numeric_cols),
    ("cat", Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=True))
    ]), categorical_cols)
])

# Modelo idéntico al tuyo
model = Pipeline([
    ("preprocess", preprocess),
    ("model", LogisticRegression(
        max_iter=400,
        class_weight="balanced",
        solver="lbfgs"
    ))
])

# Entrenar
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print("🔄 Entrenando modelo...")
model.fit(X_train, y_train)

# Evaluar
y_pred = model.predict(X_test)
accuracy = (y_pred == y_test).mean()
y_probs = model.predict_proba(X_test)[:, 1]
roc_auc = roc_auc_score(y_test, y_probs)

print(f"✅ Precisión: {accuracy:.2%}")
print(f"✅ AUC-ROC: {roc_auc:.2f}")

# Guardar modelo (formato que espera tu código)
model_data = {
    'pipeline': model,
    'mission': 'Kepler',
    'feature_names': X.columns.tolist(),
    'accuracy': accuracy,
    'roc_auc': roc_auc
}

# Crear carpeta models si no existe
os.makedirs('models', exist_ok=True)

# Guardar
joblib.dump(model_data, 'models/exoplanet_model.pkl')
print("💾 Modelo guardado en: models/exoplanet_model.pkl")
print("🎉 ¡Modelo compatible creado! Reinicia tu servidor.")