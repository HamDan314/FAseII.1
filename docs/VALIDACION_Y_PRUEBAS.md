# Documento de validación y pruebas

## Alcance

Validar la carga del modelo, contrato de API, integración frontend-backend y comportamiento ante entradas inválidas.

## Entorno de despliegue

- Python 3.11
- FastAPI
- scikit-learn 1.8.0 (misma versión usada para serializar el modelo)
- Entrenamiento y pruebas de esta revisión: Python 3.12.14; Docker y CI usan Python 3.11.
- Pruebas automatizadas con pytest
- Contenedores Linux basados en imágenes oficiales Python slim y Nginx Alpine

## Casos funcionales

| ID | Caso | Entrada | Resultado esperado |
|---|---|---|---|
| CP-01 | Salud | GET `/health` | HTTP 200 y modelo cargado |
| CP-02 | Predicción válida | 30 números | HTTP 200, clase y probabilidades |
| CP-03 | Información | GET `/model-info` | Variables, versión y métricas |
| CP-04 | Integración web | Formulario → API | Resultado mostrado en pantalla |
| CP-05 | Proxy de integración | GET `/api/health` en puerto 8080 | HTTP 200 reenviado al backend |

## Casos extremos

| ID | Caso | Resultado esperado |
|---|---|---|
| CE-01 | Menos de 30 variables | HTTP 422 |
| CE-02 | Más de 30 variables | HTTP 422 |
| CE-03 | Valores no numéricos | HTTP 422 |
| CE-04 | NaN o infinito | HTTP 422 |
| CE-05 | Modelo ausente | El contenedor no inicia o responde 503 |
| CE-06 | Campo inesperado | HTTP 422 |

## Evaluación del modelo y alcance de las métricas

El entrenamiento realiza una partición estratificada 80/20, semilla 42. La imputación y el escalado se ajustan dentro de cada fold del pipeline. El algoritmo ganador se fija por F1 promedio de validación cruzada de cinco pliegues antes de observar métricas de prueba. La prueba histórica ya había sido utilizada para comparar modelos; una validación externa adicional requiere una nueva muestra.

Los valores vigentes, matriz y trazabilidad están en `backend/model/metadata.json` y en [Trazabilidad](TRAZABILIDAD.md). La exportación del modelo y sus métricas se realiza en una misma ejecución. No se ha optimizado un umbral; se utiliza el predeterminado de 0.50 para benigno.

La clase positiva es **benigno (1)**, y la clase 0 es maligno. Por tanto:

- Falso positivo de benignidad: maligno clasificado como benigno, con posible retraso de evaluación si se usara fuera del ámbito académico.
- Falso negativo de benignidad: benigno clasificado como maligno, con posibles revisiones adicionales, ansiedad y costo.
- Recall de benignos: proporción de benignos detectados. No equivale a sensibilidad para malignidad.

No se asignan costos clínicos inventados ni se traslada la ponderación 5:1 del ejercicio crediticio. Cualquier regla operativa requiere responsables clínicos, datos independientes y revisión humana.

## Criterios de aceptación

1. Todos los tests automatizados deben aprobar.
2. `/health` reporta `model_loaded: true`.
3. Una solicitud correcta devuelve probabilidades entre 0 y 1.
4. Entradas con cardinalidad incorrecta son rechazadas.
5. El frontend consume `/api/predict`, reenviado a `/predict`.
6. El hash del modelo coincide con metadata y sus métricas se reproducen en la partición documentada.

## Conclusión

La solución separa presentación, inferencia y artefacto de ML. Docker facilita su traslado entre entornos. Las pruebas funcionales verifican el servicio y la coherencia del artefacto, no su validez clínica ni el funcionamiento del futuro chatbot. Véase [relación con el chatbot](RELACION_CHATBOT.md).
