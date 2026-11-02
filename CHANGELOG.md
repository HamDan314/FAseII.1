# Changelog

## 1.2.0 - 2026-11-01

- Selección del algoritmo por validación cruzada antes de evaluar prueba.
- Imputación y escalado dentro del pipeline de cada fold.
- Exportación conjunta de modelo, métricas, matriz, hashes e identificador MLflow.
- Interpretación explícita de benigno como clase positiva y sus errores.
- README general restaurado y vínculo con el chatbot documentado.
- Pruebas incluidas en la imagen y comprobación de integración con Compose en CI.
- Notebook alineado con el script y dependencias de entrenamiento fijadas.


## 1.1.0 - 2026-08-01

- Se alineó scikit-learn 1.8.0 con la versión usada para serializar el modelo.
- Se integró el frontend y backend mediante proxy Nginx `/api`.
- Se parametrizaron los puertos de Docker Compose mediante `.env`.
- Se ampliaron las pruebas de contrato, probabilidades y campos inesperados.
- Se agregó evidencia reproducible de construcción, ejecución e integración.
- El workflow ahora construye las imágenes de backend y frontend.
- Se incorporó el notebook final de Google Colab con sus datos, scripts y resultados.

## 1.0.0 - 2026-07-12

- Se agregó API FastAPI con endpoints de salud, metadatos y predicción.
- Se incorporó modelo serializado y metadatos versionados.
- Se creó frontend estático conectado al backend.
- Se agregaron Dockerfiles independientes y Docker Compose.
- Se añadieron pruebas funcionales y casos extremos.
- Se documentó despliegue local y en nube.
