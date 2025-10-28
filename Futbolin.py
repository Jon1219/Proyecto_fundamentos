import tkinter as tk
from PIL import Image, ImageTk
import pygame
from functools import partial
import random
import os
import json
from tkinter import messagebox
import threading
import socket
import json
from datetime import datetime

######################################################
# CLASE CLIENTE PARA COMUNICACIÓN CON RASPBERRY PI
# Maneja toda la comunicación por sockets con la Raspberry
######################################################

class ClienteRaspberry:
    def __init__(self, host='10.238.236.35', port=5000):
        """Inicializa el cliente con configuración de conexión"""
        self.host = host
        self.port = port
        self.socket = None
        self.conectado = False
        self.equipos_seleccionados = []
        self.seleccion_final = {}
        self.reconectar_automatico = True

######################################################
# CONECTAR CON RASPBERRY PI
# Establece conexión con Raspberry Pi en hilo separado
######################################################
        
    def conectar_raspberry(self):
        if self.conectado:
            return
            
        def conectar_loop():
            try:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.settimeout(5)
                print(f"🔗 Conectando a Raspberry en {self.host}:{self.port}...")
                self.socket.connect((self.host, self.port))
                self.socket.settimeout(1.0)
                self.conectado = True
                print("✅ Conectado a Raspberry Pi")
                self.recibir_mensajes()
            except Exception as e:
                print(f"❌ Error conectando a Raspberry: {e}")
                self.conectado = False
                if self.reconectar_automatico:
                    print("🔄 Reintentando conexión en 5 segundos...")
                    ventana.after(5000, self.conectar_raspberry)
        
        thread = threading.Thread(target=conectar_loop, daemon=True)
        thread.start()

######################################################
# RECIBIR MENSAJES DE RASPBERRY
# Escucha mensajes entrantes de la Raspberry en hilo separado
######################################################
    
    def recibir_mensajes(self):
        def recibir_loop():
            while self.conectado:
                try:
                    datos = self.socket.recv(1024)
                    if not datos:
                        print("🔌 Conexión cerrada por Raspberry")
                        self.conectado = False
                        break
                    
                    mensajes = datos.decode().strip().split('\n')
                    for mensaje_str in mensajes:
                        if mensaje_str:
                            try:
                                mensaje = json.loads(mensaje_str)
                                ventana.after(0, lambda: self.procesar_mensaje(mensaje))
                            except json.JSONDecodeError:
                                print(f"❌ Mensaje JSON inválido: {mensaje_str}")
                except socket.timeout:
                    continue
                except Exception as e:
                    print(f"❌ Error recibiendo mensajes: {e}")
                    self.conectado = False
                    break
            
            if self.reconectar_automatico:
                print("🔄 Intentando reconexión...")
                ventana.after(2000, self.conectar_raspberry)
        
        thread = threading.Thread(target=recibir_loop, daemon=True)
        thread.start()

######################################################
# PROCESAR MENSAJES RECIBIDOS
# Procesa los diferentes tipos de mensajes recibidos de Raspberry
######################################################
    
    def procesar_mensaje(self, mensaje):
        tipo = mensaje.get("tipo")
        datos = mensaje.get("datos", {})
        
        print(f"📥 Mensaje de Raspberry: {tipo}")
        
        if tipo == "EQUIPO_SELECCIONADO":
            equipo = datos.get("equipo")
            print(f"🏆 Equipo seleccionado en Raspberry: {equipo}")
            
        elif tipo == "JUGADOR_SELECCIONADO":
            jugador = datos.get("jugador")
            tipo_jugador = datos.get("tipo")
            print(f"👤 {tipo_jugador.title()} seleccionado: {jugador}")
            
        elif tipo == "EQUIPO_CONFIRMADO":
            equipo = datos.get("equipo")
            tipo_equipo = datos.get("tipo")
            print(f"✅ {tipo_equipo.title()} confirmado: {equipo}")
            
        elif tipo == "JUGADOR_CONFIRMADO":
            jugador = datos.get("jugador")
            tipo_jugador = datos.get("tipo")
            equipo = datos.get("equipo")
            print(f"✅ {tipo_jugador.title()} {equipo} confirmado: {jugador}")
            
        elif tipo == "CONFIGURACION_COMPLETADA":
            print("🎯 Configuración completada en Raspberry")
            self.equipos_seleccionados = [
                datos.get("equipo_local"), 
                datos.get("equipo_visitante")
            ]
            self.seleccion_final = {
                datos.get("equipo_local"): {
                    "portero": datos.get("portero_local"),
                    "jugador": datos.get("tirador_local")
                },
                datos.get("equipo_visitante"): {
                    "portero": datos.get("portero_visitante"), 
                    "jugador": datos.get("tirador_visitante")
                }
            }
            self.mostrar_configuracion_raspberry()
            
        elif tipo == "PARTIDA_INICIADA":
            print("🎮 Partida iniciada desde Raspberry")
            
        elif tipo == "TIRO_INICIADO":
            equipo = datos.get("equipo")
            tirador = datos.get("tirador")
            print(f"🎯 Tiro iniciado: {tirador} de {equipo}")
            
        elif tipo == "GOL":
            equipo = datos.get("equipo")
            tirador = datos.get("tirador")
            print(f"🎉 ¡GOL de {tirador} del equipo {equipo}!")
            
        elif tipo == "ATAJADA":
            equipo = datos.get("equipo")
            tirador = datos.get("tirador")
            print(f"🧤 ¡ATAJADA al tiro de {tirador} del equipo {equipo}!")
            
        elif tipo == "MARCADOR_ACTUALIZADO":
            goles_local = datos.get("goles_local")
            goles_visitante = datos.get("goles_visitante")
            print(f"📊 Marcador actualizado: {goles_local} - {goles_visitante}")
            
        elif tipo == "PARTIDA_FINALIZADA":
            goles_local = datos.get("goles_local")
            goles_visitante = datos.get("goles_visitante")
            ganador = datos.get("ganador")
            print(f"🏁 Partida finalizada: {goles_local} - {goles_visitante}")
            print(f"🎊 Ganador: {ganador}")

######################################################
# MOSTRAR CONFIGURACIÓN DE RASPBERRY
# Muestra la configuración recibida de Raspberry en consola
######################################################
    
    def mostrar_configuracion_raspberry(self):
        if self.equipos_seleccionados and self.seleccion_final:
            print("\n" + "="*50)
            print("CONFIGURACIÓN RECIBIDA DE RASPBERRY:")
            print(f"LOCAL: {self.equipos_seleccionados[0]}")
            print(f"  Portero: {self.seleccion_final[self.equipos_seleccionados[0]]['portero']}")
            print(f"  Tirador: {self.seleccion_final[self.equipos_seleccionados[0]]['jugador']}")
            print(f"VISITANTE: {self.equipos_seleccionados[1]}")
            print(f"  Portero: {self.seleccion_final[self.equipos_seleccionados[1]]['portero']}")
            print(f"  Tirador: {self.seleccion_final[self.equipos_seleccionados[1]]['jugador']}")
            print("="*50)
            self.preguntar_inicio_juego()

