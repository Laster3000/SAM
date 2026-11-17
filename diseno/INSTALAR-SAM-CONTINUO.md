# SAM 0.4 — Ejecución continuada (sin prometer cómputo imposible)

Para que SAM siga ejecutándose fuera de esta conversación, necesita una máquina encendida, los modelos instalados y un proceso que supervise al worker.

## Windows (usuario local, sin instalar servicio por defecto)
Con el repositorio y Python instalados, abrir una terminal en la carpeta SAM:
python -m sam.supervisor --model-a X:\ruta\qwen3.gguf --model-b X:\ruta\qwen25.gguf --llama-cli X:\ruta\llama-cli.exe --state X:\SAM-ESTADO --reports X:\SAM-RESULTADOS --batch 18 --research-topics 2

El supervisor vuelve a arrancar el worker si se cae; usa espera incremental. No reinicia si el worker detecta disco insuficiente o si existe el archivo STOP. Las rutas X: son ejemplos que hay que sustituir por rutas reales. No registrar claves, no usar datos personales ni compartir carpetas internas de AF.

Para iniciar automáticamente tras reiniciar el equipo debe registrarse en el Programador de tareas bajo una cuenta autorizada, con reinicio en fallo; **esa configuración NO está instalada ni verificada aún**.

## Linux
Configurar un servicio systemd de usuario cuyo ExecStart sea el comando anterior con las rutas del equipo. Restart=on-failure, RestartSec=30, y limitar RAM, disco y CPU. Ni el servicio ni un servidor Linux permanente han sido instalados.

## Qué quiere decir «no parar»
Hay continuidad entre sesiones y recuperación de caídas, pero no se garantiza funcionar si la máquina está apagada o no hay recursos. Es mejor dejar constancia de un bloqueo real que ocultarlo con reintentos infinitos.

Los resultados de esta infraestructura quedan CANDIDATE_PENDING_TCSA hasta importar a SAM-CORE, con comprobaciones de hash y permisos.
