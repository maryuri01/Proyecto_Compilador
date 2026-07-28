# -*- coding: utf-8 -*-

from parser import Ventana, Widget

# Mapeo de colores a valores CSS válidos
MAPEO_COLORES = {
    "azul": "blue",
    "rojo": "red",
    "verde": "green",
    "amarillo": "yellow",
    "negro": "black",
    "blanco": "white",
    "gris": "gray"
}

class GeneradorHTML:
    def __init__(self):
        # set para guardar los nombres de las funciones JS y evitar duplicados
        self.funciones_js = set()

    def generar(self, ast: Ventana) -> str:
        """
        Punto de entrada. Recibe la Ventana raíz y devuelve el HTML completo en un string.
        """
        cuerpo_html = self._procesar_ventana(ast)
        scripts_js = self._generar_scripts()

        # Plantilla base de HTML
        html_final = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{ast.titulo}</title>
    <style>
        /* CSS Base para normalizar la vista */
        body {{ font-family: sans-serif; padding: 20px; background-color: #f4f4f9; }}
        .panel {{ border: 1px solid #ccc; padding: 15px; margin: 10px 0; border-radius: 5px; }}
        .widget-container {{ margin-bottom: 10px; }}
        label {{ margin-right: 10px; font-weight: bold; }}
    </style>
</head>
<body>
    {cuerpo_html}

    <!-- Scripts generados dinámicamente -->
    {scripts_js}
</body>
</html>"""
        return html_final

    def _procesar_ventana(self, ventana: Ventana) -> str:
        """Procesa el contenedor principal (Ventana)."""
        estilos = self._mapear_atributos_css(ventana.atributos, tipo_widget="Ventana", es_contenedor=True)
        html_hijos = self._procesar_hijos(ventana.contenido)
        
        return f'<div id="ventana-principal" style="{estilos}">\n{html_hijos}\n</div>'

    def _procesar_hijos(self, lista_widgets: list) -> str:
        """Recorre de forma recursiva los widgets hijos."""
        return "\n".join([self._procesar_widget(w) for w in lista_widgets])

    def _procesar_widget(self, widget: Widget) -> str:
        """Convierte cada tipo de widget en su etiqueta HTML correspondiente."""
        tipo = widget.tipo
        titulo = widget.titulo
        
        attrs_dict = {attr.nombre: attr.valor for attr in widget.atributos}
        estilos_css = self._mapear_atributos_css(widget.atributos, tipo_widget=tipo, es_contenedor=(tipo == "Panel"))
        
        html = ""

        # Contenedores
        if tipo == "Panel":
            # Anidamiento recursivo
            hijos = self._procesar_hijos(widget.contenido)
            html = f'<div class="panel" style="{estilos_css}">\n{hijos}\n</div>'

        # Entrada de datos
        elif tipo == "Input":
            identificador = attrs_dict.get("id", titulo.lower().replace(" ", "_"))
            placeholder = attrs_dict.get("placeholder", "")
            tipo_input = attrs_dict.get("tipo", "text")
            # Mapeo simple si el tipo es 'numero'
            tipo_input = "number" if tipo_input == "numero" else tipo_input 
            html = f'<div class="widget-container"><input type="{tipo_input}" id="{identificador}" placeholder="{placeholder}" style="{estilos_css}"></div>'

        elif tipo == "TextArea":
            identificador = attrs_dict.get("id", titulo.lower().replace(" ", "_"))
            filas = attrs_dict.get("filas", 3)
            html = f'<div class="widget-container"><textarea id="{identificador}" rows="{filas}" style="{estilos_css}"></textarea></div>'

        elif tipo == "Checkbox":
            identificador = attrs_dict.get("id", titulo.lower().replace(" ", "_"))
            texto = attrs_dict.get("texto", titulo)
            marcado = "checked" if attrs_dict.get("marcado") else ""
            html = f'<div class="widget-container"><input type="checkbox" id="{identificador}" {marcado}> <label for="{identificador}">{texto}</label></div>'

        elif tipo == "RadioButton":
            identificador = attrs_dict.get("id", titulo.lower().replace(" ", "_"))
            grupo = attrs_dict.get("grupo", "default")
            texto = attrs_dict.get("texto", titulo)
            html = f'<div class="widget-container"><input type="radio" id="{identificador}" name="{grupo}"> <label for="{identificador}">{texto}</label></div>'

        elif tipo == "ComboBox":
            identificador = attrs_dict.get("id", titulo.lower().replace(" ", "_"))
            opciones = attrs_dict.get("opciones", [])
            opts_html = "".join([f'<option value="{opt}">{opt}</option>' for opt in opciones])
            html = f'<div class="widget-container"><select id="{identificador}" style="{estilos_css}">{opts_html}</select></div>'

        elif tipo == "Slider":
            identificador = attrs_dict.get("id", titulo.lower().replace(" ", "_"))
            min_val = attrs_dict.get("min", 0)
            max_val = attrs_dict.get("max", 100)
            html = f'<div class="widget-container"><input type="range" id="{identificador}" min="{min_val}" max="{max_val}" style="{estilos_css}"></div>'

        # Salida / Visualización
        elif tipo == "Label":
            html = f'<div class="widget-container"><label style="{estilos_css}">{titulo}</label></div>'

        elif tipo == "Imagen":
            src = attrs_dict.get("src", "")
            html = f'<div class="widget-container"><img src="{src}" alt="{titulo}" style="{estilos_css}"></div>'

        # Acción
        elif tipo == "Boton":
            click_func = attrs_dict.get("click", None)
            onclick_html = ""
            if click_func:
                self.funciones_js.add(str(click_func))
                onclick_html = f'onclick="{click_func}()"'
            html = f'<div class="widget-container"><button {onclick_html} style="{estilos_css}">{titulo}</button></div>'

        return html

    def _mapear_atributos_css(self, atributos: list, tipo_widget: str = None, es_contenedor: bool = False) -> str:
        """
        Recibe una lista de objetos Atributo y los traduce a un string de CSS inline.
        """
        css = []
        for attr in atributos:
            nombre = attr.nombre
            valor = attr.valor

            # Traducción de dimensiones
            if nombre in ("ancho", "alto"):
                # En CSS usamos 'width' y 'height'
                prop = "width" if nombre == "ancho" else "height"
                css.append(f"{prop}: {valor}px;")
            
            # Traducción de fuentes
            elif nombre == "tamañoFuente":
                css.append(f"font-size: {valor}px;")
            
            # Traducción de color
            elif nombre == "color":
                valor_str = str(valor)
                # Si es un color en hexadecimal, se usa directamente si no se busca en el mapeo
                color_css = valor_str if valor_str.startswith("#") else MAPEO_COLORES.get(valor_str.lower(), "black")
                
                if es_contenedor or tipo_widget == "Boton":
                    css.append(f"background-color: {color_css};")
                    # Contraste de texto para botones/paneles oscuros
                    if color_css not in ["white", "yellow"]: 
                        css.append("color: white;") 
                else:
                    css.append(f"color: {color_css};")

        return " ".join(css)

    def _generar_scripts(self) -> str:
        """
        Genera el bloque <script> con funciones placeholder basadas en los eventos encontrados.
        """
        if not self.funciones_js:
            return ""

        js_funciones = "\n".join([
            f"        function {func}() {{\n"
            f"            console.log('Evento ejecutado: {func} ()');\n"
            f"            alert('La función {func} ha sido llamada.');\n"
            f"        }}" 
            for func in self.funciones_js
        ])

        return f"<script>\n{js_funciones}\n    </script>"