# P13 Sistematizador (Selenium + SQL) — v29

Este proyecto tiene 3 comandos:

- `preview`: lee **un solo TXT** (prompt) y lo ejecuta por Selenium en **chatgpt.com**.
- `run`: une el TSV generado por `preview` con las preguntas SQL de `VW_PREGUNTA_POR_EVALUACION` por `EvaluacionId`.
- `load`: sube una matriz (Excel/CSV) a `dbo.Respuesta` usando MERGE (3 columnas: SituacionActual/Notas/RespuestaLiteral).

## 1) Preparar venv (PowerShell)

```powershell
cd "C:\ruta\a\P13_sistematizador_selenium_v29"

python -m venv .venv
.\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
python -m pip install -r .\requirements.txt
```

## 2) Configurar DB

Crea `db_config.json` en la raíz del repo:

### Ejemplo Azure SQL (usuario + password)

```json
{
  "server": "gaeval.database.windows.net",
  "database": "gaeval_v2",
  "username": "gaevaluser",
  "password": "TU_PASSWORD",
  "encrypt": "yes",
  "trust_server_certificate": "no"
}
```

### Ejemplo LocalDB (Windows Auth)

```json
{
  "server": "(localdb)\\MSSQLLocalDB",
  "database": "gaeval_v2",
  "encrypt": "no",
  "trust_server_certificate": "yes"
}
```

## 3) preview (Selenium)

Por defecto lee este prompt:

- `G:\Mi unidad\TGA_PROYECTO\Nuevotxt\combined_output.txt`

y lo copia a:

- `01.02 Promp\prompt_trabajo.txt`

Luego ejecuta Selenium y guarda salida en `01.03 Resultado ChatGPT\`:

- `resultado.tsv`
- `resultado.csv`
- `resultado.xlsx`

Comando:

```powershell
python .\main.py preview
```

## 4) run (unir con SQL)

Lee `resultado.tsv` y une con preguntas por EvaluacionId:

```powershell
python .\main.py run --evaluacion-id 17 --db-config ".\db_config.json"
```

Salida:

- `01.03 Resultado ChatGPT\resultado_unido.tsv`
- `01.03 Resultado ChatGPT\resultado_unido.csv`
- `01.03 Resultado ChatGPT\resultado_unido.xlsx`

## 5) load (subir matriz a dbo.Respuesta)

```powershell
python .\main.py load --evaluacion-id 17 --informante-id 108 --db-config ".\db_config.json" --excel "C:\ruta\MATRIZ_sistematización.xlsx"
```

> Importante: la Matriz debe contener `PREGUNTA_CODIGO` y alguna(s) columnas de conversación/análisis.
El loader detecta dinámicamente columnas que contengan:
- `CONVERSACION_ENTREVISTADOR` (se agrupa en NOTAS)
- `CONVERSACION_INFORMANTE` (se agrupa en SITUACION)
- `ANÁLISIS_DE_COBERTURA` / `ANALISIS_DE_COBERTURA` (ANALISIS)


## Inventario de Google Drive

- Nombre: SistematizadorEntrevistas - copia.
- Propósito documentado: P13 Sistematizador (Selenium + SQL) — v29.
- Periodo de archivos: 2026-01-10 a 2026-07-03.
- Tecnologías y formatos: .md, .py, .txt.
- Estructura: Léeme-ejecución.txt, README.md, REGLA DE CARGA COMPLETA.txt, config.py, inputs, main.py, requirements.txt, src.
- Módulos principales: src/selenium_runner.py, src/loaders.py, src/excel_reader.py, src/tsv_utils.py, src/prompt_builder.py, src/merge_runner.py, src/db.py, src/repo.py, src/db_questions.py, src/exporter.py, src/mapping.py, config.py.
- Origen: carpeta Drive `1T_htLys7u_3UTUB42n2wzKpzT9y4td7L`.
- Archivos originales seleccionados: 18.
- Observaciones: se conserva el original de Drive cuando existen archivos excluidos o insumos no copiados. Se conserva cada proyecto por separado.
