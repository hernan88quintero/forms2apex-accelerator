from __future__ import annotations
from f2a.model import FormModel

import oracledb



class OracleRepository:
    def __init__(
        self,
        user: str,
        password: str,
        dsn: str = "localhost:1521/FREEPDB1",
    ) -> None:
        self.user = user
        self.password = password
        self.dsn = dsn
        self.connection: oracledb.Connection | None = None

    def connect(self) -> None:
        if self.connection is not None:
            return

        self.connection = oracledb.connect(
            user=self.user,
            password=self.password,
            dsn=self.dsn,
        )

    def close(self) -> None:
        if self.connection is not None:
            self.connection.close()
            self.connection = None

    def __enter__(self) -> "OracleRepository":
        self.connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()

    def get_database_info(self) -> dict[str, str]:
        if self.connection is None:
            raise RuntimeError(
                "Database connection has not been opened."
            )

        with self.connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT USER,
                       SYS_CONTEXT('USERENV', 'CON_NAME')
                FROM DUAL
                """
            )

            row = cursor.fetchone()

        if row is None:
            raise RuntimeError(
                "Unable to retrieve database information."
            )

        return {
            "user": row[0],
            "container": row[1],
        }

    def get_form_counts(
        self,
        form_id: int,
    ) -> dict[str, int]:
        if self.connection is None:
            raise RuntimeError(
                "Database connection has not been opened."
            )

        with self.connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    (SELECT COUNT(*)
                       FROM F2A_BLOCK
                      WHERE FORM_ID = :form_id),

                    (SELECT COUNT(*)
                       FROM F2A_ITEM i
                       JOIN F2A_BLOCK b
                         ON b.BLOCK_ID = i.BLOCK_ID
                      WHERE b.FORM_ID = :form_id),

                    (SELECT COUNT(*)
                       FROM F2A_TRIGGER
                      WHERE FORM_ID = :form_id),

                    (SELECT COUNT(*)
                       FROM F2A_PROGRAM_UNIT
                      WHERE FORM_ID = :form_id),

                    (SELECT COUNT(*)
                       FROM F2A_LOV
                      WHERE FORM_ID = :form_id)
                FROM DUAL
                """,
                form_id=form_id,
            )

            row = cursor.fetchone()

        if row is None:
            raise RuntimeError(
                "Unable to retrieve canonical model counts."
            )

        return {
            "blocks": row[0],
            "items": row[1],
            "triggers": row[2],
            "program_units": row[3],
            "lovs": row[4],
        }
    
    def _require_connection(self) -> oracledb.Connection:
        if self.connection is None:
            raise RuntimeError(
                "Database connection has not been opened."
            )

        return self.connection


    @staticmethod
    def _nextval(
        cursor: oracledb.Cursor,
        sequence_name: str,
    ) -> int:

        cursor.execute(
            f"SELECT {sequence_name}.NEXTVAL FROM DUAL"
        )

        row = cursor.fetchone()

        if row is None:
            raise RuntimeError(
                f"Unable to retrieve NEXTVAL from {sequence_name}."
            )

        return int(row[0])


    def replace_form_model(
        self,
        form_id: int,
        model: FormModel,
    ) -> None:

        connection = self._require_connection()

        try:
            with connection.cursor() as cursor:

                # ------------------------------------------------------
                # Confirm that the parent form exists
                # ------------------------------------------------------
                cursor.execute(
                    """
                    SELECT COUNT(*)
                    FROM F2A_FORM
                    WHERE FORM_ID = :form_id
                    """,
                    form_id=form_id,
                )

                row = cursor.fetchone()

                if row is None or row[0] != 1:
                    raise ValueError(
                        f"F2A_FORM FORM_ID={form_id} does not exist."
                    )

                # ------------------------------------------------------
                # DELETE CURRENT CANONICAL CHILDREN
                #
                # Order matters because of foreign keys.
                # ------------------------------------------------------

                cursor.execute(
                    """
                    DELETE FROM F2A_LOV_VALUE
                    WHERE LOV_ID IN
                    (
                        SELECT LOV_ID
                        FROM F2A_LOV
                        WHERE FORM_ID = :form_id
                    )
                    """,
                    form_id=form_id,
                )

                cursor.execute(
                    """
                    DELETE FROM F2A_TRIGGER
                    WHERE FORM_ID = :form_id
                    """,
                    form_id=form_id,
                )

                cursor.execute(
                    """
                    DELETE FROM F2A_ITEM
                    WHERE BLOCK_ID IN
                    (
                        SELECT BLOCK_ID
                        FROM F2A_BLOCK
                        WHERE FORM_ID = :form_id
                    )
                    """,
                    form_id=form_id,
                )

                cursor.execute(
                    """
                    DELETE FROM F2A_BLOCK
                    WHERE FORM_ID = :form_id
                    """,
                    form_id=form_id,
                )

                cursor.execute(
                    """
                    DELETE FROM F2A_PROGRAM_UNIT
                    WHERE FORM_ID = :form_id
                    """,
                    form_id=form_id,
                )

                cursor.execute(
                    """
                    DELETE FROM F2A_LOV
                    WHERE FORM_ID = :form_id
                    """,
                    form_id=form_id,
                )

                # ------------------------------------------------------
                # BLOCKS / ITEMS / BLOCK+ITEM TRIGGERS
                # ------------------------------------------------------

                for block in model.blocks:

                    block_id = self._nextval(
                        cursor,
                        "F2A_BLOCK_SEQ",
                    )

                    cursor.execute(
                        """
                        INSERT INTO F2A_BLOCK
                        (
                            BLOCK_ID,
                            FORM_ID,
                            BLOCK_NAME,
                            BLOCK_TYPE,
                            DATABASE_BLOCK,
                            DATA_SOURCE,
                            RECORDS_DISPLAYED
                        )
                        VALUES
                        (
                            :block_id,
                            :form_id,
                            :block_name,
                            :block_type,
                            :database_block,
                            :data_source,
                            :records_displayed
                        )
                        """,
                        block_id=block_id,
                        form_id=form_id,
                        block_name=block.name,
                        block_type=block.block_type,
                        database_block=block.database_block,
                        data_source=block.data_source,
                        records_displayed=block.records_displayed,
                    )

                    # --------------------------------------------------
                    # ITEMS
                    # --------------------------------------------------
                    for item in block.items:

                        item_id = self._nextval(
                            cursor,
                            "F2A_ITEM_SEQ",
                        )

                        cursor.execute(
                            """
                            INSERT INTO F2A_ITEM
                            (
                                ITEM_ID,
                                BLOCK_ID,
                                ITEM_NAME,
                                ITEM_TYPE,
                                DATA_TYPE,
                                DATABASE_ITEM,
                                COLUMN_NAME,
                                REQUIRED_FLAG,
                                LOV_NAME
                            )
                            VALUES
                            (
                                :item_id,
                                :block_id,
                                :item_name,
                                :item_type,
                                :data_type,
                                :database_item,
                                :column_name,
                                :required_flag,
                                :lov_name
                            )
                            """,
                            item_id=item_id,
                            block_id=block_id,
                            item_name=item.name,
                            item_type=item.item_type,
                            data_type=item.data_type,
                            database_item=item.database_item,
                            column_name=item.column_name,
                            required_flag=item.required,
                            lov_name=item.lov_name,
                        )

                        # ----------------------------------------------
                        # ITEM TRIGGERS
                        # ----------------------------------------------
                        for trigger in item.triggers:

                            trigger_id = self._nextval(
                                cursor,
                                "F2A_TRIGGER_SEQ",
                            )

                            cursor.execute(
                                """
                                INSERT INTO F2A_TRIGGER
                                (
                                    TRIGGER_ID,
                                    FORM_ID,
                                    BLOCK_ID,
                                    ITEM_ID,
                                    TRIGGER_NAME,
                                    TRIGGER_LEVEL,
                                    SOURCE_CODE
                                )
                                VALUES
                                (
                                    :trigger_id,
                                    :form_id,
                                    :block_id,
                                    :item_id,
                                    :trigger_name,
                                    'ITEM',
                                    :source_code
                                )
                                """,
                                trigger_id=trigger_id,
                                form_id=form_id,
                                block_id=block_id,
                                item_id=item_id,
                                trigger_name=trigger.name,
                                source_code=trigger.source_code,
                            )

                    # --------------------------------------------------
                    # BLOCK TRIGGERS
                    # --------------------------------------------------
                    for trigger in block.triggers:

                        trigger_id = self._nextval(
                            cursor,
                            "F2A_TRIGGER_SEQ",
                        )

                        cursor.execute(
                            """
                            INSERT INTO F2A_TRIGGER
                            (
                                TRIGGER_ID,
                                FORM_ID,
                                BLOCK_ID,
                                ITEM_ID,
                                TRIGGER_NAME,
                                TRIGGER_LEVEL,
                                SOURCE_CODE
                            )
                            VALUES
                            (
                                :trigger_id,
                                :form_id,
                                :block_id,
                                NULL,
                                :trigger_name,
                                'BLOCK',
                                :source_code
                            )
                            """,
                            trigger_id=trigger_id,
                            form_id=form_id,
                            block_id=block_id,
                            trigger_name=trigger.name,
                            source_code=trigger.source_code,
                        )

                # ------------------------------------------------------
                # FORM TRIGGERS
                # ------------------------------------------------------
                for trigger in model.form_triggers:

                    trigger_id = self._nextval(
                        cursor,
                        "F2A_TRIGGER_SEQ",
                    )

                    cursor.execute(
                        """
                        INSERT INTO F2A_TRIGGER
                        (
                            TRIGGER_ID,
                            FORM_ID,
                            BLOCK_ID,
                            ITEM_ID,
                            TRIGGER_NAME,
                            TRIGGER_LEVEL,
                            SOURCE_CODE
                        )
                        VALUES
                        (
                            :trigger_id,
                            :form_id,
                            NULL,
                            NULL,
                            :trigger_name,
                            'FORM',
                            :source_code
                        )
                        """,
                        trigger_id=trigger_id,
                        form_id=form_id,
                        trigger_name=trigger.name,
                        source_code=trigger.source_code,
                    )

                # ------------------------------------------------------
                # PROGRAM UNITS
                # ------------------------------------------------------
                for unit in model.program_units:

                    program_unit_id = self._nextval(
                        cursor,
                        "F2A_PROGRAM_UNIT_SEQ",
                    )

                    cursor.execute(
                        """
                        INSERT INTO F2A_PROGRAM_UNIT
                        (
                            PROGRAM_UNIT_ID,
                            FORM_ID,
                            PROGRAM_UNIT_NAME,
                            PROGRAM_UNIT_TYPE,
                            SOURCE_CODE
                        )
                        VALUES
                        (
                            :program_unit_id,
                            :form_id,
                            :program_unit_name,
                            :program_unit_type,
                            :source_code
                        )
                        """,
                        program_unit_id=program_unit_id,
                        form_id=form_id,
                        program_unit_name=unit.name,
                        program_unit_type=unit.unit_type,
                        source_code=unit.source_code,
                    )

                # ------------------------------------------------------
                # LOVs
                # ------------------------------------------------------
                for lov in model.lovs:

                    lov_id = self._nextval(
                        cursor,
                        "F2A_LOV_SEQ",
                    )

                    cursor.execute(
                        """
                        INSERT INTO F2A_LOV
                        (
                            LOV_ID,
                            FORM_ID,
                            LOV_NAME,
                            LOV_TYPE,
                            QUERY_TEXT
                        )
                        VALUES
                        (
                            :lov_id,
                            :form_id,
                            :lov_name,
                            :lov_type,
                            :query_text
                        )
                        """,
                        lov_id=lov_id,
                        form_id=form_id,
                        lov_name=lov.name,
                        lov_type=lov.lov_type,
                        query_text=lov.query_text,
                    )

                    for value in lov.values:

                        lov_value_id = self._nextval(
                            cursor,
                            "F2A_LOV_VALUE_SEQ",
                        )

                        cursor.execute(
                            """
                            INSERT INTO F2A_LOV_VALUE
                            (
                                LOV_VALUE_ID,
                                LOV_ID,
                                RETURN_VALUE,
                                DISPLAY_VALUE,
                                DISPLAY_ORDER
                            )
                            VALUES
                            (
                                :lov_value_id,
                                :lov_id,
                                :return_value,
                                :display_value,
                                :display_order
                            )
                            """,
                            lov_value_id=lov_value_id,
                            lov_id=lov_id,
                            return_value=value.return_value,
                            display_value=value.display_value,
                            display_order=value.display_order,
                        )

                # ------------------------------------------------------
                # Synchronize summary counts in F2A_FORM
                # ------------------------------------------------------
                cursor.execute(
                    """
                    UPDATE F2A_FORM f
                    SET BLOCK_COUNT =
                        (
                            SELECT COUNT(*)
                            FROM F2A_BLOCK b
                            WHERE b.FORM_ID = f.FORM_ID
                        ),

                        ITEM_COUNT =
                        (
                            SELECT COUNT(*)
                            FROM F2A_ITEM i
                            JOIN F2A_BLOCK b
                              ON b.BLOCK_ID = i.BLOCK_ID
                            WHERE b.FORM_ID = f.FORM_ID
                        ),

                        TRIGGER_COUNT =
                        (
                            SELECT COUNT(*)
                            FROM F2A_TRIGGER t
                            WHERE t.FORM_ID = f.FORM_ID
                        ),

                        PROGRAM_UNIT_COUNT =
                        (
                            SELECT COUNT(*)
                            FROM F2A_PROGRAM_UNIT pu
                            WHERE pu.FORM_ID = f.FORM_ID
                        ),

                        LOV_COUNT =
                        (
                            SELECT COUNT(*)
                            FROM F2A_LOV l
                            WHERE l.FORM_ID = f.FORM_ID
                        )

                    WHERE f.FORM_ID = :form_id
                    """,
                    form_id=form_id,
                )

            connection.commit()

        except Exception:
            connection.rollback()
            raise