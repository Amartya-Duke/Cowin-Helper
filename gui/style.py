from tkinter.ttk import Style as tkStyle
import tkinter.font as tkFont

class Style:

    BUTTON_STYLE = 'W.TButton'
    LABEL_BOLD_STYLE = 'LBold.TLabel'
    LABEL_LIGHT_STYLE = 'LLight.TLabel'
    LABEL_LIGHT_ITALIC_STYLE = 'LLightItalic.TLabel'


    @staticmethod
    def configure():
        style = tkStyle()
        style.configure(Style.BUTTON_STYLE, font=("Times New Roman",20, 'bold'),
                        foreground='green')

        style = tkStyle()
        style.configure(Style.LABEL_BOLD_STYLE, font=("Times New Roman", 20, 'bold'))

        style = tkStyle()
        style.configure(Style.LABEL_LIGHT_STYLE, font=("Times New Roman", 15))

        style = tkStyle()
        style.configure(Style.LABEL_LIGHT_ITALIC_STYLE, font=("Times New Roman", 15, 'italic'))

        print("Style configured")
