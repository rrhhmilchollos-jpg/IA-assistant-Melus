# Configuración de GitHub OAuth para Melus AI

## Paso 1: Crear una GitHub OAuth App

1. Ve a **GitHub** → **Settings** → **Developer settings** → **OAuth Apps**
2. Haz clic en **"New OAuth App"**
3. Completa los campos:

| Campo | Valor (Local) | Valor (Producción) |
|-------|---------------|-------------------|
| Application name | `Melus AI Local` | `Melus AI` |
| Homepage URL | `http://localhost:3000` | `https://melusai.com` |
| Authorization callback URL | `http://localhost:8001/api/github/auth/callback` | `https://api.melusai.com/api/github/auth/callback` |

4. Haz clic en **"Register application"**
5. Copia el **Client ID**
6. Genera y copia el **Client Secret**

## Paso 2: Configurar las Variables de Entorno

### Para desarrollo local (Windows)

Edita el archivo `backend\.env`:

```env
# GitHub OAuth
GITHUB_CLIENT_ID=tu_client_id_aqui
GITHUB_CLIENT_SECRET=tu_client_secret_aqui
GITHUB_REDIRECT_URI=http://localhost:8001/api/github/auth/callback
```

### Para producción

```env
GITHUB_CLIENT_ID=tu_client_id_produccion
GITHUB_CLIENT_SECRET=tu_client_secret_produccion
GITHUB_REDIRECT_URI=https://api.melusai.com/api/github/auth/callback
```

## Paso 3: Reiniciar el Backend

```powershell
# En Windows (PowerShell)
cd C:\ruta\a\tu\proyecto\backend
python server.py
```

## Verificar la Conexión

1. Abre la aplicación en `http://localhost:3000`
2. Inicia sesión
3. Genera un proyecto
4. Haz clic en **Deploy** → **GitHub** → **Conectar GitHub**
5. Autoriza la aplicación en GitHub
6. ¡Listo! Ya puedes subir proyectos a GitHub

## Costos

- **Subir a GitHub**: 50 créditos por proyecto
- **Usuario Owner** (`rrhh.milchollos@gmail.com`): Créditos ilimitados

## Troubleshooting

### Error "GitHub no conectado"
- Verifica que `GITHUB_CLIENT_ID` y `GITHUB_CLIENT_SECRET` estén correctos
- Asegúrate de que la URL de callback coincida exactamente

### Error de autorización
- Verifica que el `GITHUB_REDIRECT_URI` sea el mismo en GitHub y en tu `.env`
- Para local debe ser: `http://localhost:8001/api/github/auth/callback`

### Error al crear repositorio
- Verifica que tu cuenta de GitHub tenga permisos para crear repositorios
- Si usas una organización, asegúrate de que la OAuth App tenga acceso

---

Generado para Melus AI
