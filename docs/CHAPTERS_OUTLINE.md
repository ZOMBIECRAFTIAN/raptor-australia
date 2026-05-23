# Thesis Chapters Outline — Australian Raptor CNN + AUSLAN

This document mirrors the chapter structure of the author's prior
project (`raptors-cnn`, Veracruz, México) and adapts it to the
Australian scope. It is meant as a **scaffolding** for writing the
five thesis chapters — section headings, key content per section,
and citations to seed each one.

**Author:** Brian Fernández Báez, Computer Systems Engineer,
Instituto Tecnológico Nacional de México — Campus Veracruz.

**Target program:** Master of Philosophy, University of Queensland.

**Related prior work:** `github.com/ZOMBIECRAFTIAN/raptors-cnn`
(53 Mexican diurnal raptors; same author).

---

## Capítulo 1 — Introducción

### 1.1 Contexto general
- Crisis de biodiversidad en Australia: estado post-Black Summer
  2019-2020 (Ward et al., 2020 — *Nature Ecology & Evolution*).
- Rol de las aves rapaces como bioindicadores de calidad de
  ecosistemas terrestres (Sergio et al., 2006).
- Ausencia documentada de herramientas digitales accesibles para
  identificación de rapaces en Australia.

### 1.2 Antecedente metodológico
- Trabajo previo del autor en el corredor de Veracruz, México
  (raptors-cnn, V1.1, 2026): 53 especies, comparación de 4
  arquitecturas CNN, catálogo de 53 señas en International Sign.
- Lecciones aprendidas trasplantables al contexto australiano:
  reclasificaciones taxonómicas formales, pipeline modular,
  Grad-CAM, co-diseño participativo de señas.

### 1.3 Planteamiento del problema
- Problema 1 — Identificación: las 8 especies clave de rapaces de
  sudeste-Australia requieren expertise especializado para su
  reconocimiento; el monitoreo post-incendio es manual y
  costoso.
- Problema 2 — Inclusión: ausencia de vocabulario científico en
  Australian Sign Language (AUSLAN) para rapaces, lo que excluye
  sistemáticamente a 3.6 M de australianos con pérdida auditiva
  (Hearing Australia, 2022) de la ciencia participativa.
- Problema 3 — Interoperabilidad: las herramientas existentes no
  exportan en formato Darwin Core, fragmentando los datos.

### 1.4 Justificación

**1.4.1 Ecológica.** Las rapaces como indicadores apicales del
estado de los ecosistemas; prioridad nacional documentada por
DAWE (2021) Threatened Species Strategy 2021-2026.

**1.4.2 Tecnológica.** Estado del arte en visión computacional
para fauna (Norouzzadeh et al., 2018; Tabak et al., 2019);
viabilidad de transfer learning con datasets de escala media.

**1.4.3 Social.** Disability Discrimination Act 1992 + NDIS como
marco legal/financiero para inclusión; ausencia documentada de
vocabulario AUSLAN científico para rapaces.

### 1.5 Objetivos

**General.** Desarrollar un sistema integrado de identificación
automatizada de aves rapaces australianas mediante CNN,
complementado con vocabulario AUSLAN provisional para
accesibilidad, orientado al monitoreo de recuperación poblacional
post-incendio.

**Específicos.**
- OE1. Sistematizar el estado del arte (ecología + CNN + AUSLAN).
- OE2. Construir dataset curado de 8 especies (iNaturalist + ALA).
- OE3. Entrenar y comparar 4 arquitecturas CNN (ResNet-50,
  EfficientNet-B4, MobileNetV3-Large, ConvNeXt-Tiny) bajo el
  mismo régimen de transfer learning.
- OE4. Diseñar vocabulario AUSLAN provisional para las 8 especies,
  documentando el protocolo de validación participativa.
- OE5. Implementar interfaz multilingüe (10 idiomas) con
  exportación Darwin Core.
- OE6. Verificar interpretabilidad del modelo mediante Grad-CAM.

### 1.6 Hipótesis
- H1. Un CNN EfficientNet-B4 con transfer learning sobre ~5,000
  imágenes alcanza F1-macro ≥ 0.75 sobre 8 especies.
- H2. Los mapas de Grad-CAM concentran la activación en las
  regiones morfológicas diagnósticas (cola, alas, cabeza) más
  que en el fondo.
- H3. La interfaz multilingüe (10 idiomas) reduce el sesgo de
  accesibilidad lingüística sin comprometer el rendimiento.

### 1.7 Tabla comparativa Veracruz–Australia
| Parámetro | Veracruz (V1.1) | Australia (V1.x) |
|---|---|---|
| Especies | 53 | 8 (con expansión a 24 planeada) |
| Datos | 20,502 imgs (desbalance extremo) | ~5,000 imgs (>500/sp.) |
| Arquitecturas | 4 comparadas | 1 (próxima v2: las 4) |
| Lengua de señas | International Sign | AUSLAN + IS |
| Estado | Iteración 1 | v1.3 operacional |

