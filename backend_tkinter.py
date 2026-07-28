from parser import Ventana, Widget

MAPEO_COLORES = {
    "azul": "blue",
    "rojo": "red",
    "verde": "green",
    "amarillo": "yellow",
    "negro": "black",
    "blanco": "white",
    "gris": "gray",
}


def _color_tk(valor):
    """Traduce un valor de color del DSL (nombre o #hex) a texto usable en Tkinter."""
    if valor is None:
        return None
    valor_str = str(valor)
    if valor_str.startswith("#"):
        return valor_str
    return MAPEO_COLORES.get(valor_str.lower(), valor_str.lower())


class GeneradorTkinter:
    def __init__(self):
        self.funciones_callback = set()   
        self.grupos_radio = {}          
        self._contador_ids = {}           
        self.usa_imagenes = False

    def generar(self, ast: Ventana) -> str:
        """Punto de entrada. Recibe la Ventana raiz y devuelve el .py completo en un string."""
        self.funciones_callback.clear()
        self.grupos_radio.clear()
        self._contador_ids.clear()
        self.usa_imagenes = False

        self._recolectar_metadatos(ast.contenido)

        cuerpo = self._procesar_hijos(ast.contenido, "app")

        lineas = ["import customtkinter as ctk"]
        if self.usa_imagenes:
            lineas.append("from PIL import Image")
        lineas.append("")
        lineas.append("app = ctk.CTk()")
        lineas.append(f'app.title("{ast.titulo}")')

        attrs_ventana = {a.nombre: a.valor for a in ast.atributos}
        ancho = attrs_ventana.get("ancho")
        alto = attrs_ventana.get("alto")
        if ancho and alto:
            lineas.append(f'app.geometry("{ancho}x{alto}")')
        lineas.append("")

        # Funciones placeholder para los callbacks de los botones
        if self.funciones_callback:
            for nombre_func in sorted(self.funciones_callback):
                lineas.append(f"def {nombre_func}():")
                lineas.append("    pass")
                lineas.append("")

        # Variables compartidas para agrupar RadioButtons (StringVar)
        if self.grupos_radio:
            for grupo, var_nombre in self.grupos_radio.items():
                lineas.append(f'{var_nombre} = ctk.StringVar(value="")')
            lineas.append("")

        lineas.append(cuerpo)
        lineas.append("")
        lineas.append("app.mainloop()")

        return "\n".join(lineas)


    def _recolectar_metadatos(self, widgets):
        """Recorre el AST solo para juntar callbacks y grupos de radio."""
        for w in widgets:
            attrs = {a.nombre: a.valor for a in w.atributos}
            if w.tipo == "Boton" and "click" in attrs:
                self.funciones_callback.add(str(attrs["click"]))
            if w.tipo == "RadioButton" and "grupo" in attrs:
                grupo = str(attrs["grupo"])
                if grupo not in self.grupos_radio:
                    self.grupos_radio[grupo] = f"var_{grupo}"
            if w.tipo == "Imagen":
                self.usa_imagenes = True
            if w.contenido:
                self._recolectar_metadatos(w.contenido)

    def _nombre_variable(self, tipo):
        """Genera nombres de variable unicos por tipo: boton_1, boton_2, panel_1, etc."""
        prefijo = tipo.lower()
        self._contador_ids[prefijo] = self._contador_ids.get(prefijo, 0) + 1
        return f"{prefijo}_{self._contador_ids[prefijo]}"

    def _procesar_hijos(self, widgets, nombre_padre):
        return "\n".join(self._procesar_widget(w, nombre_padre) for w in widgets)

    def _procesar_widget(self, widget, nombre_padre):
        tipo = widget.tipo
        titulo = widget.titulo
        attrs = {a.nombre: a.valor for a in widget.atributos}
        var = self._nombre_variable(tipo)
        lineas = []

        # Contenedor
        if tipo == "Panel":
            color = _color_tk(attrs.get("color"))
            args = [nombre_padre]
            if color:
                args.append(f'fg_color="{color}"')
            lineas.append(f"{var} = ctk.CTkFrame({', '.join(args)})")
            lineas.append(f"{var}.pack(padx=10, pady=10, fill='both')")
            hijos_codigo = self._procesar_hijos(widget.contenido, var)
            if hijos_codigo:
                lineas.append(hijos_codigo)

        # Accion
        elif tipo == "Boton":
            color = _color_tk(attrs.get("color"))
            click_func = attrs.get("click")
            args = [nombre_padre, f'text="{titulo}"']
            if color:
                args.append(f'fg_color="{color}"')
            if click_func:
                args.append(f"command={click_func}")
            lineas.append(f"{var} = ctk.CTkButton({', '.join(args)})")
            lineas.append(f"{var}.pack(padx=5, pady=5)")

        # Entrada de datos
        elif tipo == "Input":
            placeholder = attrs.get("placeholder", "")
            tipo_input = attrs.get("tipo")
            args = [nombre_padre]
            if placeholder:
                args.append(f'placeholder_text="{placeholder}"')
            if tipo_input == "password":
                args.append('show="*"')
            lineas.append(f"{var} = ctk.CTkEntry({', '.join(args)})")
            lineas.append(f"{var}.pack(padx=5, pady=5)")

        elif tipo == "TextArea":
            filas = attrs.get("filas", 3)
            altura = int(filas) * 24
            lineas.append(f"{var} = ctk.CTkTextbox({nombre_padre}, height={altura})")
            lineas.append(f"{var}.pack(padx=5, pady=5, fill='x')")

        elif tipo == "Checkbox":
            texto = attrs.get("texto", titulo)
            marcado = attrs.get("marcado", False)
            lineas.append(f'{var} = ctk.CTkCheckBox({nombre_padre}, text="{texto}")')
            lineas.append(f"{var}.pack(padx=5, pady=5, anchor='w')")
            if marcado:
                lineas.append(f"{var}.select()")

        elif tipo == "RadioButton":
            texto = attrs.get("texto", titulo)
            grupo = attrs.get("grupo")
            var_grupo = self.grupos_radio.get(str(grupo), "var_default")
            lineas.append(
                f'{var} = ctk.CTkRadioButton({nombre_padre}, text="{texto}", '
                f'variable={var_grupo}, value="{titulo}")'
            )
            lineas.append(f"{var}.pack(padx=5, pady=5, anchor='w')")

        elif tipo == "ComboBox":
            opciones = attrs.get("opciones", [])
            valores = ", ".join(f'"{o}"' for o in opciones)
            lineas.append(f"{var} = ctk.CTkComboBox({nombre_padre}, values=[{valores}])")
            lineas.append(f"{var}.pack(padx=5, pady=5)")

        elif tipo == "Slider":
            minimo = attrs.get("min", 0)
            maximo = attrs.get("max", 100)
            lineas.append(f"{var} = ctk.CTkSlider({nombre_padre}, from_={minimo}, to={maximo})")
            lineas.append(f"{var}.pack(padx=5, pady=5, fill='x')")

        # Salida / visualizacion
        elif tipo == "Label":
            color = _color_tk(attrs.get("color"))
            tamano = attrs.get("tamañoFuente")
            args = [nombre_padre, f'text="{titulo}"']
            if color:
                args.append(f'text_color="{color}"')
            if tamano:
                args.append(f'font=("Arial", {tamano})')
            lineas.append(f"{var} = ctk.CTkLabel({', '.join(args)})")
            lineas.append(f"{var}.pack(padx=5, pady=5)")

        elif tipo == "Imagen":
            src = attrs.get("src", "")
            ancho = attrs.get("ancho", 100)
            alto = attrs.get("alto", 100)
            img_var = f"_img_{var}"
            lineas.append(
                f'{img_var} = ctk.CTkImage(light_image=Image.open("{src}"), size=({ancho}, {alto}))'
            )
            lineas.append(f'{var} = ctk.CTkLabel({nombre_padre}, image={img_var}, text="")')
            lineas.append(f"{var}.pack(padx=5, pady=5)")

        else:
            lineas.append(f"# tipo de widget no reconocido: {tipo}")

        return "\n".join(lineas)