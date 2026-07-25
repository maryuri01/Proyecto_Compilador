
## Gramática formal (EBNF)

programa        := ventana EOF

ventana         := KW_VENTANA STRING atributos? bloque

bloque          := LLAVE_IZQ contenido* LLAVE_DER

contenido       := panel | widget

panel           := KW_PANEL STRING atributos? bloque

widget          := widget_tag STRING atributos?

widget_tag      := KW_INPUT | KW_TEXTAREA | KW_CHECKBOX | KW_RADIOBUTTON
                  | KW_COMBOBOX | KW_SLIDER | KW_LABEL | KW_IMAGEN | KW_BOTON

atributos       := CORCHETE_IZQ atributo (COMA atributo)* CORCHETE_DER

atributo        := IDENTIFICADOR IGUAL valor

valor           := STRING | NUMERO | COLOR_HEX | booleano | IDENTIFICADOR | lista

booleano        := KW_TRUE | KW_FALSE

lista           := CORCHETE_IZQ STRING (COMA STRING)* CORCHETE_DER