# SAM 0.2 — Contrato de verdad y continuidad

SAM = Sistema Autónomo Modular. Proyecto canónico: SAM-CORE en TCSA3000.
Repositorio de ejecución: Laster3000/SAM (público).

## Directrices de producto (todos los requisitos siguen vigentes)
- Inteligencia local-first con modelos de pesos abiertos y nube opcional sin servicios de pago.
- Modos Trabajo y Evolución; el segundo no altera código aprobado.
- Estudio del español panhispánico, ironía, sátira, crítica y humor intelectual absurdo, y biología, física, química, matemáticas y psicología.
- Fundamento interdominios: entender, divergir, conectar, abducir, interpolar, extrapolar, refutar y probar.
- Estudio riguroso de autismo, TDAH, altas capacidades y excepcionalidad múltiple sin atribuir diagnósticos a una IA ni estereotipar a personas.
- Especialistas internos: intérprete, constructor, crítico, corrector, simplificador, escéptico, mutador adversario aislado, detector de errores, generador de alternativas, verificador, árbitro, memoria y supervisor.
- Interrogación autorizada de modelos externos, destilación, RAG, cápsulas jerárquicas y lenguaje compacto medido.
- Componentes versionados, fusión/división y reutilización de habilidades, poda reversible y evolución con benchmarks ciegos; preservar contratos y recuperación.
- Aprendizaje distribuido en nube con múltiples workers, memoria compartida verificada y entrenamiento de pesos opcional con licencia.
- Cero promesas de cómputo ilimitado: no se paga API ni se crea infraestructura de pago.

## Qué hace este código realmente
- Python estándar: invoca dos modelos GGUF distintos mediante llama-cli: creador -> crítico -> creador.
- Intenta responder a ejercicios originales, con campo RESPUESTA, evalúa coincidencia literal y mide si mejora.
- En Evolución conserva únicamente cápsulas CANDIDATAS que superan la prueba estrecha; NO entrena pesos, no hace RAG, no automejora el orquestador.
- El registro de agentes tiene 13 roles y crea fichas de candidatos a fusión y poda, sin ejecutar cambios destructivos.
- CI: tests sin modelos, descarga de dos modelos gratuitos y una ejecución CPU. Corrida semanal si GitHub la permite.
- Todos los artefactos CI son CANDIDATE_PENDING_TCSA; no se crean commits automáticos ni se aprueban por consenso.

## Límite canónico imprescindible
GitHub Actions NO puede escribir de manera garantizada en TCSA3000 cuando el equipo local está apagado. La única forma honesta de conservar ese requisito es dejar los artefactos remotos como PENDIENTES hasta su importación verificada a TCSA3000 con hash, journal, lease y cierre. No afirmar continuidad completa ni aprendizaje continuo hasta probar dicho puente.

## Cómo ejecutar
Python 3.10+ y llama-cli reciente, dos modelos GGUF descargados previamente, sin API:
python -m unittest discover -s tests -v
python -m sam.pilot --mode evolucion --model-a ruta/a.gguf --model-b ruta/b.gguf --llama-cli ruta/llama-cli

## Lo que permanece sin construir o certificar
Autoejecución 24/7 garantizada, aprendizaje neuronal, memoria RAG online, autoedición de agentes en sandbox y restauración E2E, transferencia real de herramientas entre agentes, arbitraje avanzado con tests ciegos, multiworkers elásticos y sincronización autónoma TCSA con el PC apagado. Estos son requisitos activos, NO características declaradas terminadas.

## Documentación fuente
La conversación literal está en TCSA3000, no se publica en este repositorio.
Registros TCSA: LISTA-TCSA-047...052, PROP-108, PROP-109, PROP-110 y PROP-111.
