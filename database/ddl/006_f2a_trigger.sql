--------------------------------------------------------------------------------
-- Forms2APEX Accelerator
-- Table   : F2A_TRIGGER
-- Purpose : Stores triggers and their source code detected in Oracle Forms
-- Version : 0.1
--------------------------------------------------------------------------------

CREATE TABLE F2A_TRIGGER
(
    TRIGGER_ID           NUMBER                     NOT NULL,

    FORM_ID              NUMBER                     NOT NULL,
    BLOCK_ID             NUMBER,
    ITEM_ID              NUMBER,

    TRIGGER_NAME         VARCHAR2(200)              NOT NULL,
    TRIGGER_LEVEL        VARCHAR2(20)               NOT NULL,

    SOURCE_CODE          CLOB                       NOT NULL,

    CREATED_AT           TIMESTAMP WITH TIME ZONE   DEFAULT SYSTIMESTAMP NOT NULL,

    CONSTRAINT PK_F2A_TRIGGER
        PRIMARY KEY (TRIGGER_ID),

    CONSTRAINT FK_F2A_TRIGGER_FORM
        FOREIGN KEY (FORM_ID)
        REFERENCES F2A_FORM (FORM_ID),

    CONSTRAINT FK_F2A_TRIGGER_BLOCK
        FOREIGN KEY (FORM_ID, BLOCK_ID)
        REFERENCES F2A_BLOCK (FORM_ID, BLOCK_ID),

    CONSTRAINT FK_F2A_TRIGGER_ITEM
        FOREIGN KEY (BLOCK_ID, ITEM_ID)
        REFERENCES F2A_ITEM (BLOCK_ID, ITEM_ID),

    CONSTRAINT CK_F2A_TRIGGER_LEVEL
        CHECK
        (
            TRIGGER_LEVEL IN
            (
                'FORM',
                'BLOCK',
                'ITEM'
            )
        ),

    CONSTRAINT CK_F2A_TRIGGER_SCOPE
        CHECK
        (
               (
                   TRIGGER_LEVEL = 'FORM'
                   AND BLOCK_ID IS NULL
                   AND ITEM_ID IS NULL
               )

            OR (
                   TRIGGER_LEVEL = 'BLOCK'
                   AND BLOCK_ID IS NOT NULL
                   AND ITEM_ID IS NULL
               )

            OR (
                   TRIGGER_LEVEL = 'ITEM'
                   AND BLOCK_ID IS NOT NULL
                   AND ITEM_ID IS NOT NULL
               )
        )
);

--------------------------------------------------------------------------------
-- Functional unique index
--
-- NVL is required because Oracle UNIQUE constraints allow multiple rows
-- when nullable columns participate in the unique key.
--------------------------------------------------------------------------------

CREATE UNIQUE INDEX UQ_F2A_TRIGGER_SCOPE_NAME
ON F2A_TRIGGER
(
    FORM_ID,
    NVL(BLOCK_ID, -1),
    NVL(ITEM_ID, -1),
    TRIGGER_NAME
);