import tkinter as tk
from PIL import Image, ImageTk
import pygame

ventana = tk.Tk()
ventana.title("Mi primera interfaz gráfica")
ventana.state("zoomed")

ventana.update()
ancho = ventana.winfo_width()
alto = ventana.winfo_height()

# Imagen de fondo
imagen_fondo = Image.open("Champions.png")
imagen_fondo = imagen_fondo.resize((ancho, alto), Image.Resampling.LANCZOS)
fondo = ImageTk.PhotoImage(imagen_fondo)

# Imagen de texto superpuesta
imagen_texto = Image.open("Texto.png")
texto = ImageTk.PhotoImage(imagen_texto)

canvas = tk.Canvas(ventana, width=ancho, height=alto)
canvas.pack(fill="both", expand=True)

# Poner imagen de fondo
canvas.create_image(0, 0, image=fondo, anchor="nw")

# Poner imagen de texto superpuesta (centrada horizontalmente y arriba)
canvas.create_image(ancho // 2, 100, image=texto, anchor="center")

# Texto debajo de la imagen de texto
boton_new_partida = tk.Button(ventana, text="Start new game", fg="Black", bg="Lightblue", font=("Algerian", 20))
boton_new_partida.place(relx=0.5, rely=0.25, anchor="center")


# Botón EXIT en esquina superior derecha
boton_exit = tk.Button(ventana, text="EXIT", command=ventana.destroy, fg="Black", bg="red")
canvas.create_window(ancho - 20, 20, window=boton_exit, anchor="ne")

# Mantener referencias para que las imágenes no se borren
canvas.fondo = fondo
canvas.texto = texto

# Inicializar pygame mixer y reproducir música en bucle
pygame.mixer.init()
pygame.mixer.music.load("musica_fondo.mp3")
pygame.mixer.music.play(-1)  # -1 para loop infinito

ventana.mainloop()
