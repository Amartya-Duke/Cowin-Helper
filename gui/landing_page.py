import datetime
import tkinter as tk
from tkinter import messagebox
from tkinter import  ttk
import tkinter.font as tkFont
from tkcalendar import Calendar,DateEntry
from CowinHelper.gui.combo_picker import Combopicker
from CowinHelper.gui.style import Style


class InputVars:
    def __init__(self, master):
        self.PHONE_INPUT_VAR = tk.StringVar(master=master, value="Phone Number")
        self.STATE_INPUT_VAR = tk.StringVar(master=master)
        self.DISTRICT_LIST_INPUT_VAR = tk.Variable(master=master, )
        self.MIN_AGE_INPUT_VAR = tk.StringVar(master=master, value="18+")
        self.VACCINE_DOSE_INPUT_VAR = tk.StringVar(master=master, value='dose_1')
        self.START_DATE_INPUT_VAR = tk.StringVar(master=master, )
        self.END_DATE_INPUT_VAR = tk.StringVar(master=master )
        self.USE_PUBLIC_API_VAR = tk.BooleanVar(master=master, value=True)


class LandingPage:
    LABEL_FONT = None
    def __init__(self, master, fetch_states_callback, fetch_districts_callback):
        self.master = master
        self.fetch_states_callback = fetch_states_callback
        self.fetch_districts_callback = fetch_districts_callback
        self.district_id_map = dict()
        self.state_id_map = dict()
        self.input_vars = InputVars(master=self.master)


    def validate(self, user_input):
        if not user_input['phone'] or (user_input['phone'] and len(user_input['phone']) != 10):
            messagebox.showinfo("Error", "Please enter valid phone number")
            return False
        if user_input['start_date'] > user_input['end_date']:
            messagebox.showinfo("Error", "Start date cannot be less that end date")
            return False
        if not user_input['districts']:
            messagebox.showinfo("Error", "Please select atleast one district")
            return False
        return True

    def start_scan(self, start_scan_callback):
        user_input = dict()
        user_input['phone'] = self.input_vars.PHONE_INPUT_VAR.get()
        user_input['state'] = (self.state_id_map[self.input_vars.STATE_INPUT_VAR.get()],self.input_vars.STATE_INPUT_VAR.get())
        user_input['districts'] = [ (self.district_id_map[district_name], district_name) for district_name in self.input_vars.DISTRICT_LIST_INPUT_VAR.get()]
        user_input['age_group'] = self.input_vars.MIN_AGE_INPUT_VAR.get()
        user_input['vaccine_dose_no'] = self.input_vars.VACCINE_DOSE_INPUT_VAR.get()
        user_input['start_date'] = self.input_vars.START_DATE_INPUT_VAR.get()
        user_input['end_date'] = self.input_vars.END_DATE_INPUT_VAR.get()
        user_input['use_public_api'] = self.input_vars.USE_PUBLIC_API_VAR.get()

        if self.validate(user_input):
            self.main_frame.pack_forget()
            start_scan_callback(user_input)

    def clear_entry(self, input_var, entry):
        input_var.set("")
        entry.unbind('<Button-1>')

    def setup_widgets(self, bt_callback):
        Style.configure()

        self.main_frame = tk.Frame(master=self.master)
        self.main_frame.pack()
        header_frame = tk.Frame(master=self.main_frame)
        header_frame.pack(expand=True, pady=10)

        header_label = ttk.Label(master=header_frame, text='CoWIN Helper Portal',font=tkFont.Font(family="Times New Roman", size=40, weight='bold'), foreground='Green')
        header_label.pack()

        top_frame = tk.Frame(master=self.main_frame)
        top_frame.pack(expand=True)

        bottom_frame = tk.Frame(master=self.main_frame)
        bottom_frame.pack(expand=True)

        # Start scan btn
        frame = tk.Frame(master=self.main_frame)
        frame.pack(expand=True)
        scan_bt = ttk.Button(master=frame, text='Submit', style=Style.BUTTON_STYLE, command=lambda: self.start_scan(bt_callback))
        scan_bt.pack(pady=20, padx=50)

        self.setup_top_frame(top_frame)
        self.setup_slot_filters_frame(bottom_frame)

        # district list display
        district_list_frame = tk.Frame(master=bottom_frame, height=15)
        district_list_frame.pack(padx=10, expand=True, fill=tk.Y)

        ttk.Label(master=district_list_frame, text='Selected districts', style=Style.LABEL_BOLD_STYLE).pack(side=tk.TOP)
        self.district_display = tk.Text(master=district_list_frame, width=20, height=10, background='pink',
                                        font=tkFont.Font(family="Times New Roman", size=20))
        self.district_display.pack()

    def setup_top_frame(self, parent_frame):
        phone_input = tk.Entry(parent_frame, fg='green',
                               font="Times 20 bold", borderwidth=4, justify="center")
        phone_input['textvariable'] = self.input_vars.PHONE_INPUT_VAR
        phone_input.bind("<Button-1>", lambda event: self.clear_entry(self.input_vars.PHONE_INPUT_VAR, phone_input))
        phone_input.pack()

        phone_label = ttk.Label(master=parent_frame, style=Style.LABEL_BOLD_STYLE, justify="center",
                                text='Enter registered number')
        phone_label.pack()

        canvas = tk.Canvas(master=parent_frame, width=720,
                           height=3, bg="black")
        canvas.pack(pady=10)

    def setup_slot_filters_frame(self, parent_frame):
        label = tk.Label(master=parent_frame, font="Times 20 bold underline", justify="center", width=20, text='Slot filters')
        label.pack(side=tk.TOP, pady=5)

        slot_params_frame = tk.Frame(master=parent_frame)
        slot_params_frame.pack(side=tk.LEFT, expand=True, fill=tk.Y)

        districts_combo = self.setup_district_selectors(slot_params_frame)
        self.setup_state_selectors(slot_params_frame, districts_combo)
        self.setup_age_selector(slot_params_frame)
        self.setup_vaccine_dose_selectors(slot_params_frame)
        self.setup_date_range_selectors(slot_params_frame)
        self.setup_use_public_api_selector(slot_params_frame)

    def update_district_selector(self, district_combo, state_id):
        districts_dict = self.fetch_districts_callback(state_id)
        self.district_id_map = districts_dict
        district_names = list(districts_dict.keys())
        district_combo.set_values(district_names)

    def district_selector_callback(self, selected_districts):
        print(selected_districts)
        display_text = ''
        for district in selected_districts:
            display_text = display_text+'\u2022'+ district+ '\n' # create bullet list
        self.district_display.delete("1.0", tk.END)
        self.district_display.insert("1.0", display_text, "center")

    def setup_district_selectors(self, frame):
        # district selector
        label = ttk.Label(master=frame, text="District ", style=Style.LABEL_BOLD_STYLE)
        label.grid(row=1, column=0, padx=10, sticky=tk.W)

        districts_combo = Combopicker(master=frame,
                                      select_callback=lambda values: self.district_selector_callback(values),
                                      selected_items_var=self.input_vars.DISTRICT_LIST_INPUT_VAR,
                                      head_value="Select Districts",
                                      font=tkFont.Font(family="Times New Roman", size=20))
        districts_combo.grid(row=1, column=1, rowspan=1, stick=tk.W)

        return districts_combo

    def setup_state_selectors(self,frame, districts_combo):
        # state selector
        label = ttk.Label(master=frame, text="State ", style=Style.LABEL_BOLD_STYLE)
        label.grid(row=0, column=0, padx=10, sticky=tk.W)
        states_list_dict = self.fetch_states_callback()
        self.state_id_map = states_list_dict
        state_names = list(states_list_dict.keys())
        default_state = state_names[0]
        self.input_vars.STATE_INPUT_VAR.set(default_state)
        self.update_district_selector(districts_combo, states_list_dict[default_state])
        states_combo = ttk.Combobox(master=frame, width=20,font =tkFont.Font(family="Times New Roman", size=20), state="readonly", textvariable=self.input_vars.STATE_INPUT_VAR)
        states_combo['values'] = state_names

        states_combo.bind("<<ComboboxSelected>>",lambda event: self.update_district_selector(districts_combo, states_list_dict[states_combo.get()]))
        states_combo.grid(row=0, column=1, stick=tk.W)

    def setup_age_selector(self, frame):
        # min age selector
        label = ttk.Label(master=frame, text="Age group ", style=Style.LABEL_BOLD_STYLE)
        label.grid(row=2, column=0, padx=10, sticky=tk.W)

        rb_frame = tk.Frame(master=frame)
        rb_frame.grid(row=2, column=1, sticky=tk.W)
        tk.Radiobutton(master=rb_frame, text="18+", variable=self.input_vars.MIN_AGE_INPUT_VAR, value='18+',
                       font=tkFont.Font(family="Times New Roman", size=20)).pack(side=tk.LEFT)
        tk.Radiobutton(master=rb_frame, text="45+", variable=self.input_vars.MIN_AGE_INPUT_VAR, value='45+',
                       font=tkFont.Font(family="Times New Roman", size=20)).pack()

    def setup_vaccine_dose_selectors(self, frame):
        # vaccine dose selector
        label = ttk.Label(master=frame, text="Vaccine dose# ", style=Style.LABEL_BOLD_STYLE)
        label.grid(row=3, column=0, padx=10, sticky=tk.W)

        rb_frame = tk.Frame(master=frame)
        rb_frame.grid(row=3, column=1, sticky=tk.W)

        tk.Radiobutton(master=rb_frame, text="Dose 1", variable=self.input_vars.VACCINE_DOSE_INPUT_VAR, value='dose_1',
                       font=tkFont.Font(family="Times New Roman", size=20)).pack(side=tk.LEFT)
        tk.Radiobutton(master=rb_frame, text="Dose 2", variable=self.input_vars.VACCINE_DOSE_INPUT_VAR, value='dose_2',
                       font=tkFont.Font(family="Times New Roman", size=20)).pack()


    def setup_date_range_selectors(self, frame):
        # date range selector
        label = ttk.Label(master=frame, text="Start date", style=Style.LABEL_BOLD_STYLE)
        label.grid(row=4, column=0, padx=10, sticky=tk.W)
        cal1 = DateEntry(master=frame, width=10, background='darkblue',
                        font=tkFont.Font(family="Times New Roman", size=20),
                        foreground='white', borderwidth=2, year=2021)
        cal1.bind("<<DateEntrySelected>>", lambda ev: self.input_vars.START_DATE_INPUT_VAR.set(cal1.get_date()))
        cal1.grid(row=4, column=1, sticky=tk.W)
        cal1.set_date(date=datetime.datetime.today())
        self.input_vars.START_DATE_INPUT_VAR.set(cal1.get_date())

        label = ttk.Label(master=frame, text="End date", style=Style.LABEL_BOLD_STYLE)
        label.grid(row=5, column=0, padx=10, sticky=tk.W)
        cal2 = DateEntry(master=frame, width=10, background='darkblue',
                        font=tkFont.Font(family="Times New Roman", size=20),
                        foreground='white', borderwidth=2, year=2021)
        cal2.bind("<<DateEntrySelected>>", lambda ev: self.input_vars.END_DATE_INPUT_VAR.set(cal2.get_date()))
        cal2.grid(row=5, column=1, sticky=tk.W)
        cal2.set_date(date=datetime.datetime.today())
        self.input_vars.END_DATE_INPUT_VAR.set(cal2.get_date())

    def setup_use_public_api_selector(self, frame):
        # use public api selector
        label = ttk.Label(master=frame, text="Use Public API ", style=Style.LABEL_BOLD_STYLE)
        label.grid(row=6, column=0, padx=10, sticky=tk.W)
        use_public_api = ttk.Checkbutton(master=frame, variable=self.input_vars.USE_PUBLIC_API_VAR,
                                         onvalue=1, offvalue=0,
                                         width=20)
        use_public_api.grid(row=6, column=1, sticky=tk.W)

        label = ttk.Label(master=frame,
                          text="(Slot availability data can be upto 30mins old when usign Public API\n If you don't use Public API, the data will be real time, however this will require re-authentication every 15mins)",
                          font=tkFont.Font(family="Times New Roman", size=15, slant='italic'), wraplength=600)
        label.grid(row=7, column=0, padx=10, columnspan=2, sticky=tk.W)