### 1.8 Bibliografía (semilla)
Ward et al. 2020; Olsen et al. 1993; Marchant & Higgins 1993;
Debus 1998; DAWE 2021; Selvaraju et al. 2017; Tan & Le 2019;
Norouzzadeh et al. 2018; Hearing Australia 2022; NDIS 2022.

---

## Capítulo 2 — Marco Teórico

### 2.1 Biología y ecología de las 8 especies objetivo
Una subsección por especie con:
- Clasificación taxonómica (incluyendo reclasificación
  *Accipiter → Tachyspiza* 2024; ver `TAXONOMY_VERSIONING.md`).
- Descripción morfológica para identificación visual.
- Hábitat, dieta, comportamiento.
- Estado de conservación EPBC.
- Relevancia como indicador ecológico.

### 2.2 Respuesta de rapaces a disturbios por incendio
- Fuego como factor estructurante en ecosistemas australianos.
- 3 fases temporales post-incendio (respuesta inmediata, corto y
  largo plazo) según Whelan 1995; Legge et al. 2022.
- Rapaces como indicadores de segundo orden (Tulloch et al. 2016).

### 2.3 Fundamentos de redes neuronales convolucionales
- Capas convolucionales, ReLU, pooling, fully-connected.
- Transfer learning (Tan et al. 2018; Razavian et al. 2014).
- EfficientNet (Tan & Le 2019), ResNet (He et al. 2016),
  MobileNetV3 (Howard et al. 2019), ConvNeXt (Liu et al. 2022).
- Grad-CAM como herramienta de interpretabilidad (Selvaraju et
  al. 2017).

### 2.4 Métricas de evaluación
Accuracy, Precision, Recall, F1, F1-macro, F1-weighted, matriz
de confusión. Diferencia entre métricas closed-set y open-set
(Bendale & Boult 2016).

### 2.5 IA aplicada a conservación
Norouzzadeh et al. 2018 (camera traps); Tabak et al. 2019;
Van Horn et al. 2018 (iNaturalist taxonomy).

### 2.6 AUSLAN y diseño de vocabularios científicos
Johnston & Schembri 2007; Quinto-Pozos & Reynolds 2012; Hyde &
Power 2006. Marco del Universal Design for Learning (UDL).

### 2.7 Ciencia ciudadana en Australia
Atlas of Living Australia, eBird Australia, BirdLife Australia
Breeding Bird Atlas. Sesgos documentados (Szabo et al. 2012).

### 2.8 Marco legal — EPBC Act, NDIS, Disability Discrimination Act
EPBC Act 1999; NDIS Act 2013; Disability Discrimination Act 1992.

---

## Capítulo 3 — Metodología

### 3.1 Diseño experimental
- Diagrama de pipeline (mermaid o equivalente).
- Reproducibilidad: seeds fijos (42), `requirements.txt` pinned,
  `CITATION.cff`, contenedor Docker.

### 3.2 Construcción del dataset
- Fuentes: iNaturalist Australia + Atlas of Living Australia.
- `notebooks/download_ala_images.py` — pipeline ETL.
- Filtrado de calidad: `filter_ala_quality.py --use-detector`.
- División 80/10/10 estratificada.
- Reclasificaciones AOS 2024 aplicadas (ver
  `TAXONOMY_VERSIONING.md`).

### 3.3 Preprocesamiento
- Redimensionado 420 → CenterCrop 380.
- Normalización ImageNet.
- Data augmentation (RandomResizedCrop, ColorJitter, Rotation,
  Blur — agresiva pero realista).

### 3.4 Arquitecturas CNN comparadas
Tabla:
| Arquitectura | Parámetros | Input | Top-1 ImageNet | Notas |
|---|---|---|---|---|
| ResNet-50 | 25 M | 224×224 | 80.4 % | Baseline robusto |
| EfficientNet-B4 | 19 M | 380×380 | 83.0 % | Escogido para producción |
| MobileNetV3-L | 5 M | 224×224 | 75.2 % | Edge / móvil |
| ConvNeXt-Tiny | 28 M | 224×224 | 82.1 % | Estado del arte 2022 |

### 3.5 Régimen de entrenamiento
- Stage 1 (10 epochs): backbone congelado, sólo cabeza.
- Stage 2 (20 epochs): últimas 20 capas descongeladas, LR/10.
- Cosine annealing scheduler en Stage 2.
- Class-weighted CrossEntropyLoss + label smoothing 0.05.
- Optimizador AdamW.

### 3.6 Evaluación
Métricas globales y por clase, matriz de confusión, curvas de
aprendizaje, F1 por especie. Verificación de interpretabilidad
mediante Grad-CAM (`notebooks/gradcam.py`).

