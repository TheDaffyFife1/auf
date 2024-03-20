import sqlite3
import pandas as pd
from datetime import datetime
import emoji
import mysql.connector
import os

config_file_path = 'config.txt'

def get_or_prompt_config():
    """Lee la configuración de un archivo o la solicita al usuario."""
    if os.path.isfile(config_file_path) and os.path.getsize(config_file_path) > 0:
        with open(config_file_path, 'r') as file:
            config = {line.split('=')[0]: line.split('=')[1].strip() for line in file if line.strip()}
    else:
        print("Bienvenido, configuraremos algunos detalles antes de empezar.")
        config = {
            'cliente': input('Ingrese el nombre del cliente: ').strip(),
            'estado': input('Ingrese el nombre del estado: ').strip(),
            'municipio': input('Ingrese el nombre del municipio: ').strip(),
        }
        with open(config_file_path, 'w') as file:
            for key, value in config.items():
                file.write(f'{key}={value}\n')
    return config

# Uso de la función para obtener la configuración
config = get_or_prompt_config()

# Conexión a la base de datos msgstore.db y lectura de datos
con = sqlite3.connect('/sdcard/msgstore.db')
try:
    chv = pd.read_sql_query("SELECT * from chat_view", con)
except pd.io.sql.DatabaseError:
    chv = None  # En caso de que el query no devuelva resultados

usuarios = pd.read_sql_query("SELECT * from 'jid'",con)

msg = pd.read_sql_query("SELECT * from message", con)
con.close()

# Conexión a la base de datos wa.db y lectura de datos
con1 = sqlite3.connect('/sdcard/wa.db')
contacts = pd.read_sql_query("SELECT * from wa_contacts", con1)
contacts['jid'] = contacts['jid'].str.split('@').str[0]

descriptions = pd.read_sql_query("SELECT * FROM wa_group_descriptions", con1)
descriptions['jid'] = descriptions['jid'].str.split('@').str[0]

names = pd.read_sql_query("SELECT * from wa_vnames", con1)
names['jid'] = names['jid'].str.split('@').str[0]
con1.close()

usuarios['user'] = usuarios['user'].astype(str)
usuarios['user'] = usuarios['user'].str[3:]
usuarios['server'] = usuarios['server'].apply(lambda x: 'celular' if x.endswith('.net') else ('grupo' if x.endswith('.us') else 'otro'))

# Pre-procesamiento de msg
msg = msg.loc[:, ['chat_row_id', 'timestamp', 'received_timestamp', 'text_data', 'from_me']]
msg = msg.dropna(subset=['text_data'])  # Eliminar filas donde text_data es NaN
msg['timestamp'] = pd.to_datetime(msg['timestamp'], unit='ms')
msg['received_timestamp'] = pd.to_datetime(msg['received_timestamp'], unit='ms')

# Función para mapear chat_row_id a número de teléfono
def mapping(id):
    phone = chv.loc[chv['_id'] == id, 'raw_string_jid'].iloc[0]
    phone = phone.split('@')[0]
    return phone

def mapping2(id):
    phone2 = usuarios.loc[usuarios['_id'] == id, 'user'].iloc[0]
    return phone2

def mapping3(id):
    server = usuarios.loc[usuarios['_id'] == id, 'server'].iloc[0]
    return server

def mapping4(id):
    server = usuarios.loc[usuarios['_id'] == id, 'device'].iloc[0]
    return server

def mapping5(id):
    name = chv.loc[chv['_id'] == id, 'subject'].iloc[0]
    return name



msg['number'] = msg['chat_row_id'].apply(lambda x: mapping(x))
msg['number2'] = msg['chat_row_id'].apply(lambda x: mapping2(x))
msg = pd.merge(msg, contacts[['jid', 'status']], left_on='number2', right_on='jid', how='left').drop('jid', axis=1)
msg = pd.merge(msg, names[['jid', 'verified_name']], left_on='number2', right_on='jid', how='left').drop('jid', axis=1)
msg['server'] = msg['chat_row_id'].apply(lambda x: mapping3(x))
msg['device'] = msg['chat_row_id'].apply(lambda x: mapping4(x))
msg['group'] = msg['chat_row_id'].apply(lambda x: mapping5(x))
msg = pd.merge(msg, descriptions[['jid', 'description']], left_on='number', right_on='jid', how='left').drop('jid', axis=1)

