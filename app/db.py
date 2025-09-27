import psycopg2
#Conexión de postgreSQL
def get_connection():
    return psycopg2.connect(
        dbname="exoplanets00",
        user="kamimimi",
        password="",
        host="localhost",
        port="5432"
    )
