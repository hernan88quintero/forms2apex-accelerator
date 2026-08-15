--------------------------------------------------------------------------------
-- Forms2APEX Accelerator
-- Table: F2A_PROJECT
-- Version: 0.1
--------------------------------------------------------------------------------

CREATE TABLE F2A_PROJECT
(
    PROJECT_ID       NUMBER         NOT NULL,
    PROJECT_NAME     VARCHAR2(200)  NOT NULL,
    DESCRIPTION      VARCHAR2(2000),

    SOURCE_PLATFORM  VARCHAR2(50),
    SOURCE_VERSION   VARCHAR2(50),

    TARGET_PLATFORM  VARCHAR2(50)   DEFAULT 'ORACLE_APEX' NOT NULL,
    TARGET_VERSION   VARCHAR2(50),

    STATUS            VARCHAR2(20)   DEFAULT 'NEW' NOT NULL,

    CREATED_AT        TIMESTAMP WITH TIME ZONE      DEFAULT SYSTIMESTAMP NOT NULL,
    CREATED_BY        VARCHAR2(128)  DEFAULT USER NOT NULL,

    UPDATED_AT       TIMESTAMP WITH TIME ZONE,
    UPDATED_BY        VARCHAR2(128),

    CONSTRAINT PK_F2A_PROJECT
        PRIMARY KEY (PROJECT_ID),

    CONSTRAINT CK_F2A_PROJECT_STATUS
        CHECK (
            STATUS IN (
                'NEW',
                'ANALYZING',
                'ANALYZED',
                'ERROR',
                'ARCHIVED'
            )
        )
);