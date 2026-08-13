# Golden Sample #001 — PFPR_F1053017

## Objetivo

Este formulario será utilizado como primer caso de referencia para validar
el comportamiento de Forms2APEX Accelerator.

El objetivo del Golden Sample es comparar el formulario Oracle Forms
original contra su implementación migrada a Oracle APEX, permitiendo
identificar, validar y posteriormente automatizar patrones reutilizables
de migración.

---

## Información general

- Golden Sample: GOLDEN_001
- Form: PFPR_F1053017
- Tecnología origen: Oracle Forms
- Tecnología destino: Oracle APEX
- Estado: Migrado
- Uso: Parser, Analyzer, Rules Engine y pruebas de regresión

---

## Componentes conocidos

El formulario contiene o utiliza componentes tales como:

- Data Blocks
- Control Blocks
- Items
- Triggers
- Program Units
- Validaciones
- LOVs
- Procesos PL/SQL
- Lógica de interfaz
- Acceso a tablas Oracle
- Procedures
- Functions
- Reglas de negocio
- Manejo de estados visuales

---

## Objetivos de análisis

Forms2APEX Accelerator deberá utilizar este Golden Sample para comprobar
que puede:

1. Detectar correctamente el Form.
2. Detectar Blocks.
3. Detectar Items.
4. Detectar Triggers.
5. Detectar Program Units.
6. Detectar dependencias.
7. Detectar Built-ins de Oracle Forms.
8. Aplicar reglas Forms → APEX.
9. Comparar recomendaciones automáticas contra una migración real.
10. Ejecutar pruebas de regresión.

---

## Archivos locales

Los archivos fuente reales podrán almacenarse localmente dentro de:

samples/golden_001/source/

Ejemplo:

- PFPR_F1053017.fmb
- PFPR_F1053017_fmb.xml

Estos archivos pueden contener código propietario y por lo tanto no deben
ser incorporados al repositorio Git.

El directorio `source` se conserva mediante `.gitkeep`.