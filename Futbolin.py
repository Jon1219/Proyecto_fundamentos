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

# =========================
# SERVIDOR PARA COMUNICACIÓN CON RASPBERRY
# =========================
# =========================
# CLIENTE PARA COMUNICACIÓN CON RASPBERRY
# =========================
# =========================
# CLIENTE PARA COMUNICACIÓN CON RASPBERRY (VERSIÓN CORREGIDA)
# =========================
class ClienteRaspberry:
    def __init__(self, host='10.238.236.35', port=5000):  # IP de la Raspberry
        self.host = host
        self.port = port
        self.socket = None
        self.conectado = False
        self.equipos_seleccionados = []
        self.seleccion_final = {}
        self.reconectar_automatico = True
        
    def conectar_raspberry(self):
        """Conecta con la Raspberry Pi"""
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
                # Reintentar después de 5 segundos si está habilitado
                if self.reconectar_automatico:
                    print("🔄 Reintentando conexión en 5 segundos...")
                    ventana.after(5000, self.conectar_raspberry)
        
        thread = threading.Thread(target=conectar_loop, daemon=True)
        thread.start()
    
    def recibir_mensajes(self):
        """Recibe mensajes de la Raspberry en un hilo separado"""
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
                    continue  # Timeout normal, continuar esperando
                except Exception as e:
                    print(f"❌ Error recibiendo mensajes: {e}")
                    self.conectado = False
                    break
            
            # Si salimos del loop, intentar reconectar
            if self.reconectar_automatico:
                print("🔄 Intentando reconexión...")
                ventana.after(2000, self.conectar_raspberry)
        
        thread = threading.Thread(target=recibir_loop, daemon=True)
        thread.start()
    
    def procesar_mensaje(self, mensaje):
        """Procesa los mensajes recibidos de la Raspberry"""
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
            
            # Mostrar mensaje en la interfaz
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
    
    def mostrar_configuracion_raspberry(self):
        """Muestra la configuración recibida de la Raspberry"""
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
            
            # Preguntar si iniciar el juego
            self.preguntar_inicio_juego()
    
    def preguntar_inicio_juego(self):
        """Pregunta al usuario si quiere iniciar el juego con la configuración de Raspberry"""
        try:
            respuesta = messagebox.askyesno(  # ⚡ CORREGIDO: usar messagebox directamente
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
            # Si hay error con el messagebox, iniciar automáticamente después de 3 segundos
            print("🔄 Iniciando juego automáticamente en 3 segundos...")
            ventana.after(3000, self.iniciar_juego_desde_raspberry)
    
    def iniciar_juego_desde_raspberry(self):
        """Inicia el juego con la configuración de la Raspberry"""
        if self.equipos_seleccionados and self.seleccion_final:
            print("🚀 Iniciando juego con configuración de Raspberry...")
            # Cerrar ventanas actuales
            for widget in ventana.winfo_children():
                if isinstance(widget, tk.Toplevel):
                    try:
                        widget.destroy()
                    except:
                        pass
            
            # Iniciar directamente los penales
            ventana.after(500, lambda: iniciar_penales(self.equipos_seleccionados, self.seleccion_final))
    
    def enviar_mensaje(self, tipo, datos):
        """Envía mensajes a la Raspberry"""
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
    
    def reiniciar_juego(self):
        """Envía comando de reinicio a la Raspberry"""
        self.enviar_mensaje("REINICIAR", {})
        print("🔄 Comando de reinicio enviado a Raspberry")
    
    def desconectar(self):
        """Desconecta del servidor"""
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

# =========================
# INICIALIZAR MÚSICA Y EFECTOS DE SONIDO
# =========================
try:
    pygame.mixer.init()
    pygame.mixer.music.load("musica_fondo.mp3")
    pygame.mixer.music.play(-1)  # Loop infinito
    
    # Cargar efectos de sonido
    sonido_silbato = pygame.mixer.Sound("silbato.mp3")
    sonido_gol = pygame.mixer.Sound("gol.mp3")
    sonido_cagon = pygame.mixer.Sound("cagon.mp3")
except Exception as e:
    print("Error al cargar sonidos:", e)
    # Crear placeholders para evitar errores
    class DummySound:
        def play(self): pass
    sonido_silbato = DummySound()
    sonido_gol = DummySound()
    sonido_cagon = DummySound()

# =========================
# VENTANA PRINCIPAL (se crea temprano para que otras funciones la usen)
# =========================
ventana = tk.Tk()
ventana.title("Menú principal - Champions Game")
ventana.state("zoomed")
ventana.update()
ancho = ventana.winfo_width()
alto = ventana.winfo_height()

# =========================
# VARIABLES GLOBALES
# =========================
modalidad_juego = "automática"  # "automática" o "manual"
HISTORIAL_FILE = "historial_partidos.json"
GOLEADORES_FILE = "ranking_goleadores.json"

# =========================
# SISTEMA DE HISTORIAL Y GOLEADORES
# =========================
def cargar_historial():
    """Carga el historial de partidos desde JSON"""
    try:
        with open(HISTORIAL_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"partidos": [], "ultimo_id": 0}

def guardar_historial(historial):
    """Guarda el historial en JSON"""
    try:
        with open(HISTORIAL_FILE, 'w', encoding='utf-8') as f:
            json.dump(historial, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print("Error guardando historial:", e)

def cargar_goleadores():
    """Carga el ranking de goleadores desde JSON"""
    try:
        with open(GOLEADORES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"goleadores": []}

def guardar_goleadores(goleadores):
    """Guarda el ranking de goleadores en JSON"""
    try:
        with open(GOLEADORES_FILE, 'w', encoding='utf-8') as f:
            json.dump(goleadores, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print("Error guardando goleadores:", e)

def actualizar_goleadores(jugador, equipo, goles):
    """Actualiza el ranking de goleadores"""
    goleadores_data = cargar_goleadores()
    
    # Buscar si el jugador ya existe
    encontrado = False
    for goleador in goleadores_data["goleadores"]:
        if goleador["jugador"] == jugador and goleador["equipo"] == equipo:
            goleador["goles"] += goles
            encontrado = True
            break
    
    # Si no existe, agregarlo
    if not encontrado:
        goleadores_data["goleadores"].append({
            "jugador": jugador,
            "equipo": equipo,
            "goles": goles
        })
    
    # Ordenar por goles (descendente)
    goleadores_data["goleadores"].sort(key=lambda x: x["goles"], reverse=True)
    
    # Mantener solo los top 3
    if len(goleadores_data["goleadores"]) > 3:
        goleadores_data["goleadores"] = goleadores_data["goleadores"][:3]
    
    guardar_goleadores(goleadores_data)

def registrar_partido(equipo_local, equipo_visitante, goles_local, goles_visitante, 
                     jugador_local, jugador_visitante, modalidad):
    """Registra un nuevo partido en el historial"""
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
    
    # Agregar al inicio de la lista
    historial["partidos"].insert(0, nuevo_partido)
    
    # Mantener solo los últimos 3 partidos
    if len(historial["partidos"]) > 3:
        historial["partidos"] = historial["partidos"][:3]
    
    historial["ultimo_id"] += 1
    guardar_historial(historial)
    
    # Actualizar goleadores
    actualizar_goleadores(jugador_local, equipo_local, goles_local)
    actualizar_goleadores(jugador_visitante, equipo_visitante, goles_visitante)

# =========================
# NUEVA FUNCIÓN: VER HISTORIAL
# =========================
def abrir_historial():
    ventana.withdraw
    historial_window = tk.Toplevel()
    historial_window.title("Historial de Partidos - Top Goleadores")
    historial_window.state("zoomed")
    historial_window.update()
    ancho_h = historial_window.winfo_width()
    alto_h = historial_window.winfo_height()

    # Fondo
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

    # Título
    canvas_h.create_text(ancho_h//2, 80, text="HISTORIAL Y ESTADÍSTICAS", 
                        fill="gold", font=("Algerian", 40, "bold"))

    # Cargar datos
    historial = cargar_historial()
    goleadores = cargar_goleadores()

    # ===== HISTORIAL DE PARTIDOS =====
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

    # ===== TOP GOLEADORES =====
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

    # Botón EXIT
    boton_exit_h = tk.Button(historial_window, text="EXIT", command=historial_window.destroy,
                            fg="black", bg="red", font=("Arial", 14, "bold"), width=8)
    canvas_h.create_window(ancho_h - 50, 40, window=boton_exit_h, anchor="ne")

# =========================
# PANTALLA DE CONFIGURACIÓN
# =========================
def abrir_configuracion():
    global modalidad_juego
    ventana.withdraw
    
    config = tk.Toplevel()
    config.title("Configuración del Juego - CEFoot v4.1")
    config.state("zoomed")
    config.update()
    ancho_c = config.winfo_width()
    alto_c = config.winfo_height()

    # Fondo
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

    # Título
    canvas_c.create_text(ancho_c//2, 100, text="CONFIGURACIÓN DEL JUEGO", 
                        fill="white", font=("Algerian", 40, "bold"))
    
    canvas_c.create_text(ancho_c//2, 180, text="Selecciona la modalidad de juego:", 
                        fill="yellow", font=("Arial", 24, "bold"))

    # Variable para los radio buttons
    var_modalidad = tk.StringVar(value=modalidad_juego)

    # Radio Button para Automático
    rb_auto = tk.Radiobutton(config, text="AUTOMÁTICO", variable=var_modalidad, 
                            value="automática", font=("Arial", 20, "bold"),
                            bg="lightgreen", fg="black", selectcolor="green")
    rb_auto.place(relx=0.5, rely=0.35, anchor="center")

    # Radio Button para Manual
    rb_manual = tk.Radiobutton(config, text="MANUAL", variable=var_modalidad, 
                              value="manual", font=("Arial", 20, "bold"),
                              bg="lightcoral", fg="black", selectcolor="red")
    rb_manual.place(relx=0.5, rely=0.45, anchor="center")

    # Descripción de modalidades
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
        
        # Ir a selección de equipos
        abrir_seleccion_equipos()

    # Botón CONFIRMAR
    boton_confirmar = tk.Button(config, text="CONFIRMAR", bg="gold", fg="black",
                               font=("Algerian", 22, "bold"), width=15, height=2,
                               command=confirmar_configuracion)
    boton_confirmar.place(relx=0.5, rely=0.7, anchor="center")

    # Botón EXIT
    boton_exit_c = tk.Button(config, text="EXIT", command=salir, 
                            fg="black", bg="red", font=("Arial", 14, "bold"), width=8)
    canvas_c.create_window(ancho_c - 50, 40, window=boton_exit_c, anchor="ne")

# =========================
# FUNCIÓN SALIR (DETENER MÚSICA Y CERRAR TODO)
# =========================
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

# =========================
# NUEVA FUNCIÓN: ABOUT US
# =========================
def abrir_about_us():
    ventana.withdraw
    about = tk.Toplevel()
    about.title("About Us - Champions Game")
    about.state("zoomed")
    about.update()
    ancho_a = about.winfo_width()
    alto_a = about.winfo_height()

    # Fondo
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

    # === Foto y texto de Jonathan ===
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

    # === Foto y texto de Johan ===
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

    # Botón EXIT
    boton_exit_a = tk.Button(about, text="EXIT", command=about.destroy,
                             fg="black", bg="red", font=("Arial", 14, "bold"), width=8)
    canvas_a.create_window(ancho_a - 50, 40, window=boton_exit_a, anchor="ne")

# =========================
# FASE DE PENALES (MODIFICADA PARA REGISTRAR EN JSON Y AGREGAR SONIDOS)
# =========================
# =========================
# FASE DE PENALES (MODIFICADA PARA REGISTRAR EN JSON Y AGREGAR SONIDOS)
# =========================
def iniciar_penales(equipos_seleccionados, seleccion_final):
    global modalidad_juego
    
    # PAUSAR LA MÚSICA DE FONDO AL INICIAR EL JUEGO
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

    # =========================
    # DEFINIR TODAS LAS VARIABLES PRIMERO
    # =========================
    local, visitante = equipos_seleccionados
    goles = {local: 0, visitante: 0}
    tiros = {local: 0, visitante: 0}
    turno = [local]
    total_tiros = 0
    posiciones_bloqueadas = []
    botones = []
    botones_widgets = []
    
    # Fondo y canvas
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

    # Cargar imágenes de jugadores
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

    # Elementos UI
    texto_turno = canvas_p.create_text(ancho_p//2, 80, text=f"Turno: {local}",
                                       fill="white", font=("Algerian", 36, "bold"))
    texto_marcador = canvas_p.create_text(ancho_p//2, 150,
                                          text=f"{local}: 0   -   {visitante}: 0",
                                          fill="yellow", font=("Arial", 28, "bold"))
    texto_modalidad = canvas_p.create_text(ancho_p//2, 200, 
                                         text=f"Modalidad: {modalidad_juego.upper()}",
                                         fill="cyan", font=("Arial", 20, "bold"))

    # Texto para mostrar el índice del portero
    texto_indice_portero = canvas_p.create_text(ancho_p//2, 230, 
                                              text="",
                                              fill="orange", font=("Arial", 16, "bold"))

    # Posiciones de personajes
    x_portero_inicial = ancho_p * 0.25
    x_jugador_inicial = ancho_p * 0.75
    y_personajes = alto_p * 0.6

    # Crear imágenes en canvas
    img_port = imagenes[visitante]["portero"] if imagenes[visitante]["portero"] else None
    img_jug = imagenes[local]["jugador"] if imagenes[local]["jugador"] else None
    portero_img = canvas_p.create_image(x_portero_inicial, y_personajes, image=img_port)
    jugador_img = canvas_p.create_image(x_jugador_inicial, y_personajes, image=img_jug)

    # =========================
    # NUEVO: VARIABLE PARA EL BOTÓN DE REGRESAR
    # =========================
    boton_regresar = None

    # =========================
    # FUNCIÓN PARA REGRESAR AL MENÚ PRINCIPAL (MODIFICADA PARA REANUDAR MÚSICA)
    # =========================
    def regresar_menu_principal():
        try:
            # REANUDAR LA MÚSICA DE FONDO AL REGRESAR AL MENÚ
            try:
                pygame.mixer.music.unpause()
            except:
                pass
            
            # Cerrar todas las ventanas intermedias
            ventana_penales.destroy()  # Cierra la ventana de penales
            
            # Buscar y cerrar todas las ventanas Toplevel (selección de equipos, etc.)
            for widget in ventana.winfo_children():
                if isinstance(widget, tk.Toplevel):
                    try:
                        widget.destroy()
                    except:
                        pass
            
            ventana.deiconify()  # Muestra la ventana principal nuevamente
        except Exception as e:
            print("Error al regresar al menú:", e)

    # =========================
    # FUNCIÓN PARA CREAR EL BOTÓN DE REGRESAR (SOLO AL FINAL)
    # =========================
    def crear_boton_regresar():
        nonlocal boton_regresar
        # Solo crear el botón si no existe
        if boton_regresar is None:
            boton_regresar = tk.Button(ventana_penales, text="REGRESAR AL MENÚ PRINCIPAL", 
                                     bg="gold", fg="black", font=("Arial", 16, "bold"),
                                     width=25, height=2, command=regresar_menu_principal)
            
            # Posicionar el botón debajo del mensaje de resultado
            canvas_p.create_window(ancho_p//2, alto_p//2 + 150, window=boton_regresar)

    # =========================
    # AHORA SÍ LAS FUNCIONES INTERNAS
    # =========================
    
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
        
        # SONIDO: Silbato al cambiar de jugador
        try:
            sonido_silbato.play()
        except:
            pass

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

        # REGISTRAR PARTIDO EN JSON
        jugador_local_nombre = seleccion_final[local]["jugador"]
        jugador_visitante_nombre = seleccion_final[visitante]["jugador"]
    
        registrar_partido(local, visitante, goles[local], goles[visitante],
                         jugador_local_nombre, jugador_visitante_nombre, modalidad_juego)

        rect = canvas_p.create_rectangle(ancho_p//2 - 320, alto_p//2 - 170,
                                     ancho_p//2 + 320, alto_p//2 + 170,
                                     fill="black", outline="white", width=3)
        text = canvas_p.create_text(ancho_p//2, alto_p//2, text=mensaje,
                                fill="white", font=("Algerian", 28, "bold"))

        # SONIDO: Silbato al finalizar el partido
        try:
            sonido_silbato.play()
        except:
            pass

        # =========================
        # NUEVO: CREAR BOTÓN DE REGRESAR AL FINALIZAR EL PARTIDO
        # =========================
        crear_boton_regresar()

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

    def lanzar(pos):
        nonlocal total_tiros, goles, tiros
        
        jugador_actual = turno[0]

        # Mostrar resultado
        if pos in posiciones_bloqueadas:
            resultado = "ATAJADO 🧤"
            color = "red"
            for b in botones:
                if int(b["text"]) in posiciones_bloqueadas:
                    b.config(bg="red")
            
            # SONIDO: Cagon cuando es atajado
            try:
                sonido_cagon.play()
            except:
                pass
        else:
            resultado = "¡GOL! ⚽"
            color = "lime"
            goles[jugador_actual] += 1
            
            # SONIDO: Gol cuando anota
            try:
                sonido_gol.play()
            except:
                pass

        tiros[jugador_actual] += 1
        total_tiros += 1

        # Mostrar resultado
        resultado_text = canvas_p.create_text(ancho_p//2, alto_p//2, text=resultado,
                                         fill=color, font=("Algerian", 50, "bold"))
        canvas_p.itemconfig(texto_marcador,
                        text=f"{local}: {goles[local]}   -   {visitante}: {goles[visitante]}")

        # Desactivar botones
        for b in botones:
            b.config(state="disabled")

        animar_portero(x_portero_inicial, regresar=True)

        # Cancelar tiro automático si existe
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
            # Esperar 5 segundos para cambio automático
            ventana_penales.after(3000, proceder_siguiente_tiro)
        else:
            # Modalidad manual - esperar botón de cambio
            boton_cambio_manual = tk.Button(ventana_penales, text="CAMBIAR JUGADOR", 
                                          bg="orange", fg="black", font=("Arial", 16, "bold"),
                                          command=proceder_siguiente_tiro)
            boton_cambio_manual.place(relx=0.5, rely=0.75, anchor="center")
            ventana_penales.boton_cambio = boton_cambio_manual

    def siguiente_tiro():
        # Limpiar botón de cambio manual si existe
        if hasattr(ventana_penales, 'boton_cambio'):
            try:
                ventana_penales.boton_cambio.destroy()
            except:
                pass
        
        cambiar_turno()
        crear_botones()

    def crear_botones():
        nonlocal posiciones_bloqueadas, botones, botones_widgets
        
        # Destruir botones anteriores
        for b in botones_widgets:
            try:
                b.destroy()
            except:
                pass
        botones_widgets = []
        botones = []

        # =========================
        # ALGORITMO DE POSICIÓN DEL PORTERO - 3 ÍNDICES
        # =========================
        def generar_posicion_portero():
            indice = random.choice(["AN1", "AN2", "AN3"])
            
            # Actualizar texto en la interfaz
            descripciones = {
                "AN1": "AN1: 2 paletas contiguas",
                "AN2": "AN2: 3 paletas contiguas", 
                "AN3": "AN3: 3 paletas alternas"
            }
            canvas_p.itemconfig(texto_indice_portero, text=descripciones[indice])
            print(f"Índice del portero: {indice} - {descripciones[indice]}")
            
            if indice == "AN1":
                # AN1: 2 paletas contiguas
                inicio = random.randint(1, 5)
                return [inicio, inicio + 1]
            
            elif indice == "AN2":
                # AN2: 3 paletas contiguas
                inicio = random.randint(1, 4)
                return [inicio, inicio + 1, inicio + 2]
            
            elif indice == "AN3":
                # AN3: 3 paletas alternas (dos grupos posibles)
                grupo = random.choice([[1, 3, 5], [2, 4, 6]])
                return grupo
        
        # Generar posiciones bloqueadas según el algoritmo
        posiciones_bloqueadas = generar_posicion_portero()
        print(f"Posiciones bloqueadas: {posiciones_bloqueadas}")

        # Crear botones
        for i in range(6):
            numero = i + 1
            color_fondo = "lightblue"
            b = tk.Button(ventana_penales, text=str(numero), font=("Algerian", 22, "bold"),
                        bg=color_fondo, fg="black", width=6, height=2,
                        command=lambda n=numero: lanzar(n))
            b.place(relx=0.2 + (i * 0.1), rely=0.85, anchor="center")
            botones_widgets.append(b)
            botones.append(b)

        # Animación del portero - CENTRAR EN EL MEDIO DE LAS POSICIONES BLOQUEADAS
        if posiciones_bloqueadas:
            pos_media = sum(posiciones_bloqueadas) / len(posiciones_bloqueadas)
            x_destino = ancho_p * (0.2 + (pos_media - 1) * 0.1)
            animar_portero(x_destino, regresar=True)
        
        # SONIDO: Silbato al iniciar cada turno
        try:
            sonido_silbato.play()
        except:
            pass
        
        # Tiro automático después de 7 segundos - CORREGIDO
        def tiro_automatico():
            if any(b["state"] == "normal" for b in botones):
                # SONIDO: Silbato cuando se acaba el tiempo
                try:
                    sonido_silbato.play()
                except:
                    pass
                
                # SI SE ACABA EL TIEMPO, ES SIEMPRE FALLO
                # Elegimos una posición que SEGURO esté bloqueada por el portero
                if posiciones_bloqueadas:
                    pos_aleatoria = random.choice(posiciones_bloqueadas)
                else:
                    pos_aleatoria = random.randint(1, 6)  # Fallback por seguridad
                
                print(f"⏰ TIEMPO AGOTADO - Tiro automático en posición {pos_aleatoria} - FALLO")
                lanzar(pos_aleatoria)

        # CANCELAR TEMPORIZADOR ANTERIOR Y CREAR UNO NUEVO
        if hasattr(ventana_penales, "timer_auto"):
            try:
                ventana_penales.after_cancel(ventana_penales.timer_auto)
            except:
                pass
        
        # PROGRAMAR NUEVO TEMPORIZADOR
        ventana_penales.timer_auto = ventana_penales.after(7000, tiro_automatico)

    # SONIDO: Silbato al iniciar el juego
    try:
        sonido_silbato.play()
    except:
        pass

    # Iniciar primera tanda
    crear_botones()

    # Botón EXIT (MODIFICADO PARA REANUDAR MÚSICA)
    def salir_desde_juego():
        try:
            # REANUDAR LA MÚSICA AL SALIR
            pygame.mixer.music.unpause()
        except:
            pass
        salir()
    
    boton_exit_p = tk.Button(ventana_penales, text="EXIT", command=salir_desde_juego,
                             fg="black", bg="red", font=("Arial", 14, "bold"), width=8)
    canvas_p.create_window(ancho_p - 50, 40, window=boton_exit_p, anchor="ne")

# =========================
# SELECCIÓN DE JUGADORES
# =========================

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

    # Título
    canvas_j.create_text(ancho_j//2, 80, text="SELECCIÓN DE JUGADORES", 
                        fill="white", font=("Algerian", 36, "bold"))

    # =========================
    # Jugadores por equipo (3 porteros y 3 jugadores)
    # =========================
    jugadores_img = {
        "Man City": {
            "porteros": ["bravo", "ederson", "ortega"],  # 🔥 QUITÉ .png
            "jugadores": ["haaland", "aguero", "bruyne"]  # 🔥 QUITÉ .png
        },
        "AC Milan": {
            "porteros": ["dida", "mike", "dona"],  # 🔥 QUITÉ .png
            "jugadores": ["ibra", "dinho", "cafu"]  # 🔥 QUITÉ .png
        },
        "Man United": {
            "porteros": ["peter", "sergio", "Van_der"],  # 🔥 QUITÉ .png
            "jugadores": ["BICHO", "best", "rooney"]  # 🔥 QUITÉ .png
        }
    }

    seleccionados_por_equipo = {equipo: [] for equipo in equipos_seleccionados}
    botones_jugadores = []

    def actualizar_color(boton, seleccionado):
        boton.config(bg="red" if seleccionado else "cyan")

    def seleccionar_jugador(equipo, jugador_nombre, boton):
        seleccion_actual = seleccionados_por_equipo[equipo]
        es_portero = jugador_nombre in jugadores_img[equipo]["porteros"]

        # Contar si ya hay un portero o jugador seleccionado
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

    # =========================
    # NUEVA ORGANIZACIÓN: Columnas verticales
    # =========================
    
    # Posiciones para los equipos
    # Equipo local a la izquierda, visitante a la derecha
    local, visitante = equipos_seleccionados
    
    # Configuración de columnas
    columna_local_x = ancho_j * 0.25
    columna_visitante_x = ancho_j * 0.75
    
    # Títulos de equipos
    canvas_j.create_text(columna_local_x, 150, text=f"{local}\n(LOCAL)", 
                        fill="lightblue", font=("Arial", 20, "bold"), justify="center")
    canvas_j.create_text(columna_visitante_x, 150, text=f"{visitante}\n(VISITANTE)", 
                        fill="lightcoral", font=("Arial", 20, "bold"), justify="center")
    
    # Subtítulos para porteros y artilleros
    canvas_j.create_text(columna_local_x - 100, 200, text="PORTEROS", 
                        fill="yellow", font=("Arial", 16, "bold"))
    canvas_j.create_text(columna_local_x + 100, 200, text="ARTILLEROS", 
                        fill="yellow", font=("Arial", 16, "bold"))
    
    canvas_j.create_text(columna_visitante_x - 100, 200, text="PORTEROS", 
                        fill="yellow", font=("Arial", 16, "bold"))
    canvas_j.create_text(columna_visitante_x + 100, 200, text="ARTILLEROS", 
                        fill="yellow", font=("Arial", 16, "bold"))

    # =========================
    # Crear botones en columnas verticales
    # =========================
    
    def crear_columna_jugadores(equipo, columna_x, es_local=True):
        """Crea una columna vertical de jugadores para un equipo"""
        y_start = 350  # 🔥 AUMENTÉ de 300 a 350 para mover botones más abajo
        y_spacing = 120  # Espacio entre botones
        
        # PORTEROS (columna izquierda dentro del equipo)
        x_porteros = columna_x - 100 if es_local else columna_x - 100
        for i, jugador_nombre in enumerate(jugadores_img[equipo]["porteros"]):  # 🔥 CAMBIÉ img_path por jugador_nombre
            try:
                # 🔥 AGREGAR .png aquí para cargar la imagen
                imagen_jugador = ImageTk.PhotoImage(Image.open(f"{jugador_nombre}.png").resize((100, 100), Image.Resampling.LANCZOS))
            except Exception as e:
                print(f"Error cargando imagen de {jugador_nombre}:", e)
                imagen_jugador = None
            
            boton = tk.Button(juego, image=imagen_jugador, bd=2, bg="cyan")
            boton.config(command=partial(seleccionar_jugador, equipo, jugador_nombre, boton))  # 🔥 USAR jugador_nombre
            boton.place(x=x_porteros, y=y_start + (i * y_spacing), anchor="center")
            boton.imagen = imagen_jugador
            botones_jugadores.append(boton)
            
            # Nombre del jugador debajo del botón
            nombre_display = jugador_nombre.replace("_", " ").title()
            canvas_j.create_text(x_porteros, y_start + (i * y_spacing) + 60, 
                               text=nombre_display, fill="white", font=("Arial", 10, "bold"))

        # JUGADORES/ARTILLEROS (columna derecha dentro del equipo)
        x_jugadores = columna_x + 100 if es_local else columna_x + 100
        for i, jugador_nombre in enumerate(jugadores_img[equipo]["jugadores"]):  # 🔥 CAMBIÉ img_path por jugador_nombre
            try:
                # 🔥 AGREGAR .png aquí para cargar la imagen
                imagen_jugador = ImageTk.PhotoImage(Image.open(f"{jugador_nombre}.png").resize((100, 100), Image.Resampling.LANCZOS))
            except Exception as e:
                print(f"Error cargando imagen de {jugador_nombre}:", e)
                imagen_jugador = None
            
            boton = tk.Button(juego, image=imagen_jugador, bd=2, bg="cyan")
            boton.config(command=partial(seleccionar_jugador, equipo, jugador_nombre, boton))  # 🔥 USAR jugador_nombre
            boton.place(x=x_jugadores, y=y_start + (i * y_spacing), anchor="center")
            boton.imagen = imagen_jugador
            botones_jugadores.append(boton)
            
            # Nombre del jugador debajo del botón
            nombre_display = jugador_nombre.replace("_", " ").title()
            canvas_j.create_text(x_jugadores, y_start + (i * y_spacing) + 60, 
                               text=nombre_display, fill="white", font=("Arial", 10, "bold"))

    # Crear columnas para ambos equipos
    crear_columna_jugadores(local, columna_local_x, es_local=True)
    crear_columna_jugadores(visitante, columna_visitante_x, es_local=False)

    # =========================
    # Botón CONFIRMAR (CORREGIDO)
    # =========================
    def confirmar():
        todo_correcto = all(len(seleccionados_por_equipo[e]) == 2 for e in equipos_seleccionados)
        if todo_correcto:
            seleccion_final = {}
            for equipo in equipos_seleccionados:
                seleccion = seleccionados_por_equipo[equipo]
                
                # 🔥 VERIFICACIÓN ADICIONAL PARA EVITAR None
                if len(seleccion) != 2:
                    print(f"Error: {equipo} no tiene 2 jugadores seleccionados")
                    return
                
                # Determinar quién es portero y quién es jugador
                portero = next((j for j in seleccion if j in jugadores_img[equipo]["porteros"]), None)
                jugador = next((j for j in seleccion if j in jugadores_img[equipo]["jugadores"]), None)
                
                # 🔥 VERIFICAR QUE NO HAYA None
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

    # Instrucciones
    canvas_j.create_text(ancho_j//2, alto_j - 100, 
                        text="Selecciona 1 PORTERO y 1 ARTILLERO por equipo", 
                        fill="yellow", font=("Arial", 14, "bold"))

    # Botón EXIT (vuelve a cerrar todo)
    boton_exit_j = tk.Button(juego, text="EXIT", command=salir, fg="black", bg="red",
                             font=("Arial",14,"bold"), width=8)
    canvas_j.create_window(ancho_j-50, 40, window=boton_exit_j, anchor="ne")

# =========================
# ANIMACIÓN MONEDA
# =========================
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

    # === GIF animado ===
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

# =========================
# SELECCIÓN DE EQUIPOS
# =========================
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

    # mapeo para buscar botones por nombre cuando necesitemos deseleccionar
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
                # quitar el último seleccionado y marcar su botón como no seleccionado
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

    # Botón continuar a moneda
    boton_continuar = tk.Button(seleccion, text="Continuar", bg="lightgreen", fg="black",
                                font=("Algerian",22,"bold"), width=15, height=2,
                                command=lambda: lanzar_moneda(equipos_seleccionados))
    boton_continuar.place(relx=0.5, rely=0.6, anchor="center")

# =========================
# MENÚ PRINCIPAL (MODIFICADO)
# =========================
# Fondo y texto (ya definidas ancho/alto arriba)
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

# NUEVO BOTÓN: HISTORIAL
boton_historial = tk.Button(ventana, text="Historial", fg="black", bg="lightblue",
                           font=("Algerian", 20),width=15, height=1, command=abrir_historial)
boton_historial.place(relx=0.5, rely=0.45, anchor="center")

boton_exit = tk.Button(ventana, text="EXIT", command=salir, fg="black", bg="red",
                       font=("Arial",14,"bold"), relief="raised", width=8)
canvas.create_window(ancho-50, 40, window=boton_exit, anchor="ne")

# =========================
# INICIAR CLIENTE AL ARRANCAR LA INTERFAZ
# =========================
cliente_raspberry.conectar_raspberry()

# Agregar botón de reconexión en el menú principal
boton_reconectar = tk.Button(ventana, text="Reconectar Raspberry", fg="black", bg="orange",
                           font=("Algerian", 16), width=18, height=1,
                           command=cliente_raspberry.conectar_raspberry)
boton_reconectar.place(relx=0.5, rely=0.55, anchor="center")

# Botón para forzar configuración desde Raspberry
boton_config_raspberry = tk.Button(ventana, text="Config desde Raspberry", fg="black", bg="lightgreen",
                                 font=("Algerian", 16), width=18, height=1,
                                 command=cliente_raspberry.preguntar_inicio_juego)
boton_config_raspberry.place(relx=0.5, rely=0.65, anchor="center")

ventana.mainloop()