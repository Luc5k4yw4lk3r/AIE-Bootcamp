### El Iceberg de la Conspiranoia

La metáfora del iceberg/deep web es ideal para conspiranoia porque ya trae la idea de "niveles de profundidad": arriba lo mainstream, abajo lo oscuro. Un detalle conceptual antes de arrancar: en la estética iceberg/deep web lo coherente es que la gente **baje** a medida que acierta (más profundo = más oscuro = más "iniciado"), no que suba. Queda mucho más potente narrativamente: "¿hasta qué nivel del iceberg llegás?".

La mecánica que yo armaría:

**Niveles temáticos como capas del iceberg.** Arrancás con preguntas de superficie (cosas que todos conocen: el logo de cierta marca, teorías pop) y vas bajando a capas cada vez más oscuras/nicho. Cada capa podés etiquetarla con el lenguaje de la deep web: _Surface → Deep → Dark → Marianas_. Las preguntas no tienen por qué ser de "verdadero conocimiento" — pueden ser mitad trivia, mitad encuesta de opinión ("¿cuántos acá creen que X?"), que en un after con cripto/AI da mucho juego.

**Formato de avance.** Cada persona (o equipo) tiene un avatar/punto en el iceberg. Acierta → baja un nivel; la pantalla muestra en tiempo real cuántos quedan vivos en cada capa. Al final queda un puñado en el fondo: esos son los "que saben demasiado". Es auto-dramático y genera la tensión de ir viendo cómo se va vaciando la superficie.

-  una web app simple. Pantalla grande = el iceberg animado (un SVG por capas + WebSocket). Teléfonos = un mini front donde votan con un código de sala (tipo Jackbox/Kahoot). Backend liviano con FastAPI + WebSockets maneja estado de sala, preguntas y posiciones. Es medio día de trabajo para vos y el resultado es infinitamente más vistoso. Si querés que sea reutilizable para futuras ediciones, este camino paga solo.