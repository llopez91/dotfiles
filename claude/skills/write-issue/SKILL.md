---
name: write-issue
version: 1.0.0
description: Usar cuando alguien reporta un fallo, pide una mejora o quiere dejar una tarea escrita — "esto está fallando", "crea un issue", "levanta un ticket", "reporta esto", "documenta esta tarea", "quisiera que se pudiera…". También cuando un reporte llega vago o a medias y hay que investigarlo antes de poder registrarlo.
---

# Write Issue

Convierte un reporte en lenguaje natural en un issue de GitHub que quien lo
implemente pueda tomar sin volver a investigar desde cero.

Medido sobre tres reportes reales de este repo, un agente sin esta skill ya investiga
bien y acierta la causa raíz; lo que falla es el piso: leyó los docs del proyecto 0, 1
y 4 veces según el caso, puso "lo que no hay que tocar" en 1 de 3, e inventó una
estructura distinta cada vez. Esta skill no enseña a investigar: **fija ese piso**.

## El issue son estas siete partes, en este orden

1. **Título** — el síntoma en una línea. Sin prefijo `Bug:`/`Feat:`: el label ya lo dice.
2. **Qué pasa** — el síntoma en las palabras de quien lo reportó.
3. **Comportamiento esperado** — qué debería pasar. En un `enhancement` esta parte es
   **Estado actual**: qué hay hoy y por qué no alcanza.
4. **Por qué pasa** — el mecanismo, con `archivo:línea`. Es la parte que separa un
   issue de un ticket, y la que evita que la investigación se pague dos veces.
5. **Lo que NO hay que tocar** — lo que ya funciona por diseño. Sección propia, nunca
   una frase suelta dentro del análisis: es lo que impide que alguien "arregle" algo
   intencional. Si de verdad no hay nada, se escribe "nada".
6. **Criterios de aceptación** — checkboxes que alguien más pueda verificar sin
   preguntarte.
7. **Labels** — los tres ejes: tipo, área y módulo.

Cuando una parte no aplica, se dice por qué en una línea. Omitirla en silencio es
justo el fallo que esto viene a cerrar.

**Un issue no es un plan.** Describe el problema y cómo se comprueba que quedó
resuelto; el cómo implementarlo es trabajo de `start-issue`. Secciones tipo "DoDone" o
un desglose de tareas envejecen mal dentro de un issue.

## Las cinco fases

1. **Clasificar.** El tipo, y sobre todo **cuántos issues son**. Un reporte con
   problemas independientes se parte en varios y se explica el criterio del corte; dos
   síntomas con la misma causa raíz se unen en uno.
2. **Investigar.** Código primero —backend y frontend— hasta el `archivo:línea` que
   explica el mecanismo, y se comprueba que exista: una ruta inventada manda a quien
   implemente a buscar humo. Después, los docs que apliquen según la tabla de
   `reference.md`. Y `gh issue list --search --state all` para no duplicar.
3. **Reencuadrar o preguntar.** Si la investigación contradice el reporte, dilo y
   propón el issue real: "esto ya funciona por diseño, y aquí está la prueba" es un
   resultado válido y a veces el más valioso. Si queda una ambigüedad que cambiaría el
   trabajo, pregunta; si no lo cambiaría, asume y deja la asunción escrita.
4. **Borrador.** Muestra los N borradores completos y espera el visto bueno.
   Publicar sin revisar convierte un malentendido en ruido permanente del tracker.
5. **Publicar.** `gh issue create` con los labels validados contra `gh label list` —
   nunca inventados. Devuelve la URL.

## Referencia

`reference.md`, en esta carpeta: tabla de qué doc leer, los labels con sus valores
reales, plantillas por tipo y un ejemplo bueno contra uno malo. Ábrelo en la fase 2 y
en la 4.