######################################################
# PREGUNTAR INICIO DE JUEGO
# Pregunta al usuario si quiere iniciar el juego con configuración de Raspberry
######################################################
    
    def preguntar_inicio_juego(self):
        try:
            respuesta = messagebox.askyesno(
                "Configuración Recibida", 
                f"¿Deseas iniciar el juego con esta configuración?\n\n"
                f"LOCAL: {self.equipos_seleccionados[0]}\n"
                f"VISITANTE: {self.equipos_seleccionados[1]}\n\n"
                f"Portero Local: {self.seleccion_final[self.equipos_seleccionados[0]]['portero']}\n"
                f"Tirador Local: {self.seleccion_final[self.equipos_seleccionados[0]]['jugador']}\n"
                f"Portero Visitante: {self.seleccion_final[self.equipos_seleccionados[1]]['portero']}\n"
                f"Tirador Visitante: {self.seleccion_final[self.equipos_seleccionados[1]]['jugador']}"
            )
            
            if respuesta:
                self.iniciar_juego_desde_raspberry()
        except Exception as e:
            print(f"❌ Error mostrando messagebox: {e}")
            print("🔄 Iniciando juego automáticamente en 3 segundos...")
            ventana.after(3000, self.iniciar_juego_desde_raspberry)

######################################################
# INICIAR JUEGO DESDE RASPBERRY
# Inicia el juego con la configuración de la Raspberry
######################################################
    
    def iniciar_juego_desde_raspberry(self):
        if self.equipos_seleccionados and self.seleccion_final:
            print("🚀 Iniciando juego con configuración de Raspberry...")
            for widget in ventana.winfo_children():
                if isinstance(widget, tk.Toplevel):
                    try:
                        widget.destroy()
                    except:
                        pass
            ventana.after(500, lambda: iniciar_penales(self.equipos_seleccionados, self.seleccion_final))

######################################################
# ENVIAR MENSAJE A RASPBERRY
# Envía mensajes a la Raspberry Pi
######################################################
    
    def enviar_mensaje(self, tipo, datos):
        if self.conectado and self.socket:
            try:
                mensaje = {
                    "tipo": tipo,
                    "datos": datos,
                    "timestamp": datetime.now().isoformat()
                }
                mensaje_json = json.dumps(mensaje) + "\n"
                self.socket.send(mensaje_json.encode())
                print(f"📤 Enviado a Raspberry: {tipo}")
                return True
            except Exception as e:
                print(f"❌ Error enviando mensaje a Raspberry: {e}")
                self.conectado = False
        return False

######################################################
# REINICIAR JUEGO
# Envía comando de reinicio a la Raspberry
######################################################
    
    def reiniciar_juego(self):
        self.enviar_mensaje("REINICIAR", {})
        print("🔄 Comando de reinicio enviado a Raspberry")

######################################################
# DESCONECTAR DE RASPBERRY
# Cierra la conexión con la Raspberry Pi
######################################################
    
    def desconectar(self):
        self.reconectar_automatico = False
        self.conectado = False
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        print("🔌 Desconectado de Raspberry")

# Crear instancia global del cliente
cliente_raspberry = ClienteRaspberry()

######################################################
# INICIALIZAR SONIDOS Y MÚSICA
# Configura la música de fondo y efectos de sonido
######################################################

try:
    pygame.mixer.init()
    pygame.mixer.music.load("musica_fondo.mp3")
    pygame.mixer.music.play(-1)
    
    sonido_silbato = pygame.mixer.Sound("silbato.mp3")
    sonido_gol = pygame.mixer.Sound("gol.mp3")
    sonido_cagon = pygame.mixer.Sound("cagon.mp3")
except Exception as e:
    print("Error al cargar sonidos:", e)
    class DummySound:
        def play(self): pass
    sonido_silbato = DummySound()
    sonido_gol = DummySound()
    sonido_cagon = DummySound()

######################################################
# CREAR VENTANA PRINCIPAL
# Configura la ventana principal de la aplicación
######################################################

ventana = tk.Tk()
ventana.title("Menú principal - Champions Game")
ventana.state("zoomed")
ventana.update()
ancho = ventana.winfo_width()
alto = ventana.winfo_height()

######################################################
# VARIABLES GLOBALES
# Define variables globales del sistema
######################################################

modalidad_juego = "automática"
HISTORIAL_FILE = "historial_partidos.json"
GOLEADORES_FILE = "ranking_goleadores.json"

######################################################
# CARGAR HISTORIAL DE PARTIDOS
# Carga el historial de partidos desde archivo JSON
######################################################

def cargar_historial():
    try:
        with open(HISTORIAL_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"partidos": [], "ultimo_id": 0}

######################################################
# GUARDAR HISTORIAL DE PARTIDOS
# Guarda el historial en archivo JSON
######################################################

