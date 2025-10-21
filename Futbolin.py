import tkinter as tk
from PIL import Image, ImageTk
import pygame
from functools import partial
import random
import os

# =========================
# INICIALIZAR MÚSICA
# =========================
try:
    pygame.mixer.init()
    pygame.mixer.music.load("musica_fondo.mp3")
    pygame.mixer.music.play(-1)  # Loop infinito
except Exception as e:
    print("Error al reproducir música:", e)

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
# FASE DE PENALES CON ANIMACIÓN DEL PORTERO
# =========================
def iniciar_penales(equipos_seleccionados, seleccion_final):
    ventana_penales = tk.Toplevel()
    ventana_penales.title("Tanda de penales")
    ventana_penales.state("zoomed")
    ventana_penales.update()
    ancho_p = ventana_penales.winfo_width()
    alto_p = ventana_penales.winfo_height()

    # Fondo
    try:
        fondo_img = Image.open("cancha.png").resize((ancho_p, alto_p), Image.Resampling.LANCZOS)
        fondo = ImageTk.PhotoImage(fondo_img)
    except Exception as e:
        print("Error cargando cancha.png:", e)
        # fallback a fondo simple
        fondo = None

    canvas_p = tk.Canvas(ventana_penales, width=ancho_p, height=alto_p)
    canvas_p.pack(fill="both", expand=True)
    if fondo:
        canvas_p.create_image(0, 0, image=fondo, anchor="nw")
        canvas_p.fondo = fondo
    else:
        canvas_p.create_rectangle(0,0,ancho_p,alto_p,fill="darkgreen")

    # Variables del juego
    local, visitante = equipos_seleccionados
    goles = {local: 0, visitante: 0}
    tiros = {local: 0, visitante: 0}
    turno = [local]   # mutable container
    total_tiros = 0
    posiciones_bloqueadas = []

    # Cargar imágenes de jugadores (espera nombres sin extensión en seleccion_final)
    imagenes = {}
    for equipo in equipos_seleccionados:
        imagenes[equipo] = {"portero": None, "jugador": None}
        try:
            p_name = seleccion_final[equipo]['portero']
            j_name = seleccion_final[equipo]['jugador']
            portero_img = Image.open(f"{p_name}.png").resize((180,180), Image.Resampling.LANCZOS)
            jugador_img = Image.open(f"{j_name}.png").resize((180,180), Image.Resampling.LANCZOS)
            imagenes[equipo]["portero"] = ImageTk.PhotoImage(portero_img)
            imagenes[equipo]["jugador"] = ImageTk.PhotoImage(jugador_img)
        except Exception as e:
            print("Error cargando imagen de jugador:", e)

    # Texto principal
    texto_turno = canvas_p.create_text(ancho_p//2, 80, text=f"Turno: {local}",
                                       fill="white", font=("Algerian", 36, "bold"))
    texto_marcador = canvas_p.create_text(ancho_p//2, 150,
                                          text=f"{local}: 0   -   {visitante}: 0",
                                          fill="yellow", font=("Arial", 28, "bold"))

    # Crear portero y jugador (si la imagen falta, no falla)
    # Crear portero y jugador (si la imagen falta, no falla)
    x_portero_inicial = ancho_p * 0.25
    x_jugador_inicial = ancho_p * 0.75
    y_personajes = alto_p * 0.6

