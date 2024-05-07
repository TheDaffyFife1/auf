#!/bin/sh

# Función para manejar errores
error_handler() {
    echo "Error: Ocurrió un problema al ejecutar el script."
    termux-wake-unlock
    exit 1
}

# Habilitar manejo de errores
set -e
trap 'error_handler' ERR

# Mantener el dispositivo despierto
termux-wake-lock

# Esperar 60 segundos antes de ejecutar los comandos
sleep 60

# Intentar ejecutar los scripts especificados
if [ -f /data/data/com.termux/files/home/extractor/sacar.sh ]; then
    sh /data/data/com.termux/files/home/extractor/sacar.sh
else
    echo "Advertencia: El archivo sacar.sh no fue encontrado."
fi

if [ -f /data/data/com.termux/files/home/extractor/extractor.py ]; then
    python /data/data/com.termux/files/home/extractor/extractor.py
else
    echo "Advertencia: El archivo extractor.py no fue encontrado."
fi

if [ -f /data/data/com.termux/files/home/extractor/extractor2.py ]; then
    python /data/data/com.termux/files/home/extractor/extractor2.py
else
    echo "Advertencia: El archivo extractor2.py no fue encontrado."
fi

# Liberar el bloqueo de wake-lock
termux-wake-unlock

# Iniciar crond (el daemon cron)
crond || { echo "Error: No se pudo iniciar crond"; exit 1; }

echo "El script se ha completado con éxito."
