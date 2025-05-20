from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import numpy as np
from io import StringIO
from scipy.optimize import minimize
import uvicorn
from typing import Dict, Any
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Portfolio Optimization API")

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def optimize_markowitz_portfolio(returns_df, risk_level: float, max_weight: float):
    """
    Optimiza un portafolio usando el modelo de Markowitz con restricciones.
    
    Args:
        returns_df: DataFrame con los retornos diarios
        risk_level: Nivel máximo de riesgo permitido (volatilidad)
        max_weight: Peso máximo permitido por activo
        
    Returns:
        dict: Portafolio óptimo con pesos por activo
    """
    # Calcular media de retornos diarios y matriz de covarianza
    mean_returns = returns_df.mean()
    cov_matrix = returns_df.cov()
    
    # Número de activos
    n_assets = len(returns_df.columns)
    
    # Función objetivo: maximizar el retorno esperado
    def objective(weights):
        return -np.sum(mean_returns * weights)  # Negativo porque minimizamos
    
    # Restricción de riesgo: volatilidad <= risk_level
    def risk_constraint(weights):
        portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
        return risk_level - portfolio_volatility
    
    # Restricciones
    constraints = [
        {'type': 'eq', 'fun': lambda x: np.sum(x) - 1},  # Suma de pesos = 1
        {'type': 'ineq', 'fun': risk_constraint}  # Restricción de riesgo
    ]
    
    # Límites para cada activo: entre 0 y max_weight
    bounds = tuple((0, max_weight) for _ in range(n_assets))
    
    # Pesos iniciales iguales
    initial_weights = np.array([1/n_assets] * n_assets)
    
    # Optimización
    try:
        result = minimize(
            objective,
            initial_weights,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints,
            options={'disp': False, 'maxiter': 1000}
        )
        
        if not result.success:
            logger.warning(f"Optimization failed: {result.message}")
            raise ValueError(f"Portfolio optimization did not converge: {result.message}")
        
        # Crear diccionario de pesos óptimos
        optimal_weights = result.x
        # Redondear a 4 decimales y formatear
        optimal_portfolio = {ticker: float(weight) for ticker, weight in 
                           zip(returns_df.columns, np.round(optimal_weights, 4)) 
                           if weight > 0.0001}  # Filtrar pesos muy pequeños
        
        # Verificar que la suma sea cercana a 1
        weight_sum = sum(optimal_portfolio.values())
        if abs(weight_sum - 1.0) > 0.01:
            logger.warning(f"Sum of weights ({weight_sum}) is not close to 1.")
            
        return optimal_portfolio
    
    except Exception as e:
        logger.error(f"Error in optimization: {str(e)}")
        raise ValueError(f"Failed to optimize portfolio: {str(e)}")

@app.post("/optimize-portfolio")
async def optimize_portfolio(
    file: UploadFile = File(...),
    risk_level: float = Form(...),
    max_weight: float = Form(...)
):
    """
    Endpoint para optimizar un portafolio basado en retornos históricos.
    
    Args:
        file: Archivo CSV con retornos diarios
        risk_level: Nivel máximo de riesgo permitido
        max_weight: Peso máximo permitido por activo
        
    Returns:
        dict: Portafolio óptimo con sus pesos
    """
    # Validaciones básicas
    if risk_level <= 0:
        raise HTTPException(status_code=400, detail="El nivel de riesgo debe ser positivo")
    
    if max_weight <= 0 or max_weight > 1:
        raise HTTPException(status_code=400, detail="El peso máximo debe estar entre 0 y 1")
    
    try:
        # Leer el archivo CSV
        content = await file.read()
        content_str = content.decode('utf-8')
        
        # Procesar con pandas
        returns_df = pd.read_csv(StringIO(content_str), index_col=0, parse_dates=True)
        
        # Verificar que los datos son numéricos
        if not returns_df.applymap(np.isreal).all().all():
            raise HTTPException(status_code=400, detail="El archivo debe contener solo valores numéricos")
        
        # Verificar que hay suficientes datos para la optimización
        if len(returns_df) < 30:  # Al menos 30 días de datos
            raise HTTPException(status_code=400, 
                               detail=f"Se requieren al menos 30 días de datos, se recibieron {len(returns_df)}")
        
        logger.info(f"Optimizando portafolio con {len(returns_df.columns)} activos y {len(returns_df)} días")
        
        # Optimizar portafolio
        optimal_portfolio = optimize_markowitz_portfolio(returns_df, risk_level, max_weight)
        
        return {"optimal_portfolio": optimal_portfolio}
    
    except pd.errors.ParserError:
        raise HTTPException(status_code=400, detail="Error al parsear el archivo CSV")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error inesperado: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error en el servidor: {str(e)}")

@app.get("/")
async def root():
    return {"message": "Bienvenido al servicio de optimización de portafolios"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)