def guardar_historial(historial):
    try:
        with open(HISTORIAL_FILE, 'w', encoding='utf-8') as f:
            json.dump(historial, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print("Error guardando historial:", e)

######################################################
# CARGAR RANKING DE GOLEADORES
# Carga el ranking de goleadores desde archivo JSON
######################################################

def cargar_goleadores():
    try:
        with open(GOLEADORES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"goleadores": []}

######################################################
# GUARDAR RANKING DE GOLEADORES
# Guarda el ranking de goleadores en archivo JSON
######################################################

def guardar_goleadores(goleadores):
    try:
        with open(GOLEADORES_FILE, 'w', encoding='utf-8') as f:
            json.dump(goleadores, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print("Error guardando goleadores:", e)

######################################################
# ACTUALIZAR RANKING DE GOLEADORES
# Actualiza el ranking con nuevos goles de jugadores
######################################################

def actualizar_goleadores(jugador, equipo, goles):
    goleadores_data = cargar_goleadores()
    
    encontrado = False
    for goleador in goleadores_data["goleadores"]:
        if goleador["jugador"] == jugador and goleador["equipo"] == equipo:
            goleador["goles"] += goles
            encontrado = True
            break
    
    if not encontrado:
        goleadores_data["goleadores"].append({
            "jugador": jugador,
            "equipo": equipo,
            "goles": goles
        })
    
    goleadores_data["goleadores"].sort(key=lambda x: x["goles"], reverse=True)
    
    if len(goleadores_data["goleadores"]) > 3:
        goleadores_data["goleadores"] = goleadores_data["goleadores"][:3]
    
    guardar_goleadores(goleadores_data)

######################################################
# REGISTRAR PARTIDO EN HISTORIAL
# Guarda un nuevo partido en el historial y actualiza goleadores
######################################################

def registrar_partido(equipo_local, equipo_visitante, goles_local, goles_visitante, 
                     jugador_local, jugador_visitante, modalidad):
    historial = cargar_historial()
    
    nuevo_partido = {
        "id": historial["ultimo_id"] + 1,
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "equipo_local": equipo_local,
        "equipo_visitante": equipo_visitante,
        "goles_local": goles_local,
        "goles_visitante": goles_visitante,
        "jugador_local": jugador_local,
        "jugador_visitante": jugador_visitante,
        "modalidad": modalidad,
        "ganador": equipo_local if goles_local > goles_visitante else equipo_visitante if goles_visitante > goles_local else "Empate"
    }
    
    historial["partidos"].insert(0, nuevo_partido)
    
    if len(historial["partidos"]) > 3:
        historial["partidos"] = historial["partidos"][:3]
    
    historial["ultimo_id"] += 1
    guardar_historial(historial)
    
    actualizar_goleadores(jugador_local, equipo_local, goles_local)
    actualizar_goleadores(jugador_visitante, equipo_visitante, goles_visitante)

######################################################
# ABRIR VENTANA DE HISTORIAL
# Muestra el historial de partidos y ranking de goleadores
######################################################

def abrir_historial():
    ventana.withdraw()
    historial_window = tk.Toplevel()
    historial_window.title("Historial de Partidos - Top Goleadores")
    historial_window.state("zoomed")
    historial_window.update()
    ancho_h = historial_window.winfo_width()
    alto_h = historial_window.winfo_height()

    try:
        fondo_img = Image.open("Champions.png").resize((ancho_h, alto_h), Image.Resampling.LANCZOS)
        fondo = ImageTk.PhotoImage(fondo_img)
    except Exception as e:
        print("Error cargando fondo en historial:", e)
        fondo = None

    canvas_h = tk.Canvas(historial_window, width=ancho_h, height=alto_h)
    canvas_h.pack(fill="both", expand=True)
    if fondo:
        canvas_h.create_image(0, 0, image=fondo, anchor="nw")
        canvas_h.fondo = fondo
    else:
        canvas_h.create_rectangle(0, 0, ancho_h, alto_h, fill="black")

    canvas_h.create_text(ancho_h//2, 80, text="HISTORIAL Y ESTADÍSTICAS", 
                        fill="gold", font=("Algerian", 40, "bold"))

    historial = cargar_historial()
    goleadores = cargar_goleadores()

    canvas_h.create_text(ancho_h//2, 150, text="ÚLTIMOS 3 PARTIDOS", 
                        fill="cyan", font=("Arial", 28, "bold"))

    y_pos = 220
    if historial["partidos"]:
        for partido in historial["partidos"]:
            resultado_text = f"{partido['fecha']}\n"
            resultado_text += f"{partido['equipo_local']} {partido['goles_local']} - {partido['goles_visitante']} {partido['equipo_visitante']}\n"
            resultado_text += f"Ganador: {partido['ganador']} | Modalidad: {partido['modalidad']}\n"
            resultado_text += f"Jugadores: {partido['jugador_local']} vs {partido['jugador_visitante']}"
            
            canvas_h.create_text(ancho_h//2, y_pos, text=resultado_text,
                               fill="white", font=("Arial", 14, "bold"), justify="center")
            y_pos += 120
    else:
        canvas_h.create_text(ancho_h//2, y_pos, text="No hay partidos registrados",
                           fill="white", font=("Arial", 16, "bold"))

    canvas_h.create_text(ancho_h//2, y_pos + 50, text="TOP 3 GOLEADORES", 
                        fill="lime", font=("Arial", 28, "bold"))

    y_pos_goleadores = y_pos + 100
    if goleadores["goleadores"]:
        for i, goleador in enumerate(goleadores["goleadores"]):
            goleador_text = f"{i+1}. {goleador['jugador']} ({goleador['equipo']}) - {goleador['goles']} goles"
            color = "gold" if i == 0 else "silver" if i == 1 else "orange" if i == 2 else "white"
            
            canvas_h.create_text(ancho_h//2, y_pos_goleadores, text=goleador_text,
                               fill=color, font=("Arial", 18, "bold"))
            y_pos_goleadores += 40
    else:
        canvas_h.create_text(ancho_h//2, y_pos_goleadores, text="No hay datos de goleadores",
                           fill="white", font=("Arial", 16, "bold"))

    boton_exit_h = tk.Button(historial_window, text="EXIT", command=historial_window.destroy,
                            fg="black", bg="red", font=("Arial", 14, "bold"), width=8)
    canvas_h.create_window(ancho_h - 50, 40, window=boton_exit_h, anchor="ne")

######################################################
# ABRIR CONFIGURACIÓN DE JUEGO
# Permite seleccionar modalidad de juego (automática o manual)
######################################################

def abrir_configuracion():
    global modalidad_juego
    ventana.withdraw()
    
    config = tk.Toplevel()
    config.title("Configuración del Juego - CEFoot v4.1")
    config.state("zoomed")
    config.update()
    ancho_c = config.winfo_width()
    alto_c = config.winfo_height()

    try:
        fondo_img = Image.open("Champions.png").resize((ancho_c, alto_c), Image.Resampling.LANCZOS)
        fondo = ImageTk.PhotoImage(fondo_img)
    except Exception as e:
        print("Error cargando fondo en configuración:", e)
        fondo = None

    canvas_c = tk.Canvas(config, width=ancho_c, height=alto_c)
    canvas_c.pack(fill="both", expand=True)
    if fondo:
        canvas_c.create_image(0, 0, image=fondo, anchor="nw")
        canvas_c.fondo = fondo
    else:
        canvas_c.create_rectangle(0, 0, ancho_c, alto_c, fill="black")

    canvas_c.create_text(ancho_c//2, 100, text="CONFIGURACIÓN DEL JUEGO", 
                        fill="white", font=("Algerian", 40, "bold"))
    
    canvas_c.create_text(ancho_c//2, 180, text="Selecciona la modalidad de juego:", 
                        fill="yellow", font=("Arial", 24, "bold"))

    var_modalidad = tk.StringVar(value=modalidad_juego)

    rb_auto = tk.Radiobutton(config, text="AUTOMÁTICO", variable=var_modalidad, 
                            value="automática", font=("Arial", 20, "bold"),
                            bg="lightgreen", fg="black", selectcolor="green")
    rb_auto.place(relx=0.5, rely=0.35, anchor="center")

    rb_manual = tk.Radiobutton(config, text="MANUAL", variable=var_modalidad, 
                              value="manual", font=("Arial", 20, "bold"),
                              bg="lightcoral", fg="black", selectcolor="red")
    rb_manual.place(relx=0.5, rely=0.45, anchor="center")

    desc_auto = "• Cambio automático después de 5 segundos\n• Ideal para juego fluido"
    desc_manual = "• Cambio manual con botón físico\n• Mayor control del jugador"

    canvas_c.create_text(ancho_c//2, 320, text=desc_auto, 
                        fill="lightgreen", font=("Arial", 16), justify="center")
    canvas_c.create_text(ancho_c//2, 400, text=desc_manual, 
                        fill="lightcoral", font=("Arial", 16), justify="center")

    def confirmar_configuracion():
        global modalidad_juego
        modalidad_juego = var_modalidad.get()
        print(f"Modalidad seleccionada: {modalidad_juego}")
        
        try:
            config.destroy()
        except:
            pass
        
        abrir_seleccion_equipos()

    boton_confirmar = tk.Button(config, text="CONFIRMAR", bg="gold", fg="black",
                               font=("Algerian", 22, "bold"), width=15, height=2,
                               command=confirmar_configuracion)
    boton_confirmar.place(relx=0.5, rely=0.7, anchor="center")

    boton_exit_c = tk.Button(config, text="EXIT", command=salir, 
                            fg="black", bg="red", font=("Arial", 14, "bold"), width=8)
    canvas_c.create_window(ancho_c - 50, 40, window=boton_exit_c, anchor="ne")

######################################################
# FUNCIÓN PARA SALIR DEL JUEGO
# Detiene música y cierra la aplicación
######################################################

def salir():
    try:
        pygame.mixer.music.stop()
        pygame.mixer.quit()
    except:
        pass
    try:
        ventana.destroy()
    except:
        pass

######################################################
# ABRIR VENTANA ABOUT US
# Muestra información sobre los desarrolladores
######################################################

def abrir_about_us():
    ventana.withdraw()
    about = tk.Toplevel()
    about.title("About Us - Champions Game")
    about.state("zoomed")
    about.update()
    ancho_a = about.winfo_width()
    alto_a = about.winfo_height()

    try:
        fondo_img = Image.open("Champions.png").resize((ancho_a, alto_a), Image.Resampling.LANCZOS)
        fondo = ImageTk.PhotoImage(fondo_img)
    except Exception as e:
        print("Error cargando Champions.jpg:", e)
        fondo = None

    canvas_a = tk.Canvas(about, width=ancho_a, height=alto_a)
    canvas_a.pack(fill="both", expand=True)
    if fondo:
        canvas_a.create_image(0, 0, image=fondo, anchor="nw")
        canvas_a.fondo = fondo
    else:
        canvas_a.create_rectangle(0, 0, ancho_a, alto_a, fill="black")

    try:
        jon_img = Image.open("Jon.jpg").resize((250, 300), Image.Resampling.LANCZOS)
        jon = ImageTk.PhotoImage(jon_img)
        canvas_a.create_image(ancho_a * 0.3, alto_a * 0.4, image=jon)
        canvas_a.jon = jon
    except Exception as e:
        print("Error cargando Jon.jpg:", e)

    texto_jon = (
        "Jonathan Luna Oviedo\n"
        "Carné: 2025090024\n"
        "Curso: Fundamentos de sistemas computacionales\n"
        "Profesor: Luis Alonso Barboza Artavia\n"
        "Grupo: 2\n"
        "Carrera: Ing. en Computadores\n"
        "Función: Encargado de realizar la maqueta, circuito y hardware"
    )
    canvas_a.create_text(ancho_a * 0.3, alto_a * 0.75, text=texto_jon,
                         fill="gold", font=("Arial", 14, "bold"), justify="center")

    try:
        johan_img = Image.open("Johan.jpg").resize((250, 300), Image.Resampling.LANCZOS)
        johan = ImageTk.PhotoImage(johan_img)
        canvas_a.create_image(ancho_a * 0.7, alto_a * 0.4, image=johan)
        canvas_a.johan = johan
    except Exception as e:
        print("Error cargando Johan.jpg:", e)

    texto_johan = (
        "Johan Molina Vaglio\n"
        "Carné: 2025094364\n"
        "Curso: Fundamentos de sistemas computacionales\n"
        "Profesor: Luis Alonso Barboza Artavia\n"
        "Grupo: 2\n"
        "Carrera: Ing. en Computadores\n"
        "Función: Encargado de la GUI, animaciones y experiencia visual"
    )
    canvas_a.create_text(ancho_a * 0.7, alto_a * 0.75, text=texto_johan,
                         fill="gold", font=("Arial", 14, "bold"), justify="center")
    canvas_a.create_text(ancho_a / 2, alto_a * 0.9, text="Versión: V1.0",
                         fill="white", font=("Arial", 16, "bold"), justify="center")

    boton_exit_a = tk.Button(about, text="EXIT", command=about.destroy,
                             fg="black", bg="red", font=("Arial", 14, "bold"), width=8)
    canvas_a.create_window(ancho_a - 50, 40, window=boton_exit_a, anchor="ne")

######################################################
# INICIAR FASE DE PENALES
# Configura y ejecuta la tanda de penales entre dos equipos
######################################################

def iniciar_penales(equipos_seleccionados, seleccion_final):
    global modalidad_juego
    
    try:
        pygame.mixer.music.pause()
    except:
        pass
    
    ventana_penales = tk.Toplevel()
    ventana_penales.title(f"Tanda de penales - Modalidad: {modalidad_juego}")
    ventana_penales.state("zoomed")
    ventana_penales.update()
    ancho_p = ventana_penales.winfo_width()
    alto_p = ventana_penales.winfo_height()

    local, visitante = equipos_seleccionados
    goles = {local: 0, visitante: 0}
    tiros = {local: 0, visitante: 0}
    turno = [local]
    total_tiros = 0
    posiciones_bloqueadas = []
    botones = []
    botones_widgets = []
    
    try:
        fondo_img = Image.open("cancha.png").resize((ancho_p, alto_p), Image.Resampling.LANCZOS)
        fondo = ImageTk.PhotoImage(fondo_img)
    except Exception as e:
        print("Error cargando cancha.png:", e)
        fondo = None

    canvas_p = tk.Canvas(ventana_penales, width=ancho_p, height=alto_p)
    canvas_p.pack(fill="both", expand=True)
    if fondo:
        canvas_p.create_image(0, 0, image=fondo, anchor="nw")
        canvas_p.fondo = fondo
    else:
        canvas_p.create_rectangle(0,0,ancho_p,alto_p,fill="darkgreen")

    imagenes = {}
    for equipo in equipos_seleccionados:
        imagenes[equipo] = {"portero": None, "jugador": None}
        try:
            portero_img_file = Image.open(f"{seleccion_final[equipo]['portero']}.png").resize((180,180), Image.Resampling.LANCZOS)
            jugador_img_file = Image.open(f"{seleccion_final[equipo]['jugador']}.png").resize((180,180), Image.Resampling.LANCZOS)
            imagenes[equipo]["portero"] = ImageTk.PhotoImage(portero_img_file)
            imagenes[equipo]["jugador"] = ImageTk.PhotoImage(jugador_img_file)
        except Exception as e:
            print(f"Error cargando imagen de {equipo}:", e)

    texto_turno = canvas_p.create_text(ancho_p//2, 80, text=f"Turno: {local}",
                                       fill="white", font=("Algerian", 36, "bold"))
    texto_marcador = canvas_p.create_text(ancho_p//2, 150,
                                          text=f"{local}: 0   -   {visitante}: 0",
                                          fill="yellow", font=("Arial", 28, "bold"))
    texto_modalidad = canvas_p.create_text(ancho_p//2, 200, 
                                         text=f"Modalidad: {modalidad_juego.upper()}",
                                         fill="cyan", font=("Arial", 20, "bold"))

    texto_indice_portero = canvas_p.create_text(ancho_p//2, 230, 
                                              text="",
                                              fill="orange", font=("Arial", 16, "bold"))

    x_portero_inicial = ancho_p * 0.25
    x_jugador_inicial = ancho_p * 0.75
    y_personajes = alto_p * 0.6

    img_port = imagenes[visitante]["portero"] if imagenes[visitante]["portero"] else None
    img_jug = imagenes[local]["jugador"] if imagenes[local]["jugador"] else None
    portero_img = canvas_p.create_image(x_portero_inicial, y_personajes, image=img_port)
    jugador_img = canvas_p.create_image(x_jugador_inicial, y_personajes, image=img_jug)

    boton_regresar = None

######################################################
# REGRESAR AL MENÚ PRINCIPAL
# Cierra ventana de penales y vuelve al menú principal
######################################################

    def regresar_menu_principal():
        try:
            try:
                pygame.mixer.music.unpause()
            except:
                pass
            
            ventana_penales.destroy()
            
            for widget in ventana.winfo_children():
                if isinstance(widget, tk.Toplevel):
                    try:
                        widget.destroy()
                    except:
                        pass
            
            ventana.deiconify()
        except Exception as e:
            print("Error al regresar al menú:", e)

######################################################
# CREAR BOTÓN DE REGRESAR
# Crea el botón para volver al menú principal
######################################################

    def crear_boton_regresar():
        nonlocal boton_regresar
        if boton_regresar is None:
            boton_regresar = tk.Button(ventana_penales, text="REGRESAR AL MENÚ PRINCIPAL", 
                                     bg="gold", fg="black", font=("Arial", 16, "bold"),
                                     width=25, height=2, command=regresar_menu_principal)
            
            canvas_p.create_window(ancho_p//2, alto_p//2 + 150, window=boton_regresar)

######################################################
# CAMBIAR TURNO DE EQUIPO
# Alterna entre equipo local y visitante
######################################################

    def cambiar_turno():
        nonlocal turno
        turno[0] = visitante if turno[0] == local else local
        canvas_p.itemconfig(texto_turno, text=f"Turno: {turno[0]}")
        
        equipo_portero = visitante if turno[0] == local else local
        equipo_jugador = turno[0]
        
        if imagenes[equipo_portero]["portero"]:
            canvas_p.itemconfig(portero_img, image=imagenes[equipo_portero]["portero"])
        if imagenes[equipo_jugador]["jugador"]:
            canvas_p.itemconfig(jugador_img, image=imagenes[equipo_jugador]["jugador"])
        
        try:
            sonido_silbato.play()
        except:
            pass

######################################################
# TERMINAR PARTIDA
# Finaliza el juego y muestra resultados
######################################################

    def terminar():
        nonlocal goles
        ganador = None
        if goles[local] > goles[visitante]:
            ganador = local
        elif goles[visitante] > goles[local]:
            ganador = visitante

        mensaje = f"Marcador final:\n{local}: {goles[local]} - {visitante}: {goles[visitante]}"
        if ganador:
            mensaje += f"\n🏆 ¡Ganador: {ganador}!"
        else:
            mensaje += "\n🤝 ¡Empate!"

        jugador_local_nombre = seleccion_final[local]["jugador"]
        jugador_visitante_nombre = seleccion_final[visitante]["jugador"]
    
        registrar_partido(local, visitante, goles[local], goles[visitante],
                         jugador_local_nombre, jugador_visitante_nombre, modalidad_juego)

        rect = canvas_p.create_rectangle(ancho_p//2 - 320, alto_p//2 - 170,
                                     ancho_p//2 + 320, alto_p//2 + 170,
                                     fill="black", outline="white", width=3)
        text = canvas_p.create_text(ancho_p//2, alto_p//2, text=mensaje,
                                fill="white", font=("Algerian", 28, "bold"))

        try:
            sonido_silbato.play()
        except:
            pass

        crear_boton_regresar()

######################################################
# ANIMAR PORTERO
# Mueve al portero hacia la posición del tiro
######################################################

    def animar_portero(dest_x, regresar=False):
        coords = canvas_p.coords(portero_img)
        if not coords:
            return
        actual_x = coords[0]
        paso = 12 if dest_x > actual_x else -12

        def mover():
            nonlocal actual_x
            actual_x += paso
            canvas_p.coords(portero_img, actual_x, y_personajes)
            if (paso > 0 and actual_x < dest_x) or (paso < 0 and actual_x > dest_x):
                ventana_penales.after(15, mover)
            else:
                if regresar:
                    ventana_penales.after(600, lambda: animar_portero(x_portero_inicial, regresar=False))
        mover()

######################################################
# LANZAR PENALTI
# Ejecuta el lanzamiento y determina si es gol o atajada
######################################################

    def lanzar(pos):
        nonlocal total_tiros, goles, tiros
        
        jugador_actual = turno[0]

        if pos in posiciones_bloqueadas:
            resultado = "ATAJADO 🧤"
            color = "red"
            for b in botones:
                if int(b["text"]) in posiciones_bloqueadas:
                    b.config(bg="red")
            
            try:
                sonido_cagon.play()
            except:
                pass
        else:
            resultado = "¡GOL! ⚽"
            color = "lime"
            goles[jugador_actual] += 1
            
            try:
                sonido_gol.play()
            except:
                pass

        tiros[jugador_actual] += 1
        total_tiros += 1

        resultado_text = canvas_p.create_text(ancho_p//2, alto_p//2, text=resultado,
                                         fill=color, font=("Algerian", 50, "bold"))
        canvas_p.itemconfig(texto_marcador,
                        text=f"{local}: {goles[local]}   -   {visitante}: {goles[visitante]}")

        for b in botones:
            b.config(state="disabled")

        animar_portero(x_portero_inicial, regresar=True)

        if hasattr(ventana_penales, "timer_auto"):
            try:
                ventana_penales.after_cancel(ventana_penales.timer_auto)
            except:
                pass

        def proceder_siguiente_tiro():
            canvas_p.delete(resultado_text)
            if total_tiros < 10:
                siguiente_tiro()
            else:
                terminar()

        if modalidad_juego == "automática":
            ventana_penales.after(3000, proceder_siguiente_tiro)
        else:
            boton_cambio_manual = tk.Button(ventana_penales, text="CAMBIAR JUGADOR", 
                                          bg="orange", fg="black", font=("Arial", 16, "bold"),
                                          command=proceder_siguiente_tiro)
            boton_cambio_manual.place(relx=0.5, rely=0.75, anchor="center")
            ventana_penales.boton_cambio = boton_cambio_manual

######################################################
# SIGUIENTE TIRO
# Prepara el siguiente lanzamiento
######################################################

    def siguiente_tiro():
        if hasattr(ventana_penales, 'boton_cambio'):
            try:
                ventana_penales.boton_cambio.destroy()
            except:
                pass
        
        cambiar_turno()
        crear_botones()

######################################################
# CREAR BOTONES DE TIRO
# Genera los botones para seleccionar posición de tiro
######################################################

    def crear_botones():
        nonlocal posiciones_bloqueadas, botones, botones_widgets
        
        for b in botones_widgets:
            try:
                b.destroy()
            except:
                pass
        botones_widgets = []
        botones = []

        def generar_posicion_portero():
            indice = random.choice(["AN1", "AN2", "AN3"])
            
            descripciones = {
                "AN1": "AN1: 2 paletas contiguas",
                "AN2": "AN2: 3 paletas contiguas", 
                "AN3": "AN3: 3 paletas alternas"
            }
            canvas_p.itemconfig(texto_indice_portero, text=descripciones[indice])
            print(f"Índice del portero: {indice} - {descripciones[indice]}")
            
            if indice == "AN1":
                inicio = random.randint(1, 5)
                return [inicio, inicio + 1]
            
            elif indice == "AN2":
                inicio = random.randint(1, 4)
                return [inicio, inicio + 1, inicio + 2]
            
            elif indice == "AN3":
                grupo = random.choice([[1, 3, 5], [2, 4, 6]])
                return grupo
        
        posiciones_bloqueadas = generar_posicion_portero()
        print(f"Posiciones bloqueadas: {posiciones_bloqueadas}")

        for i in range(6):
            numero = i + 1
            color_fondo = "lightblue"
            b = tk.Button(ventana_penales, text=str(numero), font=("Algerian", 22, "bold"),
                        bg=color_fondo, fg="black", width=6, height=2,
                        command=lambda n=numero: lanzar(n))
            b.place(relx=0.2 + (i * 0.1), rely=0.85, anchor="center")
            botones_widgets.append(b)
            botones.append(b)

        if posiciones_bloqueadas:
            pos_media = sum(posiciones_bloqueadas) / len(posiciones_bloqueadas)
            x_destino = ancho_p * (0.2 + (pos_media - 1) * 0.1)
            animar_portero(x_destino, regresar=True)
        
        try:
            sonido_silbato.play()
        except:
            pass
        
        def tiro_automatico():
            if any(b["state"] == "normal" for b in botones):
                try:
                    sonido_silbato.play()
                except:
                    pass
                
                if posiciones_bloqueadas:
                    pos_aleatoria = random.choice(posiciones_bloqueadas)
                else:
                    pos_aleatoria = random.randint(1, 6)
                
                print(f"⏰ TIEMPO AGOTADO - Tiro automático en posición {pos_aleatoria} - FALLO")
                lanzar(pos_aleatoria)

        if hasattr(ventana_penales, "timer_auto"):
            try:
                ventana_penales.after_cancel(ventana_penales.timer_auto)
            except:
                pass
        
        ventana_penales.timer_auto = ventana_penales.after(7000, tiro_automatico)

    try:
        sonido_silbato.play()
    except:
        pass

    crear_botones()

    def salir_desde_juego():
        try:
            pygame.mixer.music.unpause()
        except:
            pass
        salir()
    
    boton_exit_p = tk.Button(ventana_penales, text="EXIT", command=salir_desde_juego,
                             fg="black", bg="red", font=("Arial", 14, "bold"), width=8)
    canvas_p.create_window(ancho_p - 50, 40, window=boton_exit_p, anchor="ne")

######################################################
# ABRIR SELECCIÓN DE JUGADORES
# Permite seleccionar porteros y tiradores para cada equipo
######################################################

def abrir_seleccion_jugadores(equipos_seleccionados):
    juego = tk.Toplevel()
    juego.title("Selección de jugadores")
    juego.state("zoomed")
    juego.update()
    ancho_j = juego.winfo_width()
    alto_j = juego.winfo_height()

    try:
        fondo_j_img = Image.open("Champions.png").resize((ancho_j, alto_j), Image.Resampling.LANCZOS)
        fondo_j = ImageTk.PhotoImage(fondo_j_img)
    except Exception as e:
        print("Error cargando Champions.png en selección jugadores:", e)
        fondo_j = None

    canvas_j = tk.Canvas(juego, width=ancho_j, height=alto_j)
    canvas_j.pack(fill="both", expand=True)
    if fondo_j:
        canvas_j.create_image(0, 0, image=fondo_j, anchor="nw")
        canvas_j.fondo_j = fondo_j
    else:
        canvas_j.create_rectangle(0, 0, ancho_j, alto_j, fill="black")

    canvas_j.create_text(ancho_j//2, 80, text="SELECCIÓN DE JUGADORES", 
                        fill="white", font=("Algerian", 36, "bold"))

    jugadores_img = {
        "Man City": {
            "porteros": ["bravo", "ederson", "ortega"],
            "jugadores": ["haaland", "aguero", "bruyne"]
        },
        "AC Milan": {
            "porteros": ["dida", "mike", "dona"],
            "jugadores": ["ibra", "dinho", "cafu"]
        },
        "Man United": {
            "porteros": ["peter", "sergio", "Van_der"],
            "jugadores": ["BICHO", "best", "rooney"]
        }
    }

    seleccionados_por_equipo = {equipo: [] for equipo in equipos_seleccionados}
    botones_jugadores = []

    def actualizar_color(boton, seleccionado):
        boton.config(bg="red" if seleccionado else "cyan")

    def seleccionar_jugador(equipo, jugador_nombre, boton):
        seleccion_actual = seleccionados_por_equipo[equipo]
        es_portero = jugador_nombre in jugadores_img[equipo]["porteros"]

        porteros_sel = [j for j in seleccion_actual if j in jugadores_img[equipo]["porteros"]]
        jugadores_sel = [j for j in seleccion_actual if j in jugadores_img[equipo]["jugadores"]]

        if jugador_nombre in seleccion_actual:
            seleccion_actual.remove(jugador_nombre)
            actualizar_color(boton, False)
        else:
            if es_portero:
                if len(porteros_sel) == 0:
                    seleccion_actual.append(jugador_nombre)
                    actualizar_color(boton, True)
                else:
                    print("Ya seleccionaste un portero para", equipo)
            else:
                if len(jugadores_sel) == 0:
                    seleccion_actual.append(jugador_nombre)
                    actualizar_color(boton, True)
                else:
                    print("Ya seleccionaste un jugador para", equipo)

        print("Selección actual:", seleccionados_por_equipo)

    local, visitante = equipos_seleccionados
    
    columna_local_x = ancho_j * 0.25
    columna_visitante_x = ancho_j * 0.75
    
    canvas_j.create_text(columna_local_x, 150, text=f"{local}\n(LOCAL)", 
                        fill="lightblue", font=("Arial", 20, "bold"), justify="center")
    canvas_j.create_text(columna_visitante_x, 150, text=f"{visitante}\n(VISITANTE)", 
                        fill="lightcoral", font=("Arial", 20, "bold"), justify="center")
    
    canvas_j.create_text(columna_local_x - 100, 200, text="PORTEROS", 
                        fill="yellow", font=("Arial", 16, "bold"))
    canvas_j.create_text(columna_local_x + 100, 200, text="ARTILLEROS", 
                        fill="yellow", font=("Arial", 16, "bold"))
    
    canvas_j.create_text(columna_visitante_x - 100, 200, text="PORTEROS", 
                        fill="yellow", font=("Arial", 16, "bold"))
    canvas_j.create_text(columna_visitante_x + 100, 200, text="ARTILLEROS", 
                        fill="yellow", font=("Arial", 16, "bold"))

    def crear_columna_jugadores(equipo, columna_x, es_local=True):
        y_start = 350
        y_spacing = 120
        
        x_porteros = columna_x - 100 if es_local else columna_x - 100
        for i, jugador_nombre in enumerate(jugadores_img[equipo]["porteros"]):
            try:
                imagen_jugador = ImageTk.PhotoImage(Image.open(f"{jugador_nombre}.png").resize((100, 100), Image.Resampling.LANCZOS))
            except Exception as e:
                print(f"Error cargando imagen de {jugador_nombre}:", e)
                imagen_jugador = None
            
            boton = tk.Button(juego, image=imagen_jugador, bd=2, bg="cyan")
            boton.config(command=partial(seleccionar_jugador, equipo, jugador_nombre, boton))
            boton.place(x=x_porteros, y=y_start + (i * y_spacing), anchor="center")
            boton.imagen = imagen_jugador
            botones_jugadores.append(boton)
            
            nombre_display = jugador_nombre.replace("_", " ").title()
            canvas_j.create_text(x_porteros, y_start + (i * y_spacing) + 60, 
                               text=nombre_display, fill="white", font=("Arial", 10, "bold"))

        x_jugadores = columna_x + 100 if es_local else columna_x + 100
        for i, jugador_nombre in enumerate(jugadores_img[equipo]["jugadores"]):
            try:
                imagen_jugador = ImageTk.PhotoImage(Image.open(f"{jugador_nombre}.png").resize((100, 100), Image.Resampling.LANCZOS))
            except Exception as e:
                print(f"Error cargando imagen de {jugador_nombre}:", e)
                imagen_jugador = None
            
            boton = tk.Button(juego, image=imagen_jugador, bd=2, bg="cyan")
            boton.config(command=partial(seleccionar_jugador, equipo, jugador_nombre, boton))
            boton.place(x=x_jugadores, y=y_start + (i * y_spacing), anchor="center")
            boton.imagen = imagen_jugador
            botones_jugadores.append(boton)
            
            nombre_display = jugador_nombre.replace("_", " ").title()
            canvas_j.create_text(x_jugadores, y_start + (i * y_spacing) + 60, 
                               text=nombre_display, fill="white", font=("Arial", 10, "bold"))

    crear_columna_jugadores(local, columna_local_x, es_local=True)
    crear_columna_jugadores(visitante, columna_visitante_x, es_local=False)

    def confirmar():
        todo_correcto = all(len(seleccionados_por_equipo[e]) == 2 for e in equipos_seleccionados)
        if todo_correcto:
            seleccion_final = {}
            for equipo in equipos_seleccionados:
                seleccion = seleccionados_por_equipo[equipo]
                
                if len(seleccion) != 2:
                    print(f"Error: {equipo} no tiene 2 jugadores seleccionados")
                    return
                
                portero = next((j for j in seleccion if j in jugadores_img[equipo]["porteros"]), None)
                jugador = next((j for j in seleccion if j in jugadores_img[equipo]["jugadores"]), None)
                
                if portero is None or jugador is None:
                    print(f"Error: Selección inválida para {equipo} - Portero: {portero}, Jugador: {jugador}")
                    return
                
                seleccion_final[equipo] = {"portero": portero, "jugador": jugador}

            print("Selección confirmada:", seleccion_final)

            try:
                juego.destroy()
            except:
                pass

            iniciar_penales(equipos_seleccionados, seleccion_final)
        else:
            print("⚠️ Debes seleccionar 1 portero y 1 jugador por equipo")

    boton_confirmar = tk.Button(juego, text="Confirmar", bg="green", fg="white",
                                font=("Arial",16,"bold"), width=12, height=2,
                                command=confirmar)
    boton_confirmar.place(relx=0.5, rely=0.75, anchor="center")

    canvas_j.create_text(ancho_j//2, alto_j - 100, 
                        text="Selecciona 1 PORTERO y 1 ARTILLERO por equipo", 
                        fill="yellow", font=("Arial", 14, "bold"))

    boton_exit_j = tk.Button(juego, text="EXIT", command=salir, fg="black", bg="red",
                             font=("Arial",14,"bold"), width=8)
    canvas_j.create_window(ancho_j-50, 40, window=boton_exit_j, anchor="ne")

######################################################
# LANZAR MONEDA
# Realiza animación de lanzamiento de moneda para determinar equipo local
######################################################

def lanzar_moneda(equipos_seleccionados):
    ventana_moneda = tk.Toplevel()
    ventana_moneda.title("Tirada de moneda")
    ventana_moneda.state("zoomed")
    ventana_moneda.update()
    ancho_m = ventana_moneda.winfo_width()
    alto_m = ventana_moneda.winfo_height()

    try:
        fondo_img = Image.open("Champions.png").resize((ancho_m, alto_m), Image.Resampling.LANCZOS)
        fondo = ImageTk.PhotoImage(fondo_img)
    except Exception as e:
        print("Error cargando Champions.png en moneda:", e)
        fondo = None

    canvas_m = tk.Canvas(ventana_moneda, width=ancho_m, height=alto_m)
    canvas_m.pack(fill="both", expand=True)
    if fondo:
        canvas_m.create_image(0, 0, image=fondo, anchor="nw")
        canvas_m.fondo = fondo
    else:
        canvas_m.create_rectangle(0,0,ancho_m,alto_m,fill="black")

    gif_path = os.path.join("animacion_moneda", "moneda.gif")
    try:
        gif = Image.open(gif_path)
        frames = []
        try:
            while True:
                frame = gif.copy().resize((200, 200), Image.Resampling.LANCZOS)
                frames.append(ImageTk.PhotoImage(frame))
                gif.seek(len(frames))
        except EOFError:
            pass
    except Exception as e:
        print("Error cargando gif moneda:", e)
        frames = []

    if frames:
        moneda_canvas = canvas_m.create_image(ancho_m // 2, alto_m // 2, image=frames[0])
        canvas_m.frames = frames
    else:
        moneda_canvas = None

    def animar_moneda(idx=0):
        if frames and idx < len(frames) * 3:
            canvas_m.itemconfig(moneda_canvas, image=frames[idx % len(frames)])
            ventana_moneda.after(50, lambda: animar_moneda(idx + 1))
        else:
            resultado = random.choice(["cara", "cruz"])
            canvas_m.create_text(ancho_m // 2, alto_m // 2 + 150,
                                 text=f"{'CARA' if resultado == 'cara' else 'CRUZ'}",
                                 font=("Algerian", 36, "bold"), fill="white")

            if resultado == "cara":
                local, visitante = equipos_seleccionados[0], equipos_seleccionados[1]
            else:
                local, visitante = equipos_seleccionados[1], equipos_seleccionados[0]

            canvas_m.create_text(ancho_m // 2, alto_m // 2 + 220,
                                 text=f"Local: {local}\nVisitante: {visitante}",
                                 font=("Arial", 26, "bold"), fill="yellow")

            def continuar():
                try:
                    ventana_moneda.destroy()
                except:
                    pass
                ventana.after(200, lambda: abrir_seleccion_jugadores(equipos_seleccionados))

            ventana_moneda.after(2500, continuar)

    animar_moneda()

######################################################
# ABRIR SELECCIÓN DE EQUIPOS
# Permite seleccionar los dos equipos que jugarán
######################################################

def abrir_seleccion_equipos():
    global seleccion
    ventana.withdraw()
    seleccion = tk.Toplevel()
    seleccion.title("Selección de equipos")
    seleccion.state("zoomed")
    seleccion.update()
    ancho2 = seleccion.winfo_width()
    alto2 = seleccion.winfo_height()

    try:
        fondo_sel_img = Image.open("Champions.png").resize((ancho2, alto2), Image.Resampling.LANCZOS)
        fondo_sel = ImageTk.PhotoImage(fondo_sel_img)
    except Exception as e:
        print("Error cargando Champions.png en selección equipos:", e)
        fondo_sel = None

    canvas2 = tk.Canvas(seleccion, width=ancho2, height=alto2)
    canvas2.pack(fill="both", expand=True)
    if fondo_sel:
        canvas2.create_image(0,0,image=fondo_sel, anchor="nw")
        canvas2.fondo_sel = fondo_sel
    else:
        canvas2.create_rectangle(0,0,ancho2,alto2,fill="black")

    canvas2.create_text(ancho2//2, 100, text="SELECCIONA TU EQUIPO", fill="white", font=("Algerian",40,"bold"))

    equipos_seleccionados = []

    img_city = ImageTk.PhotoImage(Image.open("CITY_F.png").resize((150,150), Image.Resampling.LANCZOS))
    img_milan = ImageTk.PhotoImage(Image.open("milan_f.png").resize((150,150), Image.Resampling.LANCZOS))
    img_united = ImageTk.PhotoImage(Image.open("united_f.png").resize((150,150), Image.Resampling.LANCZOS))

    def actualizar_color(boton, seleccionado):
        boton.config(bg="red" if seleccionado else "cyan")

    botones_map = {}

    def seleccionar_equipo(nombre, boton):
        nonlocal equipos_seleccionados
        if nombre in equipos_seleccionados:
            equipos_seleccionados.remove(nombre)
            actualizar_color(boton, False)
        else:
            if len(equipos_seleccionados) < 2:
                equipos_seleccionados.append(nombre)
                actualizar_color(boton, True)
            else:
                ultimo = equipos_seleccionados.pop()
                for b_name, b_widget in botones_map.items():
                    if b_name == ultimo:
                        actualizar_color(b_widget, False)
                        break
                equipos_seleccionados.append(nombre)
                actualizar_color(boton, True)
        print("Equipos seleccionados:", equipos_seleccionados)

    boton_city = tk.Button(seleccion, image=img_city, bd=2, bg="cyan",
                           command=lambda: seleccionar_equipo("Man City", boton_city))
    boton_milan = tk.Button(seleccion, image=img_milan, bd=2, bg="cyan",
                            command=lambda: seleccionar_equipo("AC Milan", boton_milan))
    boton_united = tk.Button(seleccion, image=img_united, bd=2, bg="cyan",
                             command=lambda: seleccionar_equipo("Man United", boton_united))

    boton_city.place(relx=0.3, rely=0.3, anchor="center")
    boton_milan.place(relx=0.5, rely=0.3, anchor="center")
    boton_united.place(relx=0.7, rely=0.3, anchor="center")

    canvas2.img_city = img_city
    canvas2.img_milan = img_milan
    canvas2.img_united = img_united

    botones_map = {
        "Man City": boton_city,
        "AC Milan": boton_milan,
        "Man United": boton_united
    }

    boton_exit_sel = tk.Button(seleccion, text="EXIT", command=salir, fg="black", bg="red",
                               font=("Arial",14,"bold"), width=8)
    canvas2.create_window(ancho2-50, 40, window=boton_exit_sel, anchor="ne")

    boton_continuar = tk.Button(seleccion, text="Continuar", bg="lightgreen", fg="black",
                                font=("Algerian",22,"bold"), width=15, height=2,
                                command=lambda: lanzar_moneda(equipos_seleccionados))
    boton_continuar.place(relx=0.5, rely=0.6, anchor="center")

######################################################
# CONFIGURAR INTERFAZ PRINCIPAL
# Crea los elementos del menú principal
######################################################

try:
    imagen_fondo = Image.open("Champions.png").resize((ancho, alto), Image.Resampling.LANCZOS)
    fondo = ImageTk.PhotoImage(imagen_fondo)
    imagen_texto = Image.open("Texto.png")
    texto = ImageTk.PhotoImage(imagen_texto)
    canvas = tk.Canvas(ventana, width=ancho, height=alto)
    canvas.pack(fill="both", expand=True)
    canvas.create_image(0,0,image=fondo, anchor="nw")
    canvas.create_image(ancho//2,100,image=texto, anchor="center")
    canvas.fondo = fondo
    canvas.texto = texto
except Exception as e:
    print("Error cargando fondos del menú principal:", e)
    canvas = tk.Canvas(ventana, width=ancho, height=alto, bg="black")
    canvas.pack(fill="both", expand=True)

boton_new_partida = tk.Button(ventana, text="Start new game", fg="black", bg="lightblue",
                              font=("Algerian",20),width=15,height=1, 
                              command=abrir_configuracion)
boton_new_partida.place(relx=0.5, rely=0.25, anchor="center")

boton_about = tk.Button(ventana, text="About Us", fg="black", bg="lightblue",
                        font=("Algerian", 20),width=15, height=1, command=abrir_about_us)
boton_about.place(relx=0.5, rely=0.35, anchor="center")

boton_historial = tk.Button(ventana, text="Historial", fg="black", bg="lightblue",
                           font=("Algerian", 20),width=15, height=1, command=abrir_historial)
boton_historial.place(relx=0.5, rely=0.45, anchor="center")

boton_exit = tk.Button(ventana, text="EXIT", command=salir, fg="black", bg="red",
                       font=("Arial",14,"bold"), relief="raised", width=8)
canvas.create_window(ancho-50, 40, window=boton_exit, anchor="ne")

######################################################
# INICIAR CLIENTE RASPBERRY
# Inicia la conexión con Raspberry Pi al arrancar
######################################################

cliente_raspberry.conectar_raspberry()

ventana.mainloop()