# Forms2APEX Accelerator — Canonical Model v1

## 1. Objetivo

El Canonical Model representa la estructura interna normalizada utilizada
por Forms2APEX Accelerator.

Su objetivo es desacoplar los formatos de entrada del resto del producto.

La arquitectura será:

```text
SOURCE
  ↓
INPUT ADAPTER
  ↓
F2A_PARSER
  ↓
CANONICAL MODEL
  ↓
F2A_ANALYZER
  ↓
F2A_RULE_ENGINE
  ↓
APEX RECOMMENDATIONS
```

El modelo canónico no debe depender directamente de:

- F2A_SYNTHETIC_V1
- Oracle Forms2XML
- una versión concreta de Oracle Forms
- una versión concreta de Oracle APEX

---

## 2. Entidades v1

La primera versión estará compuesta por:

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

---

## 3. Relación principal

```text
F2A_PROJECT
     │
     │ 1:N
     ▼
F2A_SOURCE_FILE
     │
     │ 1:N
     ▼
F2A_FORM
     │
     ├───────────────┐
     │               │
     ▼               ▼
F2A_BLOCK       F2A_PROGRAM_UNIT
     │
     │
     ▼
F2A_ITEM

F2A_TRIGGER podrá asociarse a:

FORM
BLOCK
ITEM

F2A_LOV pertenecerá inicialmente al FORM.
```

---

## 4. F2A_PROJECT

Representa un proyecto de migración.

Ejemplo:

```text
PROJECT_NAME:
Demo Customers Migration
```

Campos:

```text
PROJECT_ID
PROJECT_NAME
DESCRIPTION
SOURCE_PLATFORM
SOURCE_VERSION
TARGET_PLATFORM
TARGET_VERSION
STATUS
CREATED_AT
CREATED_BY
UPDATED_AT
UPDATED_BY
```

Valores iniciales de STATUS:

```text
NEW
ANALYZING
ANALYZED
ERROR
ARCHIVED
```

---

## 5. F2A_SOURCE_FILE

Representa un archivo incorporado al proyecto.

Campos:

```text
SOURCE_FILE_ID
PROJECT_ID
FILE_NAME
FILE_TYPE
SOURCE_FORMAT
MIME_TYPE
FILE_SIZE
FILE_CONTENT
FILE_HASH
STATUS
ERROR_MESSAGE
CREATED_AT
CREATED_BY
PARSED_AT
```

Tipos inicialmente previstos:

```text
SYNTHETIC_XML
FORMS_XML
```

El contenido del archivo se almacenará inicialmente en:

```text
BLOB
```

Esto permitirá conservar trazabilidad completa sobre la fuente procesada.

---

## 6. F2A_FORM

Representa un módulo Forms detectado por el parser.

Campos:

```text
FORM_ID
PROJECT_ID
SOURCE_FILE_ID
FORM_NAME
DESCRIPTION
SOURCE_TYPE
TARGET_PLATFORM
BLOCK_COUNT
ITEM_COUNT
TRIGGER_COUNT
PROGRAM_UNIT_COUNT
LOV_COUNT
CREATED_AT
```

Ejemplo esperado para Golden Sample #001:

```text
FORM_NAME = F2A_CUSTOMERS_FORM
```

---

## 7. F2A_BLOCK

Representa un bloque Forms.

Campos:

```text
BLOCK_ID
FORM_ID
BLOCK_NAME
BLOCK_TYPE
DATABASE_BLOCK
DATA_SOURCE
RECORDS_DISPLAYED
CREATED_AT
```

Tipos inicialmente soportados:

```text
DATABASE
CONTROL
```

Golden Sample #001:

```text
CUSTOMERS
CONTROL
```

---

## 8. F2A_ITEM

Representa un item perteneciente a un block.

Campos:

```text
ITEM_ID
BLOCK_ID
ITEM_NAME
ITEM_TYPE
DATA_TYPE
DATABASE_ITEM
COLUMN_NAME
REQUIRED_FLAG
LOV_NAME
CREATED_AT
```

Tipos inicialmente soportados:

```text
TEXT_ITEM
LIST_ITEM
PUSH_BUTTON
```

Golden Sample #001:

```text
CUSTOMER_ID
FIRST_NAME
LAST_NAME
EMAIL
STATUS
BTN_SAVE
BTN_CANCEL
```

---

## 9. F2A_TRIGGER

Representa un trigger Oracle Forms.

Un trigger puede pertenecer a:

```text
FORM
BLOCK
ITEM
```

Campos:

```text
TRIGGER_ID
FORM_ID
BLOCK_ID
ITEM_ID
TRIGGER_NAME
TRIGGER_LEVEL
SOURCE_CODE
CREATED_AT
```

TRIGGER_LEVEL:

```text
FORM
BLOCK
ITEM
```

SOURCE_CODE:

```text
CLOB
```

Golden Sample #001:

```text
WHEN-NEW-FORM-INSTANCE
WHEN-VALIDATE-ITEM
WHEN-BUTTON-PRESSED
PRE-INSERT
POST-QUERY
```

---

## 10. F2A_PROGRAM_UNIT

Representa procedures y functions declarados dentro del Form.

Campos:

```text
PROGRAM_UNIT_ID
FORM_ID
UNIT_NAME
UNIT_TYPE
SOURCE_CODE
CREATED_AT
```

UNIT_TYPE inicialmente:

```text
PROCEDURE
FUNCTION
```

Golden Sample #001:

```text
VALIDATE_EMAIL
SAVE_CUSTOMER
```

---

