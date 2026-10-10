# Fix V3 - PowerShell StrictMode / propiedad Exe

## Error corregido

```text
No se encuentra la propiedad 'Exe' en este objeto. Compruebe que existe.
```

## Causa

El script `setup_command_agent.ps1` usaba `Set-StrictMode -Version Latest` y la funcion `Resolve-PythonExe` devolvia un Hashtable. En algunos entornos de PowerShell, acceder con `$Py.Exe` falla porque `Exe` no es propiedad real del objeto.

## Correccion

Ahora `Resolve-PythonExe` devuelve `[pscustomobject]`, por lo que `$Py.Exe` y `$Py.Args` funcionan correctamente.

Tambien se corrigio el uso de rutas: si no se pasa `-BaseDir`, los scripts toman automaticamente la raiz del paquete actual. Esto evita problemas cuando el ZIP queda dentro de `Transcriptor2\Transcriptor2`.

## Ejecutar despues de extraer

```powershell
cd "D:\118102025\Downloads\Nueva carpeta\Transcriptor2\Transcriptor2"
Set-ExecutionPolicy -Scope Process Bypass -Force
Get-ChildItem -Recurse -File | Unblock-File
.\scripts\setup_command_agent.ps1 -RecreateVenv -BuildExe
```

Si extraes el ZIP sin carpeta interna directamente en `Transcriptor2`, usa:

```powershell
cd "D:\118102025\Downloads\Nueva carpeta\Transcriptor2"
Set-ExecutionPolicy -Scope Process Bypass -Force
Get-ChildItem -Recurse -File | Unblock-File
.\scripts\setup_command_agent.ps1 -RecreateVenv -BuildExe
```

## Prueba local

```powershell
.\scripts\run_command_agent_exe.ps1 -NoGemma -Command "crear documento excel y crear archivo en disco c"
```

---

## Actualizacion V4

La ruta base queda fija por defecto en:

```powershell
D:\118102025\Downloads\Nueva carpeta\Transcriptor2
```

Si ejecutas scripts desde `Transcriptor2\Transcriptor2`, igual se crean `librery`, `dist_exe`, `mp3`, `salidas_doc_xls` y `acciones_grabadas` en la ruta correcta externa.
