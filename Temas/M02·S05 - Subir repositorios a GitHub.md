---
tipo: recurso
tags: [git]
---

# Subir repositorios a GitHub

Guía rápida para subir tu código a GitHub desde 3 herramientas distintas.

---

## 1️⃣ Desde VSCode (con Claude Code)

### Paso 1: Crear el repositorio en GitHub

1. Ve a [github.com/new](https://github.com/new)
2. Ponle un nombre (ej: `pomodoro-v1`)
3. Elige **Public** o **Private**
4. Activa **Add README**
5. En **Add license**, elige **MIT License** (la más simple y estándar)
6. Haz clic en **Create repository**

### Paso 2: Abrir la terminal en VS Code

Presiona `Ctrl + ñ` (Windows/Linux) o `Cmd + ñ` (Mac)

### Paso 3: Ir a la carpeta de tu proyecto

```bash
cd Documentos/mi-proyecto
```

### Paso 4: Inicializar Git (solo la primera vez)

```bash
git init
```

### Paso 5: Conectar tu carpeta con GitHub

Copia el enlace de tu repositorio (botón verde **Code** en GitHub) y pégalo aquí, cambiando `TU_USUARIO` y `NOMBRE_REPO`:

```bash
git remote add origin https://github.com/TU_USUARIO/NOMBRE_REPO.git
```

### Paso 6: Subir el código

```bash
git add .
git commit -m "v1: Versión inicial"
git branch -M main
git push -u origin main
```

> 💡 **Explicación rápida:**
> 

> - `git add .` → prepara todos los archivos
> 

> - `git commit -m "..."` → guarda un "punto" con un mensaje descriptivo
> 

> - `git branch -M main` → nombra la rama principal como `main`
> 

> - `git push -u origin main` → sube todo a GitHub
> 

---

## 2️⃣ Desde Lovable

### Opción A: Desde la terminal (con Git)

Si descargas o exportas el código de tu proyecto Lovable a tu ordenador, súbelo igual que en VS Code:

```bash
cd carpeta-de-tu-proyecto
git init
git remote add origin https://github.com/TU_USUARIO/NOMBRE_REPO.git
git add .
git commit -m "v1: Versión inicial desde Lovable"
git branch -M main
git push -u origin main
```

> 💡 Mismos comandos que en VS Code — Git funciona igual sin importar de dónde venga el código.
> 

### Opción B: Desde la web (con un clic)

Lovable tiene integración directa con GitHub, no necesitas usar comandos.

1. Abre tu proyecto en Lovable
2. Ve a la esquina superior derecha y busca el ícono de **GitHub**
3. Haz clic en **Connect to GitHub** (o **Conectar GitHub**)
4. Autoriza el acceso a tu cuenta de GitHub (te pedirá iniciar sesión si no lo has hecho)
5. Elige si quieres crear un **repositorio nuevo** o conectar uno existente
6. Lovable sincroniza automáticamente: cada cambio que hagas en el proyecto se sube solo a GitHub

> 💡 Aquí no escribes comandos. Lovable hace el `git add`, `commit` y `push` por ti cada vez que guardas cambios.
> 

---

## 3️⃣ Desde v0 (Vercel)

### Opción A: Desde la terminal (con Git)

Si descargas el código generado por v0 a tu ordenador, sigue los mismos pasos:

```bash
cd carpeta-de-tu-proyecto
git init
git remote add origin https://github.com/TU_USUARIO/NOMBRE_REPO.git
git add .
git commit -m "v1: Versión inicial desde v0"
git branch -M main
git push -u origin main
```

### Opción B: Desde la web (con un clic)

1. Abre tu proyecto en [v0.dev](https://v0.dev)
2. Busca el botón **Add to GitHub** (o el ícono de GitHub) en la parte superior del proyecto
3. Si es la primera vez, te pedirá **conectar tu cuenta de GitHub** (autorización)
4. Elige el nombre del repositorio que se creará
5. Haz clic en **Create repository** / **Push to GitHub**
6. v0 crea el repositorio automáticamente y sube el código generado

> 💡 Igual que en Lovable, la Opción B no requiere comandos de terminal — todo se hace con clics.
> 

---

## 🔑 Conceptos clave para recordar

- **Repositorio** = la carpeta de tu proyecto en la nube (en GitHub)
- **Commit** = un "guardado" de tus cambios, con un mensaje explicando qué hiciste
- **Push** = subir esos cambios guardados a GitHub
- **Rama (branch)** = una versión del código; `main` es la versión oficial

## Relacionado

- [[M02·S01 - Fundamentos de Programación]]
