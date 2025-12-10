import tkinter as tk
from tkinter import PhotoImage, messagebox
import threading
import time
import os

# ---------------- CONFIGURACIÓN ----------------
# Se dejan únicamente las GPIO 17, 22 y 27
GPIO_PINS = [17, 22, 27] 
gpio_files = {pin: f"gpio{pin}.txt" for pin in GPIO_PINS}

# Crear archivos si no existen
for pin in GPIO_PINS:
    if not os.path.exists(gpio_files[pin]):
        # Inicializa todos los pines en '0' (apagado)
        with open(gpio_files[pin], "w") as f:
            f.write("0")

# ---------------- FUNCIONES DE ARCHIVO Y BACKEND SIMULADO ----------------
def write_gpio(pin, value):
    """Función real que escribe el estado en el archivo."""
    try:
        with open(gpio_files[pin], "w") as f:
            f.write(str(value))
    except Exception as e:
        print(f"Error escribiendo en {gpio_files[pin]}: {e}")

def read_gpio(pin):
    """Lee el estado actual del archivo."""
    try:
        with open(gpio_files[pin], "r") as f:
            return f.read().strip()
    except Exception:
        return "0"

def run_backend(pin, status, backend):
    """
    Simulación de la llamada al backend (Shell, C, Ensamblador).
    En el proyecto real, aquí iría el subprocess.run('./control_c', ...)
    """
    print(f"-> [LLAMADA BACKEND {backend}] GPIO {pin} establecido a {status}")
    write_gpio(pin, status)

# ---------------- TIMER ----------------
timer_running = False

def timer_toggle():
    global timer_running
    timer_running = not timer_running

    if timer_running:
        timer_button.config(text="STOP TIMER", bg="#C70039")
        # Usamos un hilo para no bloquear la GUI
        threading.Thread(target=timer_process, daemon=True).start()
    else:
        timer_button.config(text="START TIMER", bg="#58D68D")

def timer_process():
    global timer_running
    state = 0
    while timer_running:
        # 0 -> 1 y 1 -> 0
        state = 1 - state
        for pin in GPIO_PINS:
            # Usamos el backend simulado para cambiar el estado
            run_backend(pin, state, "TIMER (BASH)") 
        time.sleep(5)

# ---------------- VENTANA PRINCIPAL (SETUP) ----------------
root = tk.Tk()
root.title("SIMULACIÓN GPIO - RASPBERRY PI")
root.geometry("700x650")
root.config(bg="#1e1e1e")

# Título principal
title = tk.Label(root, text="SIMULADOR GPIO", font=("Arial", 20, "bold"), fg="#58D68D", bg="#1e1e1e")
title.pack(pady=15)

# ---------------- IMPLEMENTACIÓN DEL SCROLLBAR ----------------

# 1. Crear el Frame Contenedor para Canvas y Scrollbar
container_frame = tk.Frame(root, bg="#1e1e1e")
container_frame.pack(fill="both", expand=True, padx=20)

# 2. Crear el Canvas
canvas = tk.Canvas(container_frame, bg="#1e1e1e", highlightthickness=0)
canvas.pack(side="left", fill="both", expand=True)

# 3. Crear la Scrollbar
scrollbar = tk.Scrollbar(container_frame, orient="vertical", command=canvas.yview)
scrollbar.pack(side="right", fill="y")

# 4. Configurar el Canvas para usar la Scrollbar
canvas.configure(yscrollcommand=scrollbar.set)
canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion = canvas.bbox("all")))

# 5. Crear el Frame Desplazable (aquí irá todo el contenido de los GPIOs)
scrollable_frame = tk.Frame(canvas, bg="#1e1e1e")

# 6. Añadir el Frame Desplazable al Canvas
canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=650) 
# NOTA: El ancho (width=650) es crucial para evitar el desplazamiento horizontal.

# ---------------- Cargar imágenes ----------------
try:
    # Usando ooff.png, que es el nombre de tu archivo
    img_on = PhotoImage(file="on.gif")
    img_off = PhotoImage(file="off.gif") 
