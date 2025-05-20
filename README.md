# Servicio de Optimización de Portafolios

Este servicio implementa una API REST que permite estimar portafolios óptimos a partir de retornos diarios de activos financieros.

## Método de Optimización

Para este servicio se ha implementado el **modelo de Markowitz con restricciones** por las siguientes razones:

1. **Balance rendimiento-riesgo**: El modelo de Markowitz permite encontrar portafolios eficientes que maximizan el rendimiento esperado para un nivel de riesgo dado.

2. **Flexibilidad en restricciones**: Permite incorporar fácilmente restricciones como el riesgo máximo permitido y el peso máximo por activo.

3. **Interpretabilidad**: Los resultados son intuitivos y ampliamente aceptados en la industria financiera.

4. **Eficiencia computacional**: Es un modelo que puede resolverse de manera eficiente mediante programación cuadrática, lo que lo hace adecuado para una API que debe responder en tiempo real.

## Métrica de Riesgo

Como métrica de riesgo se utiliza la **volatilidad (desviación estándar)** del portafolio. Esta elección se basa en:

- Es la métrica estándar en el modelo de Markowitz
- Es fácilmente interpretable
- Captura adecuadamente el riesgo para inversores con horizontes de inversión de medio plazo

## Criterio de Optimalidad

El criterio de optimalidad es **maximizar el rendimiento esperado** sujeto a:
- La volatilidad del portafolio no debe superar el nivel de riesgo especificado
- Ningún activo puede tener un peso superior al máximo permitido
- La suma de los pesos debe ser 1 (inversión total del capital)
- No se permiten posiciones cortas (pesos negativos)

## Requisitos

- Python 3.8 o superior
- Dependencias listadas en `requirements.txt`

## Instalación y Ejecución Local

1. Clonar este repositorio
```bash
git clone https://github.com/tu-usuario/portfolio-optimization-service.git
cd portfolio-optimization-service
```

2. Crear un entorno virtual e instalar dependencias
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Ejecutar el servicio
```bash
uvicorn main:app --reload
```

El servicio estará disponible en `http://localhost:8000`

## Ejecución con Docker

1. Construir la imagen
```bash
docker build -t portfolio-optimization-service .
```

2. Ejecutar el contenedor
```bash
docker run -p 8000:8000 portfolio-optimization-service
```

## Uso de la API

### Endpoint de Optimización

```
POST /optimize-portfolio
```

#### Parámetros de entrada:
- `file`: Archivo CSV con los retornos diarios del universo de activos (formato ticker/fecha)
- `risk_level` (float): Nivel máximo de riesgo permitido
- `max_weight` (float): Peso máximo permitido por activo

#### Ejemplo de solicitud con curl:
```bash
curl -X POST http://localhost:8000/optimize-portfolio \
-H "Content-Type: multipart/form-data" \
-F "file=@returns.csv" \
-F "risk_level=1.0" \
-F "max_weight=0.15"
```

#### Respuesta (formato JSON):
```json
{
  "optimal_portfolio": {
    "ticker_1": 0.15,
    "ticker_2": 0.1,
    "ticker_3": 0.15,
    ...
  }
}
```

## Documentación de la API

La documentación interactiva de la API está disponible en:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Despliegue

El servicio puede desplegarse en plataformas como:
- Heroku
- Google Cloud Run
- AWS Lambda + API Gateway
- Digital Ocean App Platform

Para desplegar en alguna de estas plataformas, consulta la documentación específica de cada una.

## Licencia

MIT