---
tipo: clase
fecha: 2026-06-22
modulo: 2
tags: [python, regex, linux]
---

# Python y Linux — Expresiones regulares

## Resumen

- Aplicar regex a un archivo de logs real con formatos mezclados (syslog, Apache, ISO 8601).
- 12 ejercicios con `re.findall()`: PIDs, niveles de severidad, IPs, timeouts, usuarios de CRON, emails, fechas y códigos HTTP.
- Grupos de captura, alternancia `(A|B)`, escapado de `[`, `.` y `(`, y el flag `re.MULTILINE`.
- `re.sub()` con referencias `\1 \2 \3` para reordenar una fecha.

## Aplicar regex a los logs

Log.txt

```python
Oct 25 10:15:30 server1 sshd[1432]: Failed password for invalid user root from 192.168.1.15 port 49152 ssh2
Oct 25 10:17:01 server1 CRON[2050]: (admin) CMD (/scripts/backup.sh)
2023-10-25 10:20:05,123 ERROR [db-service] - Connection timeout after 5000ms
[25/Oct/2023:10:25:36 -0300] "GET /api/v1/users?id=88 HTTP/1.1" 404 234 "-" "Mozilla/5.0"
Oct 25 10:30:00 server1 systemd[1]: Started Nginx Web Server.
2023-10-25 10:32:10,450 WARN [auth] - User john.doe@empresa.com failed login 3 times.
Oct 25 10:35:01 server1 CRON[2101]: (root) CMD (/scripts/cleanup.py)
[25/Oct/2023:10:40:12 -0300] "POST /api/v1/login HTTP/1.1" 500 1024 "-" "PostmanRuntime/7.28.4"
2023-10-25 10:45:00,000 CRITICAL [main] - Disk space critically low on /dev/sda1
```

```python
import re

# Leer el archivo

# 1. PIDs (Escapando corchetes y usando grupo de captura)
pids = re.findall(r"\[(d+)\]", log_text)

# 2. Niveles de severidad (Alternancia)
severities = re.findall(r"[ERROR|WARN|CRITICAL]", log_text)

# 3. Direcciones IP (Escapando puntos)
ips = re.findall(r"[0-9]{3}.[0-9]{3}.[0-9]{1,3}.[0-9]{1,3}", log_text)

# 4. Tiempos de espera (ms)
timeouts = re.findall(r"timeout after ([0-9]+ms)", log_text)

# 5. Usuarios de CRON (Escapando paréntesis)
cron_users = re.findall(r"t)

# 6. Scripts de CRON
cron_scripts = re.findall(r")", log_text)

# 7. Usuarios inválidos en SSH
invalid_ssh_users = re.findall(r"", log_text)

# 8. Correos electrónicos
emails = re.findall(r"", log_text)

# 9. Fechas ISO 8601 al inicio de la línea (con flag re.MULTILINE)
iso_dates = re.findall(r"", log_text, re.MULTILINE)

# 10. Método HTTP y ruta
http_requests = re.findall(r'', log_text)

# 11. Códigos de estado HTTP
http_codes = re.findall(r'', log_text)
# (Una forma más precisa: limpiar los espacios del resultado o capturar solo los 3 dígitos)
http_codes_clean = re.findall(r'', log_text)

# 12. Sustitución de fechas (YYYY-MM-DD a DD/MM/YYYY)
# Grupo 1: Año, Grupo 2: Mes, Grupo 3: Día
log_modificado = re.sub(r"", log_text, flags=re.MULTILINE)
```

## Solucion

```python
import re

# 1. PIDs (Escapando corchetes y usando grupo de captura)
pids = re.findall(r"\[(\d+)\]", log_text)

# 2. Niveles de severidad (Alternancia)
severities = re.findall(r"\b(ERROR|WARN|CRITICAL)\b", log_text)

# 3. Direcciones IP (Escapando puntos)
ips = re.findall(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b", log_text)

# 4. Tiempos de espera (ms)
timeouts = re.findall(r"(\d+)ms\b", log_text)

# 5. Usuarios de CRON (Escapando paréntesis)
cron_users = re.findall(r"CRON\[\d+\]: \((.*?)\)", log_text)

# 6. Scripts de CRON
cron_scripts = re.findall(r"CMD \((.*?)\)", log_text)

# 7. Usuarios inválidos en SSH
invalid_ssh_users = re.findall(r"Failed password for invalid user (\w+)", log_text)

# 8. Correos electrónicos
emails = re.findall(r"[\w.-]+@[\w.-]+", log_text)

# 9. Fechas ISO 8601 al inicio de la línea (con flag re.MULTILINE)
iso_dates = re.findall(r"^\d{4}-\d{2}-\d{2}", log_text, re.MULTILINE)

# 10. Método HTTP y ruta
http_requests = re.findall(r'"(GET|POST|PUT|DELETE) (.*?) HTTP', log_text)

# 11. Códigos de estado HTTP
http_codes = re.findall(r'" (1|2|3|4|5)\d{2} ', log_text)
# (Una forma más precisa: limpiar los espacios del resultado o capturar solo los 3 dígitos)
http_codes_clean = re.findall(r'" ([1-5]\d{2}) ', log_text)

# 12. Sustitución de fechas (YYYY-MM-DD a DD/MM/YYYY)
# Grupo 1: Año, Grupo 2: Mes, Grupo 3: Día
log_modificado = re.sub(r"^(\d{4})-(\d{2})-(\d{2})", r"\3/\2/\1", log_text, flags=re.MULTILINE)
```

## Relacionado

- [[Python y Sistemas Operativos]]
