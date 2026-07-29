# -*- coding: utf-8 -*-
"""
Lexer (tokenizador) para el DSL del Generador de Interfaces Gráficas.
Entrega: tokenize(codigo_fuente) -> List[Token]
"""

import re
from dataclasses import dataclass


@dataclass
class Token:
    tipo: str
    lexema: str
    linea: int
    columna: int

    def __repr__(self):
        return f"Token({self.tipo}, {self.lexema!r}, linea={self.linea}, col={self.columna})"


class ErrorLexico(Exception):
    def __init__(self, mensaje, linea, columna):
        super().__init__(f"Error léxico en línea {linea}, columna {columna}: {mensaje}")
        self.linea = linea
        self.columna = columna


PALABRAS_RESERVADAS = {
    "Ventana": "KW_VENTANA",
    "Panel": "KW_PANEL",
    "Input": "KW_INPUT",
    "TextArea": "KW_TEXTAREA",
    "Checkbox": "KW_CHECKBOX",
    "RadioButton": "KW_RADIOBUTTON",
    "ComboBox": "KW_COMBOBOX",
    "Slider": "KW_SLIDER",
    "Label": "KW_LABEL",
    "Imagen": "KW_IMAGEN",
    "Boton": "KW_BOTON",
    "true": "KW_TRUE",
    "false": "KW_FALSE",
}


especificacion_tokens = [
    ("COMENTARIO",     r"//[^\n]*"),
    ("SALTO_LINEA",     r"\r\n|\n"),
    ("ESPACIO",         r"[ \t]+"),
    ("STRING",          r'"[^"\n]*"'),
    ("COLOR_HEX",       r"\#[0-9A-Fa-f]{6}"),
    ("NUMERO",          r"[0-9]+"),
    ("IDENTIFICADOR",   r"[a-zA-ZÀ-ÿ_][a-zA-Z0-9À-ÿ_]*"),
    ("LLAVE_IZQ",       r"\{"),
    ("LLAVE_DER",       r"\}"),
    ("CORCHETE_IZQ",    r"\["),
    ("CORCHETE_DER",    r"\]"),
    ("IGUAL",           r"="),
    ("COMA",            r","),
]

_regex_maestro = re.compile(
    "|".join(f"(?P<{nombre}>{patron})" for nombre, patron in especificacion_tokens)
)

TOKENS_DESCARTABLES = {"COMENTARIO", "ESPACIO"}


def _reportar_error(codigo_fuente, posicion, linea, columna):
    caracter = codigo_fuente[posicion]

    if caracter == '"':
        raise ErrorLexico("string sin cerrar (falta comilla de cierre)", linea, columna)

    if caracter == "#":
        raise ErrorLexico(
            "código de color hexadecimal mal formado (se esperan # y 6 dígitos hexadecimales)",
            linea, columna
        )

    raise ErrorLexico(f"símbolo inesperado {caracter!r}", linea, columna)


def tokenize(codigo_fuente):
    tokens = []
    linea = 1
    inicio_linea = 0
    posicion = 0
    longitud = len(codigo_fuente)

    while posicion < longitud:
        coincidencia = _regex_maestro.match(codigo_fuente, posicion)

        if coincidencia is None:
            columna = posicion - inicio_linea + 1
            _reportar_error(codigo_fuente, posicion, linea, columna)

        tipo = coincidencia.lastgroup
        lexema = coincidencia.group()
        columna = posicion - inicio_linea + 1

        if tipo == "SALTO_LINEA":
            linea += 1
            inicio_linea = coincidencia.end()
        elif tipo == "IDENTIFICADOR" and lexema in PALABRAS_RESERVADAS:
            tokens.append(Token(PALABRAS_RESERVADAS[lexema], lexema, linea, columna))
        elif tipo not in TOKENS_DESCARTABLES:
            tokens.append(Token(tipo, lexema, linea, columna))

        posicion = coincidencia.end()

    tokens.append(Token("EOF", "", linea, posicion - inicio_linea + 1))
    return tokens


