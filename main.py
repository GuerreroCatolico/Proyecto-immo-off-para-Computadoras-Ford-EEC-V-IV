import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import json
import os
import sys


def cargar_config_checksum():
    try:
        base_dir = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        config_path = os.path.join(base_dir, "checksum_config.json")
        
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        messagebox.showerror("Error", "Archivo checksum_config.json no encontrado 😱")
        return None
    except json.JSONDecodeError:
        messagebox.showerror("Error", "Archivo checksum_config.json con formato inválido 🤨")
        return None
    except Exception as e:
        messagebox.showerror("Error", f"No se cargó la configuración:\n{str(e)}")
        return None


def calcular_checksum(datos, config_tipo, tipo_modulo):
    if not config_tipo:
        return None, None
    
    try:
        if tipo_modulo == "EEC V":
            inicio = int(config_tipo["rango_calculo_eecv"][0], 16)
            fin = int(config_tipo["rango_calculo_eecv"][1], 16)
            dir_cs = int(config_tipo["direccion_checksum_eecv"], 16)
        else:
            inicio = int(config_tipo["rango_calculo_eeciv"][0], 16)
            fin = int(config_tipo["rango_calculo_eeciv"][1], 16)
            dir_cs = int(config_tipo["direccion_checksum_eeciv"], 16)
        
        if inicio < 0 or fin >= len(datos) or dir_cs >= len(datos):
            messagebox.showwarning("Advertencia", "Rango o dirección de checksum fuera de límites 📏")
            return None, dir_cs
        
        suma = sum(datos[inicio:fin+1])
        return suma % 256, dir_cs
    except KeyError as e:
        messagebox.showerror("Error", f"Falta configuración para: {str(e)} 📝")
        return None, None
    except ValueError as e:
        messagebox.showerror("Error", f"Valor inválido en configuración:\n{str(e)}")
        return None, None


def verificar_checksum(datos, config_tipo, tipo_modulo):
    checksum_calculado, dir_cs = calcular_checksum(datos, config_tipo, tipo_modulo)
    if checksum_calculado is None or dir_cs is None:
        return False, 0, 0
    
    checksum_archivo = datos[dir_cs]
    return (checksum_calculado == checksum_archivo), checksum_archivo, checksum_calculado


def aplicar_modificacion_eecv(datos, tipo_vehiculo):
    formulacion = {
        "3.8L V6 Manual": [{"dir": "0x00000003", "orig": "0xF1", "nuevo": "0x79"}],
        "3.8L V6 Automática": [{"dir": "0x00000003", "orig": "0xF1", "nuevo": "0x79"}],
        "4.2L V6 Manual": [{"dir": "0x00000003", "orig": "0xF1", "nuevo": "0x79"}],
        "4.2L V6 Automática": [{"dir": "0x00000003", "orig": "0xF1", "nuevo": "0x79"}],
        "5.0L V8 Manual": [{"dir": "0x00000003", "orig": "0xF1", "nuevo": "0x79"}],
        "5.0L V8 Automática": [{"dir": "0x00000003", "orig": "0xF1", "nuevo": "0x79"}]
    }
    
    if tipo_vehiculo not in formulacion:
        return None, "Tipo de vehículo no válido 🚗"
    
    for mod in formulacion[tipo_vehiculo]:
        try:
            dir_mod = int(mod["dir"], 16)
            val_orig = int(mod["orig"], 16)
            val_nuevo = int(mod["nuevo"], 16)
            
            if dir_mod >= len(datos):
                messagebox.showwarning("Advertencia", f"Dirección {hex(dir_mod)} fuera de límites 📍")
                continue
            
            if datos[dir_mod] == val_orig:
                datos[dir_mod] = val_nuevo
            else:
                if not messagebox.askyesno("Oye mi caramelito! 🤔", 
                                        f"Valor actual {hex(datos[dir_mod])} no coincide con {hex(val_orig)}\n¿Seguir igual?"):
                    return None, "Operación cancelada por ti 😉"
        
        except ValueError as e:
            return None, f"Error en datos de modificación:\n{str(e)}"
    
    return datos, "Modificación EEC V aplicada correctamente! 🎉"