# CORRECCIÓN: Portero del visitante, jugador del local
    img_port = imagenes[visitante]["portero"] if imagenes[visitante]["portero"] else None
    img_jug = imagenes[local]["jugador"] if imagenes[local]["jugador"] else None

    portero_img = canvas_p.create_image(x_portero_inicial, y_personajes, image=img_port)
    jugador_img = canvas_p.create_image(x_jugador_inicial, y_personajes, image=img_jug)

    # Cambiar turno (y actualizar imágenes)
    def cambiar_turno():
        turno[0] = visitante if turno[0] == local else local
        canvas_p.itemconfig(texto_turno, text=f"Turno: {turno[0]}")
    
    # CORRECCIÓN: El portero es del equipo contrario al que tira
        equipo_portero = visitante if turno[0] == local else local
        equipo_jugador = turno[0]  # El que tira
    
    # Actualizar imágenes
        if imagenes[equipo_portero]["portero"]:
            canvas_p.itemconfig(portero_img, image=imagenes[equipo_portero]["portero"])
        if imagenes[equipo_jugador]["jugador"]:
            canvas_p.itemconfig(jugador_img, image=imagenes[equipo_jugador]["jugador"])

    # Terminar tanda
    def terminar():
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

        # Mostrar recuadro final
        rect = canvas_p.create_rectangle(ancho_p//2 - 320, alto_p//2 - 170,
                                         ancho_p//2 + 320, alto_p//2 + 170,
                                         fill="black", outline="white", width=3)
        text = canvas_p.create_text(ancho_p//2, alto_p//2, text=mensaje,
                                    fill="white", font=("Algerian", 28, "bold"))

    # Movimiento del portero con animación hacia dest_x; si regresar=True vuelve al centro
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
            # continuar movimiento hasta el destino
            if (paso > 0 and actual_x < dest_x) or (paso < 0 and actual_x > dest_x):
                ventana_penales.after(15, mover)
            else:
                # si se pide regresar, esperar y volver al centro
                if regresar:
                    ventana_penales.after(600, lambda: animar_portero(x_portero_inicial, regresar=False))
        mover()

    # Lógica cuando se presiona una posición
    def lanzar(pos):
        nonlocal total_tiros
        jugador_actual = turno[0]

        # Mostrar resultado
        if pos in posiciones_bloqueadas:
            resultado = "ATAJADO 🧤"
            color = "red"
        else:
            resultado = "¡GOL! ⚽"
            color = "lime"
            goles[jugador_actual] += 1

        tiros[jugador_actual] += 1
        total_tiros += 1

        # Mostrar resultado en pantalla (borrar resultados previos en esa zona)
        resultado_text = canvas_p.create_text(ancho_p//2, alto_p//2, text=resultado,
                                             fill=color, font=("Algerian", 50, "bold"))
        canvas_p.itemconfig(texto_marcador,
                            text=f"{local}: {goles[local]}   -   {visitante}: {goles[visitante]}")

        # Desactivar botones hasta siguiente
        for b in botones:
            b.config(state="disabled")

        # animar regreso del portero al centro antes del siguiente tiro
        animar_portero(x_portero_inicial, regresar=True)

        # decidir siguiente
        if total_tiros < 10:
            ventana_penales.after(1400, lambda: (canvas_p.delete(resultado_text), siguiente_tiro()))
        else:
            ventana_penales.after(1400, lambda: (canvas_p.delete(resultado_text), terminar()))

    # Prepara siguiente tiro: alterna turno, limpia botones y crea nuevos
    def siguiente_tiro():
        cambiar_turno()
        crear_botones()

    # Crear botones de las 6 posiciones y marcar las bloqueadas en rojo
    botones = []
    botones_widgets = []  # guardamos referencias
    posiciones_rects = []  # rectángulos de color (si se quieren más adelante)
    def crear_botones():
        nonlocal posiciones_bloqueadas, botones, botones_widgets, posiciones_rects
        # destruir botones anteriores
        for b in botones_widgets:
            try:
                b.destroy()
            except:
                pass
        botones_widgets = []
        botones = []

        # elegir bloqueos consecutivos
        inicio = random.randint(1, 5)
        posiciones_bloqueadas = [inicio, inicio + 1]

        # crear botones y colorear bloques en rojo
        for i in range(6):
            numero = i + 1
            color_fondo = "red" if numero in posiciones_bloqueadas else "lightblue"
            b = tk.Button(ventana_penales, text=str(numero), font=("Algerian", 22, "bold"),
                          bg=color_fondo, fg="black", width=6, height=2,
                          command=lambda n=numero: lanzar(n))
            b.place(relx=0.2 + (i * 0.1), rely=0.85, anchor="center")
            botones_widgets.append(b)
            botones.append(b)

        # animar al portero hacia la zona bloqueada (centro entre las dos posiciones)
        pos_media = (posiciones_bloqueadas[0] + posiciones_bloqueadas[1]) / 2.0
        # calcular x destino proporcionalmente (ajuste para que coincida con relx usado)
        # relx usado: 0.2 + i*0.1 -> x = ancho_p * (0.2 + (pos_media-1)*0.1)
        x_destino = ancho_p * (0.2 + (pos_media - 1) * 0.1)
        animar_portero(x_destino, regresar=False)

    # iniciar primera tanda de botones (ya con portero en centro)
    crear_botones()

    # Botón de salida
    boton_exit_p = tk.Button(ventana_penales, text="EXIT", command=salir,
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
        canvas_j.create_image(0,0,image=fondo_j, anchor="nw")
        canvas_j.fondo_j = fondo_j
    else:
        canvas_j.create_rectangle(0,0,ancho_j,alto_j,fill="black")

    jugadores_img = {
        "Manchester City": ["ederson.png", "haaland.png", "aguero.png"],
        "AC Milan": ["dida.png", "ibra.png", "dinho.png"],
        "Manchester United": ["Van_der.png", "BICHO.png", "rooney.png"]
    }

    x_positions = [0.25,0.5,0.75]
    y_positions = [0.35,0.6]
    seleccionados_por_equipo = {equipo: [] for equipo in equipos_seleccionados}
    botones_jugadores = []

    def actualizar_color(boton, seleccionado):
        boton.config(bg="red" if seleccionado else "cyan")

    def seleccionar_jugador(equipo, jugador_nombre, boton):
        if jugador_nombre in seleccionados_por_equipo[equipo]:
            seleccionados_por_equipo[equipo].remove(jugador_nombre)
            actualizar_color(boton, False)
        else:
            if len(seleccionados_por_equipo[equipo]) < 2:
                seleccionados_por_equipo[equipo].append(jugador_nombre)
                actualizar_color(boton, True)
            else:
                print(f"Ya seleccionaste 2 jugadores de {equipo}")
        print("Selección actual:", seleccionados_por_equipo)

    # Botones de jugadores
    for equipo_idx, equipo in enumerate(equipos_seleccionados):
        for i, img_path in enumerate(jugadores_img[equipo]):
            nombre_jugador = img_path.split(".")[0]
            try:
                imagen_jugador = ImageTk.PhotoImage(Image.open(img_path).resize((150,150), Image.Resampling.LANCZOS))
            except Exception as e:
                print("Error cargando imagen de jugador:", img_path, e)
                imagen_jugador = None
            boton = tk.Button(juego, image=imagen_jugador, bd=2, bg="cyan")
            boton.config(command=partial(seleccionar_jugador, equipo, nombre_jugador, boton))
            boton.place(relx=x_positions[i], rely=y_positions[equipo_idx], anchor="center")
            boton.imagen = imagen_jugador
            botones_jugadores.append(boton)

    # Botón confirmar
    def confirmar():
        todo_correcto = all(len(seleccionados_por_equipo[e]) == 2 for e in equipos_seleccionados)
        if todo_correcto:
            seleccion_final = {}
            for equipo in equipos_seleccionados:
            # Identificar automáticamente quién es portero por el nombre
                porteros = {"ederson", "dida", "Van_der"}
                jugadores_seleccionados = seleccionados_por_equipo[equipo]
            
            # Buscar el portero
                portero = next((j for j in jugadores_seleccionados if j in porteros), None)
                if portero:
                    jugador = next((j for j in jugadores_seleccionados if j != portero), None)
                else:
                # Si no se identifica, usar el primero como portero
                    portero = jugadores_seleccionados[0]
                    jugador = jugadores_seleccionados[1]
            
                seleccion_final[equipo] = {"portero": portero, "jugador": jugador}
        
            print("Selección confirmada:", seleccion_final)
            try:
                juego.destroy()
            except:
                pass
            iniciar_penales(equipos_seleccionados, seleccion_final)
        else:
            print("Debes seleccionar 2 jugadores por cada equipo")

    boton_confirmar = tk.Button(juego, text="Confirmar", bg="green", fg="white",
                                font=("Arial",16,"bold"), width=12, height=2,
                                command=confirmar)
    boton_confirmar.place(relx=0.5, rely=0.85, anchor="center")

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
                           command=lambda: seleccionar_equipo("Manchester City", boton_city))
    boton_milan = tk.Button(seleccion, image=img_milan, bd=2, bg="cyan",
                            command=lambda: seleccionar_equipo("AC Milan", boton_milan))
    boton_united = tk.Button(seleccion, image=img_united, bd=2, bg="cyan",
                             command=lambda: seleccionar_equipo("Manchester United", boton_united))

    boton_city.place(relx=0.3, rely=0.3, anchor="center")
    boton_milan.place(relx=0.5, rely=0.3, anchor="center")
    boton_united.place(relx=0.7, rely=0.3, anchor="center")

    canvas2.img_city = img_city
    canvas2.img_milan = img_milan
    canvas2.img_united = img_united

    botones_map = {
        "Manchester City": boton_city,
        "AC Milan": boton_milan,
        "Manchester United": boton_united
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
# MENÚ PRINCIPAL
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
                              font=("Algerian",20), command=abrir_seleccion_equipos)
boton_new_partida.place(relx=0.5, rely=0.25, anchor="center")

boton_exit = tk.Button(ventana, text="EXIT", command=salir, fg="black", bg="red",
                       font=("Arial",14,"bold"), relief="raised", width=8)
canvas.create_window(ancho-50, 40, window=boton_exit, anchor="ne")

ventana.mainloop()
