import tkinter as tk
import datetime
from CowinHelper.app import CowinHelper
from CowinHelper.app import GUI_CALLBACK_TYPES
import threading
import time

from CowinHelper.gui.landing_page import LandingPage
from CowinHelper.gui.scan_page import ScanPage
from CowinHelper.otp_utils.read_otp import check_otp
from CowinHelper.config import AUTO_READ_OTP
class CowinGui:
    def __init__(self, master):
        self.master = master
        self.captcha_var = tk.StringVar()
        self.landing_page = LandingPage(master=self.master, fetch_states_callback=lambda: CowinHelper.get_all_states(), fetch_districts_callback=lambda state_id: CowinHelper.get_all_districts(state_id))
        self.landing_page.setup_widgets(bt_callback=lambda params: self.submit_btn_callback(params))

    def display_available_slots(self, available_slots):
        print("Called")
        self.scan_page.setup_slots_available_display(available_slots)

    def read_otp(self, invalid_otp_flag):
        print("Called for read OTP")

        if AUTO_READ_OTP:
            otp = check_otp('9629778910', timeout=180)
        else:
            otp=input("Enter OTP:")

        return otp

    def get_gui_callbacks(self):
        return {
            GUI_CALLBACK_TYPES.TYPE_READ_OTP: lambda invalid_otp_flag: self.read_otp(invalid_otp_flag),
            GUI_CALLBACK_TYPES.TYPE_BOOK_SLOT: lambda slots: self.display_available_slots(slots)
        }

    def start_scan(self):
        threading.Thread(target=self.cowin_helper.run_periodically, args=(1,)).start()
        #self.cowin_helper.run_periodically(1).start()
    def submit_btn_callback(self, user_input):
        print("User input: {}".format(user_input))
        phone = user_input['phone']
        state = user_input['state']
        start_id, state_name = state
        districts = user_input['districts']
        age_group = user_input['age_group']
        vaccine_dose_no = user_input['vaccine_dose_no']
        start_date = datetime.datetime.strptime(user_input['start_date'], '%Y-%m-%d').date()
        end_date = datetime.datetime.strptime(user_input['end_date'], '%Y-%m-%d').date()
        use_public_api = user_input['use_public_api']

        min_age_limit = int(age_group.split('+')[0])
        vaccine_dose_no = vaccine_dose_no.split("_")[1]

        gui_callback_map = self.get_gui_callbacks()

        self.cowin_helper = CowinHelper(phone=phone, state_id=state, districts=[district_id for district_id, name in districts],
                                   min_age_limit=min_age_limit, vaccine_dose_no=vaccine_dose_no,
                                   start_date=start_date, end_date=end_date,use_public_api=use_public_api,
                                   gui_callback_map=gui_callback_map)
        #cowin_helper.run_periodically(interval_in_mins=1, gui_callback=self.book_slot_callback)
        #threading.Thread(target=cowin_helper.run_periodically, args=(1, lambda captcha_svg_content, payload: self.setup_widgets(captcha_svg_content, payload))).start()

        self.scan_page = ScanPage(self.master, state_id_name=state, districts=districts,cowin_helper=self.cowin_helper, start_scan_callback=self.start_scan,
                                  refresh_captcha_callback=self.cowin_helper.refresh_captcha,
                                  book_slot_callback = lambda slot, beneficiaries, selected_slot, captcha, err_callback : self.cowin_helper.book(slot, beneficiaries, selected_slot, captcha, err_callback))
        self.scan_page.setup_widgets()


if __name__ == '__main__':
    root = tk.Tk()

    app = CowinGui(master=root)

    root.title("Cowin Helper")
    root.geometry("1024x720")
    tk.mainloop()
