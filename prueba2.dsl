Ventana "Sistema de Registro" [
    ancho = 800,
    alto = 600
] {

    Panel "Formulario" [
        id = "panelFormulario",
        color = azul
    ] {

        Label "Registro de Usuario" [
            color = blanco,
            tamañoFuente = 20
        ]

        Input "Nombre" [
            id = "nombre",
            placeholder = "Ingrese su nombre",
            tipo = texto
        ]

        Input "Contraseña" [
            id = "contrasena",
            placeholder = "Ingrese su contraseña",
            tipo = password
        ]

        TextArea "Descripcion" [
            id = "descripcion",
            filas = 5
        ]

        Checkbox "Aceptar términos" [
            id = "terminos",
            texto = "Acepto los términos y condiciones",
            marcado = false
        ]

        RadioButton "Masculino" [
            id = "masculino",
            grupo = genero,
            texto = "Masculino"
        ]

        RadioButton "Femenino" [
            id = "femenino",
            grupo = genero,
            texto = "Femenino"
        ]

        ComboBox "Carrera" [
            id = "carrera",
            opciones = ["Ingeniería", "Medicina", "Derecho", "Administración"]
        ]

        Slider "Edad" [
            id = "edad",
            min = 18,
            max = 60
        ]

        Boton "Guardar" [
            color = verde,
            click = guardarDatos
        ]
    }
}