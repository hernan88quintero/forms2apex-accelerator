# F2A_SYNTHETIC_V1 — XML Contract

## 1. Objetivo

`F2A_SYNTHETIC_V1` es el primer formato XML controlado por
Forms2APEX Accelerator.

Su finalidad es proporcionar un formato reproducible para desarrollar
y validar:

- F2A_PARSER
- F2A_ANALYZER
- F2A_RULE_ENGINE
- pruebas unitarias
- pruebas de regresión

Este formato NO representa el XML oficial generado por Oracle Forms2XML.

Los XML reales de Oracle Forms serán soportados posteriormente mediante
un adapter específico.

---

## 2. Identificación del formato

Todo documento debe utilizar como nodo raíz:

```xml
<f2a-form-fixture
    format="F2A_SYNTHETIC_V1"
    name="F2A_CUSTOMERS_FORM">
```

### Atributos obligatorios

| Atributo | Descripción |
|---|---|
| format | Versión del formato |
| name | Nombre lógico del formulario |

El parser deberá validar el atributo `format`.

---

## 3. Jerarquía principal

```text
f2a-form-fixture
│
├── metadata
│
├── blocks
│   └── block
│       ├── items
│       │   └── item
│       │       └── triggers
│       │           └── trigger
│       └── triggers
│           └── trigger
│
├── form-triggers
│   └── trigger
│
├── program-units
│   └── program-unit
│
├── lovs
│   └── lov
│
└── expected-results
```

---

## 4. Form

El nodo raíz representa un formulario.

### Mapping futuro

```text
f2a-form-fixture
        ↓
F2A_FORM
```

El atributo:

```text
name
```

se almacenará como:

```text
F2A_FORM.FORM_NAME
```

---

## 5. Metadata

El nodo:

```xml
<metadata>
```

puede contener:

- description
- source-type
- target-platform

Ejemplo:

```xml
<metadata>
    <description>Forms2APEX synthetic sample</description>
    <source-type>SYNTHETIC</source-type>
    <target-platform>ORACLE_APEX</target-platform>
</metadata>
```

---

## 6. Blocks

Los bloques se encuentran bajo:

```xml
<blocks>
```

Cada bloque está representado por:

```xml
<block>
```

Ejemplo:

```xml
<block
    name="CUSTOMERS"
    type="DATABASE"
    database-block="Y"
    data-source="CUSTOMERS"
    records-displayed="1">
```

### Atributos soportados inicialmente

| Atributo | Descripción |
|---|---|
| name | Nombre del block |
| type | DATABASE o CONTROL |
| database-block | Y/N |
| data-source | Fuente de datos |
| records-displayed | Registros visibles |

### Mapping

```text
block
  ↓
F2A_BLOCK
```

---

## 7. Block Types

Inicialmente se soportan:

```text
DATABASE
CONTROL
```

### DATABASE

Bloque asociado a una fuente de datos.

Ejemplo:

```text
CUSTOMERS
```

### CONTROL

Bloque no asociado directamente a una tabla.

Ejemplo:

```text
CONTROL
```

---

## 8. Items

Todo item pertenece a un block.

Jerarquía:

```text
FORM
 ↓
BLOCK
 ↓
ITEM
```

Ejemplo:

```xml
<item
    name="EMAIL"
    type="TEXT_ITEM"
    data-type="VARCHAR2"
    database-item="Y"
    column-name="EMAIL"
    required="Y"/>
```

### Atributos iniciales

| Atributo | Descripción |
|---|---|
| name | Nombre del item |
| type | Tipo de item |
| data-type | Tipo de dato |
| database-item | Y/N |
| column-name | Columna asociada |
| required | Y/N |
| lov-name | LOV asociada |

### Tipos inicialmente soportados

```text
TEXT_ITEM
LIST_ITEM
PUSH_BUTTON
```

### Mapping

```text
item
 ↓
F2A_ITEM
```

---

## 9. Triggers

Un trigger puede pertenecer a tres niveles:

```text
FORM
BLOCK
ITEM
```

El parser deberá conservar el nivel al que pertenece cada trigger.

---

## 10. Form Triggers

Jerarquía:

```text
FORM
 ↓
TRIGGER
```

Ejemplo:

```xml
<form-triggers>

    <trigger name="WHEN-NEW-FORM-INSTANCE">

        <source-code>
            ...
        </source-code>

    </trigger>

</form-triggers>
```

El parser deberá registrar:

```text
TRIGGER_LEVEL = FORM
```

---

## 11. Block Triggers

Jerarquía:

```text
FORM
 ↓
BLOCK
 ↓
TRIGGER
```

El parser deberá registrar:

```text
TRIGGER_LEVEL = BLOCK
```

Ejemplos:

```text
PRE-INSERT
POST-QUERY
```

---

## 12. Item Triggers

Jerarquía:

```text
FORM
 ↓
BLOCK
 ↓
ITEM
 ↓
TRIGGER
```

El parser deberá registrar:

```text
TRIGGER_LEVEL = ITEM
```

Ejemplos:

```text
WHEN-VALIDATE-ITEM
WHEN-BUTTON-PRESSED
```

---

## 13. Source Code

El código PL/SQL se almacena mediante:

```xml
<source-code><![CDATA[
...
]]></source-code>
```

El parser deberá conservar el código fuente sin alteraciones relevantes.

### Mapping futuro

```text
source-code
    ↓
CLOB
```

`F2A_PARSER` no interpretará inicialmente el PL/SQL.

Su responsabilidad será exclusivamente extraerlo y persistirlo.

La interpretación posterior será responsabilidad de:

```text
F2A_ANALYZER
```

---

## 14. Program Units

Las Program Units pertenecen al Form.

Ejemplo:

```xml
<program-unit
    name="SAVE_CUSTOMER"
    type="PROCEDURE">
```

### Atributos

| Atributo | Descripción |
|---|---|
| name | Nombre |
| type | Tipo |

### Tipos inicialmente soportados

```text
PROCEDURE
FUNCTION
```

### Mapping

```text
program-unit
      ↓
F2A_PROGRAM_UNIT
```

---

## 15. LOVs

Las LOV pertenecen al Form.

Ejemplo:

```xml
<lov name="LOV_STATUS">
```

Una LOV puede contener valores como:

```xml
<value
    return-value="ACTIVE"
    display-value="Active"/>
```

### Mapping futuro

```text
lov
 ↓
F2A_LOV
```

---

## 16. Expected Results

El nodo:

```xml
<expected-results>
```

es metadata exclusiva del entorno de pruebas de Forms2APEX Accelerator.

No representa funcionalidad de Oracle Forms.

Ejemplo:

```xml
<expected-results>
    <forms>1</forms>
    <blocks>2</blocks>
    <items>7</items>
    <triggers>5</triggers>
    <program-units>2</program-units>
    <lovs>1</lovs>
</expected-results>
```

Esto permitirá comparar automáticamente:

```text
EXPECTED RESULT
       VS
PARSER RESULT
```

durante las futuras pruebas de regresión.

---

## 17. Golden Sample #001

El archivo utilizado como primer Golden Sample es:

```text
samples/golden_001/fixtures/f2a_customers_form.xml
```

Debe producir exactamente los siguientes resultados:

```text
Forms           1
Blocks          2
Items           7
Triggers        5
Program Units   2
LOVs            1
```

### Form esperado

```text
F2A_CUSTOMERS_FORM
```

### Blocks esperados

```text
CUSTOMERS
CONTROL
```

### Items esperados

```text
CUSTOMER_ID
FIRST_NAME
LAST_NAME
EMAIL
STATUS
BTN_SAVE
BTN_CANCEL
```

### Triggers esperados

```text
WHEN-NEW-FORM-INSTANCE
WHEN-VALIDATE-ITEM
WHEN-BUTTON-PRESSED
PRE-INSERT
POST-QUERY
```

### Program Units esperadas

```text
VALIDATE_EMAIL
SAVE_CUSTOMER
```

### LOV esperada

```text
LOV_STATUS
```

---

## 18. Dependencias conocidas

El Golden Sample contiene deliberadamente referencias a las siguientes
dependencias:

```text
TABLE
CUSTOMERS

PACKAGE
F2A_CUSTOMER_API

SEQUENCE
CUSTOMERS_SEQ
```

Estas dependencias no serán detectadas inicialmente por `F2A_PARSER`.

Serán utilizadas posteriormente para probar:

```text
F2A_ANALYZER
```

---

## 19. Built-ins conocidos

El Golden Sample contiene deliberadamente referencias a:

```text
GO_BLOCK
EXECUTE_QUERY
COMMIT_FORM
FORM_TRIGGER_FAILURE
```

Su detección será responsabilidad de:

```text
F2A_ANALYZER
```

y no de:

```text
F2A_PARSER
```

Esta separación de responsabilidades es obligatoria.

---

## 20. Responsabilidades de los componentes

### F2A_PARSER

Responsable de transformar:

```text
XML
 ↓
Metadata estructurada
```

Responsabilidades:

- validar el formato de entrada;
- identificar el formulario;
- extraer blocks;
- extraer items;
- extraer triggers;
- identificar el nivel de cada trigger;
- extraer Program Units;
- extraer LOVs;
- conservar código fuente;
- mantener las relaciones jerárquicas.

No interpreta reglas de negocio.

---

### F2A_ANALYZER

Responsable de analizar:

```text
SOURCE CODE
     ↓
BUILT-INS
DEPENDENCIAS
COMPLEJIDAD
PATRONES
```

Responsabilidades futuras:

- identificar built-ins Oracle Forms;
- detectar tablas;
- detectar vistas;
- detectar packages;
- detectar procedures;
- detectar functions;
- detectar sequences;
- detectar DB Links;
- analizar navegación Forms;
- calcular complejidad;
- identificar patrones de modernización.

---

### F2A_RULE_ENGINE

Responsable de transformar:

```text
Objeto Forms
     +
Regla conocida
     ↓
Recomendación APEX
```

