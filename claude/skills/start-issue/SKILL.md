---
name: start-issue
version: 3.0.0
description: Start work on issue, update project board, analyze, and save plan
---

# Start Issue Workflow

`$1` = el número del issue. Sustituye el número real en cada comando.

## 0. Dónde vive cada cosa (poly-repo)

Fletix son **cinco repos** de la org `alcoreintelligence`. Los **issues viven
solo en `fletix`**; el código de cada historia va al repo que le toque según su
label `capa:`.

| Repo | Contiene | Labels que lo mandan aquí |
|---|---|---|
| `fletix` | Doc (PRD, ER, TDD, DESIGN, WORKFLOW) **y todos los issues** | — |
| `fletix-api` | API en Go | `capa:backend`, `capa:data` |
| `fletix-web` | Portal React/Vite | `capa:web` |
| `fletix-mobile-app` | App del operador (Expo) | `capa:mobile` |
| `fletix-landing` | Landing pública (Astro) | — |

Constantes del tablero **Fletix MVP**
(`https://github.com/orgs/alcoreintelligence/projects/1`):

| Qué | Valor |
|---|---|
| project number / owner | `1` / `alcoreintelligence` |
| project-id | `PVT_kwDOEexqVM4Bc34L` |
| campo *Status* | `PVTSSF_lADOEexqVM4Bc34LzhXdhEM` |
| Backlog · Todo | `58d2ee09` · `c1678944` |
| **En progreso** | `6758f949` |
| Bloqueado · **En revisión** | `38f649e0` · `d47c5860` |
| **Hecho** | `c5354515` |

## 1. Política de ramas

**Una rama por issue, desde `main`**, en el repo del código — es lo que fija
[WORKFLOW sección 3](../../../fletix/docs/WORKFLOW.md) y lo que espera el
tablero:

| Prefijo | Uso |
|---|---|
| `feat/<n>-<slug>` | funcionalidad nueva (historias) |
| `fix/<n>-<slug>` | correcciones |
| `chore/<n>-<slug>` | infraestructura, CI, tooling |
| `docs/<n>-<slug>` | documentación |

El trabajo aterriza por **PR con cierre cross-repo**
(`Closes alcoreintelligence/fletix#$1`), no empujando a `main` directo. Eso lo
cierra la skill `complete-issue`.

Convenciones de commit del repo: mensaje **en español e imperativo** con
`(#$1)`; **sin** `Co-Authored-By`, sin `--author`, sin tocar la firma GPG.

## 2. Shell y plataforma

Corre los comandos con la herramienta **Bash** — existe en macOS, Linux y
Windows (Git Bash), así que la sintaxis POSIX (`$(...)`, `|| true`, `~`)
funciona igual en todos lados. Si tu runtime no tiene Bash, usa el equivalente
en PowerShell. Para escribir archivos dentro del repo prefiere las herramientas
Write/Read: el texto en español lleva acentos y el heredoc de Git Bash los
maltrata.

## 3. Modelo

- **App de escritorio de Claude:** no admite `opusplan`. Planea con
  `/model opus` y, con el plan aprobado (paso 8), pásate a `/model sonnet`.
- **Cualquier otro runtime:** `/model opusplan`.
- Luego `/effort high`.

En sesiones no interactivas estos comandos no se pueden abrir: sigue con el
modelo que ya tengas y dilo en el reporte.

## 4. Leer el issue — y si es épica, sus sub-issues

```bash
gh issue view $1 --repo alcoreintelligence/fletix --json number,title,state,labels,body
```

Si el estado sale `MERGED` o la URL termina en `/pull/`, **ese número es un PR,
no un issue**: en `fletix` issues y PRs comparten numeración. Dilo y pide el
número bueno en vez de trabajar sobre un PR ya mergeado.

Con label `epic`, lee también sus sub-issues antes de planear: el trabajo real
vive ahí.

## 5. Asignarlo (idempotente)

```bash
gh issue edit $1 --repo alcoreintelligence/fletix --add-assignee @me || true
```

## 6. Mover el tablero a *En progreso*

`item-add` es idempotente: si el issue ya está en el tablero devuelve el id
existente, sin duplicar. Necesita el scope `project`; si falla con *missing
required scopes*, corre `gh auth refresh -s project,read:project`, avísale al
usuario y sigue con el resto (no te bloquees aquí).

```bash
ITEM_ID=$(gh project item-add 1 --owner alcoreintelligence --url https://github.com/alcoreintelligence/fletix/issues/$1 --format json -q '.id')
gh project item-edit --id "$ITEM_ID" --project-id PVT_kwDOEexqVM4Bc34L --field-id PVTSSF_lADOEexqVM4Bc34LzhXdhEM --single-select-option-id 6758f949 || true
```

Si es una épica, mueve cada sub-issue conforme la empieces, no todas de golpe.

## 7. Planear

Usa la skill `superpowers:writing-plans`. Antes de escribir una línea de plan:

1. **Lee el código**, backend y frontend, hasta el `archivo:línea` que explica lo
   que hay hoy. Una ruta inventada manda a quien implemente a buscar humo.
2. **Lee la doc que aplique** en `fletix/docs/`: PRD (reglas RN-XXX), ER (modelo
   de datos), TDD (diseño técnico), DESIGN (design system y paridad con el
   prototipo), WORKFLOW.
3. **Reconcilia primero ER/PRD/TDD** con las tablas, columnas y buckets que la
   historia implique — antes de codear, no después.
4. **Historias de UI:** cita el par pantalla → componente del prototipo que
   portas ([DESIGN sección 9.1](../../../fletix/docs/DESIGN.md)) y planea a
   **paridad completa en este pase**, no en issues sucesivos de "pulir".

Si la épica cubre subsistemas independientes, escribe **un plan por historia**
en vez de uno gigante. Cada plan debe producir software funcionando y
verificable por sí solo.

## 8. Guardar el plan donde el repo lo guarda

Dos sitios, los dos obligatorios:

1. **Archivo** en el repo de doc: `fletix/docs/superpowers/plans/YYYY-MM-DD-<slug>.md`
   (uno por historia). El plan de una épica va en
   `fletix/docs/plans/plan-issue-$1.md` con las decisiones transversales y el
   índice de los demás.
2. **En el propio issue**, como sección `## Plan`
   ([WORKFLOW sección 2](../../../fletix/docs/WORKFLOW.md)): qué se va a
   construir, las decisiones y cómo se verificará. Así queda ligado a la tarea.

```bash
gh issue comment $1 --repo alcoreintelligence/fletix --body-file <ruta-del-comentario>
```

## 9. Implementar

Si estás en la app de escritorio, pásate a `/model sonnet`. Revisa el plan con
el usuario y ejecútalo.

Recuerda la política del paso 1: rama por issue desde `main`, en el repo del
código. El commit y el PR los cierra `complete-issue` — no empujes a `main`
antes salvo que el usuario lo pida.
