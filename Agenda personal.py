# agenda_personal.py
"""
Yo desarrollé una Agenda Personal en Python con interfaz gráfica usando Tkinter.
La aplicación me permite agregar, visualizar y eliminar eventos.
También utilicé un archivo JSON para guardar la información y no perderla al cerrar el programa.
"""

import json       # Para guardar y cargar los eventos en un archivo
import os         # Para verificar si el archivo existe
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta  # Para manejar fechas y horas

# Nombre del archivo donde se guardarán los eventos
DATA_FILE = 'agenda_events.json'

class AgendaApp(tk.Tk):
    def __init__(self):
        # Inicializo la ventana principal
        super().__init__()
        self.title('Agenda Personal')
        self.geometry('640x360')   # Tamaño de la ventana
        self.resizable(False, False)  # Desactivo cambiar tamaño

        # ---- CREO CONTENEDORES (Frames) ----
        # Un frame superior para la lista de eventos
        top = ttk.Frame(self, padding=8)
        top.pack(fill='both', expand=True)

        # Un frame inferior para las entradas y botones
        bottom = ttk.Frame(self, padding=8)
        bottom.pack(fill='x')

        # ---- LISTA DE EVENTOS (Treeview) ----
        ttk.Label(top, text='Eventos programados', font=('Helvetica', 12, 'bold')).pack(anchor='w')

        # Defino columnas para la tabla
        cols = ('fecha', 'hora', 'descripcion')
        self.tree = ttk.Treeview(top, columns=cols, show='headings', height=10)

        # Encabezados de cada columna
        self.tree.heading('fecha', text='Fecha')
        self.tree.heading('hora', text='Hora')
        self.tree.heading('descripcion', text='Descripción')

        # Ajusto anchos de columnas
        self.tree.column('fecha', width=110, anchor='center')
        self.tree.column('hora', width=80, anchor='center')
        self.tree.column('descripcion', width=420, anchor='w')

        # Scrollbar para la tabla
        vsb = ttk.Scrollbar(top, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side='right', fill='y')
        self.tree.pack(fill='both', expand=True)

        # ---- CAMPOS DE ENTRADA ----
        entradas = ttk.Frame(bottom)
        entradas.pack(fill='x', pady=(0,8))

        # Campo de fecha
        ttk.Label(entradas, text='Fecha (YYYY-MM-DD):').grid(row=0, column=0, padx=4, sticky='e')
        self.e_fecha = ttk.Entry(entradas, width=14)
        self.e_fecha.grid(row=0, column=1, padx=4, sticky='w')
        # Pongo la fecha de hoy como valor por defecto
        self.e_fecha.insert(0, (datetime.now()).strftime('%Y-%m-%d'))

        # Campo de hora
        ttk.Label(entradas, text='Hora (HH:MM):').grid(row=0, column=2, padx=4, sticky='e')
        self.e_hora = ttk.Entry(entradas, width=8)
        self.e_hora.grid(row=0, column=3, padx=4, sticky='w')
        self.e_hora.insert(0, '12:00')  # Valor por defecto

        # Campo de descripción
        ttk.Label(entradas, text='Descripción:').grid(row=1, column=0, padx=4, pady=6, sticky='e')
        self.e_desc = ttk.Entry(entradas, width=64)
        self.e_desc.grid(row=1, column=1, columnspan=3, padx=4, pady=6, sticky='w')

        # ---- BOTONES ----
        botones = ttk.Frame(bottom)
        botones.pack(fill='x')
        ttk.Button(botones, text='Agregar', command=self.agregar).pack(side='left', padx=6)
        ttk.Button(botones, text='Eliminar', command=self.eliminar).pack(side='left', padx=6)
        ttk.Button(botones, text='Salir', command=self.quit).pack(side='right')

        # ---- LISTA DE EVENTOS EN MEMORIA ----
        self.events = []          # Aquí guardo temporalmente los eventos
        self.cargar_eventos()     # Cargo eventos desde archivo si existe
        self.refrescar()          # Muestro en pantalla

    # ---- FUNCIÓN PARA AGREGAR EVENTOS ----
    def agregar(self):
        fecha = self.e_fecha.get().strip()
        hora = self.e_hora.get().strip()
        desc = self.e_desc.get().strip()

        if not fecha or not hora or not desc:
            messagebox.showwarning('Atención', 'Complete fecha, hora y descripción.')
            return

        # Valido formato de fecha
        try:
            datetime.strptime(fecha, '%Y-%m-%d')
        except Exception:
            messagebox.showerror('Error', 'Fecha inválida. Use YYYY-MM-DD.')
            return

        # Valido formato de hora
        try:
            datetime.strptime(hora, '%H:%M')
        except Exception:
            messagebox.showerror('Error', 'Hora inválida. Use HH:MM (24h).')
            return

        # Creo el evento y lo guardo
        evento = {'fecha': fecha, 'hora': hora, 'descripcion': desc}
        self.events.append(evento)
        self.guardar_eventos()
        self.refrescar()

        # Limpio hora y descripción para un siguiente evento
        self.e_hora.delete(0, tk.END); self.e_hora.insert(0, '12:00')
        self.e_desc.delete(0, tk.END)

    # ---- FUNCIÓN PARA ELIMINAR EVENTOS ----
    def eliminar(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo('Atención', 'Seleccione un evento para eliminar.')
            return

        item = sel[0]
        vals = self.tree.item(item, 'values')

        # Confirmo con el usuario
        confirmar = messagebox.askyesno('Confirmar', f'¿Eliminar: {vals[0]} {vals[1]} - {vals[2]} ?')
        if not confirmar:
            return

        # Elimino el evento de la lista
        for i, ev in enumerate(self.events):
            if ev['fecha'] == vals[0] and ev['hora'] == vals[1] and ev['descripcion'] == vals[2]:
                del self.events[i]
                break

        self.guardar_eventos()
        self.refrescar()

    # ---- FUNCIÓN PARA MOSTRAR EN TABLA ----
    def refrescar(self):
        # Limpio tabla
        for r in self.tree.get_children():
            self.tree.delete(r)
        # Ordeno por fecha y hora
        for ev in sorted(self.events, key=lambda e: (e['fecha'], e['hora'])):
            self.tree.insert('', 'end', values=(ev['fecha'], ev['hora'], ev['descripcion']))

    # ---- FUNCIÓN PARA GUARDAR EN ARCHIVO ----
    def guardar_eventos(self):
        try:
            with open(DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.events, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print('Error guardando:', e)

    # ---- FUNCIÓN PARA CARGAR ARCHIVO ----
    def cargar_eventos(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, 'r', encoding='utf-8') as f:
                    self.events = json.load(f)
            except Exception:
                self.events = []
        else:
            # Si no hay archivo, creo algunos ejemplos
            hoy = datetime.now()
            ejemplos = [
                {'fecha': hoy.strftime('%Y-%m-%d'), 'hora': '09:00', 'descripcion': 'Ejemplo: Revisión tarea'},
                {'fecha': (hoy + timedelta(days=1)).strftime('%Y-%m-%d'), 'hora': '14:30', 'descripcion': 'Ejemplo: Reunión de grupo'},
                {'fecha': (hoy + timedelta(days=2)).strftime('%Y-%m-%d'), 'hora': '17:00', 'descripcion': 'Ejemplo: Entrega práctica'}
            ]
            self.events = ejemplos
            self.guardar_eventos()

# ---- EJECUCIÓN DE LA APLICACIÓN ----
if __name__ == '__main__':
    app = AgendaApp()
    app.mainloop()