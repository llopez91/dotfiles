# write-issue — referencia

Se abre en la fase 2 (qué docs leer) y en la 4 (montar el borrador). No hace falta
leerla entera: ve a la sección que necesites.

- [Qué doc leer](#qué-doc-leer)
- [Labels](#labels)
- [Plantillas por tipo](#plantillas-por-tipo)
- [Un ejemplo bueno y uno malo](#un-ejemplo-bueno-y-uno-malo)

## Qué doc leer

Leer los doce docs en cada issue es caro y termina en que se leen mal. Lee los que
toque el issue — y **siempre** los dos de la última fila, que son los que evitan
reabrir decisiones cerradas o duplicar trabajo ya planeado.

| Si el issue toca… | Lee |
| --- | --- |
| Regla de negocio: elegibilidad, montos, categorías, multas, comisiones | `docs/PRD.md`, `docs/CREDIT.md`, `docs/TDD.md` §1 |
| Tablas, columnas, migraciones, RLS | `docs/TDD.md` §2 — **el modelo entidad-relación vive ahí** — y `backend/db/migrations/` |
| Pantalla, componente, tabla, formulario, color | `docs/DESIGN_SYSTEM.md` y `frontend/src/styles/variables.css` |
| Endpoint, handler, servicio, DTO | `docs/TDD.md` §0 y §3, y la cadena `dto → repository → service → handler → app router` |
| Correos, notificaciones in-app | `docs/NOTIFICATIONS.md` |
| Direcciones, SEPOMEX, geolocalización | `docs/ADDRESSES.md` |
| Ajustes de la app, feature flags | `docs/SETTINGS.md` |
| El reparto de la demo (C1…C8, Gaby, Hugo…) | `docs/DEMO_PLAYBOOK.md` |
| **Siempre** | `docs/OPERATIONAL_DECISIONS.md` y `docs/OPEN_QUESTIONS.md` (no re-litigar lo decidido) · `docs/ROADMAP.md` (no duplicar lo planeado) |

Cita el doc cuando cambie el issue: si el PRD dice que la categoría D exige
autorización del admin, eso pertenece al issue, no a la cabeza de quien lo escribió.

## Labels

Tres ejes, siempre los tres. Valídalos con `gh label list` antes de usarlos; si no
existe el módulo que necesitas, dilo en el issue en vez de forzar uno que no encaja.

**Tipo** — `bug` · `enhancement` · `documentation` · `tech-debt` · `epic` · `feature` · `story`

**Área** — `backend` (Go) · `frontend` (Vue) · `infra` (Docker, deploy, migraciones)

**Módulo** — `module:auth` · `module:addresses` · `module:customers` · `module:users` ·
`module:collections` (cobranza y multas) · `module:loans` · `module:renewals` ·
`module:contract` · `module:reports` · `module:notifications` · `module:pwa` ·
`module:zones`

Si el arreglo puede ser solo de frontend **o** tocar backend según el enfoque, ponlo
en el issue: el label de área condiciona quién lo toma.

## Plantillas por tipo

### bug

```markdown
## Qué pasa
[El síntoma, en las palabras de quien reportó. Presente, sin diagnóstico.]

## Comportamiento esperado
[Qué debería pasar en su lugar.]

## Por qué pasa
[El mecanismo. Cada afirmación con su `archivo:línea`. Una tabla ayuda cuando hay
varios caminos que se comportan distinto.]

## Lo que NO hay que tocar
[Lo que ya funciona por diseño y alguien podría "arreglar" de paso. "Nada" si no hay.]

## Criterios de aceptación
- [ ] …
```

### enhancement / feature / story

Igual, pero **Por qué pasa** se cambia por **Estado actual**: qué existe hoy, dónde
(`archivo:línea`) y por qué no alcanza. Sin esto, un enhancement se lee como un deseo
y quien lo tome empieza por descubrir lo que ya hay.

Añade **Alcance propuesto** cuando el trabajo cruce capas: qué toca en backend, qué en
frontend y qué queda fuera.

### tech-debt

**Estado actual** + **Qué duele** (el costo concreto: qué se rompe, qué se ralentiza,
qué no se puede hacer) + **Lo que NO hay que tocar**. Una deuda sin costo descrito no
se prioriza nunca.

### documentation

**Qué dice el doc** vs **qué hace el código**, ambos con su cita. Las derivas de
documentación se arreglan en minutos si el issue trae las dos líneas enfrentadas.

## Un ejemplo bueno y uno malo

**Malo** — todo síntoma, sin mecanismo:

> **Título:** Bug: las multas no se actualizan
>
> Cuando el admin rechaza una negociación, el carterista sigue viendo la multa como
> pendiente. Debería actualizarse. Revisar el módulo de multas.
>
> Labels: `bug`

Falla en todo lo que cuesta caro después: no dice **dónde** está el mecanismo, así que
quien lo tome vuelve a investigar; no distingue qué resoluciones sí se ven y cuáles
no, que es el corazón del problema; no advierte que volver a negociar tras un rechazo
ya funciona a propósito, así que invita a "arreglarlo"; no tiene criterios de
aceptación; y le faltan dos de los tres ejes de label.

**Bueno** — el issue #173 de este repo. Lo que lo hace útil:

- La causa raíz en una tabla que enfrenta las cuatro resoluciones con lo que cada una
  escribe en `penalties`, y con eso queda claro por qué `ACCEPT` se ve y `REJECT` no.
- Cada afirmación con su `archivo:línea` verificado.
- Una sección **Lo que NO hay que tocar** que dice explícitamente que reenviar
  negociaciones tras un rechazo ya funciona y es intencional (#128), y que por eso no
  se añadan guardas nuevas.
- Siete criterios de aceptación verificables, incluido uno de no-regresión.
- Los tres ejes de label.

Un issue así se implementa sin volver a abrir la investigación. Ese es el estándar.
