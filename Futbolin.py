import tkinter as tk
from PIL import Image, ImageTk
import pygame
from functools import partial
import random

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
# FUNCIÓN SALIR (DETENER MÚSICA Y CERRAR TODO)
# =========================
def salir():
    try:
        pygame.mixer.music.stop()
        pygame.mixer.quit()
    except:
        pass
    ventana.destroy()

# =========================
# VENTANA PRINCIPAL
# =========================
ventana = tk.Tk()
ventana.title("Menú principal - Champions Game")
ventana.state("zoomed")
ventana.update()
ancho = ventana.winfo_width()
alto = ventana.winfo_height()

# Fondo y texto
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

    fondo_j_img = Image.open("Champions.png").resize((ancho_j, alto_j), Image.Resampling.LANCZOS)
    fondo_j = ImageTk.PhotoImage(fondo_j_img)
    canvas_j = tk.Canvas(juego, width=ancho_j, height=alto_j)
    canvas_j.pack(fill="both", expand=True)
    canvas_j.create_image(0,0,image=fondo_j, anchor="nw")
    canvas_j.fondo_j = fondo_j

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
            imagen_jugador = ImageTk.PhotoImage(Image.open(img_path).resize((100,100), Image.Resampling.LANCZOS))
            boton = tk.Button(juego, image=imagen_jugador, bd=2, bg="cyan")
            boton.config(command=partial(seleccionar_jugador, equipo, nombre_jugador, boton))
            boton.place(relx=x_positions[i], rely=y_positions[equipo_idx], anchor="center")
            boton.imagen = imagen_jugador
            botones_jugadores.append(boton)

    # Botón confirmar
    def confirmar():
        todo_correcto = all(len(seleccionados_por_equipo[e]) == 2 for e in equipos_seleccionados)
        if todo_correcto:
            for equipo in equipos_seleccionados:
                portero = seleccionados_por_equipo[equipo][0]
                jugador = seleccionados_por_equipo[equipo][1]
                print(f"{equipo} -> Portero: {portero}, Jugador: {jugador}")
            print("¡Selección confirmada!")
        else:
            print("Debes seleccionar 2 jugadores por cada equipo")

    boton_confirmar = tk.Button(juego, text="Confirmar", bg="green", fg="white",
                                font=("Arial",16,"bold"), width=12, height=2,
                                command=confirmar)
    boton_confirmar.place(relx=0.5, rely=0.85, anchor="center")

    # Botón EXIT
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

    fondo_img = Image.open("Champions.png").resize((ancho_m, alto_m), Image.Resampling.LANCZOS)
    fondo = ImageTk.PhotoImage(fondo_img)
    canvas_m = tk.Canvas(ventana_moneda, width=ancho_m, height=alto_m)
    canvas_m.pack(fill="both", expand=True)
    canvas_m.create_image(0,0,image=fondo, anchor="nw")
    canvas_m.fondo = fondo

    # Imágenes moneda
    img_cara = ImageTk.PhotoImage(Image.open("cara.png").resize((150,150), Image.Resampling.LANCZOS))
    img_cruz = ImageTk.PhotoImage(Image.open("cruz.png").resize((150,150), Image.Resampling.LANCZOS))
    
    canvas_m.img_cara = img_cara
    canvas_m.img_cruz = img_cruz

    moneda_canvas = canvas_m.create_image(ancho_m//2, alto_m//2, image=img_cara)

    # Animación recursiva
    def animar_moneda(contador=0):
        if contador < 15:
            canvas_m.itemconfig(moneda_canvas, image=img_cara if contador%2==0 else img_cruz)
            ventana_moneda.after(100, lambda: animar_moneda(contador+1))
        else:
            resultado = random.choice(["cara","cruz"])
            canvas_m.itemconfig(moneda_canvas, image=img_cara if resultado=="cara" else img_cruz)

            if resultado == "cara":
                local = equipos_seleccionados[0]
                visitante = equipos_seleccionados[1]
            else:
                local = equipos_seleccionados[1]
                visitante = equipos_seleccionados[0]

            canvas_m.create_text(ancho_m//2, alto_m//2 + 120, text=f"Local: {local}\nVisitante: {visitante}",
                                 font=("Algerian",30,"bold"), fill="white")

            ventana_moneda.after(2000, lambda: (ventana_moneda.destroy(), abrir_seleccion_jugadores(equipos_seleccionados)))

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

    fondo_sel_img = Image.open("Champions.png").resize((ancho2, alto2), Image.Resampling.LANCZOS)
    fondo_sel = ImageTk.PhotoImage(fondo_sel_img)
    canvas2 = tk.Canvas(seleccion, width=ancho2, height=alto2)
    canvas2.pack(fill="both", expand=True)
    canvas2.create_image(0,0,image=fondo_sel, anchor="nw")
    canvas2.fondo_sel = fondo_sel
    canvas2.create_text(ancho2//2, 100, text="SELECCIONA TU EQUIPO", fill="white", font=("Algerian",40,"bold"))

    equipos_seleccionados = []

    # Imágenes equipos
    img_city = ImageTk.PhotoImage(Image.open("CITY_F.png").resize((150,150), Image.Resampling.LANCZOS))
    img_milan = ImageTk.PhotoImage(Image.open("milan_f.png").resize((150,150), Image.Resampling.LANCZOS))
    img_united = ImageTk.PhotoImage(Image.open("united_f.png").resize((150,150), Image.Resampling.LANCZOS))

    def actualizar_color(boton, seleccionado):
        boton.config(bg="red" if seleccionado else "cyan")

    def seleccionar_equipo(nombre, boton):
        if nombre in equipos_seleccionados:
            equipos_seleccionados.remove(nombre)
            actualizar_color(boton, False)
        else:
            if len(equipos_seleccionados) < 2:
                equipos_seleccionados.append(nombre)
                actualizar_color(boton, True)
            else:
                ultimo = equipos_seleccionados.pop()
                for b, n in botones.items():
                    if n == ultimo:
                        actualizar_color(b, False)
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

    botones = {boton_city: "Manchester City", boton_milan: "AC Milan", boton_united: "Manchester United"}

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
boton_new_partida = tk.Button(ventana, text="Start new game", fg="black", bg="lightblue",
                              font=("Algerian",20), command=abrir_seleccion_equipos)
boton_new_partida.place(relx=0.5, rely=0.25, anchor="center")

boton_exit = tk.Button(ventana, text="EXIT", command=salir, fg="black", bg="red",
                       font=("Arial",14,"bold"), relief="raised", width=8)
canvas.create_window(ancho-50, 40, window=boton_exit, anchor="ne")

ventana.mainloop()
