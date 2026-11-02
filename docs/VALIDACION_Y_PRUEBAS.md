# Validación y pruebas del clasificador de tumores

Clasificador de tumores · Fase II · Modelo 1.2.0
Actualización del 1 de noviembre de 2026

La versión 1.2.0 se ejecutó correctamente en Docker en el equipo del usuario. Las capturas aportadas muestran nueve pruebas aprobadas, ambos contenedores saludables y una respuesta de predicción desde localhost:8080. Este documento distingue las pruebas de software, la evaluación del modelo y los casos todavía no acreditados por ejecución.

## Entorno y alcance

El backend se construye desde Python 3.11 slim y utiliza FastAPI 0.115.12, scikit-learn 1.8.0, pandas 2.2.3, joblib 1.4.2 y pytest 8.3.5. El frontend usa Nginx. La ejecución documentada se realizó con Docker Desktop en Windows. El entrenamiento registrado en metadata corresponde a Python 3.12.14.

## Pruebas automatizadas ejecutadas

| Prueba | Comprobación |

| --- | --- |

| test_health | HTTP 200 y modelo cargado |

| test_root_and_model_info | Raíz e información de 30 variables |

| test_valid_prediction | Clase válida y probabilidades coherentes |

| test_missing_features | Rechazo 422 con dos características |

| test_non_numeric_value | Rechazo 422 de valores no numéricos |

| test_extra_features | Rechazo 422 con 31 características |

| test_missing_body_and_unexpected_field | Rechazo 422 sin cuerpo o con campo adicional |

| test_artifact_hash_and_positive_class | Hash del modelo y mapeo de clases |

| test_deployed_metrics_match_documented_split | Métricas y matriz de la partición registrada |

Resultado mostrado en la ejecución dentro del contenedor: 9 passed, 1 warning in 1.52s. La advertencia se refiere a una API obsoleta de AnyIO usada por TestClient; no representa una prueba fallida.

## Integración y evidencias de ejecución

El script comprobar_integracion.py informó éxito para web, proxy Nginx, salud, metadatos, predicción y rechazo HTTP 422. docker compose ps mostró cancer-api y cancer-frontend en estado healthy, publicados en los puertos 8000 y 8080.

Figura 1. Resultado de INICIAR_DOCKER.bat en el equipo del usuario, aportado el 1 de noviembre de 2026.

Figura 2. Interfaz en localhost:8080 con resultado del caso de ejemplo. Se recorta la captura para concentrar la evidencia en la predicción.

Respuesta observada: prediction 0, diagnosis maligno, probability_malignant 0.999968, probability_benign 0.000032 y model_version 1.2.0. La latencia de esta captura fue 11.194 ms; es una observación individual, no una medición de rendimiento bajo carga.

## Evaluación del modelo y trazabilidad

El dataset Breast Cancer Wisconsin Diagnostic contiene 569 registros y 30 características. Se divide de forma estratificada en 455 ejemplos de entrenamiento y 114 de prueba, con semilla 42. La imputación y el escalado se ajustan dentro del pipeline de cada fold. La selección utiliza F1 promedio de validación cruzada de cinco pliegues antes de evaluar la prueba en el procedimiento vigente.

| Indicador | Valor |

| --- | --- |

| Modelo | Regresión logística |

| Accuracy | 0.982456 |

| Precision de benignos | 0.986111 |

| Recall de benignos | 0.986111 |

| F1 de benignos | 0.986111 |

| ROC AUC con benigno positivo | 0.996032 |

| F1 promedio de validación cruzada | 0.986056 |

| Desviación del F1 de validación cruzada | 0.004287 |

La clase positiva es benigno (1); maligno corresponde a 0. La matriz usa filas reales y columnas predichas, en orden maligno y benigno.

| Clase real | Predicho maligno | Predicho benigno |

| --- | --- | --- |

| Maligno | 41 | 1 |

| Benigno | 1 | 71 |

Un falso positivo de benignidad es un maligno clasificado como benigno. Un falso negativo de benignidad es un benigno clasificado como maligno. El recall de benignos no equivale a sensibilidad para malignidad; esta última es 41/42, aproximadamente 97.62 % en esta muestra.

Se mantiene predict() con el umbral predeterminado de 0.50 para benigno; no se optimizó el umbral. La prueba histórica ya había sido consultada en versiones anteriores. Corregir el procedimiento no convierte esta muestra en una evaluación externa inédita.

MLflow run: 813d7c9b85614044bf7d75dd2581c632

SHA 256 del modelo desplegado:

f7ce8136c5ccc012cce5471f54957033
316514f0a514d961a85a6339b6bf99c1

## Criterios de aceptación y límites

| Criterio | Estado |

| --- | --- |

| Contenedores saludables | Comprobado en captura |

| Nueve pruebas del backend | Aprobadas dentro del contenedor |

| Predicción y proxy Nginx | Comprobados por script e interfaz |

| Entradas de longitud incorrecta y campos extra | Rechazo 422 comprobado por pytest |

| Hash y métricas del artefacto | Comprobados por pytest |

| Despliegue real en nube | No acreditado; se proporciona manual |

| Pruebas de carga y autenticación | No realizadas; no se implementa login |

## Casos adicionales propuestos

El código rechaza NaN e infinito y falla durante el arranque si faltan el modelo o metadata. Estos escenarios no aparecen como casos específicos ejecutados en las nueve pruebas actuales. Para acreditarlos, añadir pruebas que envíen valores no finitos mediante JSON admisible y que simulen la ausencia del artefacto en un entorno aislado. No se consideran aprobados por la sola existencia de validaciones en el código.

## Reproducción

docker compose up -d --build --wait --wait-timeout 180
docker compose exec -T backend python -m pytest -q
docker compose exec -T backend python tests/comprobar_integracion.py
docker compose ps

En Windows puede utilizarse INICIAR_DOCKER.bat para ejecutar esa secuencia y consultar logs ante fallos. Abrir localhost:8080, cargar el ejemplo y realizar la predicción para comprobar la interfaz.

## Conclusión

Se cumplen los criterios de funcionamiento local de Docker y de integración del prototipo observado. Las pruebas verifican software y coherencia del artefacto; no demuestran validez clínica, generalización externa ni funcionamiento de un chatbot. El repositorio no implementa el chatbot generativo ni autenticación de usuarios.

Fuentes: backend/tests/test_api.py, backend/tests/comprobar_integracion.py, backend/model/metadata.json, entrenamiento/fuentes/train.py y capturas aportadas. Código de referencia: d883fb7e5eaa43768caa57a5eae352c31743bd06.

Evidencias integradas en las versiones Word y PDF de la raíz del repositorio.