// Formulario de registro 
Ventana "Registro de Usuario" [ancho=520, alto=700] {

    Label "Crear cuenta" [color=negro, tamañoFuente=26]

    Panel "datosPersonales" [color=blanco] {

        Label "Nombre completo" [color=gris, tamañoFuente=13]
        Input "nombre" [placeholder="Tu nombre completo", tipo=texto]

        Label "Correo electronico" [color=gris, tamañoFuente=13]
        Input "correo" [placeholder="ejemplo@correo.com", tipo=texto]

        Label "Contraseña" [color=gris, tamañoFuente=13]
        Input "clave" [placeholder="Minimo 8 caracteres", tipo=password]

        Checkbox "terminos" [texto="Acepto los terminos y condiciones", marcado=false]
    }

    Boton "Crear cuenta" [color=azul, click=registrarUsuario]

}