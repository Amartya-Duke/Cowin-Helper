import tkinter as tk
from CowinHelper.gui.style import Style


class SlotFrame():
    SELECTED = (None, None)    # (frame_ref, slot)

    def __init__(self, parent, slots, on_slot_selected_callback):
        self.parent = parent
        self.slots = slots
        self.on_slot_selected_callback = on_slot_selected_callback

    def create_label(self, slot_frame, text, row, column, font=None):
        lbl = tk.Label(master=slot_frame, text=text,relief=tk.FLAT)
        if font:
            lbl['font']=font
        lbl.grid(row=row, column=column, sticky=tk.W, padx=5)
        bindtags = list(lbl.bindtags())
        bindtags.insert(1, slot_frame)
        lbl.bindtags(tuple(bindtags))

    def on_enter(self, event, widget):
        if event and not event.widget.children: # child enter. Don't do anything
            return "break"
        if widget == SlotFrame.SELECTED[0]: # if already clicked, do nothing
            return "break"
        widget.config(background='SkyBlue2')
        # apply to all children
        for child_type, child in widget.children.items():
            child.config(background='SkyBlue2')

    def on_leave(self, event, widget):
        if event and not event.widget.children: # child enter. Don't do anything
            return "break"
        if event and widget == SlotFrame.SELECTED[0]: # if already clicked, do nothing
            return "break"
        widget.config(background='SystemButtonFace')
        # apply to all children
        for child_type, child in widget.children.items():
            child.config(background='SystemButtonFace')

    def select_frame(self, widget):
        widget.config(relief=tk.SUNKEN)

    def unselect_frame(self, widget):
        widget.config(relief=tk.RAISED)

    def on_click(self, event, widget, slot):
        if widget != SlotFrame.SELECTED[0]:
            if SlotFrame.SELECTED[0]:
                self.unselect_frame(SlotFrame.SELECTED[0])
                self.on_leave(None, SlotFrame.SELECTED[0])
            self.select_frame(widget)
            SlotFrame.SELECTED = (widget, slot)
            self.on_slot_selected_callback(slot)
        else:
            self.unselect_frame(widget)
            SlotFrame.SELECTED = (None, None)
            self.on_enter(None, widget)
        print(SlotFrame.SELECTED)

    def create_slot_frames(self):
        font_style_key_label = ("Times New Roman", 15, 'bold', 'italic')
        font_style_value_label = ("Times New Roman", 15)
        for index, slot in enumerate(self.slots):
            def make_lambda(func,*args):
                return lambda ev: func(ev, *args)

            slot_frame = tk.Frame(master=self.parent,borderwidth=3, relief=tk.RAISED, cursor='hand2')
            slot_frame.pack(expand=True, fill=tk.BOTH,padx=20)
            tk.Radiobutton(master=slot_frame, variable='slot_center_id_selection', value=slot.center_id).grid(row=0, column=0)

            row_index = 0
            self.create_label(slot_frame, 'Center ID', row_index, 1, font=font_style_key_label)
            self.create_label(slot_frame, slot.center_id, row_index, 2, font=font_style_value_label)

            row_index += 1
            self.create_label(slot_frame, 'Date',row_index, 1, font=font_style_key_label)
            self.create_label(slot_frame, str(slot.date), row_index, 2,font=font_style_value_label)

            row_index += 1
            self.create_label(slot_frame, 'Center Name',row_index, 1, font=font_style_key_label)
            self.create_label(slot_frame, slot.center_name, row_index, 2,font=font_style_value_label)

            row_index += 1
            self.create_label(slot_frame, 'Vaccine Type',row_index, 1, font=font_style_key_label)
            self.create_label(slot_frame, slot.vaccine_type, row_index, 2, font=font_style_value_label)

            row_index += 1
            self.create_label(slot_frame, 'Vacancy',row_index, 1, font=font_style_key_label)
            self.create_label(slot_frame, slot.slots_available, row_index, 2, font=font_style_value_label)

            slot_frame.bind('<Button-1>', make_lambda(self.on_click, slot_frame, slot))
            slot_frame.bind("<Enter>", make_lambda(self.on_enter, slot_frame))
            slot_frame.bind("<Leave>", make_lambda(self.on_leave, slot_frame))
