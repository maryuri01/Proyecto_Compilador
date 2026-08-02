from tokenizador import tokenize, ErrorLexico
from parser import parse, ErrorSintactico
from validador_semantico import validar_semantica
from backend_html import GeneradorHTML


DSL_EJEMPLO = '''// Formulario de registro de usuario
Ventana "Sistema de Registro" [ancho=800, alto=600] {
    Panel "encabezado" [color=gris] {
        Label "Formulario de Registro" [color=negro, tamañoFuente=20]
        Imagen "logo" [src="logo.png", ancho=100, alto=100]
    }
    Panel "datosPersonales" [color=blanco] {
        Label "Nombre completo:" [color=negro]
        Input "nombre" [placeholder="Escribe tu nombre", tipo=texto]
        Label "Comentarios:" [color=negro]
        TextArea "comentario" [filas=4]
        Checkbox "acepto" [texto="Acepto los terminos", marcado=false]
        RadioButton "op1" [grupo=genero, texto="Masculino"]
        RadioButton "op2" [grupo=genero, texto="Femenino"]
        ComboBox "pais" [opciones=["Guatemala","Mexico","Honduras"]]
        Slider "volumen" [min=0, max=100]
    }
    Boton "Enviar" [color=azul, click=enviarFormulario]
}'''


def ejecutar_pipeline(codigo_fuente, nombre_caso):
    """Corre el pipeline completo y reporta las acciones"""
    print(f"--- {nombre_caso} ---")
    try:
        tokens = tokenize(codigo_fuente)
    except ErrorLexico as e:
        print(f"  Fallo en el LEXER: {e}")
        return None

    try:
        ast = parse(tokens)
    except ErrorSintactico as e:
        print(f"  Fallo en el PARSER: {e}")
        return None

    errores_semanticos = validar_semantica(ast)
    if errores_semanticos:
        print("  Fallo en la VALIDACION SEMANTICA:")
        for err in errores_semanticos:
            print(f"    {err}")
        return None

    html = GeneradorHTML().generar(ast)
    print("  OK -- se genero HTML sin errores.")
    return html


if __name__ == "__main__":

    # 1. Ejemplo DSL
    html = ejecutar_pipeline(DSL_EJEMPLO, "Caso 1: ejemplo completo del documento de diseño")
    if html:
        with open("salida_ejemplo.html", "w", encoding="utf-8") as f:
            f.write(html)
        print("  HTML guardado en salida_ejemplo.html (abrir en el navegador)")
    print()

    # 2. Error lexico: string sin cerrar 
    dsl_error_lexico = '''Ventana "Mi App" {
    Boton "Guardar
}'''
    ejecutar_pipeline(dsl_error_lexico, "Caso 2: string sin cerrar (deberia fallar en el lexer)")
    print()

    # 3. Error sintactico: un Boton con bloque {} 
    dsl_error_sintactico = '''Ventana "Mi App" {
    Boton "Guardar" [color=azul] {
        Input "esto no deberia poder existir aqui"
    }
}'''
    ejecutar_pipeline(dsl_error_sintactico, "Caso 3: Boton con hijos (deberia fallar en el parser)")
    print()

    # 4. Error semantico: atributo invalido para ese widget 
    dsl_error_semantico = '''Ventana "Mi App" {
    Boton "Guardar" [src="no_deberia_estar_aqui.png"]
}'''
    ejecutar_pipeline(dsl_error_semantico, "Caso 4: atributo invalido (deberia fallar en la validacion semantica)")
    print()

    # 5. El ejemplo original del proyecto
    dsl_ejemplo_simple = '''Ventana "Mi App" {
    Boton "Guardar" [color=azul, click=guardarDatos]
    Input "Nombre"
}'''
    html_simple = ejecutar_pipeline(dsl_ejemplo_simple, "Caso 5: ejemplo original y simple del documento del proyecto")
    if html_simple:
        with open("ejemplo_proyecto.html", "w", encoding="utf-8") as f:
            f.write(html_simple)
        print("  HTML guardado en ejemplo_proyecto.html (abrir en el navegador)")