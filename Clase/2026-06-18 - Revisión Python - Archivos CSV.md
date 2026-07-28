---
tipo: clase
fecha: 2026-06-18
modulo: 2
tags: [python, archivos, csv]
---

# Revisión Python — Archivos CSV

## Resumen

- Leer un CSV con `csv.reader()` en lugar de partir las líneas a mano.
- Desempaquetar cada fila en variables: `name, phone, role = row`.
- Formatear la salida con `.format()`.

Leer de una archivo csv

archivo_csv.csv

```jsx
nombre,phone,role
Juan Pérez,+34 611 223 344,Administrador
María Rodríguez,+34 622 334 455,Desarrollador
Carlos Gómez,+34 633 445 566,Diseñador
Ana Martínez,+34 644 556 677,Soporte Técnico

```

Solucion

```jsx
import csv
 f = open("csv_file.txt")
 csv_f = csv.reader(f)
 for row in csv_f:
     name, phone, role = row
     print("Name: {}, Phone: {}, Role: {}".format(name, phone, role))
f.close()
```

## Relacionado

- [[2026-06-16 - Revisión Python - Archivos y módulo os]]
