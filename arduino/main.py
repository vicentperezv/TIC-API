import serial
import time
import logging
import asyncio
import pandas as pd
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# Configurar la conexión serial con Arduino
ser = serial.Serial('COM3', 9600, timeout=1)  # Cambia 'COM3' al puerto correcto si es necesario
time.sleep(2)  # Esperar un poco para que la conexión se establezca

# Configuración inicial de medición
tiempo_total = 5  # Tiempo total en minutos (valor inicial)
intervalo_medicion = 30  # Intervalo en segundos (valor inicial)
mediciones = []  # Lista para almacenar las mediciones
medidor_sonido_activo = False  # Estado del medidor de sonido

# Configurar logging para registrar solo INFO o superior
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Función para enviar comandos al Arduino
def enviar_comando_arduino(comando):
    comando_con_salto = comando + '\n'
    ser.write(comando_con_salto.encode('utf-8'))
    time.sleep(1)
    while ser.in_waiting > 0:
        respuesta = ser.readline().decode('utf-8').rstrip()
        return respuesta
    return "Comando enviado, esperando respuesta del Arduino..."

# Funciones para manejar los comandos de Telegram
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logging.info("Comando /start recibido")
    await mostrar_menu(update)

async def mostrar_menu(update: Update) -> None:
    keyboard = [
        [InlineKeyboardButton("Encender LED", callback_data='modo1')],
        [InlineKeyboardButton("Apagar LED", callback_data='modo2')],
        [InlineKeyboardButton("Medir Temperatura", callback_data='medir_temperatura')],
        [InlineKeyboardButton("Medir Sonido", callback_data='medir_sonido')],
        [InlineKeyboardButton("Encender LED RGB", callback_data='modo4')],
        [InlineKeyboardButton("Apagar LED RGB", callback_data='modo5')],
        [InlineKeyboardButton("Detener Bot", callback_data='detener')]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    if isinstance(update, Update) and update.callback_query:
        await update.callback_query.edit_message_text(
            text="Selecciona una opción:",
            reply_markup=reply_markup
        )
    else:
        await update.message.reply_text(
            "¡Hola! Soy tu bot para controlar el Arduino. Selecciona una opción:",
            reply_markup=reply_markup
        )

# Función para manejar las respuestas de los botones
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global tiempo_total, intervalo_medicion, medidor_sonido_activo

    query = update.callback_query
    await query.answer()

    if query.data == 'modo1':
        logging.info("Botón 'Encender LED' presionado")
        respuesta = enviar_comando_arduino("modo1")
        await query.edit_message_text(text=f"Encender LED: {respuesta}")
        await mostrar_menu(query)

    elif query.data == 'modo2':
        logging.info("Botón 'Apagar LED' presionado")
        respuesta = enviar_comando_arduino("modo2")
        await query.edit_message_text(text=f"Apagar LED: {respuesta}")
        await mostrar_menu(query)

    elif query.data == 'medir_temperatura':
        logging.info("Botón 'Medir Temperatura' presionado")
        # Mostrar opciones para medir la temperatura
        keyboard = [
            [InlineKeyboardButton("Medir al Instante", callback_data='medir_instantaneo')],
            [InlineKeyboardButton("Medir por Intervalo", callback_data='configurar_intervalo')],
            [InlineKeyboardButton("Volver al Menú", callback_data='volver_menu')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text="Selecciona cómo deseas medir la temperatura:", reply_markup=reply_markup)

    elif query.data == 'medir_instantaneo':
        logging.info("Botón 'Medir al Instante' presionado")
        respuesta = enviar_comando_arduino("modo3")
        await query.message.reply_text(text=f"Temperatura: {respuesta} *C")
        await mostrar_menu(query)

    elif query.data == 'configurar_intervalo':
        logging.info("Botón 'Configurar Intervalo de Medición' presionado")
        # Mostrar menú de configuración de tiempos
        await mostrar_configurar_tiempos(query)

    elif query.data == 'incrementar_tiempo':
        tiempo_total += 1
        await mostrar_configurar_tiempos(query)

    elif query.data == 'decrementar_tiempo':
        if tiempo_total > 1:
            tiempo_total -= 1
        await mostrar_configurar_tiempos(query)

    elif query.data == 'incrementar_intervalo':
        intervalo_medicion += 10
        await mostrar_configurar_tiempos(query)

    elif query.data == 'decrementar_intervalo':
        if intervalo_medicion > 10:
            intervalo_medicion -= 10
        await mostrar_configurar_tiempos(query)

    elif query.data == 'confirmar_intervalo':
        logging.info(f"Tiempo total: {tiempo_total} min, Intervalo: {intervalo_medicion} seg")
        await query.edit_message_text(text=f"Tiempo total configurado: {tiempo_total} min, Intervalo configurado: {intervalo_medicion} segundos")
        await realizar_medicion_por_intervalo(query)

    elif query.data == 'modo4':
        logging.info("Botón 'Encender LED RGB' presionado")
        respuesta = enviar_comando_arduino("modo4")
        await query.message.reply_text(text=f"Encender LED RGB: {respuesta}")
        await mostrar_menu(query)

    elif query.data == 'modo5':
        logging.info("Botón 'Apagar LED RGB' presionado")
        respuesta = enviar_comando_arduino("modo5")
        await query.message.reply_text(text=f"Apagar LED RGB: {respuesta}")
        await mostrar_menu(query)

    elif query.data == 'medir_sonido':
        logging.info("Botón 'Medir Sonido' presionado")
        # Mostrar opciones para medir el sonido
        keyboard = [
            [InlineKeyboardButton("Activar/Desactivar Medidor de Sonido", callback_data='activar_sonido')],
            [InlineKeyboardButton("Medir por Intervalo", callback_data='configurar_intervalo_sonido')],
            [InlineKeyboardButton("Volver al Menú", callback_data='volver_menu')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text="Selecciona cómo deseas medir el sonido:", reply_markup=reply_markup)

    elif query.data == 'activar_sonido':
        medidor_sonido_activo = not medidor_sonido_activo
        estado = "activado" if medidor_sonido_activo else "desactivado"
        logging.info(f"Medidor de sonido {estado}")
        respuesta = enviar_comando_arduino("modo6" if medidor_sonido_activo else "modo7")
        await query.message.reply_text(text=f"Medidor de sonido {estado}: {respuesta}")
        await mostrar_menu(query)

    elif query.data == 'configurar_intervalo_sonido':
        logging.info("Botón 'Configurar Intervalo de Medición de Sonido' presionado")
        # Mostrar menú de configuración de tiempos para el sonido
        await mostrar_configurar_tiempos(query, sonido=True)

    elif query.data == 'detener':
        logging.info("Botón 'Detener Bot' presionado")
        await query.edit_message_text(text="Deteniendo el bot. ¡Hasta luego!")
        await asyncio.sleep(1)
        await context.application.stop()
        return

    elif query.data == 'volver_menu':
        await mostrar_menu(query)

async def mostrar_configurar_tiempos(query, sonido=False):
    global tiempo_total, intervalo_medicion

    # Mostrar menú para ajustar tiempo total e intervalo
    keyboard = [
        [InlineKeyboardButton(f"Tiempo Total: {tiempo_total} min", callback_data='none')],
        [InlineKeyboardButton("+1 min", callback_data='incrementar_tiempo'), InlineKeyboardButton("-1 min", callback_data='decrementar_tiempo')],
        [InlineKeyboardButton(f"Intervalo: {intervalo_medicion} seg", callback_data='none')],
        [InlineKeyboardButton("+10 seg", callback_data='incrementar_intervalo'), InlineKeyboardButton("-10 seg", callback_data='decrementar_intervalo')],
        [InlineKeyboardButton("Confirmar y Comenzar Medición", callback_data='confirmar_intervalo_sonido' if sonido else 'confirmar_intervalo')],
        [InlineKeyboardButton("Volver al Menú", callback_data='volver_menu')]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text="Configura el tiempo total y el intervalo de medición:", reply_markup=reply_markup)

# Función para realizar la medición por intervalos
async def realizar_medicion_por_intervalo(query):
    global tiempo_total, intervalo_medicion, mediciones

    if tiempo_total == 0 or intervalo_medicion == 0:
        await query.message.reply_text(text="Por favor configura primero el tiempo total y el intervalo de medición.")
        return

    total_iteraciones = (tiempo_total * 60) // intervalo_medicion
    suma_temperaturas = 0.0
    iteraciones_validas = 0
    mediciones = []  # Limpiar las mediciones previas
    tiempo_inicio = datetime.now()

    for i in range(total_iteraciones):
        respuesta = enviar_comando_arduino("modo3")
        tiempo_actual = datetime.now()
        tiempo_transcurrido = str(timedelta(seconds=(i + 1) * intervalo_medicion))
        hora_actual = tiempo_actual.strftime("%H:%M:%S")

        try:
            temperatura = float(respuesta)
            suma_temperaturas += temperatura
            iteraciones_validas += 1
            mediciones.append({
                'Medición N°': iteraciones_validas,
                'Temperatura (°C)': temperatura,
                'Tiempo Transcurrido': tiempo_transcurrido,
                'Hora de Medición': hora_actual
            })
            await query.message.reply_text(text=f"Medición {iteraciones_validas}: Temperatura = {temperatura:.2f} *C, Tiempo Transcurrido = {tiempo_transcurrido}, Hora de Medición = {hora_actual}")
        except ValueError:
            await query.message.reply_text(text=f"Error al leer la temperatura en la iteración {i + 1}")

        await asyncio.sleep(intervalo_medicion)

    if iteraciones_validas > 0:
        promedio = suma_temperaturas / iteraciones_validas
        await query.message.reply_text(text=f"Mediciones completadas. Promedio de temperatura: {promedio:.2f} *C")
        await generar_excel(query, promedio)
    else:
        await query.message.reply_text(text="No se pudieron obtener mediciones válidas.")
    
    await mostrar_menu(query)

# Función para generar y enviar el archivo Excel con las mediciones
async def generar_excel(query, promedio):
    global mediciones

    # Crear un DataFrame con las mediciones y el promedio
    df = pd.DataFrame(mediciones)
    df.loc[len(df.index)] = ['Promedio', promedio, '', '']  # Añadir el promedio al final

    # Guardar el DataFrame como un archivo Excel
    nombre_archivo = 'mediciones_temperatura.xlsx'
    df.to_excel(nombre_archivo, index=False)

    # Enviar el archivo Excel al usuario de Telegram
    with open(nombre_archivo, 'rb') as f:
        await query.message.reply_document(document=f, filename=nombre_archivo)

async def main() -> None:
    TOKEN = "7895502311:AAEY1Db6DfdL32ONFDEiRNjE5WQgQjPpVbE"
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))

    logging.info("Iniciando bot en modo polling")
    await application.initialize()
    await application.start()

    try:
        print("Bot iniciado. Presiona Ctrl+C para detenerlo manualmente o utiliza 'Detener Bot' en Telegram.")
        await application.updater.start_polling()
        await asyncio.Future()  
    except (KeyboardInterrupt, SystemExit):
        print("\nFinalizando el bot...")

    await application.stop()
    await application.shutdown()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Finalizando...")
    finally:
        ser.close()
