--------------------------------------------------------------------------------
-- Forms2APEX Accelerator
-- Tables  : F2A_LOV / F2A_LOV_VALUE
-- Purpose : Stores Forms LOV definitions and static LOV values
-- Version : 0.1
--------------------------------------------------------------------------------

CREATE TABLE F2A_LOV
(
    LOV_ID              NUMBER                     NOT NULL,
    FORM_ID             NUMBER                     NOT NULL,

    LOV_NAME            VARCHAR2(200)              NOT NULL,
    LOV_TYPE            VARCHAR2(20)               DEFAULT 'STATIC' NOT NULL,

    QUERY_TEXT          CLOB,

    CREATED_AT          TIMESTAMP WITH TIME ZONE   DEFAULT SYSTIMESTAMP NOT NULL,

    CONSTRAINT PK_F2A_LOV
        PRIMARY KEY (LOV_ID),

    CONSTRAINT FK_F2A_LOV_FORM
        FOREIGN KEY (FORM_ID)
        REFERENCES F2A_FORM (FORM_ID),

    CONSTRAINT UQ_F2A_LOV_FORM_NAME
        UNIQUE (FORM_ID, LOV_NAME),

    CONSTRAINT CK_F2A_LOV_TYPE
        CHECK
        (
            LOV_TYPE IN ('STATIC', 'QUERY')
        ),

    CONSTRAINT CK_F2A_LOV_QUERY
        CHECK
        (
            LOV_TYPE NOT IN ('STATIC', 'QUERY')
            OR (LOV_TYPE = 'STATIC' AND QUERY_TEXT IS NULL)
            OR (LOV_TYPE = 'QUERY'  AND QUERY_TEXT IS NOT NULL)
        )
);


CREATE TABLE F2A_LOV_VALUE
(
    LOV_VALUE_ID        NUMBER                     NOT NULL,
    LOV_ID              NUMBER                     NOT NULL,

    RETURN_VALUE        VARCHAR2(4000)             NOT NULL,
    DISPLAY_VALUE       VARCHAR2(4000)             NOT NULL,
    DISPLAY_ORDER       NUMBER                     NOT NULL,

    CREATED_AT          TIMESTAMP WITH TIME ZONE   DEFAULT SYSTIMESTAMP NOT NULL,

    CONSTRAINT PK_F2A_LOV_VALUE
        PRIMARY KEY (LOV_VALUE_ID),

    CONSTRAINT FK_F2A_LOV_VALUE_LOV
        FOREIGN KEY (LOV_ID)
        REFERENCES F2A_LOV (LOV_ID),

    CONSTRAINT UQ_F2A_LOV_VALUE_RETURN
        UNIQUE (LOV_ID, RETURN_VALUE),

    CONSTRAINT CK_F2A_LOV_VALUE_ORDER
        CHECK (DISPLAY_ORDER > 0)
);