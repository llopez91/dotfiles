# dotfiles

Configuración personal y skills de Claude Code, para Windows y Linux/macOS.

| Carpeta | Qué hay |
|---------|---------|
| [claude/](claude/) | Skills propias de Claude Code y su instalador |
| [oh-my-posh/](oh-my-posh/) | Tema del prompt, con segmento de Python y venv |
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

## Oh My Posh

Tema `zash` con un segmento de Python añadido: icono, nombre del venv y versión
del intérprete.

```
@llope ➜ mi-proyecto git(main)   .venv 3.14.4
```

El segmento aparece solo cuando hay contexto de Python — un venv activo o
archivos `.py` en la carpeta. Con el venv activo muestra su nombre; sin él, solo
la versión.

```powershell
cd dotfiles/oh-my-posh
.\install.ps1
```

Apunta los perfiles de PowerShell 7 y Windows PowerShell 5.1 al tema local
(guarda un `.bak` de cada uno) y comenta cualquier `oh-my-posh init` previo. Al
ser local, el prompt ya no se descarga en cada arranque.

### Fuentes: la variante importa

```powershell
oh-my-posh font install JetBrainsMono
```

Cada Nerd Font se instala en tres variantes, y **no son intercambiables**:

| Familia | Iconos | Para qué |
|---------|--------|----------|
| `JetBrainsMono NF` | doble ancho | editores, no terminales |
| `JetBrainsMono NFM` | **una celda** | **terminales** |
| `JetBrainsMono NFP` | proporcional | texto |

Dónde se configura: en VS Code, `terminal.integrated.fontFamily`; en Windows
Terminal, el `face` del perfil.

**Dos síntomas, dos causas distintas:**

- **Los iconos salen como cuadros vacíos (□)** — la fuente que nombraste no está
  instalada, o no es una Nerd Font. El terminal cae a otra sin glifos.
- **Las letras salen espaciadísimas** (`c u r r e n c y`) — estás usando la
  variante `NF` en vez de `NFM`. El terminal de VS Code mide el ancho de celda a
  partir de la fuente, y los iconos de doble ancho le estiran toda la rejilla.
  Windows Terminal no sufre esto porque hace su propio layout, así que la misma
  fuente puede verse bien ahí y fatal en VS Code.

Por eso aquí VS Code usa `JetBrainsMono NFM` y Windows Terminal se queda con
`0xProto Nerd Font`.

### VS Code no ve una fuente recién instalada

Si instalaste la fuente con VS Code abierto, **no la va a encontrar aunque
recargues la ventana**. VS Code corre sobre Chromium, que enumera las fuentes
del sistema al arrancar el proceso y las cachea; `Developer: Reload Window`
solo reinicia el renderizado, no esa caché.

Ciérralo del todo y vuelve a abrirlo. Que no quede ningún proceso:

```powershell
Get-Process Code -ErrorAction SilentlyContinue | Measure-Object | Select-Object -ExpandProperty Count
```

Para probar el glifo aislado, sin depender del prompt:

```powershell
"fae=`u{E235} dev=`u{E73C} seti=`u{E606}"
```

Tres iconos de Python significa que la fuente cargó. Si siguen saliendo cajas
con la fuente correcta y VS Code reiniciado, prueba
`terminal.integrated.gpuAcceleration: "off"` — el renderer WebGL cachea el
atlas de glifos.

Evita listar fuentes de respaldo en `terminal.integrated.fontFamily`. Chromium
hace fallback por carácter y con codepoints del Área de Uso Privado a veces se
salta la primaria y cae a una sin glifos.

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
