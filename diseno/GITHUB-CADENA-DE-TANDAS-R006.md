# SAM R006 — GitHub encadena las tandas (sin usar el PC)
El objetivo operativo es ejecutar pruebas del software SAM **de forma consecutiva en GitHub**, sin acudir al PC local ni a AUTOFABRICADOR.

**Dos niveles de encadenamiento:**
- Dentro de cada ejecución de GitHub Actions, el worker realiza **2 tandas seguidas** con `--interval 0`, guardando la memoria local y los informes.
- Al finalizar correctamente la publicación en `sam-candidates` y el artefacto GitHub, el mismo workflow llama a la API oficial `workflow_dispatch` mediante `GITHUB_TOKEN` para iniciar la siguiente ejecución en GitHub. Se permiten **3 ejecuciones por disparador** (etapas 0, 1, 2). Al agotarlas, el cron mantiene cuatro oportunidades diarias para continuar. El límite protege la cuenta y cumple la finalidad de pruebas de software sin ofrecer hosting ininterrumpido.

Las ramas `main` y `sam-candidates` están separadas: GitHub conserva las respuestas, fallos, auditoría y manifiesto de cada tanda. `CANDIDATE_PENDING_TCSA` sigue siendo obligatorio y una coincidencia literal no demuestra aprendizaje neuronal.

**Importante:** GitHub Actions tiene restricciones contractuales: no es un servicio de computación continua ni permite cargar de forma desproporcionada sus servidores. No se afirma que este mecanismo opere 24/7 ni que pueda ejecutar un bucle infinito. Si el runner o el API fallan, el cron intenta recuperar en el siguiente disparador. No se usan credenciales de usuario ni tokens externos. Un presupuesto o consentimiento distinto debe configurarse fuera de la cuota de CI.

Configuración deliberadamente no invasiva: ningún programa, tarea de Windows ni GPU en el equipo del propietario se toca en R006. La tarea local SAM-Continuous-R005 previamente deshabilitada permanece como estaba.

Pruebas esperadas: CI y `sam.chain` pasan; primera ejecución `push` produce `workflow_dispatch` paso 1, y ésta paso 2; el paso 2 detiene el encadenamiento hasta la siguiente activación. Verificar números de ejecución y archivo de candidatos, no presuponer éxito.
