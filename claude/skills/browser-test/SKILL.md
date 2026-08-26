---
name: browser-test
description: Prueba funcionalidad web en un navegador real, con Playwright CLI o con el Chrome de Claude Desktop. Úsalo siempre que haya que verificar una pantalla, un formulario, un flujo de UI o un bug visual — y antes de dar por terminada cualquier tarea que toque frontend.
---

# Probar en el navegador

**Ninguna tarea de UI está terminada hasta que se abrió en un navegador real y
se ejercitó el flujo.** Que compile no es verificar. Que pasen las pruebas
unitarias tampoco.

Hay dos herramientas. Elige una, no las mezclas en la misma corrida.

## Cuál usar

| Situación | Herramienta |
|---|---|
| App local (`localhost`), flujo repetible, quieres dejar la prueba escrita | **Playwright CLI** |
| Necesitas la sesión ya iniciada del usuario (Google, banco, panel privado) | **Chrome de Claude Desktop** |
| Sitio externo, staging con SSO, cualquier cosa que pida login real | **Chrome de Claude Desktop** |
| Necesitas capturar traza, video o mockear la red | **Playwright CLI** |
| Exploración rápida de una pantalla, un vistazo | Cualquiera; el de Claude es más directo |

Por defecto: **Playwright CLI**. Es reproducible y no depende del estado del
navegador del usuario. Pásate al Chrome de Claude solo cuando necesites una
sesión autenticada que Playwright tendría que volver a levantar.

## Opción A — Playwright CLI

Usa la skill `playwright-cli`, que ya trae las referencias de sesiones, mockeo
de red, trazas, video y generación de pruebas.

Antes de nada, comprueba que la app esté corriendo:

```bash
curl -sS -o /dev/null -w "%{http_code}" http://localhost:3000
```

Si no responde, levántala primero — no pruebes contra un puerto muerto.

Ciclo:

1. Navega a la ruta concreta del cambio, no a la home.
2. Ejercita el flujo como lo haría una persona: clic, escribir, enviar, esperar.
3. Comprueba el resultado en el DOM, no solo que no haya reventado.
4. Captura pantalla del estado final.
5. Revisa la consola y la red por errores.

Si el flujo se va a repetir, deja la prueba escrita en el repo en vez de
ejecutarla suelta.

## Opción B — Chrome de Claude Desktop

Dos superficies distintas:

- **`mcp__claude-in-chrome__*`** — el Chrome real del usuario, con sus sesiones
  ya iniciadas. Esta es la que quieres cuando hace falta estar logueado.
- **`mcp__Claude_Browser__*`** — el navegador embebido del panel. Sirve para
  `localhost` y sitios públicos, sin sesiones del usuario.

Si las herramientas están diferidas, cárgalas en **una sola** llamada a
`ToolSearch` con la lista completa separada por comas; una llamada por
herramienta desperdicia un viaje cada vez.

Ciclo:

1. `tabs_context` para ver qué pestañas hay antes de abrir otra.
2. `navigate` a la ruta del cambio.
3. `read_page` para leer el árbol de accesibilidad — **prefiérelo al screenshot**
   para verificar texto y estructura; es más fiable y más barato.
4. Interactúa con `computer` usando los `ref_N` de `read_page`.
5. `screenshot` solo para lo visual: layout, colores, alineación, overflow.
6. `read_console_messages` y `read_network_requests` para los errores.

Encadena los pasos que puedas predecir en un solo `browser_batch` en vez de una
llamada por acción.

### Límites que debes respetar

El Chrome del usuario es su navegador real, con sus sesiones. **Nunca** metas
contraseñas, tarjetas ni datos personales en un formulario, no aceptes términos
ni banners de consentimiento, no envíes formularios ni hagas compras sin
pedírselo antes al usuario en el chat. Para probar login, usa credenciales de
prueba en un entorno de prueba — o Playwright con una sesión guardada.

## Qué verificar siempre

- **El flujo feliz completo**, de principio a fin, no solo que la pantalla pinte.
- **Un caso de error**: campo vacío, dato inválido, respuesta 500.
- **La consola limpia.** Un error de React o un 404 de asset cuentan como fallo.
- **La red**: que las peticiones salgan con los parámetros correctos y vuelvan
  con lo esperado.
- **Responsive**, si el cambio toca layout: `resize_window` a mobile (375x812) y
  recarga, porque hay gates que solo corren al cargar.
- **Tema claro y oscuro**, si el cambio toca colores.

### Clics de verdad

Un `.click()` por JavaScript dispara el handler aunque el elemento esté tapado
por un overlay, un modal o un `z-index` mal puesto — la prueba pasa y el usuario
no puede hacer clic. Cuando importe, verifica con hit-testing que el punto
realmente pertenece al elemento:

```js
document.elementFromPoint(x, y)
```

Con Playwright, los clics nativos ya hacen esta comprobación; con
`javascript_tool` no.

## Cómo reportar

Corto y con evidencia:

- Qué ruta abriste y qué hiciste, en una línea.
- Qué esperabas y qué pasó.
- Los errores de consola o red, si los hubo, textuales.
- La captura, si el problema es visual.

Si algo falló, **dilo**. No reportes "verificado" sobre un flujo que no
completaste, y si no pudiste probar algo, di explícitamente qué quedó sin
probar y por qué.
