# Instalación y Extracción para WhatsApp

Para hacer funcionar esta herramienta, utilizaremos Termux. Además, para la automatización, agregaremos Tasker y Termux:Tasker.

## Requisitos

1. [Descarga Termux desde F-Droid](https://f-droid.org/es/packages/com.termux/).
2. Instala Tasker y Termux:Tasker para la automatización.

## Configuración del Emulador

Sigue estos pasos para configurar el emulador y hacer que el código funcione automáticamente:

### Actualización de Paquetes

Abre Termux y ejecuta los siguientes comandos para actualizar los paquetes:

```sh
pkg update
pkg upgrade
pkg install git
pkg install tur-repo -y
pkg install python-pandas -y
pip install mysql-connector-python
pip install emoji
```
### Clonar el Repositorio
Clona el repositorio necesario ejecutando el siguiente comando:

```sh
git clone https://github.com/TheDaffyFife1/extractor.git
```

### Permisos para los Scripts
Otorga permisos de ejecución a los scripts necesarios:

```sh
chmod +x sacar.sh
chmod +x sacar2.sh
chmod +x main.sh
```

### Ejecución Automática del Código
Para ejecutar el código de manera automática, ejecuta el script principal:
```sh
./main.sh
```
**Este es solo para funcionar con Termux**
