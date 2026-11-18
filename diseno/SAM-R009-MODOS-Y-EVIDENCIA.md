# SAM R009 — Arquitectura coherente y evidencia de aprendizaje

## Límites operativos
Esta entrega añade **contratos de software**, no una IA plenamente entrenada ni un servicio 24/7. SAM sigue en laboratorio de CI GitHub con presupuesto de ejecuciones. Los términos de GitHub Actions limitan los runners a desarrollo y pruebas, no a alojar una IA permanente. No usar el ordenador del propietario ni los servicios de AUTOFABRICADOR.

## Dos modos
`sam.architecture.Arquitectura` proporciona `TRABAJO` y `EVOLUCION`.
- **TRABAJO:** únicamente puede anunciar capacidades con `VERIFICADA_INDEPENDIENTEMENTE` y licencia explícita; ninguna operación de mutación está permitida.
- **EVOLUCION:** puede formular planes de fusión, división y poda de agentes; son *candidatos reversibles*, sin ejecución ni autopromoción. El SHA256 del inventario previo acompaña al rollback y no cambia con la propuesta.
- Las piezas de permisos, autoridad, auditoría, recuperación y verificación son protegidas; se prohíbe retirarlas o trasplantarlas. Se validan dependencias, inexistentes y ciclos.

La implementación todavía **no** incluye un sistema integrado capaz de cumplir encargos arbitrarios en modo TRABAJO, ni trasplantar habilidades internas de pesos entre modelos. Estos contratos sirven para construirlo y mantenerlo coherente.

## Evidencia
`python3 -m sam.metrics state/eventos.jsonl --output learning-metrics.json` valida el historial con `sam.quality` y muestra por disciplina tasa literal, ejercicios distintos y repeticiones de evaluación reservada. Un banco público y repetido no certifica aprendizaje ni generalización, aunque una tasa mejore. Las muestras de práctica no se mezclan con holdout. Las futuras evaluaciones deberán ser **externas, independientes y suficientemente amplias** antes de atribuir mejorías a SAM.

Las funciones R007/R008 de la rama experimental incluyen: selección diversa de tareas, comparación de estrategias, propuestas de modificación del código generadas desde catálogo cerrado y captura de textos consentidos en base privada **inactiva en GitHub**. Nunca promueven código de salida neuronal a `main`, ejecutan arbitrariamente respuestas de IA ni sincronizan conversaciones sin permiso.

## Estado de capacidades
- Verificados como software: arquitectura de modos, planes reversibles de evolución, modelos duales en CI, memoria experimental, diversidad, evaluación de estrategias, auditoría de integridad.
- Prototipos: curiosidad y búsqueda pública Wikipedia (una fuente no es contraste), identificador de propietario con gateway simulado, candidatos de autoedición de estrategias, captura privada consentida.
- **Pendientes**: conocimiento fiable multifuente a gran escala, aprendizaje de pesos y de transferencia certificado, mejor modelo autónomo de código, Trabajo utilizable con encargos generales, autenticación real del propietario, reconciliación automática GitHub→TCSA, despliegue externo verdadero 24/7 sin utilizar equipos del usuario y economía de recursos comparada.
