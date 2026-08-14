# Golden Sample #001 — F2A_CUSTOMERS_FORM

## Objetivo

Este Golden Sample es un caso de prueba creado específicamente para
Forms2APEX Accelerator.

No contiene código ni información perteneciente a ningún sistema real.

Su objetivo es proporcionar una referencia controlada para desarrollar
y validar el parser, analyzer, rules engine y las pruebas de regresión
del producto.

---

## Identificación

- Golden Sample: GOLDEN_001
- Form: F2A_CUSTOMERS_FORM
- Tipo: Synthetic Oracle Forms Sample
- Propietario: Forms2APEX Accelerator
- Tecnología origen simulada: Oracle Forms
- Tecnología destino: Oracle APEX

---

## Estructura funcional

El formulario representa un mantenimiento simple de clientes.

### Database Block

CUSTOMERS

Items:

- CUSTOMER_ID
- FIRST_NAME
- LAST_NAME
- EMAIL
- STATUS

### Control Block

CONTROL

Items:

- BTN_SAVE
- BTN_CANCEL

---

## Triggers

El Golden Sample deberá contener los siguientes triggers:

- WHEN-NEW-FORM-INSTANCE
- WHEN-VALIDATE-ITEM
- WHEN-BUTTON-PRESSED
- PRE-INSERT
- POST-QUERY

---

## Program Units

Se utilizarán inicialmente:

- VALIDATE_EMAIL
- SAVE_CUSTOMER

---

## LOV

Se utilizará:

- LOV_STATUS

Valores previstos:

- ACTIVE
- INACTIVE

---

## Dependencias simuladas

El formulario utilizará como dependencias:

- Tabla CUSTOMERS
- Package F2A_CUSTOMER_API
- Sequence CUSTOMERS_SEQ

Estas dependencias serán ficticias y creadas únicamente con fines
de prueba.

---

## Objetivos del parser

Forms2APEX Accelerator deberá ser capaz de detectar:

- 1 Form
- 2 Blocks
- 7 Items
- 5 Triggers
- 2 Program Units
- 1 LOV

Además deberá conservar:

- Nombre de cada componente
- Jerarquía de componentes
- Código fuente PL/SQL
- Propiedades relevantes
- Dependencias detectadas

---

## Objetivos futuros del Rules Engine

El Golden Sample permitirá probar inicialmente patrones como:

| Oracle Forms | Oracle APEX |
|---|---|
| Database Block | Form Region |
| Control Block | Static Region / Page Items |
| Text Item | Page Item |
| WHEN-VALIDATE-ITEM | Validation |
| WHEN-BUTTON-PRESSED | Button + Process / Dynamic Action |
| PRE-INSERT | Before DML Process |
| POST-QUERY | Query / rendering logic |
| LOV | APEX LOV |
| Program Unit | PL/SQL Process / Database Package |

---

## Archivos

Los archivos de prueba pertenecientes a este Golden Sample se
almacenarán dentro de:

samples/golden_001/source/

Todos los archivos contenidos en este Golden Sample deberán ser
sintéticos, públicos o creados específicamente para Forms2APEX
Accelerator.