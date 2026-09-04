---
tipo: clase
fecha: 2026-06-16
modulo: 2
tags: [python, archivos]
---

# Revisión Python — Archivos y módulo os

## Resumen

- `open()` frente a `with open(...) as f`: el segundo cierra el archivo solo.
- `readline()`, `readlines()` y recorrer el archivo directamente con un `for`.
- Ejercicio: crear un archivo, leerlo y generar una copia con una línea separadora entre líneas.
- Módulo `os`: `getcwd`, `remove`, `rename`, `path.exists`, `path.getsize`, `path.getmtime`, `mkdir`, `rmdir`, `listdir`.

```jsx
file = open("hola_mundo.tx", "wr")
print(file.readline())
print(file.readline())
print(file.readline())
file.close()

file = open("hola_mundo.txt", "wr")

with open("hola_mundo.txt", "r") as file:
    print(file.readlines())

with open("hola_mundo.txt", "r+") as file:
    with open("hola_mundo_new.txt", "w") as file_new:
        for line in file:
            print(line)
            print("---------------")
            file_new.write("new world")
            file_new.write(line)

```

## Ejercicio

1- Crear archivo con ese texto.

2 - Leer el archivo creado

3 - Generar uno actualizado con una linea separadora"--------"

```jsx
Introduction
This follow-along reading is organized to match the content in the video that follows. It contains the same code shown in the next video. These code blocks will provide you with the opportunity to see how the code is written, allow you to practice running it, and can be used as a reference to refer back to.

You can follow along in the reading as the instructor discusses the code or review the code after watching the video.
```

```jsx
texto_archivo_1 = """
Introduction
This follow-along reading is organized to match the content in the video that follows. It contains the same code shown in the next video. These code blocks will provide you with the opportunity to see how the code is written, allow you to practice running it, and can be used as a reference to refer back to.

You can follow along in the reading as the instructor discusses the code or review the code after watching the video.
"""

with open("texto_inicial.txt", "w+") as file_1_write:
    file_1_write.write(texto_archivo_1)

with open("texto_inicial.txt", "r") as file_1_read:
    with open("texto_inicial_actualizado.txt", "w") as file_1_write:
        for line in file_1_read:
            # print(line)
            # print("----")
            file_1_write.write(line)
            file_1_write.write("\n----\n")
```

## Comandos

```jsx
import os 

os.getcwd() # Obtiene el actual directorio donde se esta trabajando
os.remove("novel.txt")
os.rename("first_draft.txt", "finished_masterpiece.txt")
 os.path.exists("finished_masterpiece.txt")

# This code will provide the file size
os.path.getsize("spider.txt") 

# This code will provide a unix timestamp for the file
os.path.getmtime("spider.txt") 

# This code will provide the date and time for the file in an 
import datetime
timestamp = os.path.getmtime("spider.txt")
datetime.datetime.fromtimestamp(timestamp)

os.mkdir("new_dir")
os.chdir("new_dir")
os.getcwd()

os.mkdir("newer_dir")
os.rmdir("newer_dir")

import os
os.listdir("website")

 dir = "website"
 for name in os.listdir(dir):
```

## Relacionado

- [[2026-06-18 - Revisión Python - Archivos CSV]]
- [[M02·S03 - Python y Sistemas Operativos]]
