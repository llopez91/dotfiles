---
name: git-flow
description: Ciclo de vida de ramas, commits, push, PR y merge. Úsalo siempre que vayas a crear una rama, hacer commit, subir cambios, abrir o mergear un PR, o escribir comentarios en GitHub. Fija el formato de los mensajes (Conventional Commits con número de ticket), obliga a sincronizar antes de commitear y prohíbe cualquier rastro de IA en el historial.
---

# Git — ciclo de vida

Aplica a **todo** lo que toca el historial: ramas, commits, push, PRs, merges y
comentarios. No es opcional ni depende del proyecto.

## La regla que no se negocia

**Nada en el repositorio delata que se usó una IA.**

Prohibido en commits, PRs, merges, comentarios, descripciones y nombres de rama:

- `Co-Authored-By: Claude ...` o cualquier `Co-Authored-By` de un agente
- `🤖 Generated with [Claude Code]` o cualquier firma equivalente
- Menciones a Claude, Codex, Copilot, GPT, "asistente", "IA" o "generado por"
- Emojis de robot, banners o pies de página automáticos

Tampoco uses `--author` para atribuirle el trabajo a otra persona, ni desactives
la firma GPG (`--no-gpg-sign`), ni saltes hooks (`--no-verify`).

Si una plantilla de PR del repo trae un bloque de estos, bórralo antes de abrir.

## 1. Antes de tocar nada: sincronizar

**Siempre** antes de crear la rama y **otra vez** antes de commitear. Es lo que
evita el conflicto, no lo que lo resuelve tarde.

```bash
git status
git fetch origin
git pull --rebase origin main
```

`--rebase` mantiene el historial lineal y evita los merges de "Merge branch
'main' into..." que ensucian el log.

Si el pull trae conflictos, resuélvelos **antes** de seguir trabajando. No
commitees encima de un árbol en conflicto.

Si `git status` muestra cambios que no son tuyos o de otro trabajo, **no los
arrastres**. Commitea solo lo que pertenece a esta tarea.

## 2. Rama

Una rama por ticket, siempre desde `main` (o la rama base del repo) ya
actualizada.

| Prefijo | Cuándo |
|---|---|
| `feat/` | funcionalidad nueva |
| `fix/` | corrección de bug |
| `chore/` | infraestructura, dependencias, tooling, CI |
| `refactor/` | reestructurar sin cambiar comportamiento |
| `docs/` | documentación |
| `test/` | pruebas |

Formato: `<prefijo>/<ticket>-<slug-corto>`

```bash
git switch -c feat/1234-login-google
```

El slug va en minúsculas, con guiones, tres o cuatro palabras máximo.

## 3. Commit

**Conventional Commits**, con el número de ticket y una descripción breve.

```
<tipo>(<alcance opcional>): <descripción breve> (#1234)
```

Tipos: `feat`, `fix`, `chore`, `refactor`, `docs`, `test`, `perf`, `style`, `build`, `ci`.

Reglas del mensaje:

- **Una línea.** Si necesitas explicar más, el commit probablemente hace dos cosas.
- **Imperativo**: "agrega", no "agregado" ni "agregando".
- **Minúscula** después de los dos puntos, sin punto final.
- **Máximo ~70 caracteres** antes del `(#1234)`.
- El idioma del mensaje sigue al del repo. Si el historial está en español,
  escribe en español; si está en inglés, en inglés. Míralo antes:
  `git log --oneline -20`.

Ejemplos:

```
feat(auth): agrega login con Google (#1234)
fix(api): corrige timeout en carga de reportes (#1287)
chore(deps): actualiza react a 19.2 (#1290)
refactor(pagos): extrae validación de tarjeta a su propio módulo (#1301)
```

Nada de: `fix: cambios varios`, `update`, `wip`, `arreglos`.

Antes de commitear:

```bash
git pull --rebase origin main   # otra vez: pudo llegar algo mientras trabajabas
git add <solo los archivos de este ticket>
git commit -m "feat(auth): agrega login con Google (#1234)"
```

**No uses `git add -A` a ciegas.** Revisa `git status` y agrega lo tuyo.
**No uses `--amend`** sobre commits ya empujados.

## 4. Push

```bash
git push -u origin feat/1234-login-google
```

Si el push se rechaza porque la base avanzó:

```bash
git pull --rebase origin main
git push
```

Nunca `git push --force` sobre una rama compartida. Si tienes que reescribir tu
propia rama, usa `--force-with-lease`.

## 5. Pull Request

**Título** = el mensaje del commit principal, mismo formato:

```
feat(auth): agrega login con Google (#1234)
```

**Cuerpo breve.** Tres bloques cortos, nada más:

```markdown
## Qué hace
Una o dos frases.

## Cómo se verificó
Los comandos o pasos que corriste.

Closes #1234
```

Lo que **no** va en el cuerpo:

- El listado de archivos modificados — el diff ya lo muestra
- Párrafos explicando la implementación línea por línea
- Secciones vacías ("N/A", "Ninguno") — bórralas
- Cualquier firma o mención de IA

Si el repo es poly-repo y el issue vive en otro repositorio, el cierre es
cross-repo: `Closes <org>/<repo-de-issues>#1234`.

```bash
gh pr create --title "feat(auth): agrega login con Google (#1234)" --body-file pr.md
```

Usa `--body-file` en vez de `--body` con heredoc: Git Bash en Windows maltrata
los acentos.

## 6. Comentarios

En issues, PRs y revisiones: **cortos y precisos**. Una idea por comentario.

- Si señalas un problema, di **dónde** (`archivo:línea`) y **qué** cambiar.
- Si respondes, responde: "hecho", "no aplica porque X". Sin párrafos.
- Sin preámbulos ("¡Buena observación!", "Tienes toda la razón").

## 7. Merge

Antes de mergear:

1. CI en verde.
2. La rama al día con la base (`git pull --rebase origin main` y push si hace falta).
3. Conversaciones resueltas.

Estrategia por defecto: **squash merge**, para que cada PR quede como un commit
limpio en `main`.

```bash
gh pr merge --squash --delete-branch
```

El mensaje del squash es el título del PR — con su formato y su `(#1234)`. Si
GitHub arrastra el listado de commits al cuerpo, límpialo.

**PRs apilados:** si tu PR sale de la rama de otro que aún no se mergea, dilo en
el cuerpo y mergéalos en orden. Mergear el de arriba primero arrastra commits
que no le tocan.

## Checklist rápido

- [ ] `git fetch` + `git pull --rebase` antes de empezar y antes de commitear
- [ ] Rama `<tipo>/<ticket>-<slug>` desde la base actualizada
- [ ] Commit en una línea, Conventional, con `(#ticket)`
- [ ] Solo los archivos de este ticket en el stage
- [ ] PR con título igual al commit y cuerpo de tres bloques
- [ ] Cero rastro de IA en cualquier texto
- [ ] Squash merge con la rama borrada
