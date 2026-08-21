from getpass import getpass

from f2a.persistence.oracle_repository import OracleRepository


def main() -> None:
    print()
    print("Forms2APEX Accelerator - Oracle Repository")
    print("------------------------------------------")

    password = getpass("Password F2A_OWNER: ")

    with OracleRepository(
        user="F2A_OWNER",
        password=password,
    ) as repository:

        info = repository.get_database_info()

        print()
        print(f"User      : {info['user']}")
        print(f"Container : {info['container']}")

        counts = repository.get_form_counts(
            form_id=1
        )

        print()
        print("Canonical Model")
        print("------------------------------------------")
        print(f"Blocks        : {counts['blocks']}")
        print(f"Items         : {counts['items']}")
        print(f"Triggers      : {counts['triggers']}")
        print(f"Program Units : {counts['program_units']}")
        print(f"LOVs          : {counts['lovs']}")

        print()
        print("Repository status: OK")


if __name__ == "__main__":
    main()