from parser import Ventana, Widget

# Mapeo de colores a valores CSS válidos (paleta suavizada, no colores "puros")
MAPEO_COLORES = {
    "azul": "#3B82F6",
    "rojo": "#E5484D",
    "verde": "#22A06B",
    "amarillo": "#F5C518",
    "negro": "#1A1A1A",
    "blanco": "#FFFFFF",
    "gris": "#9AA0A6"
}

# Nombres de color (en el DSL, no en CSS) que se consideran "claros"
# y por lo tanto necesitan texto oscuro en vez de blanco encima.
COLORES_CLAROS = ("blanco", "amarillo")


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
        * {{ box-sizing: border-box; }}

        body {{
            font-family: -apple-system, "Segoe UI", Roboto, sans-serif;
            background-color: #f4f4f9;
            margin: 0;
            padding: 40px 20px;
            display: flex;
            justify-content: center;
            align-items: flex-start;
            min-height: 100vh;
        }}

        #ventana-principal {{
            background-color: #ffffff;
            border-radius: 14px;
            box-shadow: 0 4px 24px rgba(0, 0, 0, 0.08);
            padding: 32px;
            margin: 0 auto;
        }}

        .panel {{
            border: 1px solid #eee;
            background-color: #f8f9fb;
            padding: 20px;
            margin: 16px 0;
            border-radius: 10px;
        }}

        .widget-container {{ margin-bottom: 16px; }}

        label {{
            display: block;
            margin-bottom: 6px;
            font-weight: 600;
            color: #333;
        }}

        input:not([type="checkbox"]):not([type="radio"]):not([type="range"]),
        textarea,
        select {{
            width: 100%;
            padding: 10px 12px;
            border: 1px solid #ddd;
            border-radius: 8px;
            font-size: 14px;
            font-family: inherit;
        }}

        input:focus, textarea:focus, select:focus {{
            outline: none;
            border-color: #3B82F6;
        }}

        textarea {{ resize: vertical; }}

        input[type="checkbox"], input[type="radio"] {{
            width: auto;
            margin-right: 6px;
            vertical-align: middle;
        }}

        input[type="range"] {{ width: 100%; }}

        button {{
            padding: 10px 22px;
            border: none;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
            transition: opacity 0.15s ease, transform 0.15s ease;
        }}

        button:hover {{ opacity: 0.88; }}
        button:active {{ transform: scale(0.98); }}

        #toast {{
            position: fixed;
            bottom: 24px;
            left: 50%;
            transform: translateX(-50%) translateY(20px);
            background-color: #1A1A1A;
            color: white;
            padding: 12px 22px;
            border-radius: 8px;
            font-size: 14px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.2s ease, transform 0.2s ease;
        }}

        #toast.visible {{
            opacity: 1;
            transform: translateX(-50%) translateY(0);
        }}
    </style>
</head>
<body>
    {cuerpo_html}

    <div id="toast"></div>

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
            html = f'<div class="widget-container"><input type="checkbox" id="{identificador}" {marcado}> <label for="{identificador}" style="display:inline;">{texto}</label></div>'

        elif tipo == "RadioButton":
            identificador = attrs_dict.get("id", titulo.lower().replace(" ", "_"))
            grupo = attrs_dict.get("grupo", "default")
            texto = attrs_dict.get("texto", titulo)
            html = f'<div class="widget-container"><input type="radio" id="{identificador}" name="{grupo}"> <label for="{identificador}" style="display:inline;">{texto}</label></div>'

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
                color_css = valor_str if valor_str.startswith("#") else MAPEO_COLORES.get(valor_str.lower(), "#1A1A1A")
                
                if es_contenedor or tipo_widget == "Boton":
                    css.append(f"background-color: {color_css};")
                    # Contraste de texto: si el color del DSL es claro (blanco/amarillo), texto oscuro
                    if valor_str.lower() in COLORES_CLAROS:
                        css.append("color: #1A1A1A;")
                    else:
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
            f"            mostrarToast('{func} ejecutada correctamente');\n"
            f"        }}" 
            for func in self.funciones_js
        ])

        js_toast = """
        let toastTimeout;
        function mostrarToast(mensaje) {
            const toast = document.getElementById('toast');
            toast.textContent = mensaje;
            toast.classList.add('visible');
            clearTimeout(toastTimeout);
            toastTimeout = setTimeout(() => {
                toast.classList.remove('visible');
            }, 2500);
        }
        """

        return f"<script>\n{js_toast}\n{js_funciones}\n    </script>"