# SAM 0.3 — Laboratorio recurrente y memoria pendiente de TCSA

SAM prueba código con un runner público de GitHub **cuatro veces al día** en cargas delimitadas. No es servicio 24/7 ni debe confundirse con entrenamiento neuronal. Cada tanda intenta 12 tareas y emite un informe con respuestas reales y errores.

## Persistencia remota
La rama `sam-candidates` contiene `state/eventos.jsonl` y `runs/*.json`, para que las experiencias de un lote puedan recuperarse en el siguiente. Todo permanece **CANDIDATE_PENDING_TCSA**: no se promociona ninguna cápsula como verdad ni se modifica código desde modelos.

La rama es pública. Solo se prueban casos de ejemplo originales o sintéticos; nunca se entregan datos internos de AF ni claves.

TCSA3000, proyecto SAM-CORE, es el único registro canónico. La rama de candidatos es una cola de revisión, no sustituto de importar y comprobar hashes de cada lote en TCSA. El importador completo todavía requiere implementarse y certificarse.

## Worker persistente
`python -m sam.worker --model-a ... --model-b ... --llama-cli ... --batch 18 --interval 20` permite encadenar lotes mientras un host esté encendido. Con `--max-cycles 0` no hay límite de rondas; puede detenerse con fichero STOP, SIGTERM o al superar el límite de disco y fallos. Sus archivos son locales y sobrevivirán al reinicio del worker.

## Límites del experimento
- GitHub no garantiza horarios ni uso continuo; los jobs deben seguir siendo pruebas relacionadas con el proyecto.
- Las sesiones que comparan contra números/líneas exactas miden una parte muy estrecha de la calidad. La exploración interdominios requiere un evaluador riguroso independiente.
- Las versiones de modelos y herramientas están fijadas por hash.
- Si la publicación a la rama falla, GitHub conserva un artefacto temporal; no afirmar que el aprendizaje se haya sincronizado.
