# SAM — TRABAJO (interfaz de laboratorio, NO desplegada)

SAM ofrece ahora un ejecutor bajo demanda que pide a dos modelos abiertos una propuesta, crítica y revisión de un encargo. **No ejecuta código, comandos, cambios en el ordenador ni modifica componentes.** No activa nada por sí solo y **no está ejecutándose en el PC**.

Preparar manualmente un fichero UTF-8 `encargo.txt` con el texto de una tarea autorizada y, en un sistema de pruebas autorizado con los modelos ya disponibles, usar:

```bash
python -m sam.trabajo --request-file encargo.txt --model-a modelo-a.gguf --model-b modelo-b.gguf --llama-cli /ruta/llama-cli
```

El resultado se conserva en un nombre aleatorio nuevo dentro de `.sam-private/trabajos` (excluido por `.gitignore`) y se marca `SIN_VALIDACION_EXTERNA`. La entrada no se copia a GitHub ni a TCSA automáticamente. Para datos privados se debe usar almacenamiento controlado y autorización adecuada. `TRABAJO` no está unido todavía al gateway autenticado real del propietario.

El modo **EVOLUCIÓN** continúa en `sam.worker` con experimentos acotados por GitHub y planes que nunca se autoejecutan. El modo TRABAJO sigue siendo un **prototipo para encargos**, no una IA general capaz de corregir autónomamente sistemas ajenos. La promoción de una respuesta requiere pruebas independientes y autorización.
