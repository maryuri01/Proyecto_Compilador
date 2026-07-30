# -*- coding: utf-8 -*-

import argparse
import sys
from pathlib import Path

from tokenizador import tokenize, ErrorLexico
from parser import parse, ErrorSintactico

from validador_semantico import validar_semantica

from backend_html import GeneradorHTML
from backend_tkinter import GeneradorTkinter

# LEER ARCHIVO DSL

def leer_archivo(ruta):
    
    #Lee el archivo DSL y devuelve su contenido.
    
    archivo = Path(ruta)

    if not archivo.exists():
        raise FileNotFoundError(
            f"No se encontró el archivo '{ruta}'."
        )

    if not archivo.is_file():
        raise ValueError(
            f"La ruta '{ruta}' no corresponde a un archivo."
        )

    try:
        return archivo.read_text(
            encoding="utf-8"
        )

    except OSError as error:
        raise OSError(
            f"No se pudo leer el archivo '{ruta}': {error}"
        )


# GUARDAR ARCHIVO

def guardar_archivo(ruta, contenido):
    
    #Guarda el código generado en un archivo.
    
    archivo = Path(ruta)

    archivo.write_text(
        contenido,
        encoding="utf-8"
    )


# ANALIZAR Y VALIDAR DSL

def procesar_dsl(ruta_entrada):
    """
    Ejecuta el pipeline:
    1. Lectura del archivo.
    2. Análisis léxico.
    3. Análisis sintáctico.
    4. Construcción del AST.
    5. Validación semántica.
    Devuelve el AST si no existen errores.
    """

    # 1. LEER ARCHIVO
   
    codigo = leer_archivo(
        ruta_entrada
    )

    # 2. ANÁLISIS LÉXICO
   
    tokens = tokenize(
        codigo
    )
 
    # 3. ANÁLISIS SINTÁCTICO
 
    ast = parse(
        tokens
    )

    # 4. VALIDACIÓN SEMÁNTICA

    errores = validar_semantica(
        ast
    )

    # SI EXISTEN ERRORES, NO SE GENERA CÓDIGO

    if errores:

        mensaje = "\n".join(
            str(error)
            for error in errores
        )

        raise ValueError(
            mensaje
        )

    # AST CORRECTO

    return ast


# GENERAR CÓDIGO SEGÚN EL TARGET

def generar_codigo(ast, target):
    """
    Selecciona el backend correspondiente.
    target = html selecciona  backend_html.py
    target = tkinter selecciona backend_tkinter.py
    """

    if target == "html":

        generador = GeneradorHTML()

        return generador.generar(
            ast
        )

    elif target == "tkinter":

        generador = GeneradorTkinter()

        return generador.generar(
            ast
        )

    else:

        raise ValueError(
            f"Target no soportado: {target}"
        )


# DETERMINAR ARCHIVO DE SALIDA

def obtener_archivo_salida(
    archivo_entrada,
    target
):
    # Genera automáticamente el nombre del archivo de salida.

    archivo = Path(
        archivo_entrada
    )

    if target == "html":

        return archivo.with_suffix(
            ".html"
        )

    elif target == "tkinter":

        return archivo.with_name(
            archivo.stem
            + "_tkinter.py"
        )

    else:

        raise ValueError(
            f"Target no soportado: {target}"
        )


# CONFIGURAR CLI

def crear_cli():
    
    #Configura los argumentos de la línea de comandos.
    
    parser_cli = argparse.ArgumentParser(

        prog="main",

        description=(
            "Generador de interfaces gráficas a partir de un lenguaje DSL."
        )
    )

    # ARCHIVO DE ENTRADA

    parser_cli.add_argument(

        "input",

        help=(
            "Archivo DSL que se desea procesar."
        )
    )
  
    # TARGET

    parser_cli.add_argument(

        "--target",

        required=True,

        choices=[
            "html",
            "tkinter"
        ],

        help=(
            "Backend utilizado para generar el código de salida."
        )
    )

    return parser_cli

# FUNCIÓN PRINCIPAL

def main():
    # CREAR CLI
    
    cli = crear_cli()

    argumentos = cli.parse_args()

    archivo_entrada = argumentos.input

    target = argumentos.target

    try:

        print()
        print("=" * 60)
        print("           GENERADOR")
        print("=" * 60)

        print(
            f"Archivo de entrada: {archivo_entrada}"
        )

        print(
            f"Target seleccionado: {target}"
        )

        print()
        # PASO 1
        
        print(
            "[1/4] Procesando archivo DSL..."
        )

        ast = procesar_dsl(
            archivo_entrada
        )

        print(
            "      ✓ Análisis léxico correcto"
        )

        print(
            "      ✓ Análisis sintáctico correcto"
        )

        print(
            "      ✓ AST construido correctamente"
        )

        print(
            "      ✓ Validación semántica correcta"
        )

        # PASO 2
        print()

        print(
            "[2/4] Seleccionando backend..."
        )

        if target == "html":

            print(
                "      ✓ Backend HTML seleccionado"
            )

        else:

            print(
                "      ✓ Backend Tkinter seleccionado"
            )
  
        # PASO 3

        print()

        print(
            "[3/4] Generando código..."
        )

        codigo_generado = generar_codigo(
            ast,
            target
        )

        print(
            "      ✓ Código generado correctamente"
        )
 
        # PASO 4

        print()

        print(
            "[4/4] Guardando archivo..."
        )

        archivo_salida = obtener_archivo_salida(
            archivo_entrada,
            target
        )

        guardar_archivo(
            archivo_salida,
            codigo_generado
        )

        print(
            f"      ✓ Archivo generado: "
            f"{archivo_salida}"
        )

        # FINAL

        print()

        print("=" * 60)
        print("          GENERACIÓN EXITOSA")
        print("=" * 60)

        print()

        return 0

    # ERROR LÉXICO

    except ErrorLexico as error:

        print(
            str(error),
            file=sys.stderr
        )

        return 1

    # ERROR SINTÁCTICO

    except ErrorSintactico as error:

        print(
            str(error),
            file=sys.stderr
        )

        return 1

    # ERROR SEMÁNTICO

    except ValueError as error:

        print(
            str(error),
            file=sys.stderr
        )

        return 1

    # ARCHIVO NO ENCONTRADO

    except FileNotFoundError as error:

        print(
            f"Error: {error}",
            file=sys.stderr
        )

        return 1

    # OTROS ERRORES

    except Exception as error:

        print(
            (
                "Error inesperado durante "
                f"la ejecución: {error}"
            ),
            file=sys.stderr
        )

        return 1


# PUNTO DE ENTRADA

if __name__ == "__main__":

    sys.exit(
        main()
    )