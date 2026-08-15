import getpass
import hashlib
from pathlib import Path

import oracledb


DB_USER = "F2A_OWNER"
DB_DSN = "localhost:1521/FREEPDB1"

PROJECT_ID = 1

FIXTURE_RELATIVE_PATH = Path(
    "samples/golden_001/fixtures/f2a_customers_form.xml"
)

FILE_TYPE = "SYNTHETIC_XML"
SOURCE_FORMAT = "F2A_SYNTHETIC_V1"
MIME_TYPE = "application/xml"


def main():

    # ------------------------------------------------------------
    # Resolve repository root
    # ------------------------------------------------------------

    repo_root = Path(__file__).resolve().parents[1]

    fixture_path = repo_root / FIXTURE_RELATIVE_PATH

    if not fixture_path.exists():
        raise FileNotFoundError(
            f"Fixture not found: {fixture_path}"
        )

    # ------------------------------------------------------------
    # Read XML
    # ------------------------------------------------------------

    file_content = fixture_path.read_bytes()

    file_size = len(file_content)

    file_hash = hashlib.sha256(
        file_content
    ).hexdigest()

    print()
    print("Forms2APEX Accelerator - Fixture Loader")
    print("---------------------------------------")
    print(f"File        : {fixture_path.name}")
    print(f"Size        : {file_size} bytes")
    print(f"SHA-256     : {file_hash}")
    print(f"Project ID  : {PROJECT_ID}")

    # ------------------------------------------------------------
    # Oracle password
    # ------------------------------------------------------------

    password = getpass.getpass(
        "Password F2A_OWNER: "
    )

    try:

        with oracledb.connect(
            user=DB_USER,
            password=password,
            dsn=DB_DSN
        ) as connection:

            with connection.cursor() as cursor:

                # ------------------------------------------------
                # Validate project
                # ------------------------------------------------

                cursor.execute(
                    """
                    SELECT PROJECT_NAME
                    FROM F2A_PROJECT
                    WHERE PROJECT_ID = :project_id
                    """,
                    project_id=PROJECT_ID
                )

                project = cursor.fetchone()

                if project is None:
                    raise RuntimeError(
                        f"Project ID {PROJECT_ID} does not exist."
                    )

                print(
                    f"Project     : {project[0]}"
                )

                # ------------------------------------------------
                # Prevent duplicate fixture
                # ------------------------------------------------

                cursor.execute(
                    """
                    SELECT
                        SOURCE_FILE_ID,
                        STATUS
                    FROM F2A_SOURCE_FILE
                    WHERE PROJECT_ID = :project_id
                      AND FILE_NAME  = :file_name
                      AND FILE_HASH  = :file_hash
                    """,
                    project_id=PROJECT_ID,
                    file_name=fixture_path.name,
                    file_hash=file_hash
                )

                existing = cursor.fetchone()

                if existing:

                    print()
                    print(
                        "Fixture already loaded."
                    )
                    print(
                        f"Source File ID : {existing[0]}"
                    )
                    print(
                        f"Status         : {existing[1]}"
                    )

                    return

                # ------------------------------------------------
                # Get next ID
                # ------------------------------------------------

                cursor.execute(
                    """
                    SELECT F2A_SOURCE_FILE_SEQ.NEXTVAL
                    FROM DUAL
                    """
                )

                source_file_id = cursor.fetchone()[0]

                # ------------------------------------------------
                # Insert file
                # ------------------------------------------------

                cursor.execute(
                    """
                    INSERT INTO F2A_SOURCE_FILE
                    (
                        SOURCE_FILE_ID,
                        PROJECT_ID,
                        FILE_NAME,
                        FILE_TYPE,
                        SOURCE_FORMAT,
                        MIME_TYPE,
                        FILE_SIZE,
                        FILE_CONTENT,
                        FILE_HASH
                    )
                    VALUES
                    (
                        :source_file_id,
                        :project_id,
                        :file_name,
                        :file_type,
                        :source_format,
                        :mime_type,
                        :file_size,
                        :file_content,
                        :file_hash
                    )
                    """,
                    source_file_id=source_file_id,
                    project_id=PROJECT_ID,
                    file_name=fixture_path.name,
                    file_type=FILE_TYPE,
                    source_format=SOURCE_FORMAT,
                    mime_type=MIME_TYPE,
                    file_size=file_size,
                    file_content=file_content,
                    file_hash=file_hash
                )

                connection.commit()

                print()
                print("Fixture loaded successfully.")
                print("---------------------------------------")
                print(
                    f"Source File ID : {source_file_id}"
                )
                print(
                    "Status         : UPLOADED"
                )
                print(
                    "Database       : FREEPDB1"
                )

    except oracledb.Error as error:

        print()
        print("Oracle error:")
        print(error)

        raise


if __name__ == "__main__":
    main()