### 3.7 Diseño del vocabulario AUSLAN
- Cinco parámetros estándar por seña: hand shape, location,
  palm orientation, movement, non-manual.
- Iconicidad + economía fonológica.
- Protocolo participativo de validación
  (`docs/auslan_consultation/validation_protocol.md`).

### 3.8 Interfaz web y exportación científica
- Stack Flask + Jinja2.
- Internacionalización en 10 idiomas (cookie-based).
- Exportación Darwin Core (TDWG/GBIF compatible).
- Feedback loop para retraining incremental.

---

## Capítulo 4 — Resultados

### 4.1 Composición del dataset final
Tabla con N por especie post-curación, tras filtro de calidad.
Visualización: `dataset_preprocesado.png`.

### 4.2 Comparación de las 4 arquitecturas
Tabla maestra:
| Arq. | Acc | F1-macro | F1-weighted | Tiempo entreno | Inferencia (ms/img) |
|---|---|---|---|---|---|
| ResNet-50 | — | — | — | — | — |
| EfficientNet-B4 | 75.6 % | 0.76 | 0.76 | 106 min | — |
| MobileNetV3-L | — | — | — | — | — |
| ConvNeXt-Tiny | — | — | — | — | — |

Discusión: el mejor compromiso precisión/eficiencia
(probablemente EfficientNet-B4 o ConvNeXt-Tiny).

### 4.3 Rendimiento por especie
F1 por clase + matriz de confusión + identificación de pares
confusos.

### 4.4 Curvas de aprendizaje
Análisis de convergencia, overfitting potencial, early-stopping
implícito.

### 4.5 Interpretabilidad — Grad-CAM
- 8 figuras (una por especie) mostrando activación en regiones
  morfológicas correctas.
- Verificación de hipótesis H2.

### 4.6 Análisis de errores
Casos donde el modelo falla: juveniles, especímenes,
ángulos extremos, fotos de hábitat (poco bird-in-frame).
Justifica `filter_ala_quality.py --use-detector`.

### 4.7 Interfaz web — UX y métricas de usabilidad
Screenshots de las pantallas principales. Cobertura
multilingüe. Feedback recibido.

### 4.8 Vocabulario AUSLAN provisional
Catálogo de las 8 señas, cinco parámetros por seña, animaciones
SVG generadas. Estatus de validación.

### 4.9 Exportación Darwin Core
Esquema generado, compatibilidad con ALA, GBIF.

---

## Capítulo 5 — Discusión y Conclusiones

### 5.1 Cumplimiento de objetivos
Tabla OE1-OE6 con estatus (✓ cumplido / parcial / pendiente).

### 5.2 Comparación con el antecedente Veracruz
- Tabla comparativa metodológica.
- Lecciones aprendidas: importancia del tamaño mínimo por clase,
  estandarización de la pose.

### 5.3 Limitaciones
- Closed-set (mitigado en v1.3 con banner OOD).
- Sólo 8 de las 24 rapaces australianas.
- AUSLAN provisional, pendiente validación participativa.
- Dataset desbalanceado (Aquila audax 763 vs Hieraaetus 601).

### 5.4 Trabajo futuro
- v2.0: expansión a 14 especies (ver `SPECIES_ROADMAP.md`).
- v3.0: 24 especies + clasificación jerárquica familia→especie.
- Validación AUSLAN con Deaf Society NSW
  (`docs/auslan_consultation/`).
- Comportamiento de vuelo (planeo, hovering, kettle, stoop)
  como segundo input multimodal.
- Open-vocabulary mediante CLIP/DINOv2 (v4.0).

### 5.5 Contribuciones del trabajo
- C1. Primer sistema CNN de identificación de rapaces
  específicamente australianas con interfaz multilingüe.
- C2. Vocabulario AUSLAN provisional con protocolo formal de
  validación.
- C3. Sistema con exportación Darwin Core lista para integración
  ALA/GBIF.
- C4. Continuidad metodológica documentada desde el proyecto
  Veracruz, demostrando transferibilidad del enfoque.

### 5.6 Conclusiones
Cierre — el sistema cumple los objetivos planteados a nivel
prototipo MPhil; la roadmap establece un programa de
investigación de 3 años escalable a comunidad raptorial
completa de Australia.

### 5.7 Acknowledgements
ALA, iNaturalist AU, comunidad sorda australiana (pendiente),
University of Queensland CBCS.

---

## Anexos

- **A.** `SETUP.md` — guía técnica de reproducibilidad.
- **B.** `SPECIES_ROADMAP.md` — plan de expansión a 24 especies.
- **C.** `TAXONOMY_VERSIONING.md` — reclasificaciones AOS aplicadas.
- **D.** `docs/auslan_consultation/` — paquete de consultoría
  para validación con la comunidad sorda.
- **E.** Catálogo visual de las 8 señas AUSLAN provisionales.
- **F.** Resultados intermedios (`results/`).
