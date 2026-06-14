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

## B. Crear el entorno local moderno (una sola vez)

Abre PowerShell o Anaconda Prompt.

```
cd E:\Projects\raptor_australia
python -m venv .venv-modern
.\.venv-modern\Scripts\activate
python -m pip install --upgrade pip setuptools wheel
```

El prompt cambia de `(base)` a `(.venv-modern)`.

---

## C. Clonar el proyecto (una sola vez)

```
cd E:\Projects
git clone https://github.com/ZOMBIECRAFTIAN/raptor-australia.git
cd E:\Projects\raptor_australia
```

---

## D. Instalar dependencias (una sola vez por entorno)

```
$env:TEMP = "E:\Projects\raptor_australia\.tmp-pip"
$env:TMP = "E:\Projects\raptor_australia\.tmp-pip"
pip install --no-cache-dir -r requirements.txt
```

**Si necesitas PyTorch con GPU:**

El entorno moderno instala `torch==2.12.0+cu130` y `torchvision==0.27.0+cu130` desde el índice oficial de PyTorch. En esta máquina se validó con RTX 3050 Laptop GPU y CUDA disponible.

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
cd E:\Projects\raptor_australia
.\.venv-modern\Scripts\activate
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

Todos se corren desde la raíz del proyecto con `(.venv-modern)` activo:

```
REM Descargar imágenes ALA
python notebooks/download_ala_images.py

REM Filtrar imágenes por calidad
python notebooks/filter_ala_quality.py --use-detector --dry-run
python notebooks/filter_ala_quality.py --use-detector

REM Re-entrenar el modelo (~1.5-2 horas en GPU)
python notebooks/retrain.py --batch-size 4

REM Datos eBird
python notebooks/fetch_ebird_data.py

REM Generar SVGs AUSLAN
python notebooks/generate_auslan_svgs.py

REM Generar predicciones por imagen para tesis
python notebooks/export_test_predictions.py

REM Intervalos bootstrap, ECE y análisis de error
python notebooks/bootstrap_metrics.py --report-md
python notebooks/calibration_ece.py
python notebooks/error_analysis.py

REM Generar/auditar tesis y manifiesto de release
python notebooks/build_thesis_docx.py
powershell -NoProfile -ExecutionPolicy Bypass -File notebooks\export_thesis_pdf.ps1
python notebooks/audit_thesis_docx.py
python notebooks/audit_thesis_pdf.py
python notebooks/build_release_manifest.py
```

### YOLO detector

La release v1.5 usa EfficientNetB4 como clasificador y YOLO como
detector/cropper. `requirements.txt` instala `ultralytics`. Para
evitar descargas automáticas durante una demo, coloca los pesos en:

```
models/yolov8n.pt
```

O define una ruta explícita:

```
set RAPTOR_YOLO_WEIGHTS=C:\ruta\a\yolov8n.pt
```

Si YOLO no está disponible, la ruta de imagen completa sigue
clasificando con EfficientNetB4, pero el cropping/detector de video
no cambia a otra arquitectura.

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

Última actualización: 2026-06-13 · v1.5.0
