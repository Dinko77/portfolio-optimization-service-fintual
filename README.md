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
git clone https://github.com/dinko-damjanic11/portfolio-optimization-service-fintual.git
cd portfolio-optimization-service-fintual
```

2. Crear un entorno virtual e instalar dependencias
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Ejecutar el servicio
```bash
uvicorn main:app --host 0.0.0.0 --port 8080
```

El servicio estará disponible en `http://localhost:8080`

## Ejecución con Docker

1. Construir la imagen
```bash
docker build -t portfolio-optimization-service-fintual .
```

2. Ejecutar el contenedor
```bash
docker run -p 8080:8080 portfolio-optimization-service-fintual
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
curl -X POST https://portfolio-optimization-service-fintual-463275977043.us-central1.run.app/optimize-portfolio \
-H "Content-Type: multipart/form-data" \
-F "file=@returns.csv" \
-F "risk_level=0.2" \
-F "max_weight=0.3"
```

#### Respuesta (formato JSON):
```json
{
  "optimal_portfolio": {
    "ticker_1": 0.25,
    "ticker_2": 0.30,
    "ticker_3": 0.20,
    "ticker_4": 0.25
  }
}
```

## Documentación de la API

La documentación interactiva de la API está disponible en:
- Swagger UI: `https://portfolio-optimization-service-fintual-463275977043.us-central1.run.app/docs`
- ReDoc: `https://portfolio-optimization-service-fintual-463275977043.us-central1.run.app/redoc`

## Despliegue

El servicio está actualmente desplegado en Google Cloud Run y es accesible públicamente en:
```
https://portfolio-optimization-service-fintual-463275977043.us-central1.run.app
```

Para hacer un despliegue similar:
1. Crear un proyecto en Google Cloud
2. Habilitar las APIs necesarias (Cloud Run, Cloud Build)
3. Configurar el despliegue continuo desde GitHub
4. Asegurar que la aplicación escuche en el puerto 8080 (requisito de Cloud Run)

## Autor

Dinko Damjanic

## Licencia

MIT