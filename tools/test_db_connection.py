import getpass

import oracledb


DB_USER = "F2A_OWNER"
DB_DSN = "localhost:1521/FREEPDB1"


def main():
    password = getpass.getpass("Password F2A_OWNER: ")

    try:
        with oracledb.connect(
            user=DB_USER,
            password=password,
            dsn=DB_DSN
        ) as connection:

            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    SELECT
                        USER AS current_user,
                        SYS_CONTEXT('USERENV', 'CON_NAME') AS container_name
                    FROM dual
                    """
                )

                current_user, container_name = cursor.fetchone()

                print()
                print("Forms2APEX Accelerator - Database Connection")
                print("--------------------------------------------")
                print(f"User      : {current_user}")
                print(f"Container : {container_name}")
                print("Status    : OK")

    except oracledb.Error as error:
        print()
        print("Database connection failed.")
        print(error)


if __name__ == "__main__":
    main()