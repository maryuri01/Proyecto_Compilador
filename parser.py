from dataclasses import dataclass, field
from typing import List, Optional
from lark import Lark, Transformer
from lark.lexer import Lexer, Token as LarkToken
from lark.exceptions import UnexpectedInput, UnexpectedToken
from tokenizador import Token as TokenLexico  


# aqui se definen lo que puede contener cada atributo "principal"
@dataclass
class Atributo:
    nombre: str
    valor: object  # pueden ser string, booleanos, enteros
    linea: Optional[int] = None
    columna: Optional[int] = None


@dataclass
class Widget:
    tipo: str                                    
    titulo: str
    atributos: List[Atributo] = field(default_factory=list)
    contenido: List["Widget"] = field(default_factory=list)
    linea: Optional[int] = None
    columna: Optional[int] = None


@dataclass # ventana puede tener varios atributos y widgets
class Ventana:
    titulo: str
    atributos: List[Atributo] = field(default_factory=list)
    contenido: List[Widget] = field(default_factory=list)
    linea: Optional[int] = None
    columna: Optional[int] = None


# gramatica establecida 

GRAMATICA = r"""
    programa: ventana EOF

    ventana: KW_VENTANA STRING atributos? bloque

    bloque: LLAVE_IZQ contenido* LLAVE_DER

    ?contenido: panel | widget

    panel: KW_PANEL STRING atributos? bloque

    widget: widget_tag STRING atributos? 

    ?widget_tag: KW_INPUT | KW_TEXTAREA | KW_CHECKBOX
               | KW_RADIOBUTTON | KW_COMBOBOX | KW_SLIDER | KW_LABEL
               | KW_IMAGEN | KW_BOTON

    atributos: CORCHETE_IZQ atributo (COMA atributo)* CORCHETE_DER

    atributo: IDENTIFICADOR IGUAL valor

    ?valor: STRING
          | NUMERO
          | COLOR_HEX
          | booleano
          | lista
          | IDENTIFICADOR

    booleano: KW_TRUE | KW_FALSE

    lista: CORCHETE_IZQ STRING (COMA STRING)* CORCHETE_DER

    %declare KW_VENTANA KW_PANEL KW_INPUT KW_TEXTAREA KW_CHECKBOX
    %declare KW_RADIOBUTTON KW_COMBOBOX KW_SLIDER KW_LABEL KW_IMAGEN KW_BOTON
    %declare KW_TRUE KW_FALSE
    %declare LLAVE_IZQ LLAVE_DER CORCHETE_IZQ CORCHETE_DER IGUAL COMA
    %declare STRING NUMERO COLOR_HEX IDENTIFICADOR
    %declare EOF 
"""


class LexerExterno(Lexer):
    """Lexer 'nulo': Solo se pueden utilizar los tokens que ya establecieron."""
    def __init__(self, *args, **kwargs):
        pass

    def lex(self, data):
        for tok in data:
            yield tok


_parser = Lark(GRAMATICA, start="programa", parser="lalr", lexer=LexerExterno)

# Aqui se empieza a generar el AST a partir de las listas que pueda contener
class _ListaAtributos(list):
    pass


class _ListaHijos(list):
    pass


# Cambie aqui: subclases de str/int 
#Mauricio estuvo aqui
class _StrPos(str):
    def __new__(cls, valor, linea, columna):
        obj = super().__new__(cls, valor)
        obj.linea = linea
        obj.columna = columna
        return obj


# cambie aqui: segun el Catalogo de Tokens, STRING (entre comillas) e
# IDENTIFICADOR (palabra suelta) son conceptualmente distintos, aunque los
# dos terminen siendo texto (str) en Python. Sin esta distincion, la
# validacion semantica no puede saber si "guardarDatos" en click=guardarDatos
# vino con o sin comillas. Se crean subclases para poder usar isinstance().
#Mauricio estuvo aqui
class StringLiteral(_StrPos):
    """Valor que vino de un token STRING, es decir iba entre comillas."""
    pass


class Identificador(_StrPos):
    """Valor que vino de un token IDENTIFICADOR, es decir sin comillas."""
    pass


class ASTBuilder(Transformer):

    # tipos de atributos que pueden existir
    def STRING(self, tok):
        return StringLiteral(tok.value[1:-1], tok.line, tok.column)

    def NUMERO(self, tok):
        return int(tok.value)

    def COLOR_HEX(self, tok):
        return _StrPos(tok.value, tok.line, tok.column)

    def IDENTIFICADOR(self, tok):
        return Identificador(tok.value, tok.line, tok.column)

    def booleano(self, items):
        return str(items[0]) == "true"

    def lista(self, items):
        return self._significativos(items)

    @staticmethod
    def _significativos(items):
        return [it for it in items if not isinstance(it, LarkToken)]

    def atributo(self, items):
        nombre, valor = self._significativos(items)
        return Atributo(
            nombre=str(nombre), valor=valor,
            linea=nombre.linea, columna=nombre.columna,
        )

    def atributos(self, items):
        return _ListaAtributos(self._significativos(items))

    def bloque(self, items):
        return _ListaHijos(self._significativos(items))

    def _separar_extras(self, items):
        atributos, contenido = [], []
        for extra in items:
            if isinstance(extra, _ListaAtributos):
                atributos = list(extra)
            elif isinstance(extra, _ListaHijos):
                contenido = list(extra)
        return atributos, contenido

    def panel(self, items):
        tag_tok = items[0]   
        tipo = str(tag_tok)
        resto = self._significativos(items[1:])
        titulo = resto[0]
        atributos, contenido = self._separar_extras(resto[1:])
        return Widget(
            tipo=tipo, titulo=titulo, atributos=atributos, contenido=contenido,
            linea=tag_tok.line, columna=tag_tok.column,
        )

    def widget(self, items):
        tag_tok = items[0]   
        tipo = str(tag_tok)
        resto = self._significativos(items[1:])
        titulo = resto[0]
        atributos, _ = self._separar_extras(resto[1:])
        return Widget(
            tipo=tipo, titulo=titulo, atributos=atributos, contenido=[],
            linea=tag_tok.line, columna=tag_tok.column,
        )

    def ventana(self, items):
        tag_tok = items[0]   
        resto = self._significativos(items[1:])
        titulo = resto[0]
        atributos, contenido = self._separar_extras(resto[1:])
        return Ventana(
            titulo=titulo, atributos=atributos, contenido=contenido,
            linea=tag_tok.line, columna=tag_tok.column,
        )

    def programa(self, items):
        return items[0]

