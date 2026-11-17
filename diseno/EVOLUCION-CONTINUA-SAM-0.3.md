# SAM 0.3 — Experimentos continuos, memoria y currículo

## Qué se ha ampliado
- En lugar de 2 ejercicios fijos, currículo original (16 básicos y 10 interdominios) más cientos/miles de ejercicios reproducibles en español, matemáticas, física, química, biología y metodología psicológica.
- Selección por cobertura, novedad y errores: tareas sin resolver primero, reintentos cuando corresponda, reparto de dominios.
- Dos modelos reales: alternan rol creador/crítico; 3 inferencias por tarea.
- Memoria de experiencias SQLite con WAL y JSONL de solo anexado para recuperación. Los resultados tienen run_id, hash de evento, dominio, fuente y verificación. No se añaden conocimientos a la versión canónica sin TCSA.
- Modo worker con ciclos indefinidos mientras haya equipo encendido, modelos disponibles, recursos suficientes y autorización; control STOP, SIGINT, límites de disco, fallos y recuperabilidad.
- GitHub Actions: laboratorio de pruebas de software, no servicio 24/7 ni entrenamiento neuronal. Programación 4 veces/día, lotes de varios casos, pruebas y artefactos con retención limitada. Los resultados remotos son candidatos a importar a TCSA3000.
- Nunca convertir pruebas exactas en supuestas competencias generales; los desafíos interdominios son para revisión humana y solo registran hipótesis.

## Uso local (sin API de pago)
Necesita Python 3.10+, llama.cpp y dos GGUF legítimos compatibles, descargados por el usuario o instalados en el entorno autorizado.
python -m sam.worker --dry-run
python -m unittest discover -s tests -v
python -m sam.worker --model-a ruta/modelo1.gguf --model-b ruta/modelo2.gguf --llama-cli ruta/llama-cli --state ./estado --reports ./resultados --batch 18 --interval 20
Crear un archivo llamado STOP en ./estado para detenerlo limpiamente. El estado se guarda entre sesiones.

## Límites sin resolver
1. No hay garantía de estar activo con todos los ordenadores apagados. Para ejecución ininterrumpida hace falta un equipo siempre encendido o alojamiento autorizado.
2. El currículo sintético NO equivale a aprender nuevos conocimientos científicos; mejora medición y evaluación, no los pesos neuronales.
3. La búsqueda externa y el RAG aún no están integrados en el worker de punta a punta; la curiosidad es un módulo aparte.
4. La persistencia en GitHub por artefactos es temporal. No hay importador continuo verificado en TCSA con equipo apagado.
5. Autocorrección, canibalización de agentes y consolidación de habilidades siguen en fase de diseño/requisitos y deben probarse.
6. La frase RAMSES DICE todavía no dispone de una identidad humana autenticada de forma operativa.

## Regla canónica
Todo experimento, error, dato externo o mejora generado fuera de TCSA se considera CANDIDATE_PENDING_TCSA hasta reconciliarlo por identificadores y hashes. Ningún resultado puede darse por aprendido ni aprobado automáticamente.
