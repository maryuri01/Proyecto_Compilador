#Validación semántica del DSL.
from dataclasses import dataclass
from typing import List
from parser import Ventana, Widget, StringLiteral, Identificador


@dataclass
class ErrorSemantico:
    mensaje: str
    contexto: str
    linea: int = None
    columna: int = None

    def __str__(self):
        if self.linea is not None:
            return (f"Error semántico en línea {self.linea}, columna {self.columna} "
                     f"({self.contexto}): {self.mensaje}")
        return f"Error semántico en {self.contexto}: {self.mensaje}"


# Tabla de atributos permitido
ATRIBUTOS_POR_WIDGET = {
    "Ventana":     {"ancho", "alto"},
    "Panel":       {"id", "color"},
    "Boton":       {"color", "click"},
    "Input":       {"id", "placeholder", "tipo"},
    "TextArea":    {"id", "filas"},
    "Checkbox":    {"id", "texto", "marcado"},
    "RadioButton": {"id", "grupo", "texto"},
    "ComboBox":    {"id", "opciones"},
    "Slider":      {"id", "min", "max"},
    "Label":       {"color", "tamañoFuente"},
    "Imagen":      {"src", "ancho", "alto"},
}

#Tipo de valor esperado por atributos
ATRIBUTOS_NUMERO = {"ancho", "alto", "min", "max", "filas", "tamañoFuente"}
ATRIBUTOS_STRING = {"src", "placeholder", "texto", "id"}
ATRIBUTOS_BOOLEANO = {"marcado"}
ATRIBUTOS_LISTA = {"opciones"}
ATRIBUTOS_IDENTIFICADOR = {"click", "grupo"}
VALORES_VALIDOS_TIPO = {"texto", "password", "numero"}


def _validar_valor_de_atributo(attr, errores, contexto):
    nombre, valor = attr.nombre, attr.valor

    if nombre in ATRIBUTOS_NUMERO:
        if not (isinstance(valor, int) and not isinstance(valor, bool)):
            errores.append(ErrorSemantico(
                f"'{nombre}' debe ser un número (recibió {valor!r})",
                contexto, attr.linea, attr.columna))

    elif nombre in ATRIBUTOS_STRING:
        if not isinstance(valor, StringLiteral):
            errores.append(ErrorSemantico(
                f"'{nombre}' debe ir entre comillas, ej. {nombre}=\"texto\" (recibió {valor!r})",
                contexto, attr.linea, attr.columna))

    elif nombre in ATRIBUTOS_BOOLEANO:
        if not isinstance(valor, bool):
            errores.append(ErrorSemantico(
                f"'{nombre}' debe ser true o false (recibió {valor!r})",
                contexto, attr.linea, attr.columna))

    elif nombre in ATRIBUTOS_LISTA:
        if not isinstance(valor, list):
            errores.append(ErrorSemantico(
                f"'{nombre}' debe ser una lista entre corchetes, ej. opciones=[\"a\",\"b\"]",
                contexto, attr.linea, attr.columna))

    elif nombre == "color":
        es_hex = isinstance(valor, str) and valor.startswith("#") and not isinstance(valor, (StringLiteral, Identificador))
        es_identificador = isinstance(valor, Identificador)
        if not (es_hex or es_identificador):
            errores.append(ErrorSemantico(
                "'color' debe ser un nombre sin comillas (ej. azul) o un color "
                f"hexadecimal (#RRGGBB), no un texto entre comillas (recibió {valor!r})",
                contexto, attr.linea, attr.columna))

    elif nombre == "tipo":
        if not isinstance(valor, Identificador) or str(valor) not in VALORES_VALIDOS_TIPO:
            errores.append(ErrorSemantico(
                f"'tipo' debe ser uno de: {', '.join(sorted(VALORES_VALIDOS_TIPO))} (recibió {valor!r})",
                contexto, attr.linea, attr.columna))

    elif nombre in ATRIBUTOS_IDENTIFICADOR:
        if not isinstance(valor, Identificador):
            errores.append(ErrorSemantico(
                f"'{nombre}' debe ser un nombre sin comillas, ej. {nombre}=algo (recibió {valor!r})",
                contexto, attr.linea, attr.columna))


def _validar_atributos(contexto, tipo_widget, atributos, errores):
    vistos = set()
    permitidos = ATRIBUTOS_POR_WIDGET.get(tipo_widget, set())

    for attr in atributos:
        if attr.nombre in vistos:
            errores.append(ErrorSemantico(
                f"el atributo '{attr.nombre}' está repetido",
                contexto, attr.linea, attr.columna))
        vistos.add(attr.nombre)

        if attr.nombre not in permitidos:
            errores.append(ErrorSemantico(
                f"el atributo '{attr.nombre}' no es válido para '{tipo_widget}' "
                f"(válidos: {', '.join(sorted(permitidos)) or 'ninguno'})",
                contexto, attr.linea, attr.columna))
            continue  # si el atributo ni siquiera aplica aqui, no tiene caso validar su tipo de valor

        _validar_valor_de_atributo(attr, errores, contexto)


def _validar_widget(widget: "Widget", errores: List[ErrorSemantico]):
    contexto = f'{widget.tipo} "{widget.titulo}"'
    _validar_atributos(contexto, widget.tipo, widget.atributos, errores)
    for hijo in widget.contenido:
        _validar_widget(hijo, errores)


def validar_semantica(ast: "Ventana") -> List[ErrorSemantico]:
    errores: List[ErrorSemantico] = []

    contexto = f'Ventana "{ast.titulo}"'
    _validar_atributos(contexto, "Ventana", ast.atributos, errores)

    for widget in ast.contenido:
        _validar_widget(widget, errores)

    return errores