--------------------------------------------------------------------------------
-- Forms2APEX Accelerator
-- Table   : F2A_ITEM
-- Purpose : Stores items detected inside Forms blocks
-- Version : 0.1
--------------------------------------------------------------------------------

CREATE TABLE F2A_ITEM
(
    ITEM_ID              NUMBER                     NOT NULL,
    BLOCK_ID             NUMBER                     NOT NULL,

    ITEM_NAME            VARCHAR2(200)              NOT NULL,
    ITEM_TYPE            VARCHAR2(30)               NOT NULL,

    DATA_TYPE            VARCHAR2(30),
    DATABASE_ITEM        VARCHAR2(1)                DEFAULT 'N' NOT NULL,
    COLUMN_NAME          VARCHAR2(200),

    REQUIRED_FLAG        VARCHAR2(1)                DEFAULT 'N' NOT NULL,
    LOV_NAME             VARCHAR2(200),

    CREATED_AT           TIMESTAMP WITH TIME ZONE   DEFAULT SYSTIMESTAMP NOT NULL,

    CONSTRAINT PK_F2A_ITEM
        PRIMARY KEY (ITEM_ID),

    CONSTRAINT FK_F2A_ITEM_BLOCK
        FOREIGN KEY (BLOCK_ID)
        REFERENCES F2A_BLOCK (BLOCK_ID),

    CONSTRAINT UQ_F2A_ITEM_BLOCK_NAME
        UNIQUE (BLOCK_ID, ITEM_NAME),

    CONSTRAINT CK_F2A_ITEM_TYPE
        CHECK
        (
            ITEM_TYPE IN
            (
                'TEXT_ITEM',
                'LIST_ITEM',
                'PUSH_BUTTON'
            )
        ),

    CONSTRAINT CK_F2A_ITEM_DATABASE
        CHECK
        (
            DATABASE_ITEM IN ('Y', 'N')
        ),

    CONSTRAINT CK_F2A_ITEM_REQUIRED
        CHECK
        (
            REQUIRED_FLAG IN ('Y', 'N')
        ),

    CONSTRAINT CK_F2A_ITEM_DB_CONSISTENCY
        CHECK
        (
               DATABASE_ITEM = 'N'
            OR COLUMN_NAME IS NOT NULL
        )
);