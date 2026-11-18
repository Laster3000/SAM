# R009 — Recuperación de experimentos entre ramas

El ledger de `main` vive en `sam-candidates` y el de la rama R007/R008 en `sam-r008-candidates`. Ambos son **candidatos GitHub**, nunca autoridad científica ni canónica TCSA.

`sam.ledger_union` combina fuentes íntegramente auditadas, conserva cada ID de evento una sola vez y **rechaza conflictos** si dos ramas tienen versiones distintas del mismo evento. Es transaccional: valida el resultado antes de reemplazar el archivo destino. En GitHub CI, cuando se publique desde `main`, la importación del histórico experimental se realiza en la fase de publicación para conservar la evidencia de experimentos al integrar PR. En las pruebas de una rama experimental se mantienen ledgers separados.

Se preservan los SHA anteriores y ambas ramas originales en Git; no se borran ficheros, no se promueven conocimientos, no se comparten documentos privados. Si la fuente experimental no está disponible, se sigue con el historial principal. Si existe pero está corrupta o presenta conflictos, **fallar y no publicar**.
