# SAM R007 — Experimentos variados, captura consentida y comparación de estrategias

SAM continúa siendo un **prototipo**. Las tareas se prueban en GitHub mediante modelos de pesos abiertos; ni los resultados ni el número de rondas demuestran por sí solos aprendizaje generalizable.

## Prioridad elegida: variedad
El muestreador \`sam.diversity\` prioriza cobertura de **dominios y habilidades distintas** y ejemplos poco ensayados, en lugar de repetir muchos cálculos similares. Se activa con \`--diverse\` en \`sam.worker\`.

El ensayo \`sam.strategy_eval\` compara dos estrategias sobre las **mismas tareas**, usando los mismos modelos para cada caso: respuesta directa y exploración de analogías entre disciplinas con revisión de supuestos. El informe muestra aciertos literales y diferencia, sin promocionar ninguno como aprendizaje. Los casos reservados se excluyen de memoria de práctica; como el corpus original es público, NO se trata de un benchmark ciego independiente.

En la CI pública se ejecutan tandas acotadas de tareas y hasta 3 temas de investigación pública por ciclo. Los resultados candidatos se archivan en \`sam-candidates\`. No entrenan pesos, no autorizan cambios automáticos en \`main\`, ni se consideran conocimientos canónicos sin verificación TCSA3000.

## Captura de ideas y conversaciones (privada por defecto)
El código puede ser público; las transcripciones y los datos aportados por personas **no se suben a GitHub**. Para importar una transcripción TXT con autorización:

\`\`\`bash
python -m sam.knowledge_ingest --file conversacion.txt --source chat-autorizado --consent
python -m sam.knowledge_ingest --search analogias
\`\`\`

Un lote de archivos TXT/MD autorizados:

\`\`\`bash
python -m sam.knowledge_ingest --folder corpus-autorizado --source corpus-1 --consent
\`\`\`

La base se crea localmente en \`.sam-private/conocimiento.sqlite3\` (no versionar ni publicar). Conserva texto íntegro, origen, SHA256, fragmentos y estado sin verificar. Los documentos no se convierten en «verdad» por importarse.

Para recibir entradas con un adaptador local autorizado, configurar una variable de entorno \`SAM_CAPTURE_TOKEN\` con un token largo y ejecutar \`python -m sam.capture_bridge\`. Solo escucha en \`127.0.0.1:8768\`, requiere cabecera \`Authorization: Bearer ...\` y un JSON con \`text\`, \`source_id\` y \`consent: true\`. **No existe aún conexión automática ChatGPT→SAM**; necesitaría integración específica autorizada.

## Ciclos intensivos dentro de las condiciones de GitHub
GitHub Actions es laboratorio CI, no un servidor 24/7. El workflow permite varias rondas y encadenamiento **acotado**, con timeout, concurrencia serializada y cuotas. No usar cadenas perpetuas ni evadir reglas de la plataforma. Para operación permanente se necesita una máquina que permanezca encendida, ejecutando el supervisor \`sam.supervisor\` bajo límites de recursos.

## Verificación
\`\`\`bash
python -m unittest discover -s tests -v
python -m sam.worker --dry-run
\`\`\`

Esta rama es experimental. **No fusionar sin revisar CI y verificar que los cambios no rompen el flujo anterior**.
