import tkinter as tk
from PIL import Image, ImageTk
import re
from svglib.svglib import svg2rlg
from reportlab.graphics import  renderPM
from CowinHelper.app import CowinHelper
import threading

class SlotBookingGui:
    def __init__(self, master):
        self.master = master
        self.captcha_var = tk.StringVar()
        self.cowin_helper = CowinHelper('9629778910')
        #self.cowin_helper.run_periodically(interval_in_mins=0.2, gui_callback=lambda captcha_svg_content, payload: self.setup_widgets(captcha_svg_content, payload))
        threading.Thread(target=self.cowin_helper.run_periodically, args=(1, lambda captcha_svg_content, payload: self.setup_widgets(captcha_svg_content, payload))).start()
        #self.setup_widgets()

    def clear_entry(self, event, entry):
        self.captcha_var.set("")
        entry.unbind('<Button-1>')

    def on_book_click(self, payload):
        captcha_text = self.captcha_var.get()
        self.cowin_helper.book_slot_after_captcha(captcha_text, payload)

    def setup_widgets(self, captcha_svg_content, payload):
        print(captcha_svg_content)
        with open('captcha.svg', 'w') as f:
            f.write(re.sub('(<path d=)(.*?)(fill=\"none\"/>)', '', captcha_svg_content))

        drawing = svg2rlg('captcha.svg')
        renderPM.drawToFile(drawing, "captcha.png", fmt="PNG")

        captcha_container = tk.Frame(self.master, height=500, width=600, bg='lightblue')
        captcha_container.pack(side=tk.BOTTOM)

        image=Image.open('captcha.png')
        width, height = image.size
        image = image.resize((width*2, height*2), Image.ANTIALIAS)
        width, height = image.size
        captcha_image = ImageTk.PhotoImage(image)

        label = tk.Label(master=captcha_container, image=captcha_image,width=width, height=height)
        label.image = captcha_image
        label.grid(row=0)

        captch_input = tk.Entry(captcha_container, fg='green',
                        font="Times 20 bold", borderwidth=4, justify="center", width=20)
        captch_input.bind("<Button-1>", lambda event: self.clear_entry(event, captch_input))
        captch_input.grid(row=1, pady=10)

        self.captcha_var.set("Enter captcha")
        captch_input['textvariable'] = self.captcha_var

        book_btn = tk.Button(captcha_container, width=30, height=1, font="Times 20 bold", borderwidth=4,
                       relief="raised", justify="center", text='Book', background='black', command=lambda: self.on_book_click(payload))
        book_btn.grid(row=2)

if __name__ == '__main__':
    root = tk.Tk()

    app = SlotBookingGui(master=root)

    root.title("Cowin slot booking")
    root.geometry("1920x720")
    tk.mainloop()
