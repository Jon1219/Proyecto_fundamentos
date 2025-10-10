import tkinter as tk
from PIL import Image, ImageTk
import pygame

# =========================
# VENTANA PRINCIPAL (MENÚ)
# =========================
ventana = tk.Tk()
ventana.title("Menú principal - Champions Game")
ventana.state("zoomed")

ventana.update()
ancho = ventana.winfo_width()
alto = ventana.winfo_height()

# Fondo
imagen_fondo = Image.open("Champions.png").resize((ancho, alto), Image.Resampling.LANCZOS)
fondo = ImageTk.PhotoImage(imagen_fondo)

# Texto (logo o título)
imagen_texto = Image.open("Texto.png")
texto = ImageTk.PhotoImage(imagen_texto)

# -------------------------
# CANVAS PRINCIPAL
# -------------------------
canvas = tk.Canvas(ventana, width=ancho, height=alto)
canvas.pack(fill="both", expand=True)
canvas.create_image(0, 0, image=fondo, anchor="nw")
canvas.create_image(ancho // 2, 100, image=texto, anchor="center")

# Mantener referencias
canvas.fondo = fondo
canvas.texto = texto

# =========================
# FUNCIÓN: ABRIR SELECCIÓN DE EQUIPOS
# =========================
def abrir_seleccion_equipos():
    pygame.mixer.music.stop()  # Detenemos la música
    ventana.withdraw()  # Ocultamos la ventana principal

    # Nueva ventana
    seleccion = tk.Toplevel()
    seleccion.title("Selección de equipos")
    seleccion.state("zoomed")

    seleccion.update()
    ancho2 = seleccion.winfo_width()
    alto2 = seleccion.winfo_height()

    # Fondo para la selección (Champions.png como ejemplo)
    fondo_sel_img = Image.open("Champions.png").resize((ancho2, alto2), Image.Resampling.LANCZOS)
    fondo_sel = ImageTk.PhotoImage(fondo_sel_img)

    canvas2 = tk.Canvas(seleccion, width=ancho2, height=alto2)
    canvas2.pack(fill="both", expand=True)
    canvas2.create_image(0, 0, image=fondo_sel, anchor="nw")
    canvas2.fondo_sel = fondo_sel  # mantener referencia

    # Título
    canvas2.create_text(ancho2 // 2, 100, text="SELECCIONA TU EQUIPO",
                        fill="white", font=("Algerian", 40, "bold"))

    # =========================
    # Selección de equipos
    # =========================
    equipos_seleccionados = []

    # Cargar imágenes de los equipos
    img_city = Image.open("CITY_F.png").resize((150, 150), Image.Resampling.LANCZOS)
    img_city_tk = ImageTk.PhotoImage(img_city)
    img_milan = Image.open("milan_f.png").resize((150, 150), Image.Resampling.LANCZOS)
    img_milan_tk = ImageTk.PhotoImage(img_milan)
    img_united = Image.open("united_f.png").resize((150, 150), Image.Resampling.LANCZOS)
    img_united_tk = ImageTk.PhotoImage(img_united)

    # Función para actualizar el color del botón
    def actualizar_color(boton, seleccionado):
        boton.config(bg="red" if seleccionado else "cyan")

    # Función seleccionar equipo con límite de 2
    def seleccionar_equipo(nombre, boton):
        if nombre in equipos_seleccionados:
            equipos_seleccionados.remove(nombre)
            actualizar_color(boton, False)
        else:
            if len(equipos_seleccionados) < 2:
                equipos_seleccionados.append(nombre)
                actualizar_color(boton, True)
            else:
                # Reemplazar el último elegido
                ultimo = equipos_seleccionados.pop()
                for b, n in botones.items():
                    if n == ultimo:
                        actualizar_color(b, False)
                        break
                equipos_seleccionados.append(nombre)
                actualizar_color(boton, True)
        print("Equipos seleccionados:", equipos_seleccionados)

    # =========================
    # Botones de imagen
    # =========================
    boton_city = tk.Button(seleccion, image=img_city_tk, bd=2, bg="cyan",
                           command=lambda: seleccionar_equipo("Manchester City", boton_city))
    boton_milan = tk.Button(seleccion, image=img_milan_tk, bd=2, bg="cyan",
                            command=lambda: seleccionar_equipo("AC Milan", boton_milan))
    boton_united = tk.Button(seleccion, image=img_united_tk, bd=2, bg="cyan",
                             command=lambda: seleccionar_equipo("Manchester United", boton_united))

    # Ubicación
    boton_city.place(relx=0.3, rely=0.3, anchor="center")
    boton_milan.place(relx=0.5, rely=0.3, anchor="center")
    boton_united.place(relx=0.7, rely=0.3, anchor="center")

    # Guardar referencias de imagen
    canvas2.img_city_tk = img_city_tk
    canvas2.img_milan_tk = img_milan_tk
    canvas2.img_united_tk = img_united_tk

    botones = {boton_city: "Manchester City", boton_milan: "AC Milan", boton_united: "Manchester United"}

    # =========================
    # Botón continuar
    # =========================
    def continuar():
        print("Continuando con equipos:", equipos_seleccionados)
        seleccion.destroy()  # Cierra ventana de selección

        # =========================
        # NUEVA VENTANA DE JUEGO
        # =========================
        juego = tk.Toplevel()
        juego.title("Ventana de Juego")
        juego.state("zoomed")

        juego.update()
        ancho_j = juego.winfo_width()
        alto_j = juego.winfo_height()

        # Fondo Champions.png
        fondo_juego_img = Image.open("Champions.png").resize((ancho_j, alto_j), Image.Resampling.LANCZOS)
        fondo_juego = ImageTk.PhotoImage(fondo_juego_img)

        canvas_j = tk.Canvas(juego, width=ancho_j, height=alto_j)
        canvas_j.pack(fill="both", expand=True)
        canvas_j.create_image(0, 0, image=fondo_juego, anchor="nw")
        canvas_j.fondo_juego = fondo_juego  # mantener referencia

    boton_continuar = tk.Button(seleccion, text="Continuar", bg="lightgreen", fg="black",
                                font=("Algerian", 22, "bold"), width=15, height=2, command=continuar)
    boton_continuar.place(relx=0.5, rely=0.6, anchor="center")

    # Botón para volver al menú principal
    boton_volver = tk.Button(seleccion, text="Volver al Menú",
                             command=lambda: [seleccion.destroy(), ventana.deiconify()],
                             bg="Green", fg="white", font=("Arial", 16, "bold"))
    canvas2.create_window(100, 60, window=boton_volver)

# =========================
# BOTONES DEL MENÚ PRINCIPAL
# =========================
boton_new_partida = tk.Button(ventana, text="Start new game", fg="black", bg="lightblue",
                              font=("Algerian", 20), command=abrir_seleccion_equipos)
boton_new_partida.place(relx=0.5, rely=0.25, anchor="center")

boton_exit = tk.Button(ventana, text="EXIT", command=ventana.destroy, fg="black", bg="red",
                       font=("Arial", 14, "bold"), relief="raised", width=8)
canvas.create_window(ancho - 50, 40, window=boton_exit, anchor="ne")

# =========================
# MÚSICA DE FONDO
# =========================
try:
    pygame.mixer.init()
    pygame.mixer.music.load("musica_fondo.mp3")
    pygame.mixer.music.play(-1)
except Exception as e:
    print("Error al reproducir música:", e)

ventana.mainloop()
