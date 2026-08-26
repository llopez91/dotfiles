# dotfiles

Configuración personal y skills de Claude Code, para Windows y Linux/macOS.

| Carpeta | Qué hay |
|---------|---------|
| [claude/](claude/) | Skills propias de Claude Code y su instalador |
| [scripts/](scripts/) | Scripts de mantenimiento del sistema |
| [shell/](shell/) | Aliases para bash/zsh y PowerShell |

## Claude

Skills escritas a mano: el kit de edición fotográfica y publicidad
(`studio-creative` y sus seis etapas), el flujo de issues sobre GitHub Projects,
y dos generales — `git-flow` y `browser-test`.

Lo que viene de plugins o instaladores no se versiona aquí, pero sí está
listado en [claude/README.md](claude/README.md#skills-que-no-están-en-este-repo)
para poder reconstruir la máquina.

```powershell
cd dotfiles/claude
.\install.ps1
```

```bash
cd dotfiles/claude
bash install.sh
```

Enlaza cada skill a `~/.claude/skills/` con symlinks (junctions en Windows si no
hay privilegios). El repo queda como la única copia.

> El kit creativo necesita una `KIE_API_KEY` en `claude/skills/studio-creative/.env`.
> El instalador crea el archivo a partir del `.env.example`; solo pon la llave.

## Scripts

| Script | Descripción |
|--------|-------------|
| `update` / `update.ps1` | Actualiza los paquetes del sistema |
| `cleanup` / `cleanup.ps1` | Limpia cachés, temporales y paquetes sin usar |

Las versiones sin extensión son para Linux/macOS (apt, dnf, pacman). Las `.ps1`
son para Windows (winget, scoop, npm, pip, docker).

```powershell
cd dotfiles/scripts
.\install.ps1
```

```bash
cd dotfiles/scripts
bash install.sh
```

Ambos agregan la carpeta al `PATH`.

## Shell

Atajos que se cargan en cada sesión de terminal.

| Alias | Comando |
|-------|---------|
| `cl` | `claude --dangerously-skip-permissions` |
| `cx` | `codex --dangerously-bypass-approvals-and-sandbox` (solo PowerShell) |
| `cm mensaje` | `git commit -m "mensaje"` |
| `cma mensaje` | `git add -A && git commit -m "mensaje"` |
| `gs` | `git status` |
| `ga` / `gaa` | `git add` / `git add -A` |
| `gp` / `gl` | `git push` / `git pull` |
| `gd` | `git diff` |
| `glog` | `git log --oneline --graph` |
| `gb` / `gco` / `gsw` | `git branch` / `checkout` / `switch` |
| `nd` / `nb` / `ns` / `ni` / `nt` | `npm run dev` / `build` / `start` / `install` / `test` |
| `r` | `ranger` con cd al salir (solo bash/zsh) |
| `c` | limpiar pantalla |
| `..` / `...` | subir uno o dos directorios |
| `ll` / `la` / `l` | listados |

```powershell
cd dotfiles/shell
.\install.ps1
```

```bash
cd dotfiles/shell
bash install.sh
```

## Créditos

La estructura del repo, los scripts y los aliases salen de
[fazt/dotfiles](https://github.com/fazt/dotfiles).