## 11. F2A_LOV

Representa una LOV perteneciente al formulario.

Campos:

```text
LOV_ID
FORM_ID
LOV_NAME
LOV_TYPE
SOURCE_QUERY
CREATED_AT
```

Tipos inicialmente previstos:

```text
STATIC
QUERY
UNKNOWN
```

Golden Sample #001:

```text
LOV_STATUS
```

Los valores individuales de una LOV no serán persistidos todavía en v1.

Se agregará posteriormente:

```text
F2A_LOV_VALUE
```

si resulta necesario.

---

## 12. Convenciones de nomenclatura

Todos los objetos pertenecientes al producto utilizarán prefijo:

```text
F2A_
```

Primary Keys:

```text
PK_F2A_<TABLE>
```

Foreign Keys:

```text
FK_F2A_<CHILD>_<PARENT>
```

Indexes:

```text
IX_F2A_<TABLE>_<DESCRIPTION>
```

Sequences:

```text
F2A_<ENTITY>_SEQ
```

---

## 13. Estrategia de IDs

Para mantener compatibilidad amplia entre versiones de Oracle Database se
utilizarán inicialmente sequences explícitas.

Ejemplo:

```text
F2A_PROJECT_SEQ
F2A_SOURCE_FILE_SEQ
F2A_FORM_SEQ
```

Los IDs serán NUMBER.

No se utilizarán IDs provenientes del XML como Primary Key interna.

---

## 14. Estrategia de auditoría

Las tablas principales incorporarán como mínimo:

```text
CREATED_AT
```

Las tablas modificables por usuario incorporarán adicionalmente:

```text
CREATED_BY
UPDATED_AT
UPDATED_BY
```

El origen deberá permanecer rastreable mediante:

```text
PROJECT_ID
SOURCE_FILE_ID
FORM_ID
BLOCK_ID
ITEM_ID
```

según corresponda.

---

## 15. Estrategia de código fuente

Triggers y Program Units almacenarán su código en:

```text
CLOB
```

El parser deberá almacenar el código sin interpretar su lógica.

La interpretación corresponderá posteriormente a:

```text
F2A_ANALYZER
```

---

## 16. Integridad referencial

Las relaciones principales serán:

```text
F2A_SOURCE_FILE.PROJECT_ID
    → F2A_PROJECT.PROJECT_ID

F2A_FORM.PROJECT_ID
    → F2A_PROJECT.PROJECT_ID

F2A_FORM.SOURCE_FILE_ID
    → F2A_SOURCE_FILE.SOURCE_FILE_ID

F2A_BLOCK.FORM_ID
    → F2A_FORM.FORM_ID

F2A_ITEM.BLOCK_ID
    → F2A_BLOCK.BLOCK_ID

F2A_TRIGGER.FORM_ID
    → F2A_FORM.FORM_ID

F2A_TRIGGER.BLOCK_ID
    → F2A_BLOCK.BLOCK_ID

F2A_TRIGGER.ITEM_ID
    → F2A_ITEM.ITEM_ID

F2A_PROGRAM_UNIT.FORM_ID
    → F2A_FORM.FORM_ID

F2A_LOV.FORM_ID
    → F2A_FORM.FORM_ID
```

---

## 17. Reglas de integridad para Trigger

Si:

```text
TRIGGER_LEVEL = FORM
```

entonces:

```text
FORM_ID  NOT NULL
BLOCK_ID NULL
ITEM_ID  NULL
```

Si:

```text
TRIGGER_LEVEL = BLOCK
```

entonces:

```text
FORM_ID  NOT NULL
BLOCK_ID NOT NULL
ITEM_ID  NULL
```

Si:

```text
TRIGGER_LEVEL = ITEM
```

entonces:

```text
FORM_ID  NOT NULL
BLOCK_ID NOT NULL
ITEM_ID  NOT NULL
```

Estas reglas deberán implementarse posteriormente mediante constraint o
validación del parser.

---

## 18. Golden Sample #001

Después de ejecutar F2A_PARSER sobre:

```text
samples/golden_001/fixtures/f2a_customers_form.xml
```

el modelo deberá contener:

```text
F2A_PROJECT
    1 registro de prueba

F2A_SOURCE_FILE
    1 registro

F2A_FORM
    1 registro

F2A_BLOCK
    2 registros

F2A_ITEM
    7 registros

F2A_TRIGGER
    5 registros

F2A_PROGRAM_UNIT
    2 registros

F2A_LOV
    1 registro
```

---

## 19. Entidades futuras

No forman parte de Canonical Model v1:

```text
F2A_DEPENDENCY
F2A_BUILTIN
F2A_ANALYSIS_RUN
F2A_RULE
F2A_RULE_MATCH
F2A_RECOMMENDATION
F2A_LOV_VALUE
```

Serán incorporadas progresivamente.

---

## 20. Principio arquitectónico

El Canonical Model representa hechos extraídos del sistema origen.

No debe contener directamente decisiones de migración.

Por ejemplo:

```text
CORRECTO

F2A_TRIGGER
TRIGGER_NAME = WHEN-VALIDATE-ITEM
```

No:

```text
INCORRECTO

F2A_TRIGGER
TARGET_APEX_COMPONENT = VALIDATION
```

La decisión:

```text
WHEN-VALIDATE-ITEM
        ↓
APEX Validation
```

corresponde al:

```text
F2A_RULE_ENGINE
```

---

## 21. Versión

```text
MODEL   : F2A_CANONICAL_MODEL
VERSION : 1
STATUS  : ACTIVE
```