import customtkinter as ctk
from PIL import Image

app = ctk.CTk()
app.geometry("400x400")
t = ctk.CTkTextbox(app, width=300, height=300)
t.pack(padx=20, pady=20)

t.insert("end", "Hello World\n\n")

# Create a dummy image
img = Image.new('RGB', (100, 100), color = 'red')
ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(100, 100))

lbl = ctk.CTkLabel(t, image=ctk_img, text="")
# We must keep a reference to ctk_img, which lbl does.
t._textbox.window_create("end", window=lbl)

t.insert("end", "\n\nEnd of text.")

app.after(2000, app.destroy)
app.mainloop()