# validaciones para errores sintacticos, informa que tipo de error puede haber y en donde
class ErrorSintactico(Exception):
    def __init__(self, mensaje, linea, columna):
        super().__init__(f"Error sintáctico en línea {linea}, columna {columna}: {mensaje}")
        self.linea = linea
        self.columna = columna


_DESCRIPCION_TERMINAL = {
    "LLAVE_IZQ": "'{'",
    "LLAVE_DER": "'}'",
    "CORCHETE_IZQ": "'['",
    "CORCHETE_DER": "']'",
    "IGUAL": "'='",
    "COMA": "','",
    "STRING": "un texto entre comillas",
    "NUMERO": "un número",
    "COLOR_HEX": "un color hexadecimal (#RRGGBB)",
    "IDENTIFICADOR": "un nombre de atributo",
    "KW_TRUE": "'true'",
    "KW_FALSE": "'false'",
    "KW_VENTANA": "'Ventana'",
    "KW_PANEL": "'Panel'",
    "KW_INPUT": "'Input'",
    "KW_TEXTAREA": "'TextArea'",
    "KW_CHECKBOX": "'Checkbox'",
    "KW_RADIOBUTTON": "'RadioButton'",
    "KW_COMBOBOX": "'ComboBox'",
    "KW_SLIDER": "'Slider'",
    "KW_LABEL": "'Label'",
    "KW_IMAGEN": "'Imagen'",
    "KW_BOTON": "'Boton'",
    "$END": "el fin del archivo",
}


def _describir(nombre_terminal: str) -> str:
    return _DESCRIPCION_TERMINAL.get(nombre_terminal, nombre_terminal)


_WIDGET_TAGS_EN_ORDEN = [
    "KW_INPUT", "KW_TEXTAREA", "KW_CHECKBOX", "KW_RADIOBUTTON",
    "KW_COMBOBOX", "KW_SLIDER", "KW_LABEL", "KW_IMAGEN", "KW_BOTON",
]
_TERMINALES_CON_VALOR_VARIABLE = {"STRING", "NUMERO", "COLOR_HEX", "IDENTIFICADOR"}


def _mensaje_error(e: UnexpectedInput) -> str:
    if not isinstance(e, UnexpectedToken):
        return str(e).splitlines()[0]

    encontrado = _describir(e.token.type)
    if e.token.type in _TERMINALES_CON_VALOR_VARIABLE:
        encontrado += f" ({e.token.value!r})"

    esperado_set = set(e.expected)
    partes = []

    # si se esperaba cualquier widget, agruparlos en un solo texto 
    if _WIDGET_TAGS_EN_ORDEN and set(_WIDGET_TAGS_EN_ORDEN) <= esperado_set:
        esperado_set -= set(_WIDGET_TAGS_EN_ORDEN)
        nombres = [_describir(t).strip("'") for t in _WIDGET_TAGS_EN_ORDEN]
        partes.append("un widget (" + ", ".join(nombres) + ")")

    partes.extend(sorted(_describir(t) for t in esperado_set))

    if len(partes) == 1:
        esperados_str = partes[0]
    else:
        esperados_str = ", ".join(partes[:-1]) + " o " + partes[-1]

    return f"se encontró {encontrado}, pero se esperaba {esperados_str}"


def _a_token_lark(t: TokenLexico) -> LarkToken:
    return LarkToken(
        t.tipo, t.lexema,
        line=t.linea, column=t.columna,
        end_line=t.linea, end_column=t.columna + len(t.lexema),
    )


def parse(tokens: List[TokenLexico]) -> Ventana:
    """
    Recibe los tokens y agarra el raiz (ventana), para poder empezar a construir
    el AST, construyendolo de a poco mediante lo que cada atributo pueda 
    contener
    """
    tokens_lark = [_a_token_lark(t) for t in tokens]

    try:
        arbol = _parser.parse(tokens_lark)
    except UnexpectedInput as e:
        linea = getattr(e, "line", "?")
        columna = getattr(e, "column", "?")
        raise ErrorSintactico(_mensaje_error(e), linea, columna) from e

    return ASTBuilder().transform(arbol)