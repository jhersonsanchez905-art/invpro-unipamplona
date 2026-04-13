# Convencion de commits — InvPro Unipamplona
## Formato
tipo(scope): descripcion corta en minusculas
## Tipos permitidos
feat:     nueva funcionalidad
fix:      correccion de bug
docs:     cambios en documentacion
style:    formato sin cambio de logica
refactor: refactorizacion sin nueva funcionalidad
test:     agregar o corregir tests
chore:    tareas de mantenimiento
## Ejemplos correctos
feat(auth): login con roles admin y cliente
feat(inventory): modelo Producto con soft delete
fix(movements): validar stock negativo antes de salida
docs(readme): agregar instrucciones de instalacion
style(ui): alinear tabla productos con design system
## Estrategia de ramas
main          produccion — solo merge desde develop
develop       integracion — merge desde feature/*
feature/US-01 una rama por historia de usuario
