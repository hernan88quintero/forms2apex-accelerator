--------------------------------------------------------------------------------
-- Forms2APEX Accelerator
-- Table   : F2A_SOURCE_FILE
-- Purpose : Stores source files imported into a migration project
-- Version : 0.1
--------------------------------------------------------------------------------

CREATE TABLE F2A_SOURCE_FILE
(
    SOURCE_FILE_ID      NUMBER          NOT NULL,
    PROJECT_ID          NUMBER          NOT NULL,

    FILE_NAME           VARCHAR2(500)   NOT NULL,
    FILE_TYPE           VARCHAR2(30)    NOT NULL,
    SOURCE_FORMAT       VARCHAR2(50)    NOT NULL,

    MIME_TYPE           VARCHAR2(150),
    FILE_SIZE           NUMBER,

    FILE_CONTENT        BLOB            NOT NULL,
    FILE_HASH           VARCHAR2(64),

    STATUS              VARCHAR2(20)    DEFAULT 'UPLOADED' NOT NULL,
    ERROR_MESSAGE       CLOB,

    CREATED_AT          TIMESTAMP       DEFAULT SYSTIMESTAMP NOT NULL,
    CREATED_BY          VARCHAR2(128)   DEFAULT USER NOT NULL,
    PARSED_AT           TIMESTAMP,

    CONSTRAINT PK_F2A_SOURCE_FILE
        PRIMARY KEY (SOURCE_FILE_ID),

    CONSTRAINT FK_F2A_SOURCE_FILE_PROJECT
        FOREIGN KEY (PROJECT_ID)
        REFERENCES F2A_PROJECT (PROJECT_ID),

    CONSTRAINT CK_F2A_SOURCE_FILE_TYPE
        CHECK
        (
            FILE_TYPE IN
            (
                'SYNTHETIC_XML',
                'FORMS_XML'
            )
        ),

    CONSTRAINT CK_F2A_SOURCE_FILE_STATUS
        CHECK
        (
            STATUS IN
            (
                'UPLOADED',
                'PARSING',
                'PARSED',
                'ERROR'
            )
        ),

    CONSTRAINT CK_F2A_SOURCE_FILE_SIZE
        CHECK
        (
            FILE_SIZE IS NULL
            OR FILE_SIZE >= 0
        )
);