--------------------------------------------------------------------------------
-- Forms2APEX Accelerator
-- Table   : F2A_BLOCK
-- Purpose : Stores blocks detected inside a Form module
-- Version : 0.1
--------------------------------------------------------------------------------

CREATE TABLE F2A_BLOCK
(
    BLOCK_ID             NUMBER                     NOT NULL,
    FORM_ID              NUMBER                     NOT NULL,

    BLOCK_NAME           VARCHAR2(200)              NOT NULL,
    BLOCK_TYPE           VARCHAR2(30)               NOT NULL,

    DATABASE_BLOCK       VARCHAR2(1)                DEFAULT 'N' NOT NULL,
    DATA_SOURCE          VARCHAR2(500),
    RECORDS_DISPLAYED    NUMBER                     DEFAULT 1 NOT NULL,

    CREATED_AT           TIMESTAMP WITH TIME ZONE   DEFAULT SYSTIMESTAMP NOT NULL,

    CONSTRAINT PK_F2A_BLOCK
        PRIMARY KEY (BLOCK_ID),

    CONSTRAINT FK_F2A_BLOCK_FORM
        FOREIGN KEY (FORM_ID)
        REFERENCES F2A_FORM (FORM_ID),

    CONSTRAINT UQ_F2A_BLOCK_FORM_NAME
        UNIQUE (FORM_ID, BLOCK_NAME),

    CONSTRAINT CK_F2A_BLOCK_TYPE
        CHECK
        (
            BLOCK_TYPE IN
            (
                'DATABASE',
                'CONTROL'
            )
        ),

    CONSTRAINT CK_F2A_BLOCK_DATABASE
        CHECK
        (
            DATABASE_BLOCK IN ('Y', 'N')
        ),

    CONSTRAINT CK_F2A_BLOCK_RECORDS
        CHECK
        (
            RECORDS_DISPLAYED > 0
        ),

    CONSTRAINT CK_F2A_BLOCK_CONSISTENCY
        CHECK
        (
               (BLOCK_TYPE = 'DATABASE' AND DATABASE_BLOCK = 'Y')
            OR (BLOCK_TYPE = 'CONTROL'  AND DATABASE_BLOCK = 'N')
        )
);