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
3. **Duelo:** adaptadores para dos modelos de pesos abiertos, con creador y crítico, y límites de rondas. No activado hasta disponer de ejecutores compatibles.
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
- [ ] Probar 2 modelos de pesos abiertos sin pagos y medir recursos reales.
- [ ] Registrar resultados reproducibles y crear cápsulas **candidatas**.
- [ ] Verificar generalización en casos inéditos antes de promocionar conocimiento.
- [ ] Mantener el PC apagado durante un ciclo remoto exitoso para demostrar independencia.

Este repositorio representa un **laboratorio de construcción**, no resultados E2E ya acreditados.
