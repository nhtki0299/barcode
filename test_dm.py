import tkinter as tk
import explorers.datamatrix as dm

root = tk.Tk()
root.withdraw()  # Hide main window

def check():
    try:
        dm.open_datamatrix_explorer("Hello DataMatrix!")
        print("SUCCESS")
    except Exception as e:
        print("ERROR:", e)
    root.after(100, root.destroy)

root.after(100, check)
root.mainloop()
