# Claude

Skills propias para [Claude Code](https://claude.com/claude-code). Solo las
escritas a mano — lo que viene de un plugin o de un instalador no vive aquí,
está listado abajo en [Skills que no están en este repo](#skills-que-no-están-en-este-repo).

## Instalación

Enlaza cada skill de `skills/` a `~/.claude/skills/`, así el repo queda como la
única copia y los cambios se reflejan al vuelo.

**Windows (PowerShell):**

```powershell
cd dotfiles/claude
.\install.ps1
```

Sin privilegios de symlink, cae automáticamente a junctions.

**Linux/macOS:**

```bash
cd dotfiles/claude
bash install.sh
```

El instalador crea `skills/studio-creative/.env` a partir del `.env.example` si
no existe. Ponle tu `KIE_API_KEY` antes de usar las etapas de IA del kit
creativo.

Si en `~/.claude/skills/` ya tienes la skill como directorio real y con un
`.env` dentro, el instalador lo copia al repo antes de reemplazarla. El `.env`
no se versiona, pero no se pierde.

## Skills

### Kit creativo

Edición fotográfica y publicidad para redes. `studio-creative` es la
orquestadora; las demás son las etapas y se pueden llamar sueltas.

**Las siete comparten el motor Python que vive en `studio-creative/engine/`.**
No las separes: `foto-luz` y compañía apuntan a esa ruta.

| Skill | Qué hace | IA |
|-------|----------|-----|
| `studio-creative` | Diagnostica la foto y encadena las demás etapas | — |
| `foto-luz` | Exposición, balance de blancos, sombras, color (Pillow) | no |
| `foto-encuadre` | Endereza, recorta y saca los tamaños por plataforma | no |
| `foto-fondo` | Cambia el fondo por uno de estudio | sí |
| `foto-escena` | Genera un escenario completo para campaña | sí |
| `arte-social` | Compone el arte: titular, precio, CTA, logo | no |
| `copy-social` | Escribe el copy del post y los hashtags | no |

La regla del kit: la IA solo toca lo que los píxeles no pueden hacer. Así el
sujeto de la foto no cambia de cara.

Las etapas marcadas con IA usan [Kie AI](https://kie.ai) y gastan créditos.

### Flujo de issues

Plantillas del ciclo de trabajo sobre GitHub Issues y Projects. **Están
calibradas para el poly-repo de Fletix** (IDs del tablero, nombres de repos,
rutas de doc). Para otro proyecto, cópialas y cambia las constantes del
encabezado.

| Skill | Qué hace |
|-------|----------|
| `write-issue` | Redacta el issue con su criterio de aceptación |
| `start-issue` | Asigna, mueve el tablero, analiza y guarda el plan |
| `complete-issue` | Verifica, commitea, abre el PR y cierra |

### Generales

| Skill | Qué hace |
|-------|----------|
| `git-flow` | Ramas, commits, push, PR y merge. Conventional Commits con ticket, sincronizar antes de commitear, y cero rastro de IA en el historial |
| `browser-test` | Prueba funcionalidad web en navegador real, con Playwright CLI o el Chrome de Claude Desktop |

## Skills que no están en este repo

Vienen de plugins o instaladores. Se reinstalan con un comando, no hay por qué
versionarlas aquí. Esta es la lista para reconstruir la máquina.

### Plugins

```bash
claude plugin marketplace add anthropics/claude-plugins-official
claude plugin marketplace add anthropics/skills
claude plugin marketplace add cloudflare/skills
claude plugin marketplace add warpdotdev/claude-code-warp
claude plugin marketplace add ayghri/i-have-adhd
claude plugin marketplace add DietrichGebert/ponytail
```

| Plugin | Marketplace |
|--------|-------------|
| `superpowers` | claude-plugins-official |
| `code-review` | claude-plugins-official |
| `code-simplifier` | claude-plugins-official |
| `frontend-design` | claude-plugins-official |
| `skill-creator` | claude-plugins-official |
| `context7` | claude-plugins-official |
| `vercel` | claude-plugins-official |
| `gopls-lsp` | claude-plugins-official |
| `document-skills` | anthropic-agent-skills |
| `cloudflare` | cloudflare |
| `warp` | claude-code-warp |
| `i-have-adhd` | i-have-adhd |

```bash
claude plugin install superpowers@claude-plugins-official
```

### Skills de instalador (`~/.agents/skills/`)

Se enlazan solas a `~/.claude/skills/` cuando instalas la herramienta dueña.

| Grupo | Skills | De dónde |
|-------|--------|----------|
| AWS | `amazon-bedrock`, `aws-billing-and-cost-management`, `aws-blocks`, `aws-cdk`, `aws-cloudformation`, `aws-compute`, `aws-containers`, `aws-deployment`, `aws-messaging-and-streaming`, `aws-observability`, `aws-sdk-js-v3-usage`, `aws-sdk-python-usage`, `aws-sdk-swift-usage`, `aws-serverless`, `launch-with-aws`, `signing-in-to-aws` | Instalador de skills de AWS |
| InsForge | `insforge`, `insforge-cli`, `insforge-debug`, `insforge-backend-advisor`, `insforge-integrations` | InsForge CLI |
| Orca | `orca-cli`, `orchestration`, `computer-use` | App de Orca |
| Descubrimiento | `find-skills` | Ecosistema abierto de agent skills |
| Otras | `interface-design` | — |

### Strix — pentesting (pendiente de instalar)

[Strix](https://github.com/usestrix/strix) es una herramienta open source de
pentesting con agentes. Trae nueve skills que se instalan de un jalón:

```bash
npx skills add usestrix/strix
```

| Skill | Qué hace |
|-------|----------|
| `penetration-testing-with-strix` | Corre escaneos headless con el CLI local y lee los resultados |
| `managed-pentesting-with-strix` | Usa la plataforma [app.strix.ai](https://app.strix.ai) por REST, sin Docker ni llave de LLM |
| `fix-security-vulnerabilities-with-strix` | Remedia los hallazgos y vuelve a escanear para verificar |
| `ci-security-scanning-with-strix` | Escaneo de PRs en CI |
| `application-security-testing` | Flujo por objetivo: aplicación |
| `web-app-penetration-testing` | Flujo por objetivo: app web |
| `api-security-testing` | Flujo por objetivo: API |
| `owasp-top-10-testing` | Flujo por objetivo: OWASP Top 10 |
| `find-security-vulnerabilities-in-code` | Revisión de código en busca de vulnerabilidades |

Para el CLI local hace falta **Docker corriendo** y una llave de LLM:

```bash
curl -sSL https://strix.ai/install | bash
export STRIX_LLM="anthropic/claude-opus-5"
export LLM_API_KEY="tu-llave"
strix --target ./mi-app
```

Los resultados quedan en `strix_runs/<nombre>`. La variante `managed-*` no
necesita nada local. Los identificadores de modelo válidos están en
[docs.strix.ai](https://docs.strix.ai/llm-providers/overview).

> Úsala solo contra código y objetivos propios o con autorización explícita.

### Sueltas

`drawio` y `playwright-cli` están instaladas a mano en `~/.claude/skills/` y no
son propias. `playwright-cli` es la que usa `browser-test`, así que hace falta.

Si no recuerdas de dónde salió alguna, la skill `find-skills` las busca en el
ecosistema abierto.
