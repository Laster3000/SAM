# SAM — Sistema Autónomo Modular

> Estado: prototipo experimental. **No es todavía una IA entrenada ni un sistema autónomo validado.**

SAM se está construyendo como una IA modular con dos modos: **TRABAJO** y **EVOLUCIÓN**. Su fundamento es el **razonamiento interdominios**: entender, relacionar conocimientos distantes, extrapolar e interpolar con cautela, generar hipótesis y refutarlas. También estudia la diversidad neurocognitiva, incluida la coexistencia de altas capacidades, autismo y TDAH, sin atribuir diagnósticos humanos a la IA. Su primer laboratorio estudia comprensión del español panhispánico, pragmática, ironía, sátira, crítica y humor intelectual absurdo, además de cinco ámbitos de conocimiento: **biología, física, química, matemáticas y psicología**.

## Condiciones de diseño
- **Cero gasto obligatorio:** sin APIs de pago ni servicios contratados. Los ejercicios y tests iniciales son ejecutables con Python estándar. El uso de modelos abiertos se realizará en infraestructura gratuita disponible y compatible, sin garantía de GPU o funcionamiento continuo.
- **Separado de AUTOFABRICADOR:** este repositorio no modifica AF.
- **Repo público:** nunca subir secretos, datos personales, documentos internos de AF/TCSA, respuestas de proveedores sin permiso ni materiales sin licencia.
- **Trabajo:** ejecuta solo capacidades aprobadas, con criterios medibles.
- **Evolución:** experimenta en ramas/candidatos; no despliega mejoras automáticamente.
- **Verificación interna independiente:** las pruebas de referencia no se generan ni se corrigen por el mismo agente candidato, y pueden fallar o abstenerse.
- **Aprendizaje trazable:** memoria/cápsulas con fuentes y evidencia. Pasar tests no reentrena parámetros del modelo.

## Documento fundacional
- [Fundamento cognitivo de SAM](diseno/FUNDAMENTO_COGNITIVO.md): neurodiversidad, triple excepcionalidad (término no unívoco), metacognición y transferencia entre dominios.
- [Retos interdominios originales](evaluacion/desafios_interdominios.json): analogías, refutaciones, interpolación, extrapolación y conexiones entre ciencias y humor. **Son retos de diseño, no una demostración de aprendizaje.**

## Primeros módulos
1. **Evaluación:** banco de casos con enunciado, dominio, habilidad, respuesta verificable y explicación.
2. **Cápsulas:** conocimiento estructurado, reversible y con referencias; sin confundir hipótesis con evidencias.
3. **Duelo:** ejecutado en CI con dos GGUF abiertos pequeños (Qwen3-0.6B y Qwen2.5-0.5B-Instruct), alternancia creador/crítico, evidencia experimental; sin validación de capacidad general.
4. **Entrenamiento:** opcional posterior con datos cuya licencia lo permita, evaluado contra casos inéditos.

## Objetivos de aprendizaje
- **Español panhispánico:** voseo, ustedes/vosotros, regionalismos, registro y contexto, sin reducir dialectos a estereotipos.
- **Pragmática y humor:** ironía, sarcasmo, sátira, crítica, dobles sentidos, incongruencia y absurdo intelectual; separar significado literal de intención probable.
- **Matemáticas:** aritmética, álgebra, lógica, probabilidad, demostración y cálculo verificable.
- **Física:** unidades, mecánica, energía, ondas, electromagnetismo y método experimental.
- **Química:** estructura, estequiometría, reacciones, seguridad y conservación de masa.
- **Biología:** célula, genética, evolución, ecología, fisiología y límites de inferencia.
- **Psicología:** cognición, aprendizaje, percepción, métodos, estadísticas y distinción entre evidencia e interpretación; evitar diagnósticos individualizados.

## Próximos hitos
- [ ] Incorporar corpus inicial original con revisión humana y pruebas automáticas.
- [x] Probar 2 modelos abiertos en CI sin pagos; las métricas de calidad siguen siendo insuficientes para declararlos competentes.
- [ ] Registrar resultados reproducibles y crear cápsulas **candidatas**.
- [ ] Verificar generalización en casos inéditos antes de promocionar conocimiento.
- [ ] Mantener el PC apagado durante un ciclo remoto exitoso para demostrar independencia.

Este repositorio representa un **laboratorio de construcción**, no resultados E2E ya acreditados.


## R007/R008/R009 — Módulos de laboratorio integrados en `main`
La rama de desarrollo `sam-r007-ingesta-evaluacion`, integrada tras 64 pruebas unitarias satisfactorias el 18-11-2026, incorpora un selector de dominios/habilidades variados, un comparador de razonamiento directo frente a divergente sobre ejercicios reservados y una bandeja de información con consentimiento. Véase [documentación R007](diseno/SAM-R007-EXPERIMENTOS-VARIADOS.md). El repositorio continúa público, pero el contenido de conversaciones se guarda localmente. GitHub Actions opera en tandas con límites; no puede convertirse en un servidor permanente ilimitado.


## Capacidades reales y límites (18-11-2026)

| Capacidad | Estado |
|---|---|
| Dos modelos abiertos que crean, critican y revisan | Probada en GitHub Actions, modelos muy pequeños |
| Memoria persistida entre tandas con ledger y SHA | Experimental, candidata GitHub, no canon TCSA |
| Selección variada por dominio y habilidad | Probada como código |
| Investigación Wikipedia, analogías, refutaciones | Prototipo; fuentes y respuestas no contrastadas independientemente |
| Modos TRABAJO/EVOLUCIÓN y respuesta a fichero | Interfaz de laboratorio, no servicio de producción |
| Fusionar, dividir, podar agentes de forma reversible | Planes candidatos, no autoejecución ni trasplante de pesos |
| Automejora de estrategias por modelos rivales | Candidatos desde catálogo fijo, no autopromoción |
| Entrada de conocimiento privado consentido | Código local inactivo; sin conexión ChatGPT/AF ni subida a GitHub |
| Autoridad del propietario y RAMSES DICE | Ticket HMAC simulado, NO autenticador humano real |
| Evaluación holdout y métricas por habilidad | Banco público, repeticiones expuestas, sin prueba de generalización |
| 24/7 de inferencia y entrenamiento neuronal | **NO disponible en GitHub Actions**; requiere servicio externo siempre encendido autorizado |
| Reconciliación GitHub→TCSA | Metadatos manuales, importación canónica automática pendiente |

[Modo TRABAJO](diseno/SAM-R009-INTERFAZ-TRABAJO.md) · [Arquitectura y evidencias](diseno/SAM-R009-MODOS-Y-EVIDENCIA.md) · [Recuperación de memoria entre ramas](diseno/SAM-R009-RECUPERACION-ENTRE-RAMAS.md) · [Ejecuciones GitHub](https://github.com/Laster3000/SAM/actions)

**GitHub Actions es CI de desarrollo y pruebas, no una plataforma para hospedar una IA ininterrumpida.** Los ciclos encadenados del proyecto están deliberadamente acotados. El objetivo de ejecución continua y aprendizaje generalizable sigue pendiente de verificarse en infraestructura autorizada sin tocar el PC del propietario.
