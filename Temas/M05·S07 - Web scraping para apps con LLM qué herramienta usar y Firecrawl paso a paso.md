# Web scraping para apps con LLM: qué herramienta usar y Firecrawl paso a paso

Nov 24, 2026 · @Luciano

Hay muchas formas de sacar datos de la web y ninguna sirve para todo. Esta guía te da un criterio para elegir entre las principales (Firecrawl, Apify, Playwright, Scrapling y algunas más) y después recorre Firecrawl con cinco casos simples en Python.

## Las formas de hacer scraping

Todas las herramientas hacen lo mismo de fondo: piden una página y se quedan con la parte útil. Cambia quién hace el trabajo (tu código o un servicio), dónde corre (tu máquina o la nube) y qué te devuelve (HTML para parsear o texto listo para un LLM).

| Herramienta | Qué es | Dónde corre | Costo |
| --- | --- | --- | --- |
| requests + BeautifulSoup | Un pedido HTTP y un parser de HTML | Tu máquina | Gratis |
| Scrapy / Crawlee | Frameworks para recorrer miles de páginas con colas y reintentos | Tu máquina o un servidor | Gratis, open source |
| [Playwright](https://playwright.dev/python/docs/intro) | Un navegador real (Chromium, Firefox o WebKit) manejado desde código | Tu máquina | Gratis, open source |
| [Scrapling](https://github.com/D4Vinci/Scrapling) | Librería Python que junta pedidos HTTP rápidos, un navegador sigiloso y selectores que se adaptan cuando el sitio cambia | Tu máquina | Gratis, licencia BSD-3 |
| [Crawl4AI](https://pypi.org/project/Crawl4AI/) | Crawler open source que devuelve Markdown para LLM | Tu máquina, Docker o su nube | Gratis (Apache-2.0); su nube da créditos gratis |
| [Firecrawl](https://docs.firecrawl.dev) | API que recibe una URL y devuelve Markdown o JSON | Nube | 1.000 créditos gratis por mes |
| [Jina Reader](https://jina.ai/reader) | Anteponés `r.jina.ai/` a una URL y devuelve su contenido como Markdown | Nube | Gratis con límite de pedidos |
| [Apify](https://docs.apify.com/platform/actors) | Plataforma con scrapers ya hechos (Actors) para sitios concretos, que corren en su nube | Nube | 5 USD de uso gratis por mes |
| Agentes de navegador (Browser Use, Stagehand) | Un LLM que maneja el navegador paso a paso | Tu máquina o la nube | Pagás el LLM en cada paso |

Hay una categoría más que conviene conocer aunque no la uses hoy: los servicios de proxies y desbloqueo (Bright Data, ZenRows, ScrapingBee). Se suman a cualquiera de las anteriores cuando el volumen es grande y el sitio bloquea.

## Cómo elegir

Antes de elegir, fijate si el sitio ofrece una API oficial o un dataset: si existe, es más estable y más seguro que scrapear. Si no, recorré estas preguntas en orden.

&#91;embedded content: cómo elegir herramienta · 5 preguntas\]

La primera respuesta afirmativa decide la herramienta. Si ninguna aplica, alcanza con lo más simple.

## Cuándo conviene cada una

La columna de la derecha importa tanto como la del medio: casi todos los problemas vienen de usar una buena herramienta en el caso equivocado.

| Herramienta | Conviene cuando | No conviene cuando |
| --- | --- | --- |
| Firecrawl | Necesitás el contenido de páginas como contexto para un LLM, un RAG o un agente, y no querés mantener navegadores ni proxies | Necesitás campos exactos de millones de páginas (pagás por página), o los datos no pueden salir de tu infraestructura |
| Apify | El sitio es conocido y ya existe un Actor (Google Maps, Instagram, tiendas online), o querés programar corridas sin escribir el scraper | No hay Actor para tu sitio y terminás escribiendo el scraper igual. Cada Actor tiene su precio: hay que leerlo antes |
| Playwright en tu máquina | Hay login, clicks, formularios o scroll infinito; querés control total y costo cero; el volumen es chico o mediano | El volumen es grande (cada página abre un navegador), el sitio tiene anti-bot fuerte, o no querés mantener selectores |
| Scrapling | Escribís tu propio scraper en Python y querés que sobreviva a los cambios de HTML, o el sitio bloquea los pedidos comunes | No querés mantener código: la escala, los proxies y los horarios siguen siendo tu problema |
| Crawl4AI | Querés lo mismo que da Firecrawl pero open source y en tu máquina: datos sensibles o costo por página cero | No querés instalar ni operar navegadores |
| requests + BeautifulSoup | El HTML ya trae los datos, son pocas páginas y la estructura es estable. También para entender cómo funciona todo lo demás | La página se arma con JavaScript o el sitio te bloquea |
| Scrapy / Crawlee | Son miles o millones de páginas con estructura conocida | Es un script de una tarde |
| Jina Reader | Querés probar una URL suelta en segundos, sin instalar nada | Necesitás recorrer un sitio entero |
| Agentes de navegador | La tarea es abierta y no podés escribir los pasos de antemano | La tarea es repetible: un script hace lo mismo más rápido, más barato y sin errores sutiles |

En un proyecto real se combinan. Un caso típico: Firecrawl o Crawl4AI para el contenido que va al LLM, Apify para las fuentes que ya tienen Actor y Playwright para lo que exige login.

## La misma tarea con cuatro herramientas

La tarea: traer los libros de [books.toscrape.com](https://books.toscrape.com), un catálogo ficticio hecho para practicar scraping. Mirá cuánto código y cuánta instalación pide cada opción; la quinta, Firecrawl, ocupa el resto de la guía.

**requests + BeautifulSoup.** Alcanza porque el HTML de este sitio ya trae los libros.

```python
import requests
from bs4 import BeautifulSoup

html = requests.get("https://books.toscrape.com").text
soup = BeautifulSoup(html, "html.parser")
for a in soup.select("article.product_pod h3 a"):
    print(a["title"])
```

**Playwright.** Abre un Chromium de verdad. Tarda más, pero ve también lo que se carga con JavaScript y te deja hacer clicks o loguearte.

```bash
pip install playwright
playwright install chromium
```

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto("https://books.toscrape.com")
    for a in page.locator("article.product_pod h3 a").all():
        print(a.get_attribute("title"))
    browser.close()
```

**Scrapling.** El mismo selector, con la sintaxis de Scrapy. Si el sitio bloquea los pedidos comunes, cambiás una línea y pasa a usar un navegador sigiloso.

```bash
pip install "scrapling[fetchers]"
scrapling install
```

```python
from scrapling.fetchers import Fetcher, StealthyFetcher

page = Fetcher.get("https://books.toscrape.com")
print(page.css("article.product_pod h3 a::attr(title)").getall())

# Mismo código, pero con navegador sigiloso:
# page = StealthyFetcher.fetch("https://books.toscrape.com", headless=True)
```

**Apify.** No escribís el scraper: elegís un Actor, le pasás un JSON de entrada y corre en la nube. Este ejemplo usa [Website Content Crawler](https://apify.com/apify/website-content-crawler), que devuelve el contenido de cada página en Markdown.

```python
import os
from apify_client import ApifyClient

client = ApifyClient(os.environ["APIFY_TOKEN"])
run = client.actor("apify/website-content-crawler").call(
    run_input={
        "startUrls": [{"url": "https://books.toscrape.com"}],
        "maxCrawlPages": 3,
    }
)
for item in client.dataset(run.default_dataset_id).iterate_items():
    print(item["url"], len(item["markdown"]))
```

En los tres primeros el selector `article.product_pod h3 a` lo escribiste vos, y se rompe si el sitio cambia su HTML. En Apify y en Firecrawl no hay selectores: ese mantenimiento lo paga otro, y vos pagás el servicio.

## Firecrawl a fondo: qué es y qué problema resuelve

Firecrawl es una API: le pasás una URL y te devuelve el contenido de la página limpio, en Markdown o en JSON, listo para ponerlo en un prompt. El SDK de Python solo hace la llamada; el navegador, el renderizado y la limpieza corren en los servidores de Firecrawl.

Resuelve tres problemas que aparecen apenas querés darle la web a un LLM:

- **El HTML crudo es ruido.** Menús, scripts, banners y estilos ocupan la mayor parte de la página y gastan tokens sin aportar nada.
- **Muchas páginas se arman con JavaScript.** Un `requests.get()` trae un esqueleto vacío; hace falta un navegador real que ejecute la página.
- **Cada sitio es distinto.** Con BeautifulSoup escribís selectores a mano por sitio y se rompen cuando cambia el diseño.

La idea para llevarte: Firecrawl no es "un scraper más", es la capa que convierte la web en contexto para un modelo.

## Las cuatro operaciones de un vistazo

La pregunta que ordena todo es qué tenés en la mano: una URL, un sitio o solo una pregunta.

| Operación | Qué tenés | Qué devuelve | Costo en créditos |
| --- | --- | --- | --- |
| `scrape` | Una URL | El contenido de esa página (Markdown, HTML, JSON) | 1 por página; 5 si pedís JSON |
| `map` | Un sitio | La lista de URLs del sitio, sin contenido | 1 por llamada |
| `crawl` | Un sitio | El contenido de muchas páginas, siguiendo links | 1 por página recorrida |
| `search` | Una pregunta | Resultados de búsqueda web, con contenido si lo pedís | 2 cada 10 resultados, más 1 por página que traiga |

El plan gratuito da 1.000 créditos por mes sin tarjeta. Recorrer los cinco casos de esta guía gasta unos 20 créditos en total. Costos según la [documentación de scrape](https://docs.firecrawl.dev/features/scrape), [map](https://docs.firecrawl.dev/features/map), [crawl](https://docs.firecrawl.dev/features/crawl), [search](https://docs.firecrawl.dev/features/search) y la [página de precios](https://www.firecrawl.dev/pricing).

Firecrawl tiene más cosas (Interact para hacer clicks y llenar formularios, Agent, batch scrape). Quedan fuera de esta guía a propósito.

## Setup

Son tres pasos y ninguno pide tarjeta.

1. Crear una cuenta en [firecrawl.dev](https://www.firecrawl.dev) y copiar la API key (empieza con `fc-`).
2. Instalar el SDK: `pip install firecrawl-py`.
3. Guardar la key en una variable de entorno, nunca en el notebook.

```bash
export FIRECRAWL_API_KEY=fc-TU-API-KEY
```

```python
from firecrawl import Firecrawl

fc = Firecrawl()  # lee FIRECRAWL_API_KEY del entorno
```

Si `FIRECRAWL_API_KEY` está definida, el cliente no necesita argumentos ([quickstart de Python](https://docs.firecrawl.dev/quickstarts/python)). Todos los casos de abajo reutilizan este `fc`.

Los cinco casos siguen sobre books.toscrape.com, el mismo sitio de la comparación de arriba.

## Caso 1 — Scrape: una página a Markdown

`scrape` toma una URL y devuelve esa página como Markdown. Es la operación base: las otras tres la usan por dentro.

```python
doc = fc.scrape("https://books.toscrape.com", formats=["markdown"])

print(doc.markdown[:500])          # el contenido, limpio
print(doc.metadata.title)          # título de la página
print(doc.metadata.source_url)     # de dónde salió
print(doc.metadata.status_code)    # 200 si cargó bien
```

**Claves**

- `formats` define qué querés de vuelta. Con `["markdown", "html"]` trae los dos, y cada uno queda en su atributo (`doc.markdown`, `doc.html`).
- El resultado es un objeto, no un diccionario: el SDK pasa los campos de la API a snake\_case (`sourceURL` se vuelve `source_url`).
- `only_main_content` descarta menús y pies de página. Pasalo en `False` si necesitás la página entera.

**Probalo:** imprimí `len(doc.html)` contra `len(doc.markdown)` de la misma página. La diferencia de tamaño es lo que te ahorrás en tokens.

## Caso 2 — Scrape con JSON: datos estructurados

Con el formato `json`, Firecrawl usa un LLM para sacar de la página exactamente los campos que le describís en un esquema. No hay selectores CSS: el esquema es la consulta.

```python
from pydantic import BaseModel, Field

class Libro(BaseModel):
    titulo: str
    precio: float = Field(description="Precio en libras, solo el número")
    en_stock: bool

class Catalogo(BaseModel):
    libros: list[Libro]

doc = fc.scrape(
    "https://books.toscrape.com",
    formats=[{"type": "json", "schema": Catalogo.model_json_schema()}],
)

catalogo = Catalogo.model_validate(doc.json)   # valida lo que devolvió el LLM
for libro in catalogo.libros[:5]:
    print(libro.titulo, libro.precio, libro.en_stock)
```

**Claves**

- El formato es un diccionario con `type`, `schema` y, si querés, un `prompt` que guíe la extracción. También funciona solo con `prompt`, y ahí el modelo elige la estructura ([modo JSON](https://docs.firecrawl.dev/features/scrape)).
- Las `description` de los campos son instrucciones para el modelo. Un campo bien descrito se extrae mejor.
- `doc.json` llega como diccionario. Validarlo con Pydantic es obligatorio: la extracción la hace un LLM y puede equivocarse.
- Cuesta 5 créditos por página en vez de 1. Se usa cuando hace falta estructura, no por defecto.

**Probalo:** agregá un campo `estrellas: int` al esquema y volvé a correr. No tocaste ningún selector.

## Caso 3 — Map: descubrir las URLs de un sitio

`map` devuelve la lista de URLs de un sitio sin bajar el contenido de ninguna. Sirve para mirar qué hay antes de gastar créditos en recorrerlo.

```python
res = fc.map("https://books.toscrape.com", limit=50)

print(len(res.links))
for link in res.links[:10]:
    print(link.url)

# Filtrar por tema: las URLs más relevantes para "travel"
res = fc.map("https://books.toscrape.com", search="travel", limit=10)
```

**Claves**

- Cuesta 1 crédito por llamada, devuelva 10 URLs o 5.000.
- Cada link trae `url` y a veces `title` y `description`; hay que chequear que existan antes de usarlos.
- Con `search` el resultado viene ordenado por relevancia. Es la forma barata de encontrar "la página de precios" o "la sección de docs" de un sitio.

**Probalo:** el patrón map → elegir → scrape. Tomá una URL de la lista y pasala al `scrape` del caso 1.

## Caso 4 — Crawl: recorrer un sitio chico

`crawl` arranca en una URL, sigue los links y hace scrape de cada página que encuentra. Es un scrape repetido con descubrimiento automático.

```python
from firecrawl.types import ScrapeOptions

job = fc.crawl(
    "https://books.toscrape.com",
    limit=5,                                         # SIEMPRE poner límite
    scrape_options=ScrapeOptions(formats=["markdown"]),
)

print(job.status, job.completed, "de", job.total)
print("créditos:", job.credits_used)

for doc in job.data:
    print(doc.metadata.source_url, len(doc.markdown))
```

**Claves**

- `limit` es el máximo de páginas, y cada página cuesta 1 crédito. Sin `limit` el valor por defecto es 10.000, y la API responde 402 si los créditos no lo cubren ([crawl](https://docs.firecrawl.dev/features/crawl)).
- `crawl` es bloqueante: espera a que termine y devuelve todo. Para trabajos largos existe `start_crawl`, que devuelve un id para consultar después con `get_crawl_status`.
- `include_paths` y `exclude_paths` aceptan expresiones regulares sobre la ruta, por ejemplo `include_paths=["catalogue/category/.*"]`.
- El crawl respeta el `robots.txt` del sitio.

**Fijate:** `job.data` es una lista de los mismos documentos que devuelve `scrape`. Lo que aprendiste en el caso 1 se aplica igual.

## Caso 5 — Search: buscar en la web y traer el contenido

`search` es para cuando no tenés una URL, solo una pregunta. Busca en la web y, si se lo pedís, devuelve el contenido de cada resultado ya convertido a Markdown.

```python
# Solo resultados: título, URL y descripción
res = fc.search("qué es retrieval augmented generation", limit=3)
for r in res.web:
    print(r.title, "->", r.url)

# Resultados con el contenido de cada página
from firecrawl.types import ScrapeOptions

res = fc.search(
    "qué es retrieval augmented generation",
    limit=3,
    scrape_options=ScrapeOptions(formats=["markdown"]),
)
for doc in res.web:
    print(doc.metadata.source_url)
    print(doc.markdown[:300])
```

**Claves**

- Sin `scrape_options` cada resultado es liviano (`url`, `title`, `description`). Con `scrape_options` cada resultado pasa a ser un documento como el del caso 1, con `markdown` y `metadata`.
- Los resultados vienen agrupados por tipo: `res.web`, `res.news`, `res.images`. Se elige con `sources=["web", "news"]`.
- Es búsqueda más scrape en una sola llamada, que es justo lo que necesita un agente con una tool de "buscar en internet".

**Probalo:** compará el costo de las dos variantes: 2 créditos la primera, 5 la segunda (2 de búsqueda más 3 páginas).

## Ejercicios

Cuatro consignas, de menor a mayor. La primera se resuelve con el diagrama y sin escribir código.

1. **Elegir la herramienta.** Para cada escenario, decidí qué usarías y por qué: (a) las reseñas de 200 locales de Google Maps; (b) la documentación de una librería para armar un RAG; (c) tus facturas, que están detrás del login de un proveedor; (d) los precios de una tienda chica que cambia de diseño cada mes.
2. **Medir el ahorro.** Hacé scrape de una página a elección con `formats=["markdown", "html"]` y compará el largo de los dos. ¿Cuánto más chico es el Markdown?
3. **Cambiar el esquema.** Sobre una página de categoría de books.toscrape.com, definí un esquema propio (por ejemplo, título, precio y cantidad de estrellas) y validá la respuesta con Pydantic.
4. **Preguntarle a una página.** Hacé scrape de una página de documentación, pasale el Markdown a tu LLM junto con una pregunta, y pedile que responda solo con lo que dice la página.

## Errores comunes y buenas prácticas

Casi todos los tropiezos de la primera semana con Firecrawl son de créditos o de confianza en el resultado.

- **Crawl sin `limit`.** Es el error más caro. Siempre poner límite, y hacer `map` antes para saber cuántas páginas hay.
- **JSON por defecto.** Pedir JSON multiplica el costo por cinco. Si el Markdown alcanza para el prompt, usar Markdown.
- **Resultados viejos.** Por defecto Firecrawl puede devolver una copia en caché de hasta dos días. Con `max_age=0` fuerza una lectura nueva.
- **La key en el código.** Va en una variable de entorno o en un `.env` fuera del repositorio.
- **Confiar en lo extraído.** La salida JSON la genera un LLM: validar siempre con Pydantic y revisar una muestra a mano.
- **Confiar en la página.** El contenido de una web es texto escrito por terceros. Si va a un prompt, puede traer instrucciones escondidas (inyección indirecta, el tema de M08·S03): tratarlo como dato, nunca como instrucción.
- **Scrapear sin mirar.** Revisar los términos de uso del sitio antes de recorrerlo a escala.

Y una regla que vale para todas las herramientas de esta guía: poder no es estar autorizado. Que Scrapling o un proxy logren pasar un bloqueo no cambia los términos de uso del sitio ni el GDPR cuando hay datos personales.

## Videos que vimos en clase

Los dos videos se complementan con esta guía: uno muestra Firecrawl funcionando y el otro explica por qué importa.

- [Claude Code + Firecrawl = UNLIMITED Web Scraping](https://www.youtube.com/watch?v=phuyYL0L7AA) (Chase AI). La parte práctica: por qué el `web fetch` nativo de un LLM falla con JavaScript y anti-bot, y cómo se compara con Firecrawl sobre SimilarWeb, Yellow Pages y Amazon. Muestra también Agent y Browser Interact, las dos funciones que esta guía dejó afuera.
- [Firecrawl AI clearly explained (and how to make $$)](https://www.youtube.com/watch?v=eH8JdttKIdA) (Greg Isenberg). El marco conceptual: los agentes necesitan datos web limpios, el scraping tradicional contra el modelo de una sola llamada a API, y qué productos de nicho se pueden construir vendiendo datos ya procesados.

Para repasar, volvé a la tabla de "Cuándo conviene cada una" después de verlos: los videos muestran el mejor caso de Firecrawl, y la tabla te dice cuándo otra herramienta es mejor opción.

## Fuentes

Los ejemplos están revisados contra estas versiones: `firecrawl-py` 4.57.0, `scrapling` 0.5.1, `playwright` 1.63.0 y `apify-client` 3.5.1. Se comprobaron los nombres de métodos y parámetros, pero no se ejecutaron contra los sitios: si algo falla, lo primero es comparar tu versión. Precios y planes consultados el 24 de noviembre de 2026.

- Firecrawl: [quickstart de Python](https://docs.firecrawl.dev/quickstarts/python), [referencia del SDK](https://docs.firecrawl.dev/sdks/python), [scrape](https://docs.firecrawl.dev/features/scrape), [map](https://docs.firecrawl.dev/features/map), [crawl](https://docs.firecrawl.dev/features/crawl), [search](https://docs.firecrawl.dev/features/search) y [precios](https://www.firecrawl.dev/pricing)
- Scrapling: [repositorio en GitHub](https://github.com/D4Vinci/Scrapling)
- Apify: [qué es un Actor](https://docs.apify.com/platform/actors), [precios](https://apify.com/pricing) y [Website Content Crawler](https://apify.com/apify/website-content-crawler)
- Playwright: [documentación para Python](https://playwright.dev/python/docs/intro)
- Crawl4AI: [página del proyecto en PyPI](https://pypi.org/project/Crawl4AI/)
- Jina Reader: [página del producto](https://jina.ai/reader)
