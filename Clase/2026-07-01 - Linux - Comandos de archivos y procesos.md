---
tipo: clase
fecha: 2026-07-01
modulo: 2
tags: [linux, bash]
---

# Linux — Comandos de archivos y procesos

## Resumen

- Ciclo completo sobre un directorio: `mkdir`, `cd`, `touch`, `ls -la`, `mv`, `cp`, `rm`, `rmdir`.
- Leer la salida de `ls -l`: permisos, propietario, tamaño y fecha.
- Procesos: `ping` para comprobar conectividad, `ps aux` para listar, `| grep` para filtrar y `kill` para terminar.

```bash
# crear directorio
mkdir mynewdir

#Ingresar al directorio
cd mynewdir

#Listar archivos del directorio
/mynewdir$ ls -la
#Output:
#total 12
#drwxr-xr-x  2 user user  4096 Mai 22 14:17 .
#drwxr-xr-x 56 user user 12288 Mai 22 14:17 ..
#-rw-rw-r--  1 user user     0 Mai 22 14:22 myfile.txt
#-rw-rw-r--  1 user user   192 Mai 22 14:18 spider.txt

#Crear archivos
touch myfile.txt
touch spider.txt

/mynewdir$ mv myfile.txt emptyfile.txt
/mynewdir$ cp spider.txt yetanotherfile.txt
/mynewdir$ ls -l
#Output:
#total 8
#-rw-rw-r-- 1 user user   0 Mai 22 14:22 emptyfile.txt
#-rw-rw-r-- 1 user user 192 Mai 22 14:18 spider.txt
#-rw-rw-r-- 1 user user 192 Mai 22 14:23 yetanotherfile.txt
/mynewdir$ rm *
/mynewdir$ ls -l
#total 0
/mynewdir$ cd ..
rmdir mynewdir/
ls mynewdir
#ls: cannot access 'mynewdir': No such file or directory

```

## Ping

```bash
# verifica conexion a un server
ping www.google.com

# Lista los procesos
ps aux

# Lista los procesos los redirecciona a grep para encontrar un patron
ps aux | grep ping

# Matar un proceso
kill <id de proceso>
```

## Relacionado

- [[2026-07-02 - Bash - Scripting inicial]]
- [[Python y Sistemas Operativos]]
