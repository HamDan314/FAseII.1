# Autenticación y flujo de solicitudes

Este prototipo académico no implementa autenticación ni autorización de usuarios. No existen login, cuentas, roles, contraseñas, sesiones, API keys, JWT ni renovación de tokens en la aplicación.

## Componentes y recorrido

1. `frontend/app.js` envía `POST /api/predict` con `Content-Type: application/json` y un cuerpo `{features: [...]}`. No añade un encabezado Authorization ni administra tokens o almacenamiento de credenciales.
2. `frontend/nginx.conf`, en `location /api/`, reenvía la solicitud a `http://backend:8000/`. La barra final de `proxy_pass` transforma `/api/predict` en `/predict`. Añade encabezados de host, IP y protocolo; no configura autenticación.
3. `backend/app/main.py` recibe la solicitud en `predict(payload: PredictionRequest)`. Pydantic exige 30 valores numéricos finitos y rechaza campos adicionales. Esta validación comprueba datos, no identidad.
4. El backend crea un DataFrame, ejecuta `model.predict()` y `model.predict_proba()`, y devuelve clasificación, probabilidades, latencia y versión.

Los endpoints `/`, `/health`, `/model-info` y `/predict`, así como la documentación de FastAPI, no tienen dependencias de seguridad. Las pruebas de `backend/tests/test_api.py` llaman a la API sin credenciales.

## Credenciales, tokens y configuración

- `.env.example` solo define los puertos. `.gitignore` excluye `.env`; eso no proporciona autenticación ni garantiza que nunca se hayan publicado secretos.
- `docker-compose.yml` no inyecta credenciales. Publica el frontend y también el backend, permitiendo acceder directamente a la API si la red y el firewall lo permiten.
- El middleware CORS usa `allow_origins=["*"]` y `allow_credentials=False`. CORS controla acceso desde navegadores; no autentica usuarios ni impide solicitudes de otros clientes.
- No existe código para emitir, almacenar, validar, expirar, revocar o renovar tokens. Tampoco se configura TLS en el Nginx incluido.
- `gcloud auth login` en el manual autentica al operador ante Google Cloud. Sus credenciales pertenecen a la herramienta de despliegue, no al usuario de esta aplicación. El ejemplo `--allow-unauthenticated` permite invocaciones públicas en Cloud Run.

## Alcance

El comportamiento actual es una demostración accesible sin login. Si se requiere acceso restringido, será necesario implementar y probar una capa de autenticación y autorización, además de revisar HTTPS, CORS y la exposición directa del backend. Este documento describe el código existente; no añade protección a la API.
