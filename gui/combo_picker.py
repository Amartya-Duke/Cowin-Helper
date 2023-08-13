import tkinter as tk
import tkinter.ttk as ttk

class Picker(ttk.Frame):
    def __init__(self, master=None,activebackground='#b1dcfb',values=[],entry_wid=None,activeforeground='black', selectbackground='#003eff', selectforeground='white', command=None, borderwidth=1, relief="solid"):

        self._selected_item = None

        self._values = values

        self._entry_wid = entry_wid

        self._sel_bg = selectbackground
        self._sel_fg = selectforeground

        self._act_bg = activebackground
        self._act_fg = activeforeground

        self._command = command
        ttk.Frame.__init__(self, master, borderwidth=borderwidth, relief=relief)

        self.bind("<FocusIn>", lambda event:self.event_generate('<<PickerFocusIn>>'))
        self.bind("<FocusOut>", lambda event:self.event_generate('<<PickerFocusOut>>'))

        self.dict_checkbutton = {}
        self.dict_checkbutton_var = {}
        self.dict_intvar_item = {}

        for index,item in enumerate(self._values):

            self.dict_intvar_item[item] = tk.IntVar()
            self.dict_checkbutton[item] = ttk.Checkbutton(self, text = item, variable=self.dict_intvar_item[item],command=lambda ITEM = item:self._command(ITEM))
            self.dict_checkbutton[item].grid(row=index, column=0, sticky=tk.NSEW)
            self.dict_intvar_item[item].set(0)


class Combopicker(ttk.Entry, Picker):
    def __init__(self, master,select_callback,selected_items_var, head_value="Select",  width=None, font=None):

        self.callback = select_callback
        self.header_var = tk.StringVar()
        self.header_var.set(head_value)

        self.selected_items_var = selected_items_var

        entry_config = {}
        if width is not None:
            entry_config["width"] = width

        if font:
           entry_config["font"] = font

        ttk.Entry.__init__(self, master, textvariable=self.header_var, **entry_config, state ="readonly")

        self._is_menuoptions_visible = False

        self.bind("<Escape>", lambda event: self.hide_picker())

    def set_values(self, values):
        self.selected_items_var.set([])
        self.picker_frame = Picker(self.winfo_toplevel(), values=values, entry_wid=self.header_var, command=self._on_selected_check)
        self.picker_frame.bind_all("<1>", self._on_click, "+")

    def _on_selected_check(self, SELECTED):
        cur_value = list(self.selected_items_var.get())

        if str(SELECTED) in cur_value:
            cur_value.remove(str(SELECTED))
        else:
            cur_value.append(str(SELECTED))

        self.selected_items_var.set(cur_value)
        if self.callback:
            self.callback(list(self.selected_items_var.get()))

    def _on_click(self, event):
        str_widget = str(event.widget)

        if str_widget == str(self):
            if not self._is_menuoptions_visible:
                self.show_picker()
        else:
            if not str_widget.startswith(str(self.picker_frame)) and self._is_menuoptions_visible:
                self.hide_picker()

    def show_picker(self):
        if not self._is_menuoptions_visible:
            self.picker_frame.place(in_=self, relx=0, rely=1, relwidth=1 )
            self.picker_frame.lift()

        self._is_menuoptions_visible = True

    def hide_picker(self):
        if self._is_menuoptions_visible:
            self.picker_frame.place_forget()

        self._is_menuoptions_visible = False