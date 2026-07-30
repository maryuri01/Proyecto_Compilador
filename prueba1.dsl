Ventana "Mi Aplicacion" [
    ancho = 800,
    alto = 600
] {
    
    Panel "Datos" [
        id = "panelDatos",
        color = azul
    ] {
        
        Label "Nombre" [
            color = negro,
            tamañoFuente = 18
        ]

        Input "Nombre" [
            id = "nombre",
            placeholder = "Ingrese su nombre",
            tipo = texto
        ]

        Boton "Guardar" [
            color = verde,
            click = guardarDatos
        ]
    }
}