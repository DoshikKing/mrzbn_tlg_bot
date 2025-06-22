import psycopg


class Conn:

    def __init__(
            self,
            db_name: str,
            db_host: str,
            db_port: str,
            db_user: str,
            db_pass: str
    ):
        self.db_connect = psycopg.connect(
            f"dbname=${db_name} user=${db_user} password=${db_pass} host=${db_host} post=${db_port}")

    def get_connection(self):
        return self.db_connect
