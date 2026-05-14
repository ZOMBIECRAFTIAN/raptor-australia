# Setup y Control de Versiones — Australian Raptor CNN

Guía paso a paso desde cero. Todo se ejecuta en **Anaconda Prompt**
(no en `cmd` regular ni PowerShell).

---

## A. Prerrequisitos (una sola vez por máquina)

1. **Instalar Anaconda Distribution**
   https://www.anaconda.com/download
   Descarga el instalador para Windows, ejecuta como administrador,
   marca "Add Anaconda to PATH" si te lo permite.

2. **Instalar Git para Windows**
   https://git-scm.com/download/win
   Acepta los defaults; usa "Git Bash" si lo prefieres.

3. **Cuenta en GitHub** (https://github.com) con tu usuario
   `ZOMBIECRAFTIAN` ya creada.

4. **Personal Access Token (PAT)** — para autenticación al hacer push.
   - Genera en https://github.com/settings/tokens/new
   - Note: `raptor-australia (laptop)`
   - Expiration: 90 days o "No expiration"
   - Scopes: marca solo **`repo`**
   - Copia el token (empieza con `ghp_...`) y guárdalo en tu
     gestor de contraseñas. Sólo se muestra una vez.

---

## B. Crear el entorno conda (una sola vez)

Abre **Anaconda Prompt** (busca "Anaconda Prompt" en el menú Inicio).

```
conda create -n raptor_env python=3.10 -y
conda activate raptor_env
```

El prompt cambia de `(base)` a `(raptor_env)`.

---

## C. Clonar el proyecto (una sola vez)

```
cd C:\Projects
git clone https://github.com/ZOMBIECRAFTIAN/raptor-australia.git
cd raptor-australia
```

---

## D. Instalar dependencias (una sola vez por entorno)

```
pip install -r requirements.txt
```

**Si necesitas PyTorch con GPU (NVIDIA CUDA 11.8):**

```
pip uninstall torch torchvision -y
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

**Verifica que torch ve la GPU:**

```
python -c "import torch; print('CUDA available:', torch.cuda.is_available())"
```

---

## E. Configurar tu API key de eBird (una sola vez)

Crea el archivo `.env` en la raíz del proyecto:

```
echo EBIRD_API_KEY=tu_clave_aqui > .env
```

Verifica:

```
type .env
```

Importante: `.env` está en `.gitignore`, **nunca se sube a GitHub**.

---

## F. Iniciar el proyecto en cada sesión

Cada vez que abres una nueva terminal:

```
conda activate raptor_env
cd C:\Projects\raptor_australia
```

### Lanzar la aplicación web

```
cd gui
python app.py
```

Abre `http://localhost:5000` en el navegador.

### Detener la aplicación

```
Ctrl+C
```

Para volver a la raíz:

```
cd ..
```

---

## G. Scripts útiles

Todos se corren desde la raíz del proyecto con `(raptor_env)` activo:

```
REM Descargar imágenes ALA
python notebooks/download_ala_images.py

REM Filtrar imágenes por calidad
python notebooks/filter_ala_quality.py --use-detector --dry-run
python notebooks/filter_ala_quality.py --use-detector

REM Restaurar imágenes archivadas
python notebooks/restore_archived.py --all

REM Re-elegir heros del catálogo manualmente
python notebooks/pick_hero_manual.py

REM Re-elegir heros automáticamente con detector de aves
python notebooks/pick_hero_images.py --use-detector --apply

REM Re-entrenar el modelo (~1.5-2 horas en GPU)
python notebooks/retrain.py

REM Datos eBird
python notebooks/fetch_ebird_data.py

REM Generar SVGs AUSLAN
python notebooks/generate_auslan_svgs.py

REM Descargar videos de comportamiento (ALA)
python notebooks/download_ala_videos.py
```

---

## H. Control de versiones con Git

### Ver el estado actual

```
git status
git status --short
```

### Subir cambios al repositorio (workflow normal)

```
git add -A
git status --short
```

Revisa que NO aparezcan archivos sensibles (`.env`, datasets, modelos).

Si todo se ve bien:

```
git commit -m "Descripcion breve de lo que cambiaste"
git push
```

### Cuando git te pida credenciales en push

- **Username:** `ZOMBIECRAFTIAN`
- **Password:** tu Personal Access Token (`ghp_...`), NO tu contraseña

Git puede recordarlas con:

```
git config --global credential.helper manager
```

### Mensajes de commit profesionales (ejemplos)

```
git commit -m "Add eBird enrichment fetcher with .env-based API key"
git commit -m "v1.2.0: retrain on iNat + ALA dataset"
git commit -m "Fix: CITATION.cff NULL bytes; CI render mock"
git commit -m "Docs: setup guide for new contributors"
```

### Ver el historial

```
git log --oneline -10
```

### Deshacer cambios locales (antes de commit)

```
git restore archivo.py        # revierte un archivo
git restore --staged archivo  # quita un archivo del staging
git checkout main             # vuelve a la rama main
```

### Bajar cambios del repo remoto (si trabajas en otra máquina)

```
git pull
```

---

## I. Problemas comunes y soluciones

### `git push` me pide login una y otra vez

Genera un nuevo PAT y úsalo como password.

### `del archivo.md` → "Access is denied"

VS Code u otro programa tiene el archivo abierto. Cierra todas las
instancias y reintenta.

### `git rm --cached -r carpeta/` → "did not match any files"

La carpeta no está tracked. No hay nada que hacer; está bien.

### `warning: LF will be replaced by CRLF`

Es un aviso de Windows convirtiendo saltos de línea — inofensivo.
Si te molesta:

```
git config --global core.autocrlf true
```

### CI en GitHub falla

Revisa el run en https://github.com/ZOMBIECRAFTIAN/raptor-australia/actions
Si es un error de import o template, revisa que no agregaste una
variable nueva a un template sin pasarla en el mock del workflow.

### Mi `.env` apareció en `git status`

```
git rm --cached .env
echo .env >> .gitignore
git add .gitignore
git commit -m "Untrack .env (was leaked accidentally)"
git push
```

**Y regenera la clave en eBird** — está comprometida si ya hiciste push.

---

## J. Checklist antes de cada push

- [ ] `git status --short` — confirmar qué se va a subir
- [ ] Ningún `.env`, `*.pth`, `models/` o `dataset/raw*/` en la lista
- [ ] Mensaje de commit descriptivo (1 línea, ≤ 70 caracteres)
- [ ] Si tocaste un template Jinja, también pasaste la variable nueva
      al mock del workflow CI (`.github/workflows/ci.yml`)
- [ ] Si agregaste una dependencia Python, está en `requirements.txt`

---

## K. Mantenimiento periódico

| Periodicidad | Tarea |
|---|---|
| Cada commit | `git status --short` antes de `git add` |
| Cada release | Actualizar `CHANGELOG.md` y bumpear `version` en `CITATION.cff` |
| Cada 90 días | Renovar Personal Access Token de GitHub |
| Cada retrain | Commitear `results/*.json` y `results/*.png` actualizados |
| Cada paquete nuevo | Agregar a `requirements.txt` con versión semántica |

---

Última actualización: 2026-05-12 · v1.2.0
