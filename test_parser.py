
# --> Aqui se genera un ejemplo, basado en el que tiene el tokenizador,
#     para ver la funcionalidad del parser, es decir, ver claramente como
#     genera el AST a partir de la gramatica del DSL dado. 

if __name__ == "__main__":
    from tokenizador import tokenize
    from parser import parse, ErrorSintactico
    import pprint

    ejemplo = '''// Formulario de registro de usuario
Ventana "Sistema de Registro" [ancho=800, alto=600] {
    Panel "encabezado" [color=gris] {
        Label "Formulario de Registro" [color=negro, tamañoFuente=20]
        Imagen "logo" [src="logo.png", ancho=100, alto=100]
    }
    Panel "datosPersonales" [color=blanco] {
        Input "nombre" [placeholder="Escribe tu nombre", tipo=texto]
        Checkbox "acepto" [texto="Acepto los términos", marcado=false]
        ComboBox "pais" [opciones=["Guatemala","Mexico","Honduras"]]
        Slider "volumen" [min=0, max=100]
    }
    Boton "Enviar" [color=#3498DB, click=enviarFormulario]
}'''

    tokens = tokenize(ejemplo)
    ast = parse(tokens)
    pprint.pprint(ast)

    print("\n Caso sin atributos ni bloque ")
    pprint.pprint(parse(tokenize('Ventana "x" { Boton "ok" }')))

    print("\n Caso de error sintáctico (falta '}') ")
    try:
        parse(tokenize('Ventana "x" {'))
    except ErrorSintactico as e:
        print(e)