# Reemplazando NaN por None para los campos enriquecidos
msg = msg.where(pd.notnull(msg), None)

def remove_emojis(text):
    # Verifica si el texto es None antes de procesarlo
    if text is None:
        return text  # O puedes devolver una cadena vacía si prefieres: return ''
    # Si no es None, procede a eliminar los emojis
    return emoji.replace_emoji(text, replace='')


# Asumiendo que msg es tu DataFrame y ya está definido
msg['text_data'] = msg['text_data'].apply(remove_emojis)
msg['description'] = msg['description'].apply(remove_emojis)
msg['group'] = msg['group'].apply(remove_emojis)
msg['timestamp'] = pd.to_datetime(msg['timestamp'], format='%m/%d/%Y %I:%M:%S %p')
msg['cliente'] = config['cliente']
msg['estado'] = config['estado']
msg['municipio'] = config['municipio']
msg['received_timestamp'] = pd.to_datetime(msg['received_timestamp'], format='%m/%d/%Y %I:%M:%S %p')

csv_file_path = 'messages_processed.csv'
msg.to_csv(csv_file_path, index=False)
# Define tus datos de conexión a MySQL
MYSQL_USER = "admin"
MYSQL_PASS = "F@c3b00k"
MYSQL_HOST = "158.69.26.160"
MYSQL_DB = "data_wa"

# Reabre la conexión a MySQL
mysql_con = mysql.connector.connect(
    host=MYSQL_HOST,
    user=MYSQL_USER,
    password=MYSQL_PASS,
    database=MYSQL_DB
)

# Cursor para ejecutar las consultas
cursor = mysql_con.cursor()

# Crear la tabla en MySQL si no existe
MYSQL_USER = "admin"
MYSQL_PASS = "F@c3b00k"
MYSQL_HOST = "158.69.26.160"
MYSQL_DB = "data_wa"

mysql_con = mysql.connector.connect(host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASS, database=MYSQL_DB)
cursor = mysql_con.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS extraccion4 (
    id INT AUTO_INCREMENT PRIMARY KEY,
    chat_row_id INT,
    timestamp DATETIME,
    received_timestamp DATETIME,
    text_data TEXT,
    from_me BOOLEAN,
    number VARCHAR(255),
    number2 VARCHAR(255),
    status VARCHAR(255),
    verified_name VARCHAR(255),
    server VARCHAR(255),
    device VARCHAR(255),
    group_name VARCHAR(255),          
    description TEXT,
    cliente VARCHAR(255),
    estado VARCHAR(255),
    municipio VARCHAR(255)
)
""")

# Preparar la consulta SQL para insertar los datos en MySQL
add_message = """
INSERT INTO extraccion4
(chat_row_id, timestamp, received_timestamp, text_data, from_me, number, number2, status, verified_name, server, device, group_name, description, cliente, estado, municipio) 
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
"""


msg['timestamp'] = msg['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
msg['received_timestamp'] = msg['received_timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')

# Preparar los datos para la inserción
data_to_insert = [
    (
        row['chat_row_id'],
        row['timestamp'],
        row['received_timestamp'],
        row['text_data'],
        row['from_me'],  # Convertido a booleano si es necesario
        row['number'],
        row['number2'],
        row['status'],
        row['verified_name'],
        row['server'],
        row['device'],
        row['group'],
        row['description'],
        row['cliente'],
        row['estado'],
        row['municipio']
    ) for index, row in msg.iterrows()
]   
cursor.executemany(add_message, data_to_insert)

# Hacer commit de la transacción
mysql_con.commit()

# Cerrar el cursor y la conexión
cursor.close()
mysql_con.close()

print("Tabla creada (si no existía) y datos subidos con éxito.")

