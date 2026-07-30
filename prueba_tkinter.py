import customtkinter as ctk

app = ctk.CTk()
app.title("Mi Aplicacion")
app.geometry("800x600")

def guardarDatos():
    pass

panel_1 = ctk.CTkFrame(app, fg_color="blue")
panel_1.pack(padx=10, pady=10, fill='both')
label_1 = ctk.CTkLabel(panel_1, text="Nombre", text_color="black", font=("Arial", 18))
label_1.pack(padx=5, pady=5)
input_1 = ctk.CTkEntry(panel_1, placeholder_text="Ingrese su nombre")
input_1.pack(padx=5, pady=5)
boton_1 = ctk.CTkButton(panel_1, text="Guardar", fg_color="green", command=guardarDatos)
boton_1.pack(padx=5, pady=5)

app.mainloop()