def aplicar_modificacion_eeciv(datos, modelo):
    ajustes = {
        "U4P0": [{"dir": "0x009140", "orig": "0x2A", "nuevo": "0x1F"}],
        "W4H0": [{"dir": "0x008A20", "orig": "0x3B", "nuevo": "0x2D"}],
        "A9L": [{"dir": "0x008E30", "orig": "0x4C", "nuevo": "0x3A"}]
    }
    
    if modelo not in ajustes:
        return None, "Modelo EEC IV no válido 🛠️"
    
    for mod in ajustes[modelo]:
        try:
            dir_mod = int(mod["dir"], 16)
            val_orig = int(mod["orig"], 16)
            val_nuevo = int(mod["nuevo"], 16)
            
            if dir_mod >= len(datos):
                messagebox.showwarning("Advertencia", f"Dirección {hex(dir_mod)} fuera de límites 📍")
                continue
            
            if datos[dir_mod] == val_orig:
                datos[dir_mod] = val_nuevo
            else:
                if not messagebox.askyesno("Oye mi vida! 🤔", 
                                        f"Valor actual {hex(datos[dir_mod])} no coincide con {hex(val_orig)}\n¿Seguir igual?"):
                    return None, "Operación cancelada 😉"
        
        except ValueError as e:
            return None, f"Error en ajustes:\n{str(e)}"
    
    return datos, "Modificación EEC IV aplicada correctamente! 🎉"


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("DESACTIVADOR PATs FORD - CHIKISTRIKIS EDITION 🚀")
        self.geometry("650x400")
        self.resizable(False, False)
        
        self.config_checksum = cargar_config_checksum()
        self.datos_ecu = None
        
        self.crear_interfaz()


    def crear_interfaz(self):
        # Título principal
        ttk.Label(self, text="DESACTIVADOR DE PATs FORD", font=("Arial", 16, "bold")).pack(pady=15)
        
        # Frame carga archivo
        frame_carga = ttk.Frame(self)
        frame_carga.pack(pady=5, padx=20, fill=tk.X)
        
        ttk.Label(frame_carga, text="Cargar ECU:").pack(side=tk.LEFT, padx=5)
        self.btn_cargar = ttk.Button(frame_carga, text="📂 Seleccionar Archivo", command=self.cargar_ecu)
        self.btn_cargar.pack(side=tk.LEFT, padx=5)
        
        self.lbl_ruta = ttk.Label(frame_carga, text="No hay archivo seleccionado")
        self.lbl_ruta.pack(side=tk.LEFT, padx=10)
        
        # Frame selección módulo
        frame_modulo = ttk.Frame(self)
        frame_modulo.pack(pady=10, padx=20, fill=tk.X)
        
        ttk.Label(frame_modulo, text="Seleccionar Módulo:").pack(side=tk.LEFT, padx=5)
        self.tipo_modulo = tk.StringVar(value="EEC V")
        
        ttk.Radiobutton(frame_modulo, text="EEC V", variable=self.tipo_modulo, value="EEC V").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(frame_modulo, text="EEC IV", variable=self.tipo_modulo, value="EEC IV").pack(side=tk.LEFT, padx=5)
        
        # Frame configuración
        frame_config = ttk.Frame(self)
        frame_config.pack(pady=10, padx=20, fill=tk.X)
        
        ttk.Label(frame_config, text="Configuración:").pack(side=tk.LEFT, padx=5)
        self.cmb_config = ttk.Combobox(frame_config, state="readonly")
        self.cmb_config.pack(side=tk.LEFT, padx=5)
        self.actualizar_config()
        
        # Botón aplicar
        self.btn_aplicar = ttk.Button(self, text="✨ Aplicar Modificación", command=self.aplicar_mod)
        self.btn_aplicar.pack(pady=5)
        
        # Botón guardar
        self.btn_guardar = ttk.Button(self, text="💾 Guardar Archivo", command=self.guardar_ecu, state=tk.DISABLED)
        self.btn_guardar.pack(pady=5)
        
        # Label estado
        self.lbl_estado = ttk.Label(self, text="Estado: Listo y esperando órdenes! 😎", foreground="#006600")
        self.lbl_estado.pack(pady=10)


    def actualizar_config(self):
        if self.tipo_modulo.get() == "EEC V":
            opciones = ["3.8L V6 Manual", "3.8L V6 Automática", "4.2L V6 Manual", "4.2L V6 Automática", "5.0L V8 Manual", "5.0L V8 Automática"]
        else:
            opciones = ["U4P0", "W4H0", "A9L"]
        
        self.cmb_config["values"] = opciones
        if opciones:
            self.cmb_config.current(0)


    def cargar_ecu(self):
        ruta = filedialog.askopenfilename(filetypes=[("Archivos ECU", "*.bin *.hex"), ("Todos los archivos", "*.*")])
        if ruta:
            try:
                with open(ruta, "rb") as f:
                    self.datos_ecu = bytearray(f.read())
                
                self.lbl_ruta.config(text=f"Archivo: {os.path.basename(ruta)}")
                self.lbl_estado.config(text="Estado: Archivo cargado correctamente! 🥳", foreground="#006600")
                self.btn_guardar.config(state=tk.NORMAL)
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo cargar:\n{str(e)}")
                self.lbl_estado.config(text="Estado: Error al cargar", foreground="#CC0000")


    def aplicar_mod(self):
        if not self.datos_ecu:
            messagebox.showwarning("Advertencia", "Carga un archivo primero! 📂")
            return
        
        config_seleccionada = self.cmb_config.get()
        if not config_seleccionada:
            messagebox.showwarning("Advertencia", "Selecciona una configuración! 📋")
            return
        
        if not self.config_checksum:
            messagebox.showwarning("Advertencia", "No hay configuración de checksum ⚠️")
            return
        
        config_tipo = self.config_checksum.get(config_seleccionada)
        if not config_tipo:
            messagebox.showerror("Error", f"No hay configuración para {config_seleccionada} 📝")
            return
        
        if self.tipo_modulo.get() == "EEC V":
            datos_mod, msg = aplicar_modificacion_eecv(self.datos_ecu, config_seleccionada)
        else:
            datos_mod, msg = aplicar_modificacion_eeciv(self.datos_ecu, config_seleccionada)
        
        if datos_mod:
            self.datos_ecu = datos_mod
            self.lbl_estado.config(text=f"Estado: {msg} ✅", foreground="#006600")
            
            valido, cs_archivo, cs_calculado = verificar_checksum(self.datos_ecu, config_tipo, self.tipo_modulo.get())
            if not valido:
                cs_nuevo, dir_cs = calcular_checksum(self.datos_ecu, config_tipo, self.tipo_modulo.get())
                if cs_nuevo and dir_cs:
                    self.datos_ecu[dir_cs] = cs_nuevo
                    self.lbl_estado.config(text=f"Estado: {msg} | Checksum actualizado {hex(cs_nuevo)} ✅", foreground="#006600")
                else:
                    self.lbl_estado.config(text=f"Estado: {msg} | No se pudo actualizar checksum ⚠️", foreground="#CC6600")
            else:
                self.lbl_estado.config(text=f"Estado: {msg} | Checksum válido {hex(cs_archivo)} ✅", foreground="#006600")
        else:
            self.lbl_estado.config(text=f"Estado: {msg} ❌", foreground="#CC0000")


    def guardar_ecu(self):
        ruta = filedialog.asksaveasfilename(defaultextension=".bin", filetypes=[("Archivos ECU", "*.bin *.hex"), ("Todos los archivos", "*.*")])
        if ruta:
            try:
                with open(ruta, "wb") as f:
                    f.write(self.datos_ecu)
                
                messagebox.showinfo("Éxito", "Archivo guardado correctamente, mi caramelito! 🥳")
                self.lbl_estado.config(text="Estado: Archivo guardado ✅", foreground="#006600")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar:\n{str(e)}")
                self.lbl_estado.config(text="Estado: Error al guardar ❌", foreground="#CC0000")


if __name__ == "__main__":
    app = App()
    app.mainloop()
