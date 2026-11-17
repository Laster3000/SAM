# SAM — Tandas consecutivas sin cron (R005)
El supervisor de SAM encadena las tandas directamente con `--interval 0`: cuando termina una sesión, la siguiente empieza inmediatamente en la misma máquina. Los horarios GitHub solo verifican código; **no sostienen un servicio ininterrumpido**. El proceso local requiere PC encendido.

Arranque bajo control:
```powershell
python -m sam.supervisor --model-a RUTA_QWEN3.gguf --model-b RUTA_QWEN25.gguf --llama-cli RUTA_llama-cli.exe --state D:\\TCSA3000\\SAM-RUNTIME\\state --reports D:\\TCSA3000\\SAM-RUNTIME\\reports --batch 12 --research-topics 1 --interval 0 --min-free-gb 10 --max-state-mb 256
```

- `--interval 0` no impone espera entre tandas correctamente terminadas.
- Ante caídas hay reintentos escalonados, ante falta de espacio el supervisor **se detiene**.
- Crear `STOP` en el directorio state detiene el sistema; no cancelar ni sobrescribir otras tareas existentes.
- Windows asigna prioridad **inferior a normal** al subprocess del worker, que no usa la GPU compartida de AF.
- Cada ciclo escribe evidencias JSONL/SQLite y reporte; no valida científicamente hipótesis ni cambia pesos.
- El arranque automático de Windows debe configurarse y verificarse aparte; `SAM-RUNTIME` no es el canon.
