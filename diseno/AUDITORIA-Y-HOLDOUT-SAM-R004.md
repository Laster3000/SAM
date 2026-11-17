# SAM R004 — aprendizaje medible sin autovalidación

Los errores científicos de las primeras 40 experiencias motivan tres barreras.

1. **Ledger auditable:** cada evento JSONL debe corresponder a un ID derivado del par ejecución/tarea, con resultado y evaluación coherentes. El comando `python -m sam.quality state/eventos.jsonl --manifest state/ledger-manifest.json` verifica y genera hashes SHA-256 y Git blob SHA-1. Un checksum demuestra integridad, nunca verdad científica; GitHub no sustituye TCSA3000.
2. **Holdout estable:** la función `sam-holdout-v1` reserva aproximadamente una séptima parte del currículo. Estas tareas jamás se recuperan como ejemplos; se evalúan sin memoria y se conservan en un conjunto etiquetado `holdout`. Un muestreo rotativo no permite comparar niveles de dificultad exactos entre rondas ni certificar progreso.
3. **Memoria de apoyo limitada:** los ejemplos de práctica proceden exclusivamente de resultados exactos de generadores deterministas ya verificados, del mismo dominio y habilidad, distintos de la tarea objetivo y fuera de holdout. Se usan como datos, no instrucciones; no se modifica ningún peso neuronal.

Cada CI intenta doce tareas de práctica, dos reservadas y hasta dos consultas externas, si los recursos lo permiten. Las hipótesis científicas/interdominios quedan pendientes de revisión independiente.

**Pendientes:** importación futura a TCSA autenticada, benchmark de transferencia independiente, modelos mayores y funcionamiento permanente en máquina encendida. RAMSES DICE sigue requiriendo identidad humana real, no solo la frase.
