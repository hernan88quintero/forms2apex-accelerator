--------------------------------------------------------------------------------
-- Forms2APEX Accelerator
-- Table   : F2A_PROGRAM_UNIT
-- Purpose : Stores Forms program units and their original source code
-- Version : 0.1
--------------------------------------------------------------------------------

CREATE TABLE F2A_PROGRAM_UNIT
(
    PROGRAM_UNIT_ID      NUMBER                     NOT NULL,
    FORM_ID              NUMBER                     NOT NULL,

    PROGRAM_UNIT_NAME    VARCHAR2(200)              NOT NULL,
    PROGRAM_UNIT_TYPE    VARCHAR2(30)               NOT NULL,

    SOURCE_CODE          CLOB                       NOT NULL,

    CREATED_AT           TIMESTAMP WITH TIME ZONE   DEFAULT SYSTIMESTAMP NOT NULL,

    CONSTRAINT PK_F2A_PROGRAM_UNIT
        PRIMARY KEY (PROGRAM_UNIT_ID),

    CONSTRAINT FK_F2A_PROGRAM_UNIT_FORM
        FOREIGN KEY (FORM_ID)
        REFERENCES F2A_FORM (FORM_ID),

    CONSTRAINT UQ_F2A_PROGRAM_UNIT_NAME
        UNIQUE (FORM_ID, PROGRAM_UNIT_NAME),

    CONSTRAINT CK_F2A_PROGRAM_UNIT_TYPE
        CHECK
        (
            PROGRAM_UNIT_TYPE IN
            (
                'PROCEDURE',
                'FUNCTION',
                'PACKAGE_SPEC',
                'PACKAGE_BODY'
            )
        )
);