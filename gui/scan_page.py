import tkinter as tk
from tkinter import ttk
import tkinter.font as tkFont
from CowinHelper.gui.style import Style
from CowinHelper.app import CowinHelper
from CowinHelper.app import Slot
from CowinHelper.gui.scrollable_frame import VerticalScrolledFrame
from CowinHelper.gui.slot_frame import SlotFrame
import threading
from svglib.svglib import svg2rlg
from reportlab.graphics import  renderPM
import re
from PIL import Image, ImageTk

class ScanPage:
    def __init__(self, master, state_id_name, districts, cowin_helper, start_scan_callback, refresh_captcha_callback, book_slot_callback):
        self.master = master
        self.state_id, self.state_name = state_id_name
        self.districts = districts
        self.cowin_helper = cowin_helper
        self.slot_frames = []
        self.start_scan_callback = start_scan_callback
        self.book_slot_callback = book_slot_callback
        self.refresh_captcha_callback = refresh_captcha_callback
        self.captcha_var = tk.StringVar(value="Enter Captcha")

    def setup_widgets(self):
        Style.configure()

        # header frame
        header_frame = ttk.Label(master=self.master, text="Welcome {}".format(self.cowin_helper.mobile_number), style=Style.LABEL_BOLD_STYLE)
        header_frame.grid(row=0)

        header_label = ttk.Label(master=header_frame, text="Welcome {}".format(self.cowin_helper.mobile_number), style=Style.LABEL_BOLD_STYLE)
        header_label.grid(row=0)



        # left frame
        left_frame = tk.Frame(master=self.master, )
        left_frame.grid(row=1, column=0)

        self.setup_left_frame(left_frame)

        # divider
        separator = ttk.Separator(self.master, orient=tk.VERTICAL)
        separator.grid(row=1, column=1, rowspan=10, sticky='ns', padx=100)

        #right frame
        right_frame = tk.Frame(master=self.master)
        right_frame.grid(row=1, column=2)
        print("Setting up right frame")
        self.setup_right_frame(right_frame)
        print("All widget setup done")

    def set_beneficiaries(self, parent):
        self.cowin_helper.fetch_beneficiaries()
        beneficiaries = self.cowin_helper.beneficiary_map
        row_index=0
        for id, name in beneficiaries.items():
            chk_button = tk.Checkbutton(master=parent, text=name, font=("Times New Roman", 20, 'bold'))
            chk_button.grid(row=row_index,column=0, sticky=tk.W)
            label = ttk.Label(master=parent, text='[beneficiary id={}]'.format(id), style=Style.LABEL_LIGHT_ITALIC_STYLE)
            label.grid(row=row_index, column=1, sticky=tk.W)
            row_index += 1

    def setup_left_frame(self, middle_frame):
        # beneficiary display
        beneficiary_list_frame = tk.Frame(master=middle_frame,)
        beneficiary_list_frame.grid(row=1, column=0, pady=20)

        beneficiary_list_content_frame = tk.Frame(master=beneficiary_list_frame, height=100)
        beneficiary_list_content_frame.pack(expand=True, fill=tk.BOTH)

        get_beneficiaries_btn = ttk.Button(master=beneficiary_list_frame, style=Style.BUTTON_STYLE, text='Fetch beneficiaries', command=lambda: self.set_beneficiaries(beneficiary_list_content_frame))
        get_beneficiaries_btn.pack(side=tk.BOTTOM)

        # scan params display
        scan_params_frame = tk.Frame(master=middle_frame)
        scan_params_frame.grid(row=0,column=0, sticky=tk.NW)

        self.setup_filters_frame(scan_params_frame)

        ttk.Button(master=beneficiary_list_frame, style=Style.BUTTON_STYLE, text='Start Scan',
                   command=self.start_scan_callback).pack()

    def setup_filters_frame(self, parent_frame):
        row = 0
        label = ttk.Label(master=parent_frame, text="State ", style=Style.LABEL_LIGHT_STYLE)
        label.grid(row=row, column=0, padx=10, sticky=tk.W)
        label = ttk.Label(master=parent_frame, text=self.state_name, style=Style.LABEL_LIGHT_STYLE)
        label.grid(row=row, column=1, rowspan=1, stick=tk.W)

        row+=1
        label = ttk.Label(master=parent_frame, text="Districts ", style=Style.LABEL_LIGHT_STYLE)
        label.grid(row=row, column=0, padx=10, sticky=tk.W)

        for district_id, district_name in self.districts:
            label = ttk.Label(master=parent_frame, text='\u2022' + district_name, style=Style.LABEL_LIGHT_STYLE)
            label.grid(row=row, column=1, rowspan=1, stick=tk.W)
            row += 1

        label = ttk.Label(master=parent_frame, text="Age group ", style=Style.LABEL_LIGHT_STYLE)
        label.grid(row=row, column=0, padx=10, sticky=tk.W)
        label = ttk.Label(master=parent_frame, text=":{}+".format(self.cowin_helper.min_age_limit), style=Style.LABEL_LIGHT_STYLE)
        label.grid(row=row, column=1, rowspan=1, stick=tk.W)

        row+=1
        label = ttk.Label(master=parent_frame, text="Vaccine dose# ", style=Style.LABEL_LIGHT_STYLE)
        label.grid(row=row, column=0, padx=10, sticky=tk.W)
        label = ttk.Label(master=parent_frame, text=str(self.cowin_helper.vaccine_dose_no), style=Style.LABEL_LIGHT_STYLE)
        label.grid(row=row, column=1, rowspan=1, stick=tk.W)

        row+=1
        label = ttk.Label(master=parent_frame, text="Start date", style=Style.LABEL_LIGHT_STYLE)
        label.grid(row=row, column=0, padx=10, sticky=tk.W)
        label = ttk.Label(master=parent_frame, text=str(self.cowin_helper.start_date), style=Style.LABEL_LIGHT_STYLE)
        label.grid(row=row, column=1, rowspan=1, stick=tk.W)

        row+=1
        label = ttk.Label(master=parent_frame, text="End date", style=Style.LABEL_LIGHT_STYLE)
        label.grid(row=row, column=0, padx=10, sticky=tk.W)
        label = ttk.Label(master=parent_frame, text=str(self.cowin_helper.end_date), style=Style.LABEL_LIGHT_STYLE)
        label.grid(row=row, column=1, rowspan=1, stick=tk.W)

    def setup_otp_frame(self, parent_frame):
        # otp frame
        otp_frame = tk.Frame(master=parent_frame, background='red', width=100)
        otp_frame.pack()

    def get_dummy_slots(self):
        slots = []
        import datetime
        for i in range(3):
            slots.append(Slot(session_id='session-id_{}'.format(i), center_id='center-id_1{}'.format(i), date=datetime.date.today(), center_name='ABC-{}'.format(i), district_id=1,vaccine_type='Covaxin', time_slots=["10am-12pm", "1pm-3pm", "5pm-7pm", "7pm-9pm"],slots_available=100 ))
        for i in range(4):
            slots.append(Slot(session_id='session-id_{}'.format(i), center_id='center-id_2{}'.format(i), date=datetime.date.today(), center_name='ABC-{}'.format(i), district_id=2,vaccine_type='Covaxin', time_slots=["10am-12pm", "1pm-3pm", "5pm-7pm", "7pm-9pm"],slots_available=100 ))

        return slots

    def setup_right_frame(self, parent_frame):
        self.slot_list_frame = VerticalScrolledFrame(master=parent_frame, height=500)
        self.slot_list_frame.pack(side=tk.TOP)

        #self.setup_slots_available_display(slot_list_frame,self.get_dummy_slots())

    def setup_slots_available_display(self, slots):
        #self.slot_list_frame.pack_forget()
        slots = slots[:5]
        districts_list = list(set([slot.district_id for slot in slots]))
        print(districts_list)
        for index, district_id in enumerate(districts_list):
            district_frame = tk.Frame(master=self.slot_list_frame,borderwidth=1, relief=tk.RIDGE)
            district_frame.pack(expand=True, fill=tk.X)
            district_slots = list(filter(lambda slot: slot.district_id==district_id, slots))
            district_label = ttk.Label(master=district_frame, text=list(filter(lambda district: district[0] == district_id, self.districts))[0][1], font="Times 15 bold", background='pink', anchor='center')
            district_label.pack(fill=tk.X)

            district_slots_frame = tk.Frame(master=self.slot_list_frame, borderwidth=1, relief=tk.RIDGE)
            district_slots_frame.pack()

            # prepare slot frame
            district_slots.sort(key=lambda slot: slot.date)
            SlotFrame(parent=district_slots_frame, slots=district_slots, on_slot_selected_callback=lambda slot: self.on_slot_selected(slot)).create_slot_frames()

            # divider
            separator = ttk.Separator(district_frame, orient=tk.HORIZONTAL)
            # separator.grid(row=index+1, rowspan=10, sticky=tk.EW)
            separator.pack()

        self.slot_list_frame.update()

    def on_slot_selected(self, slot):
        self.refresh_booking_frame(slot)

    def clear_captcha_entry(self, event, entry):
        self.captcha_var.set("")
        entry.unbind('<Button-1>')

    def on_book_click(self, chosen_time_slot):
        captcha_text = self.captcha_var.get()
        selected_time_slot = "10:00-12:00"
        selected_slot = SlotFrame.SELECTED[1]
        self.book_slot_callback(selected_slot, selected_time_slot, captcha_text)

    def refresh_booking_frame(self, slot):
        captcha_svg_content = self.refresh_captcha_callback()
        with open('captcha.svg', 'w') as f:
            f.write(re.sub('(<path d=)(.*?)(fill=\"none\"/>)', '', captcha_svg_content))
        drawing = svg2rlg('captcha.svg')
        renderPM.drawToFile(drawing, "captcha.png", fmt="PNG")


        image=Image.open('captcha.png')
        width, height = image.size
        image = image.resize((width*2, height*2), Image.ANTIALIAS)
        width, height = image.size
        captcha_image = ImageTk.PhotoImage(image)

        label = tk.Label(master=self.captcha_container, image=captcha_image,width=width, height=height)
        label.image = captcha_image
        label.grid(row=0)

        self.captcha_var.set("Enter captcha")

    def setup_booking_frame(self):
        self.captcha_container = tk.Frame(self.master, height=500, width=600, bg='lightblue')
        self.captcha_container.pack(side=tk.BOTTOM)

        captch_input = tk.Entry(self.captcha_container, fg='green',
                        font="Times 20 bold", borderwidth=4, justify="center", width=20)
        captch_input.bind("<Button-1>", lambda event: self.clear_captcha_entry(event, captch_input))
        captch_input.grid(row=1, pady=10)
        captch_input['textvariable'] = self.captcha_var

        book_btn = tk.Button(self.captcha_container, width=30, height=1, font="Times 20 bold", borderwidth=4,
                       relief="raised", justify="center", text='Book', command=self.on_book_click)
        book_btn.grid(row=2)