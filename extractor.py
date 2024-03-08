import sqlite3
import pandas as pd
from datetime import datetime
import emoji
import mysql.connector

# Conexión a la base de datos msgstore.db y lectura de datos
con = sqlite3.connect('/sdcard/msgstore.db')
chv = pd.read_sql_query("SELECT * from chat_view", con)
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

# Pre-procesamiento de msg
msg = msg.loc[:, ['chat_row_id', 'timestamp', 'received_timestamp', 'text_data', 'from_me']]
msg = msg.dropna(subset=['text_data'])  # Eliminar filas donde text_data es NaN
msg['timestamp'] = pd.to_datetime(msg['timestamp'], unit='ms')
msg['received_timestamp'] = pd.to_datetime(msg['received_timestamp'], unit='ms')

# Función para mapear chat_row_id a número de teléfono
def mapping(id):
    phone = chv.loc[chv['_id'] == id, 'raw_string_jid'].iloc[0].split('@')[0]
    return phone

msg['number'] = msg['chat_row_id'].apply(mapping)

# Enriquecimiento de los datos de msg con los datos de contacts, names, y descriptions
msg = pd.merge(msg, contacts[['jid', 'status']], left_on='number', right_on='jid', how='left').drop('jid', axis=1)
msg = pd.merge(msg, names[['jid', 'verified_name']], left_on='number', right_on='jid', how='left').drop('jid', axis=1)
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
msg['timestamp'] = pd.to_datetime(msg['timestamp'], format='%m/%d/%Y %I:%M:%S %p')
msg['cliente'] = 'prueba'
msg['estado'] = 'jalisco'
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
cursor.execute("""
CREATE TABLE IF NOT EXISTS extraccion (
    id INT AUTO_INCREMENT PRIMARY KEY,
    chat_row_id INT,
    timestamp DATETIME,
    received_timestamp DATETIME,
    text_data TEXT,
    from_me BOOLEAN,
    number VARCHAR(255),
    status VARCHAR(255),
    verified_name VARCHAR(255),
    description TEXT,
    cliente VARCHAR(255),
    estado VARCHAR(255)
)
""")

# Preparar la consulta SQL para insertar los datos en MySQL
add_message = ("""
INSERT INTO extraccion 
(chat_row_id, timestamp, received_timestamp, text_data, from_me, number,status,verified_name,description, cliente, estado) 
VALUES (%s, %s, %s, %s,%s, %s, %s, %s, %s, %s, %s)
""")

# Insertar los datos fila por fila
for i, row in msg.iterrows():
    data_message = (row['chat_row_id'], row['timestamp'], row['received_timestamp'], row['text_data'], 
                    row['from_me'], row['number'],row['status'],row['verified_name'],row['description'], row['cliente'], row['estado'])
    cursor.execute(add_message, data_message)

# Hacer commit de la transacción
mysql_con.commit()

# Cerrar el cursor y la conexión
cursor.close()
mysql_con.close()

print("Tabla creada (si no existía) y datos subidos con éxito.")