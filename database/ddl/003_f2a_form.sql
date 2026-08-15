--------------------------------------------------------------------------------
-- Forms2APEX Accelerator
-- Table   : F2A_FORM
-- Purpose : Stores Forms modules detected from imported source files
-- Version : 0.1
--------------------------------------------------------------------------------

CREATE TABLE F2A_FORM
(
    FORM_ID              NUMBER          NOT NULL,
    PROJECT_ID           NUMBER          NOT NULL,
    SOURCE_FILE_ID       NUMBER          NOT NULL,

    FORM_NAME            VARCHAR2(200)   NOT NULL,
    DESCRIPTION          VARCHAR2(2000),

    SOURCE_TYPE          VARCHAR2(30)    NOT NULL,
    TARGET_PLATFORM      VARCHAR2(50)    DEFAULT 'ORACLE_APEX' NOT NULL,

    BLOCK_COUNT          NUMBER          DEFAULT 0 NOT NULL,
    ITEM_COUNT           NUMBER          DEFAULT 0 NOT NULL,
    TRIGGER_COUNT        NUMBER          DEFAULT 0 NOT NULL,
    PROGRAM_UNIT_COUNT   NUMBER          DEFAULT 0 NOT NULL,
    LOV_COUNT            NUMBER          DEFAULT 0 NOT NULL,

    CREATED_AT           TIMESTAMP WITH TIME ZONE       DEFAULT SYSTIMESTAMP NOT NULL,

    CONSTRAINT PK_F2A_FORM
        PRIMARY KEY (FORM_ID),

    CONSTRAINT FK_F2A_FORM_PROJECT
        FOREIGN KEY (PROJECT_ID)
        REFERENCES F2A_PROJECT (PROJECT_ID),

    CONSTRAINT FK_F2A_FORM_SOURCE_FILE
        FOREIGN KEY (SOURCE_FILE_ID)
        REFERENCES F2A_SOURCE_FILE (SOURCE_FILE_ID),

    CONSTRAINT UQ_F2A_FORM_SOURCE_NAME
        UNIQUE (SOURCE_FILE_ID, FORM_NAME),

    CONSTRAINT CK_F2A_FORM_SOURCE_TYPE
        CHECK
        (
            SOURCE_TYPE IN
            (
                'SYNTHETIC',
                'ORACLE_FORMS'
            )
        ),

    CONSTRAINT CK_F2A_FORM_COUNTS
        CHECK
        (
            BLOCK_COUNT        >= 0
            AND ITEM_COUNT         >= 0
            AND TRIGGER_COUNT      >= 0
            AND PROGRAM_UNIT_COUNT >= 0
            AND LOV_COUNT          >= 0
        )
);