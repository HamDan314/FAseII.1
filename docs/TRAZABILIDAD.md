# Trazabilidad del modelo desplegado

Modelo versión 1.2.0: `regresion_logistica`. La instancia desplegada y sus métricas se generaron en la misma ejecución.

| Indicador | Resultado |
|---|---:|
| Accuracy | 0.982456 |
| Precision de benignos | 0.986111 |
| Recall de benignos | 0.986111 |
| F1 de benignos | 0.986111 |
| ROC-AUC con benigno positivo | 0.996032 |
| Muestras de prueba | 114 |
| F1 promedio en CV | 0.986056 |
| Desviación estándar del F1 en CV | 0.004287 |

Matriz: filas reales y columnas predichas, orden maligno (0), benigno (1): `[[41, 1], [1, 71]]`. De 42 malignos, 41 se clasifican como malignos y uno como benigno. De 72 benignos, 71 se clasifican como benignos y uno como maligno. La sensibilidad para malignidad en esta muestra es 41/42 = 97.62 %. No es una validación clínica externa.

La regla de decisión permanece en 0.50 para benigno. No hay un umbral optimizado que documentar. Si se ajusta en una etapa futura, se utilizará validación independiente y se evaluarán explícitamente las consecuencias de ambos errores.

## Procedencia

- Semilla: 42; 455 muestras de entrenamiento y 114 de prueba.
- Selección: mayor F1 promedio de CV de cinco pliegues sobre entrenamiento. La prueba no decide el ganador.
- MLflow run: `813d7c9b85614044bf7d75dd2581c632`. Resumen exportado: `entrenamiento/resultados/registro_mlflow.json`.
- Código fuente de entrenamiento SHA-256: `84b71041a8bb125b36455cb5364f1b34799e8198be6e64e8e20261e65e8c61fd`.
- Dataset SHA-256: `9e06ac25868bca5de98aa757b0112b94096ff7b3d3fc579ade591c3fa58724b5`.
- Modelo desplegado SHA-256: `f7ce8136c5ccc012cce5471f54957033316514f0a514d961a85a6339b6bf99c1`.
- Commit padre de esta revisión: `451ecf340ddd0da98f5f315234802c5cb3b3e812`. Los hashes identifican el código y el artefacto específicos de esta revisión.
- Entorno completo usado: `entrenamiento/resultados/entorno_ejecucion.txt`; parámetros y versiones principales en `backend/model/metadata.json`.

El registro exportado conserva la identidad y los resultados del experimento. El almacén MLflow completo se genera localmente al repetir el entrenamiento y no se publica como servicio desde este repositorio.

La prueba ya había sido inspeccionada en la entrega histórica. Esta revisión corrige el procedimiento; no elimina ese antecedente. Se requiere una nueva muestra para confirmar generalización externa.

## Verificaciones

Nueve pruebas de API y coherencia del modelo aprobadas en Python 3.12.14. Docker no está disponible en el entorno de esta revisión local: la ejecución de contenedores debe verificarse con `INICIAR_DOCKER.bat` o en el workflow de GitHub Actions. Se corrigió la exclusión de `tests/` del contexto de construcción y se añadió una comprobación del proxy y predicción entre contenedores. No se afirma un despliegue real en nube.