Ejemplo:

```text
WHEN-VALIDATE-ITEM
        ↓
APEX Validation
```

---

## 21. Arquitectura de Adapters

El modelo interno de Forms2APEX Accelerator no debe depender directamente
del formato XML recibido.

La arquitectura general será:

```text
XML INPUT
    ↓
INPUT ADAPTER
    ↓
CANONICAL MODEL
    ↓
ANALYZER
    ↓
RULE ENGINE
```

### Adapter actual

```text
F2A_SYNTHETIC_V1
        ↓
SYNTHETIC ADAPTER
        ↓
CANONICAL MODEL
```

### Adapter futuro

```text
ORACLE FORMS2XML
        ↓
ORACLE FORMS ADAPTER
        ↓
CANONICAL MODEL
```

Ambos deberán terminar produciendo exactamente el mismo modelo interno:

```text
F2A_FORM
F2A_BLOCK
F2A_ITEM
F2A_TRIGGER
F2A_PROGRAM_UNIT
F2A_LOV
```

De esta forma:

```text
              F2A_SYNTHETIC_V1
                     │
                     ▼
              Synthetic Adapter
                     │
                     │
                     ▼
                ┌─────────┐
                │         │
Oracle Forms2XML│         │
       │        │         │
       ▼        │         │
Oracle Adapter ─┤ CANONICAL MODEL
                │         │
                │         │
                └────┬────┘
                     │
                     ▼
                 Analyzer
                     │
                     ▼
                Rules Engine
                     │
                     ▼
                 Oracle APEX
```

Esto permite incorporar nuevos formatos de entrada sin modificar el
resto del producto.

---

## 22. Principios del Parser

`F2A_PARSER` deberá cumplir los siguientes principios:

1. El parser no contiene reglas de migración.
2. El parser no interpreta lógica de negocio.
3. El parser no decide qué componente APEX utilizar.
4. El parser únicamente transforma una fuente XML en el modelo canónico.
5. Todo objeto debe conservar trazabilidad hacia su origen.
6. El código fuente debe almacenarse completo.
7. Las relaciones Form → Block → Item → Trigger deben mantenerse.
8. El parser debe ser reproducible.
9. El parser debe producir siempre el mismo resultado para la misma entrada.
10. Los errores de parsing deberán registrarse claramente.

---

## 23. Principios del Modelo Canónico

El Canonical Model será la representación interna común utilizada por
Forms2APEX Accelerator.

Los primeros objetos previstos son:

```text
F2A_FORM
F2A_BLOCK
F2A_ITEM
F2A_TRIGGER
F2A_PROGRAM_UNIT
F2A_LOV
F2A_DEPENDENCY
F2A_RULE
F2A_RULE_MATCH
```

El modelo deberá ser independiente de:

- Oracle Forms2XML;
- XML sintético;
- versión específica de Oracle Forms;
- versión específica de Oracle APEX.

---

## 24. Trazabilidad

Todo objeto generado por el parser deberá conservar información suficiente
para determinar:

```text
¿De qué archivo vino?
        ↓
¿De qué Form vino?
        ↓
¿De qué Block vino?
        ↓
¿De qué Item vino?
        ↓
¿Qué código fuente lo originó?
```

Esta trazabilidad será necesaria posteriormente para:

- debugging;
- recomendaciones;
- generación de informes;
- comparación Forms vs APEX;
- pruebas de regresión;
- auditoría de migración.

---

## 25. Golden Sample como prueba de regresión

Golden Sample #001 será utilizado permanentemente como prueba.

Cuando `F2A_PARSER` exista, deberá cumplirse:

```text
EXPECTED                     ACTUAL

Forms            1      =      1
Blocks           2      =      2
Items            7      =      7
Triggers         5      =      5
Program Units    2      =      2
LOVs             1      =      1
```

Cualquier diferencia significará:

```text
REGRESSION TEST FAILED
```

No se considerará válido un resultado aproximado.

---

## 26. Evolución del formato

Si fuera necesario modificar el fixture en el futuro, no se deberá
alterar silenciosamente la semántica de:

```text
F2A_SYNTHETIC_V1
```

Una modificación incompatible deberá generar una nueva versión:

```text
F2A_SYNTHETIC_V2
```

Esto permitirá mantener reproducibilidad histórica de los tests.

---

## 27. Estado de la especificación

```text
FORMAT  : F2A_SYNTHETIC_V1
VERSION : 1
STATUS  : ACTIVE
PURPOSE : DEVELOPMENT / TESTING
```

---

## 28. Próximo componente

Una vez aprobado este contrato XML, el siguiente componente a diseñar será:

```text
CANONICAL RELATIONAL MODEL
```

compuesto inicialmente por:

```text
F2A_PROJECT
F2A_SOURCE_FILE
F2A_FORM
F2A_BLOCK
F2A_ITEM
F2A_TRIGGER
F2A_PROGRAM_UNIT
F2A_LOV
```

Ese modelo será la base sobre la cual posteriormente se implementará:

```text
F2A_PARSER
``````
