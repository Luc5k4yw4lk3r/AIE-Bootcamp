---
tipo: recurso
tags: [python, linux, archivos, regex, testing, bash]
---

# Resumen: Using Python to Interact with the Operating System

[https://www.youtube.com/watch?v=UYU_ki7likk&list=PLTZYG7bZ1u6oJu7Imgx8FTOjyDNwesrm5&index=1&t=1s](https://www.youtube.com/watch?v=UYU_ki7likk&list=PLTZYG7bZ1u6oJu7Imgx8FTOjyDNwesrm5&index=1&t=1s)

## 🎯 De qué trata este curso

Este curso de Google (disponible en YouTube) enseña a usar **Python para automatizar tareas de informática**, como gestionar archivos, procesar texto, trabajar con el sistema operativo Linux y escribir scripts que hagan trabajo repetitivo por ti. Está pensado para personas que quieren trabajar en IT (soporte técnico, administración de sistemas) y quieren aprender a programar con un propósito práctico.

---

## 📹 Vídeo 1 — Instalación de Python en Windows, Mac y Linux

## ¿Qué es el sistema operativo?

Antes de instalar nada, el curso explica qué es el **sistema operativo (SO)**. Es el programa que gestiona todo en el ordenador: archivos, memoria, procesos y hardware. Tiene dos partes:

- **Kernel**: el núcleo, habla directamente con el hardware. No lo tocamos directamente.
- **Espacio de usuario**: todo lo que usamos nosotros (programas, interfaz, terminal).

Los principales sistemas operativos son **Windows**, **macOS** y **Linux**. Linux es muy importante en servidores y en entornos profesionales de IT.

## ¿Por qué Python es multiplataforma?

Python funciona igual en Windows, Mac y Linux. Puedes escribir un script en tu ordenador y ejecutarlo en un servidor Linux sin cambiar nada. Eso lo hace ideal para IT.

## Cómo saber si tienes Python instalado

Abre la terminal o el símbolo del sistema y escribe:

```bash
python --version
```

> 💡 Si te dice `Python 2.x`, tienes una versión antigua. Este curso usa **Python 3**. Prueba con `python3 --version`.
> 

## Instalación en cada sistema

- **Windows**: descarga el instalador desde [python.org](http://python.org). **Importante**: marca la casilla *"Add Python to PATH"* antes de instalar.
- **macOS**: descarga desde [python.org](http://python.org) o usa Homebrew. En Mac el comando es `pip3` en lugar de `pip`.
- **Linux (Ubuntu)**: probablemente ya lo tienes. Si no, usa `sudo apt install python3`.

## ¿Qué es pip?

`pip` es la herramienta para instalar módulos externos (librerías que no vienen incluidas con Python). Por ejemplo:

```bash
pip install requests
```

Los módulos se buscan en **PyPI** (el índice de paquetes de Python), que tiene miles de librerías gratuitas.

---

## 📹 Vídeo 2 — Cómo ejecutar un script Python

## Lenguajes compilados vs. interpretados

Existen dos grandes tipos de lenguajes de programación:

| Tipo | Cómo funciona | Ejemplos | Velocidad |
| --- | --- | --- | --- |
| **Compilado** | Se traduce todo el código antes de ejecutar | C, C++, Go, Rust | Muy rápido |
| **Interpretado** | Se ejecuta línea a línea en el momento | Python, JavaScript, Bash | Más lento, pero más flexible |

Python es **interpretado**, lo que significa que no necesitas compilar: escribes el código y lo ejecutas directamente.

## Formas de ejecutar Python

**Forma 1 — Modo interactivo** (para probar cosas rápido)

```bash
python3
```

Se abre una consola donde escribes código y ves el resultado inmediatamente. El problema es que no guarda nada.

**Forma 2 — Ejecutar un archivo .py** (la forma normal)

```bash
python3 mi_script.py
```

**Forma 3 — Ejecutar directamente (solo Linux/Mac)**

Puedes añadir una línea especial al inicio del archivo llamada **shebang**:

```python
#!/usr/bin/env python3
print("Hola mundo")
```

Luego le das permiso de ejecución al archivo:

```bash
chmod +x mi_script.py
./mi_script.py
```

## Módulos propios (reutilizar código)

Cuando tu código crece, puedes organizarlo en **módulos**: archivos `.py` separados que importas desde otros scripts.

```python
# archivo: areas.py
def circulo(radio):
    return 3.14 * radio ** 2
```

```python
# en otro archivo:
import areas
print(areas.circulo(5))
```

Así evitas copiar y pegar el mismo código en varios sitios.

## Editores de código

Puedes escribir Python en cualquier editor, pero los mejores para aprender son:

- **VS Code** (recomendado para el bootcamp)
- **PyCharm** (más completo, ideal para proyectos grandes)
- **Nano o Vim** (en la terminal, útil cuando trabajas en servidores remotos)

## Automatización: ¿cuándo merece la pena?

Una regla sencilla: si el tiempo que tardarás en escribir el script es **menor** que el tiempo que ahorrarás no haciendo la tarea manualmente, **automatiza**.

> 💡 Ejemplo del curso: si generar un informe te lleva 5 minutos al día y crear el script te lleva 1 hora, en 12 días ya habrás recuperado el tiempo invertido.
> 

---

## 📹 Vídeo 3 — Manejo de archivos en Python

## Leer un archivo

```python
with open("archivo.txt") as f:
    contenido = f.read()
    print(contenido)
```

El bloque `with` es importante porque **cierra el archivo automáticamente** cuando terminas. Si no lo cierras, pueden pasar cosas malas (el archivo queda bloqueado, el sistema se queda sin recursos).

## Métodos para leer

| Método | ¿Qué hace? |
| --- | --- |
| `read()` | Lee todo el archivo de una vez |
| `readline()` | Lee una sola línea |
| `readlines()` | Lee todas las líneas y las devuelve como lista |

> ⚠️ Para archivos muy grandes (cientos de MB), no uses `read()` de golpe — usa un bucle línea a línea para no colapsar la memoria.
> 

## Escribir en un archivo

```python
with open("nuevo.txt", "w") as f:
    f.write("Hola, esto es nuevo")
```

Modos de apertura más comunes:

| Modo | Significado |
| --- | --- |
| `"r"` | Solo lectura (por defecto) |
| `"w"` | Escritura (¡borra el contenido anterior!) |
| `"a"` | Añadir al final sin borrar lo anterior |
| `"r+"` | Lectura y escritura |

## Gestionar archivos con el módulo `os`

El módulo `os` te permite hacer con Python las mismas cosas que harías en la terminal:

```python
import os

os.remove("archivo.txt")        # Borrar un archivo
os.rename("viejo.txt", "nuevo.txt")  # Renombrar
os.mkdir("nueva_carpeta")       # Crear una carpeta
os.getcwd()                     # Ver en qué carpeta estás
os.listdir(".")                 # Listar archivos de una carpeta
```

Antes de borrar algo, es buena práctica comprobar si existe:

```python
if os.path.exists("archivo.txt"):
    os.remove("archivo.txt")
```

---

## 📹 Vídeo 4 — Expresiones regulares en Python

## ¿Qué son las expresiones regulares (regex)?

Una **expresión regular** es un patrón de búsqueda de texto. Imagina que tienes miles de líneas de un log y quieres encontrar solo las que contienen un número de error. Con regex puedes hacerlo en una línea de código.

> 💡 Metáfora: es como el buscador del Word (Ctrl+H), pero con superpoderes.
> 

En Python se usan con el módulo `re`:

```python
import re
resultado = re.search(r"\d+", "Error código 404")
print(resultado.group())  # Imprime: 404
```

## Caracteres especiales más importantes

| Símbolo | Qué significa |
| --- | --- |
| `.` | Cualquier carácter |
| `\d` | Un dígito (0-9) |
| `\w` | Una letra, número o guión bajo |
| `\s` | Un espacio en blanco |
| `*` | El elemento anterior, 0 o más veces |
| `+` | El elemento anterior, 1 o más veces |
| `^` | Inicio de la línea |
| `$` | Fin de la línea |

## Usos prácticos en IT

- Extraer IPs de un log de servidor
- Encontrar todos los correos en un fichero
- Verificar que un número de teléfono tiene el formato correcto
- Filtrar líneas de error en archivos de registro

> ⚠️ Las regex son potentes pero complejas. Si algo no funciona, no te agobies: practica con ejemplos pequeños y ve aumentando la complejidad poco a poco.
> 

---

## 📹 Vídeo 5 — Gestión de datos y procesos

## Pedir datos al usuario con `input()`

```python
nombre = input("¿Cómo te llamas? ")
print(f"Hola, {nombre}")
```

> ⚠️ `input()` siempre devuelve texto (string). Si necesitas un número, conviértelo:
> 

> `python
> 

> edad = int(input("¿Cuántos años tienes? "))
> 

> `
> 

## Flujos de entrada/salida (I/O streams)

Cuando un programa se ejecuta, tiene tres "canales" de comunicación:

| Canal | Nombre | ¿Para qué? |
| --- | --- | --- |
| Entrada | `stdin` | Recibir datos (teclado) |
| Salida normal | `stdout` | Mostrar resultados (pantalla) |
| Salida de error | `stderr` | Mostrar errores |

Estos canales se pueden **redirigir**. Por ejemplo, en la terminal:

```bash
python3 script.py > resultado.txt   # Guarda la salida en un archivo
python3 script.py 2> errores.txt    # Guarda los errores en un archivo
```

## Ejecutar comandos del sistema desde Python

Con el módulo `subprocess` puedes ejecutar cualquier comando de la terminal desde Python:

```python
import subprocess
resultado = subprocess.run(["ls", "-l"], capture_output=True, text=True)
print(resultado.stdout)
```

## Variables de entorno

Son variables que el sistema operativo pone a disposición de todos los programas. Python puede leerlas:

```python
import os
print(os.environ.get("HOME"))   # En Linux/Mac, muestra tu carpeta personal
```

---

## 📹 Vídeo 6 — Testing en Python para principiantes

## ¿Por qué hacer tests?

Cuando escribes código, necesitas comprobar que funciona. Puedes hacerlo **manualmente** (ejecutando el script y mirando si el resultado es el esperado) o de forma **automática** (escribiendo otro código que lo comprueba por ti).

Los tests automáticos son mejores porque:

- Se ejecutan solos cada vez que cambias el código
- Detectan errores que habrías pasado por alto
- Te dan confianza para hacer cambios

## Tipos de tests

| Tipo | ¿Qué prueba? |
| --- | --- |
| **Unit test** (test unitario) | Una función o pequeña pieza de código aislada |
| **Integration test** | Que varias partes del código funcionan juntas |

## Ejemplo con `unittest`

```python
import unittest

def suma(a, b):
    return a + b

class TestSuma(unittest.TestCase):
    def test_suma_positivos(self):
        self.assertEqual(suma(2, 3), 5)

unittest.main()
```

Si la función `suma` devuelve algo distinto de 5, el test falla y te avisa.

## Manejo de errores con `try` / `except`

En lugar de dejar que tu programa se rompa, puedes **capturar** los errores y gestionarlos:

```python
try:
    resultado = 10 / 0
except ZeroDivisionError:
    print("No se puede dividir entre cero")
```

> 💡 Piénsalo así: el `try` es el "intento" y el `except` es el "plan B" si algo sale mal.
> 

---

## 📹 Vídeo 7 — El sistema operativo Linux y comandos Bash

## Comandos Linux más importantes

| Comando | ¿Qué hace? |
| --- | --- |
| `pwd` | Muestra en qué carpeta estás |
| `ls -l` | Lista los archivos con detalles |
| `cd carpeta` | Entra en una carpeta |
| `mkdir nombre` | Crea una carpeta |
| `cp origen destino` | Copia un archivo |
| `mv origen destino` | Mueve o renombra un archivo |
| `rm archivo` | Borra un archivo |
| `cat archivo` | Muestra el contenido de un archivo |
| `echo "texto"` | Imprime texto en pantalla |
| `chmod +x archivo` | Da permiso de ejecución a un archivo |

> 💡 Los puntos especiales: `.` significa "la carpeta actual" y `..` significa "la carpeta anterior".
> 

## Redirigir salidas

```bash
ls -l > lista.txt          # Guarda la lista de archivos en un txt
cat errores.txt | grep "ERROR"  # Filtra las líneas que contienen "ERROR"
```

El símbolo `|` (pipe) pasa la salida de un comando como entrada al siguiente.

## ¿Qué es Bash?

**Bash** es el lenguaje que usa la terminal de Linux. Puedes escribir scripts en Bash igual que en Python, pero está más pensado para combinar comandos del sistema.

> 💡 Cuándo usar Bash vs. Python:
> 

> - Usa **Bash** para tareas simples con comandos del sistema (copiar archivos, comprimir, etc.)
> 

> - Usa **Python** para lógica más compleja (procesar datos, hacer peticiones a APIs, etc.)
> 

---

## 📹 Vídeo 8 — Trabajar con Bash y Python juntos

## Tu primer script Bash

Un script Bash es un archivo de texto con comandos, uno por línea. Se guarda con extensión `.sh`:

```bash
#!/bin/bash
echo "=== INFO DEL SISTEMA ==="
echo "Fecha: $(date)"
uptime
free
who
```

Para ejecutarlo:

```bash
chmod +x info_sistema.sh
./info_sistema.sh
```

## Variables en Bash

```bash
nombre="Ana"
echo "Hola, $nombre"   # Para usar la variable, pon $ delante
```

> ⚠️ **Sin espacios** alrededor del `=`. `nombre = "Ana"` da error; `nombre="Ana"` funciona.
> 

## Condicionales en Bash

```bash
if [ $edad -gt 18 ]; then
    echo "Mayor de edad"
else
    echo "Menor de edad"
fi
```

## Combinar Bash y Python

Desde Python puedes llamar a scripts Bash (y viceversa) usando `subprocess`:

```python
import subprocess
subprocess.run(["bash", "info_sistema.sh"])
```

Esto te permite aprovechar lo mejor de cada lenguaje en el mismo flujo de trabajo.

---

## 🗺️ Mapa del curso (resumen visual)

```
1. Instalar Python        →  Tener el entorno listo
2. Ejecutar scripts       →  Saber cómo lanzar y organizar el código
3. Ficheros               →  Leer, escribir y gestionar archivos
4. Regex                  →  Buscar patrones en texto
5. Datos y procesos       →  Hablar con el SO y pedir input al usuario
6. Testing                →  Verificar que el código funciona
7. Linux y Bash           →  Comandos del sistema y primeros scripts Bash
8. Bash + Python          →  Combinar ambos lenguajes
```

---

## 💡 Conceptos clave para recordar

- **Script**: un archivo `.py` con instrucciones que se ejecuta desde la terminal.
- **Módulo**: un archivo `.py` que importas en otro script para reutilizar código.
- **pip**: la herramienta para instalar librerías externas de Python.
- **shebang** (`#!/usr/bin/env python3`): línea al inicio de un script que le dice al SO con qué programa ejecutarlo.
- **`with open(...)`**: la forma más segura de abrir archivos (se cierran solos).
- **regex**: patrones para buscar texto de forma flexible.
- **`try/except`**: capturar errores para que el programa no se rompa.
- **`subprocess`**: módulo para ejecutar comandos del sistema desde Python.
- **Bash**: el lenguaje de la terminal Linux, perfecto para scripts cortos con comandos del sistema.

---

> 📌 *Curso original*: Google IT Automation with Python Certificate — disponible en YouTube.
>

## Relacionado

- [[Python y Sistemas Operativos]]
- [[Clase]]
