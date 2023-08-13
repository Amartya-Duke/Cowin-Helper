import datetime
import hashlib
import time
import webbrowser
import math

import requests
from twilio.rest import Client

from CowinHelper.api_list import APIList
from CowinHelper.config import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, SECRET, \
    BROWSER_PATH, TWILIO_SENDER_NUMBER


MIN_SLOT_AVAILABILITY = 2
class Slot:
    def __init__(self, session_id, center_id, date, center_name, district_id, vaccine_type, time_slots, slots_available):
        self.session_id = session_id
        self.center_id = center_id
        self.date = date
        self.center_name = center_name
        self.district_id = district_id
        self.vaccine_type = vaccine_type
        self.time_slots = time_slots
        self.slots_available = slots_available

    def __str__(self):
        return "{center_name},{district}, slots available({slots}),{vaccine} on {date}".format(date=self.date,
                                                                                               center_name=self.center_name,
                                                                                               district=self.district_id,
                                                                                               slots=self.slots_available,
                                                                                               vaccine=self.vaccine_type)


class GUI_CALLBACK_TYPES:
    TYPE_READ_OTP = 'otp'
    TYPE_BOOK_SLOT = 'book_slot'


class CowinHelper:
    WAITING_FOR_GUI_CALLBACK = False
    MAX_RETRY_TO_REAUTH = 3

    default_headers = {'Content-type': 'application/json',
                       "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
                       # 'origin': "https://selfregistration.cowin.gov.in",
                       # "referer": "https://selfregistration.cowin.gov.in/",
                       "Accept-Language": "en-US,en;q=0.5",
                       "Cache-Control": "no-cache",
                       "Host": "cdn-api.co-vin.in",
                       "Pragma": "no-cache",
                        "TE": "Trailers",
                       "Accept": "application/json",
                       # "x-api-key": X_API_KEY
                       }

    def __init__(self, phone, state_id, districts, min_age_limit, vaccine_dose_no, start_date, end_date,use_public_api, gui_callback_map):

        self.mobile_number = phone
        self.state_id = state_id
        self.districts = districts
        self.min_age_limit = min_age_limit
        self.vaccine_dose_no = vaccine_dose_no
        self.start_date = start_date
        self.end_date = end_date
        self.use_public_api = use_public_api
        self.gui_callback_map = gui_callback_map

        self.available_slots = []
        self.session = None
        self.district_id_map = dict()
        self.last_notification_sent_time = None
        self.slot_booked = False
        self.beneficiary_map = dict()

    @staticmethod
    def get_all_states():
        request_type, api_path = APIList.LIST_STATES
        response = requests.request(request_type, api_path, headers=CowinHelper.default_headers)
        if response.status_code == 200:
            states_list = response.json()['states']
            states_list_dict = dict()
            for state in states_list:
                states_list_dict[state['state_name']] = state['state_id']
            return states_list_dict
        else:
            print(response.content)
            print('Failed fetching state list')

    @staticmethod
    def get_all_districts(state_id):
        request_type, api_path = APIList.LIST_DISTRICTS
        api_path = api_path.format(state_id=str(state_id))
        response = requests.request(request_type, api_path,  headers=CowinHelper.default_headers)
        if response.status_code == 200:
            districts_list = response.json()['districts']
            district_list_dict = dict()
            for district in districts_list:
                district_list_dict[district['district_name']] = district['district_id']
            return district_list_dict
        else:
            print(response.content)
            print("Failed fetching district list")


    def make_request(self, request_type, api_path, payload=None, params=None):
        if not self.session:
            self.session = requests.Session()
            self.session.headers.update(CowinHelper.default_headers)
        response = self.session.request(request_type, api_path, json=payload, params=params if params else {})
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 401:
            print(api_path)
            print(response.content)
            print("Authentication required")
            self.session.close()
            success, auth_token = self.authenticate()
            if not success:
                raise Exception(
                    "Re-Authentication limit reached. OTP not received or invlid OTP entered for {} consecutive resend".format(
                        CowinHelper.MAX_RETRY_TO_REAUTH))
            self.session = requests.Session()
            self.session.headers.update(CowinHelper.default_headers)
            self.session.headers.update({'Authorization': 'Bearer ' + auth_token})
            return self.make_request(request_type, api_path, payload, params)
        elif response.status_code == 409:
            print(response.content)
        else:
            print(response.content)
            raise Exception("Request failed with status {}".format(response.status_code))

    def authenticate(self, retry=0, invalid_otp_flag=False):

        if retry == CowinHelper.MAX_RETRY_TO_REAUTH:
            print("Re-Authentication retry limit reached. Exiting..")
            return False, None
        request_type, api_path = APIList.GENERATE_OTP
        response = self.make_request(request_type, api_path, payload={'mobile': self.mobile_number})
        # response = self.make_request(request_type, api_path, payload={'mobile': self.mobile_number})

        txn_id = response['txnId']
        print("Otp sent to {}".format(self.mobile_number))

        otp = self.gui_callback_map[GUI_CALLBACK_TYPES.TYPE_READ_OTP](invalid_otp_flag=invalid_otp_flag)

        # if AUTO_READ_OTP:
        #     otp = check_otp(self.mobile_number, timeout=180)
        # else:
        #     otp = input("Enter OTP: ")
        if not otp:
            return self.authenticate(retry=retry + 1)

        print("Got OTP :{}".format(otp))
        otp_hash = hashlib.sha256(otp.encode()).hexdigest()

        request_type, api_path = APIList.VALIDATE_OTP
        try:
            print("Validating OTP")
            response = self.make_request(request_type, api_path, payload={
                'txnId': txn_id,
                'otp': otp_hash
            })
        except Exception as e:  # most common reason of failure - Incorrect OTP
            print(e)
            return self.authenticate(retry=retry + 1, invalid_otp_flag=True)
        response = {'token': 'ddd'}
        token = response['token']
        print(token)
        print("Authenticated")
        return True, token

    def fetch_beneficiaries(self):
        if self.use_public_api:
            print("Beneficiaries cannot be fetched without Authentication. USE_PUBLIC_API is set to True")
            return
        request_type, api_path = APIList.LIST_BENEFICIARIES
        response = self.make_request(request_type, api_path)
        print(response)
        beneficiaries = response['beneficiaries']
        for benificiary in beneficiaries:
            self.beneficiary_map[benificiary['beneficiary_reference_id']] = benificiary['name']

    def search_available_slots(self):
        available_session_list = []
        if self.end_date == self.start_date:
            weeks_count = 1
        else:
            weeks_count = int(math.ceil((self.end_date-self.start_date).days/7))
            weeks_count = weeks_count or 1
        start_date = self.start_date
        for i in range(weeks_count):
            for district_id in self.districts:
                query_params = {'district_id': district_id, 'date': datetime.datetime.strftime(start_date, '%d-%m-%Y')}
                request_type, api_path = APIList.SESSIONS_BY_DISTRICT_PUBLIC if self.use_public_api else APIList.SESSIONS_BY_DISTRICT
                response = self.make_request(request_type, api_path, params=query_params)
                centers = response['centers']
                for center in centers:
                    center_id = center['center_id']
                    center_name = center['name']
                    for session in center['sessions']:  # spanning across multiple dates
                        date = session['date']
                        if datetime.datetime.strptime(date, '%d-%m-%Y').date() > self.end_date:
                            continue

                        if session['min_age_limit'] > self.min_age_limit or session[
                            'available_capacity_dose{dose_no}'.format(dose_no=self.vaccine_dose_no)] < MIN_SLOT_AVAILABILITY:
                            continue
                        vaccine = session['vaccine']
                        session_id = session['session_id']
                        time_slots = session['slots']
                        slot = Slot(session_id, center_id, date, center_name, district_id,
                                    vaccine, time_slots,
                                    session['available_capacity_dose{}'.format(self.vaccine_dose_no)])
                        available_session_list.append(slot)
                        print("Available Slot: {}".format(session))
            start_date = start_date + datetime.timedelta(days=i+1 * 7)
        self.available_slots = available_session_list

    def notify(self):
        if not self.available_slots:
            return
        account_sid = TWILIO_ACCOUNT_SID
        auth_token = TWILIO_AUTH_TOKEN
        client = Client(account_sid, auth_token)

        body = "Sessions available: {total} \n".format(total=len(self.available_slots))
        for index, session in enumerate(self.available_slots):
            if index <= 5:
                body += str(session)
                body += '\n'

        if not self.last_notification_sent_time or abs((
                                                               self.last_notification_sent_time - datetime.datetime.now()).total_seconds()) / 60 > 0.5:  # send another message only after an hour
            message = client.messages \
               .create(
               body=body,
               from_=TWILIO_SENDER_NUMBER,
               to="+91" + str(self.mobile_number)
            )
            print(message.sid)
            self.last_notification_sent_time = datetime.datetime.now()
        else:
            print("Not sending SMS. Time between prev SMS and now: {}mins".format(
                abs((self.last_notification_sent_time - datetime.datetime.now()).total_seconds()) / 60))

    def book(self, slot, beneficiaries, selected_slot, captcha, err_callback):
        request_type, api_path = APIList.SCHEDULE_ANOINTMENT
        payload = dict(center_id=slot.center_id, session_id=slot.session_id,beneficiaries=beneficiaries,
                       slot=selected_slot, dose=self.vaccine_dose_no, captcha=captcha)
        print(payload)

        try:
            self.make_request(request_type, api_path, payload=payload)
        except Exception as e:
            err_callback(error=e)

    def refresh_captcha(self):
        request_type, api_path = APIList.GET_CAPTCHA
        captcha_svg_content = self.make_request(request_type, api_path)
        return captcha_svg_content

    def book_slot(self):
        if not self.available_slots:
            return
        found = False
        request_type, api_path = APIList.SCHEDULE_ANOINTMENT
        for district in self.districts:  # searching in order of district preference
            available_slots = list(filter(lambda slot: slot.district, self.available_slots))
            if available_slots:
                for slot in available_slots:
                    time_slots = slot.time_slots
                    for time_slot in time_slots:
                        payload = {'center_id': slot.center_id, 'session_id': slot.session_id,
                                  'beneficiaries': self.beneficiary_map.keys(), 'slot': time_slot, 'dose': self.vaccine_dose_no}
                        print(payload)
                        request_type, api_path = APIList.GET_CAPTCHA
                        captcha_svg_content = self.make_request(request_type, api_path)
                        #show_gui(captcha_svg_content['captcha'], lambda captcha: self.captcha_input_callback(captcha, payload))
                        self.gui_callback_map[GUI_CALLBACK_TYPES.TYPE_BOOK_SLOT](captcha_svg_content['captcha'], payload)
                        break
                    break
                break




        print("Opening browser...")
        tab_to_open = "https://selfregistration.cowin.gov.in/dashboard"
        webbrowser.get(BROWSER_PATH).open(tab_to_open)

    def run_periodically(self, interval_in_mins, ):
        run_count = 1
        self.fetch_beneficiaries()
        while not self.slot_booked:
            if not CowinHelper.WAITING_FOR_GUI_CALLBACK:
                self.available_slots = []
                print("{} Run count: {}".format(datetime.datetime.now().strftime("%H:%M:%S"), run_count))
                self.search_available_slots()
                if self.available_slots:
                    try:
                        self.notify()
                    except Exception as e:
                        print(e)
                    # self.book_slot()
                    # CowinHelper.WAITING_FOR_GUI_CALLBACK = True
                    self.gui_callback_map[GUI_CALLBACK_TYPES.TYPE_BOOK_SLOT](self.available_slots)
                    print("Opening browser...")
                    tab_to_open = "https://selfregistration.cowin.gov.in/dashboard"
                    webbrowser.get(BROWSER_PATH).open(tab_to_open)
                run_count += 1
            else:
                print("Waiting for GUI_CALLBACK")
            time.sleep(interval_in_mins * 60)
        else:
            print("Exiting ...")
