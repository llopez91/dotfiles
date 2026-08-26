---
name: complete-issue
version: 3.0.0
description: Complete issue after push
---

# Complete Issue Workflow

`$1` = el número del issue. Sustituye el número real en cada comando.

## 0. Dónde vive cada cosa

Los **issues viven en `alcoreintelligence/fletix`**; el código, en el repo que
marque la label `capa:` (`fletix-api`, `fletix-web`, `fletix-mobile-app`). Por
eso el PR **cierra el issue cross-repo**.

Constantes del tablero **Fletix MVP**:

| Qué | Valor |
|---|---|
| project number / owner | `1` / `alcoreintelligence` |
| project-id | `PVT_kwDOEexqVM4Bc34L` |
| campo *Status* | `PVTSSF_lADOEexqVM4Bc34LzhXdhEM` |
| **En revisión** | `d47c5860` |
| **Hecho** | `c5354515` |

Corre los comandos con la herramienta **Bash** (Git Bash en Windows). Para
escribir el cuerpo del PR usa Write a un archivo y `--body-file`: el heredoc de
Git Bash maltrata los acentos.

## 1. Antes de cerrar: verificar de verdad

La DoD del [TDD sección 22.3](../../../fletix/docs/TDD.md) no se cumple con que
compile. Según la capa:

**Backend (`fletix-api`):**
```bash
go test ./... && go vet ./... && gofmt -l .
TEST_DATABASE_URL=postgres://postgres:postgres@localhost:5433/fletix_test go test ./test/rls/ -v
```
`gofmt -l` no debe imprimir nada. La prueba de RLS (A≠B) no es opcional: es la
prueba de seguridad del aislamiento entre tenants.

**Web (`fletix-web`):**
```bash
npm test && npx tsc -b && npm run lint
```

**Y el flujo ejercido en la app real**, no solo en pruebas. Si la historia toca
UI, verifica los clics con hit-testing (`document.elementFromPoint`): un
`.click()` por JavaScript pasa aunque el elemento esté tapado.

## 2. Commit y PR

En la rama del issue (`feat/$1-<slug>` o la que toque), en el repo del código:

```bash
git add <solo los archivos de este issue>
git commit -m "<Verbo en imperativo y en español> (#$1)"
git push -u origin <rama>
```

Convenciones del repo: **sin** `Co-Authored-By`, sin `--author`, sin desactivar
la firma GPG. Commitea solo lo que pertenece a este issue.

Abre el PR con el cierre cross-repo:

```bash
gh pr create --repo alcoreintelligence/<repo-del-codigo> \
  --title "<Qué hace> (#$1)" --body-file <archivo>
```

El cuerpo termina con:

```
Closes alcoreintelligence/fletix#$1
```

y, si la historia pertenece a una épica, también:

```
Parte de alcoreintelligence/fletix#<épica>
```

El cuerpo describe **qué se hizo, qué se decidió y cómo se verificó** — no un
listado de archivos.

> **PRs apilados:** si este PR sale de la rama de otro que aún no se mergea,
> dilo en el cuerpo y mergéalos **en orden**. Mergear el de arriba primero
> arrastra commits que no le tocan.

## 3. Mover el tablero

Al abrir el PR, *En revisión*:

```bash
ITEM_ID=$(gh project item-add 1 --owner alcoreintelligence --url https://github.com/alcoreintelligence/fletix/issues/$1 --format json -q '.id')
gh project item-edit --id "$ITEM_ID" --project-id PVT_kwDOEexqVM4Bc34L --field-id PVTSSF_lADOEexqVM4Bc34LzhXdhEM --single-select-option-id d47c5860 || true
```

Al mergear, *Hecho* (mismo comando con `--single-select-option-id c5354515`).

Necesita el scope `project`; si falla con *missing required scopes*, corre
`gh auth refresh -s project,read:project`, avísale al usuario y sigue — cerrar
el issue en el paso 4 no necesita ese scope.

## 4. Cerrar

El `Closes` del PR cierra el issue solo al mergear. Si hiciera falta a mano:

```bash
gh issue close $1 --repo alcoreintelligence/fletix
```

**Una épica no se auto-cierra.** Se cierra cuando todas sus sub-issues están
hechas **y** su DoD se verificó de punta a punta en la app real
([WORKFLOW sección 2](../../../fletix/docs/WORKFLOW.md)).

## 5. Si la historia tocó el contrato OpenAPI

Un cambio en `fletix-api/api/openapi.yaml` no llega solo al portal. Después de
mergear el PR del backend:

```bash
cd ../fletix-web
cp ../fletix-api/api/openapi.yaml contracts/openapi.yaml
npm run codegen
```

y abre el PR de sync en `fletix-web`. Sin eso, el front sigue compilando contra
el contrato viejo.