except Exception as e:
    messagebox.showerror("Error de Imagen", f"Error al cargar imágenes (on.png o ooff.png). Asegúrate de que los nombres son correctos. Error: {e}")
    root.destroy()
    exit()

gpio_labels = {}

# ---------------- FUNCIÓN PARA CREAR BLOQUE GPIO ----------------
def crear_bloque_gpio(parent, pin):
    """Crea y empaca un bloque completo de control para un solo GPIO."""
    frame = tk.Frame(parent, bg="#2d2d2d", bd=3, relief="ridge")
    frame.pack(pady=15, fill="x", padx=10) # Menos padx aquí para darle espacio al scrollbar

    # Título GPIO
    tk.Label(frame, text=f"GPIO {pin}", font=("Arial", 16, "bold"),
             bg="#2d2d2d", fg="white").pack(pady=10)

    # Imagen de estado
    img_label = tk.Label(frame, image=img_off, bg="#2d2d2d")
    img_label.pack()
    gpio_labels[pin] = img_label

    # Contenedor botones
    btn_container = tk.Frame(frame, bg="#2d2d2d")
    btn_container.pack(pady=10)

    # --- Botones BASH (Llaman a run_backend simulado) ---
    tk.Label(btn_container, text="BASH:", fg="white", bg="#2d2d2d", font=("Arial", 10)).grid(row=0, column=0, sticky='w')
    tk.Button(btn_container, text="ON", width=8, bg="#58D68D", fg="#1e1e1e", 
              command=lambda p=pin: run_backend(p, 1, "BASH")).grid(row=0, column=1, padx=5)
    tk.Button(btn_container, text="OFF", width=8, bg="#C70039", fg="white", 
              command=lambda p=pin: run_backend(p, 0, "BASH")).grid(row=0, column=2, padx=5)

    # --- Botones C ---
    tk.Label(btn_container, text="C:", fg="white", bg="#2d2d2d", font=("Arial", 10)).grid(row=1, column=0, sticky='w')
    tk.Button(btn_container, text="ON", width=8, bg="#58D68D", fg="#1e1e1e", 
              command=lambda p=pin: run_backend(p, 1, "C")).grid(row=1, column=1, padx=5)
    tk.Button(btn_container, text="OFF", width=8, bg="#C70039", fg="white", 
              command=lambda p=pin: run_backend(p, 0, "C")).grid(row=1, column=2, padx=5)

    # --- Botones ASM ---
    tk.Label(btn_container, text="ENSAMBLADOR:", fg="white", bg="#2d2d2d", font=("Arial", 10)).grid(row=2, column=0, sticky='w')
    tk.Button(btn_container, text="ON", width=8, bg="#58D68D", fg="#1e1e1e", 
              command=lambda p=pin: run_backend(p, 1, "ENSAMBLADOR")).grid(row=2, column=1, padx=5)
    tk.Button(btn_container, text="OFF", width=8, bg="#C70039", fg="white", 
              command=lambda p=pin: run_backend(p, 0, "ENSAMBLADOR")).grid(row=2, column=2, padx=5)

# ---------------- CREAR BLOQUES ----------------
# Se empaquetan dentro del frame desplazable (scrollable_frame)
for pin in GPIO_PINS:
    crear_bloque_gpio(scrollable_frame, pin)

# ---------------- BOTÓN TIMER (Fuera del Scroll) ----------------
timer_frame = tk.Frame(root, bg="#1e1e1e")
timer_frame.pack(pady=20)

timer_button = tk.Button(timer_frame, text="START TIMER", width=15, height=2,
                         font=("Arial", 14, "bold"), bg="#58D68D", fg="#1e1e1e",
                         command=timer_toggle)
timer_button.pack()

# ---------------- ACTUALIZAR IMÁGENES ----------------
def update_images():
    """Lee archivos periódicamente y actualiza la GUI."""
    for pin in GPIO_PINS:
        state = read_gpio(pin)
        gpio_labels[pin].config(image=img_on if state == "1" else img_off)
    # Se actualiza cada 500ms
    root.after(500, update_images)

# Iniciar la actualización y el bucle principal
update_images()
root.mainloop()
