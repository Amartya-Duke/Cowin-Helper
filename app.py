import datetime
import hashlib
import time
import webbrowser

import requests
from twilio.rest import Client

from CowinHelper.config import APIList, PHONE_NUMBER, SLOT_CONFIG, TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, SECRET, \
    BROWSER_PATH


class Slot:
    def __init__(self, session_id, center_id, date, center_name, district, vaccine_type, time_slots, slots_available):
        self.session_id = session_id
        self.center_id = center_id
        self.date = date
        self.center_name = center_name
        self.district = district
        self.vaccine_type = vaccine_type
        self.time_slots = time_slots
        self.slots_available = slots_available

    def __str__(self):
        return "{center_name},{district}, slots available({slots}),{vaccine} on {date}".format(date=self.date,
                                                                                               center_name=self.center_name,
                                                                                               district=self.district,
                                                                                               slots=self.slots_available,
                                                                                               vaccine=self.vaccine_type)


class CowinHelper:
    default_headers = {'Content-type': 'application/json',
                       "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
                       'origin': "https://selfregistration.cowin.gov.in",
                       "referer": "https://selfregistration.cowin.gov.in/"}

    def __init__(self, mobile_number):
        self.mobile_number = mobile_number
        self.available_slots = []
        self.session = None
        self.district_id_map = dict()
        self.last_notification_sent_time = None
        self.slot_booked = False
        self.beneficiaries = []

    def make_request(self, request_type, api_path, payload=None, params=None):
        if not self.session:
            self.session = requests.Session()
            self.session.headers.update(CowinHelper.default_headers)

        response = self.session.request(request_type, api_path, json=payload, params=params if params else {})
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 401:
            print("Authentication required")
            self.session.close()
            auth_token = self.authenticate()
            self.session = requests.Session()
            self.session.headers.update(CowinHelper.default_headers)
            self.session.headers.update({'Authorization': 'Bearer ' + auth_token})
            return self.make_request(request_type, api_path, payload, params)
        else:
            print(response.content)
            raise Exception("Request failed with status {}".format(response.status_code))

    def authenticate(self):
        request_type, api_path = APIList.GENERATE_OTP
        response = self.make_request(request_type, api_path, payload={'mobile': self.mobile_number, "secret": SECRET})

        txn_id = response['txnId']
        print("Otp sent to {}".format(self.mobile_number))
        otp = input("Enter OTP: ")
        otp_hash = hashlib.sha256(otp.encode()).hexdigest()

        request_type, api_path = APIList.VALIDATE_OTP
        response = self.make_request(request_type, api_path, payload={
            'txnId': txn_id,
            'otp': otp_hash
        })

        token = response['token']
        print(token)
        print("Authenticated")
        return token

    def fetch_beneficiaries(self):
        request_type, api_path = APIList.LIST_BENEFICIARIES
        response = self.make_request(request_type, api_path)
        print(response)
        beneficiaries = response['beneficiaries']
        benificiary_ids = [benificiary['beneficiary_reference_id'] for benificiary in beneficiaries]
        self.beneficiaries = benificiary_ids

    def get_state_id(self, state_name):
        request_type, api_path = APIList.LIST_STATES
        response = self.make_request(request_type, api_path)
        states_list = response['states']
        myState = list(filter(lambda state: state['state_name'] == state_name, states_list))[0]
        return myState['state_id']

    def get_district_id(self, state_id, district_name):
        request_type, api_path = APIList.LIST_DISTRICTS
        api_path = api_path.format(state_id=str(state_id))
        response = self.make_request(request_type, api_path)
        district_list = response['districts']
        myDistrict = list(filter(lambda districts: districts['district_name'] == district_name, district_list))[0]
        self.district_id_map[myDistrict['district_id']] = district_name
        return myDistrict['district_id']

    def search_available_slots(self, state, districts, min_age_limit, dose=1, weeks=4):
        state_id = self.get_state_id(state)
        district_ids = list(map(lambda district_name: self.get_district_id(state_id, district_name), districts))
        available_session_list = []
        for i in range(weeks):
            start_date = datetime.datetime.now() + datetime.timedelta(days=i * 7)
            for district_id in district_ids:
                query_params = {'district_id': district_id, 'date': datetime.datetime.strftime(start_date, '%d-%m-%Y')}
                request_type, api_path = APIList.SESSIONS_BY_DISTRICT
                response = self.make_request(request_type, api_path, params=query_params)
                centers = response['centers']
                for center in centers:
                    center_id = center['center_id']
                    center_name = center['name']
                    for session in center['sessions']:  # spanning across multiple dates
                        if session['available_capacity_dose{dose_no}'.format(dose_no=dose)] == 0:
                            continue
                        vaccine = session['vaccine']
                        date = session['date']
                        session_id = session['session_id']
                        time_slots = session['slots']
                        slot = Slot(session_id, center_id, date, center_name, self.district_id_map[district_id],
                                    vaccine, time_slots,
                                    session['available_capacity_dose{}'.format(dose)])
                        available_session_list.append(slot)
                        print("Available Slot: {}".format(str(slot)))
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
                from_='+12105987550',
                to="+91" + str(PHONE_NUMBER)
            )
            print(message.sid)
            self.last_notification_sent_time = datetime.datetime.now()
        else:
            print("Not sending SMS. Time between prev SMS and now: {}mins".format(
                abs((self.last_notification_sent_time - datetime.datetime.now()).total_seconds()) / 60))

    def book_slot(self):
        if not self.available_slots:
            return
        # request_type, api_path = APIList.SCHEDULE_ANOINTMENT
        # for district in SLOT_CONFIG['districts']:  # searching in order of district preference
        #    available_slots = list(filter(lambda slot: slot.district, self.available_slots))
        #    if available_slots:
        #       for slot in available_slots:
        #            time_slots = slot.time_slots
        #            for time_slot in time_slots:
        #                payload = {'center_id': slot.center_id, 'session_id': slot.session_id,
        #                           'beneficiaries': self.beneficiaries, 'slot': time_slot, 'dose': SLOT_CONFIG['dose']}
        #                print(payload)
        #                try:
        #                    payload['captcha'] = 'kfmxg'
        #                    self.make_request(request_type, api_path, payload=payload)
        #                except:
        #                    print("Failed booking slot")
        #                    return
        #                print("Slot booked at {} | {}".format(str(slot), time_slot))
        #                self.slot_booked = True
        #                break
        #            if self.slot_booked:
        #                break
        #    if self.slot_booked:
        #        break
        print("Opening browser...")
        tab_to_open = "https://selfregistration.cowin.gov.in/dashboard"
        webbrowser.get(BROWSER_PATH).open(tab_to_open)

    def run_periodically(self, interval_in_mins):
        run_count = 1
        self.fetch_beneficiaries()
        while not self.slot_booked:
            self.available_slots = []
            print("Run count: {}".format(run_count))
            self.search_available_slots(state=SLOT_CONFIG['state'], districts=SLOT_CONFIG['districts'],
                                        min_age_limit=SLOT_CONFIG['min_age'], dose=SLOT_CONFIG['dose'],
                                        weeks=SLOT_CONFIG['weeks'])
            if self.available_slots:
                self.notify()
                self.book_slot()

            run_count += 1
            time.sleep(interval_in_mins * 60)
        else:
            print("Exiting ...")

if __name__ == '__main__':
    helper = CowinHelper(PHONE_NUMBER)
    # .authenticate()
    #helper.list_beneficiaries()
    # sessions = helper.search_available_slots(state=SLOT_CONFIG['state'], districts=SLOT_CONFIG['districts'], min_age_limit=45, weeks=6)
    # helper.notify()
    # helper.book_slot()

    helper.run_periodically(interval_in_mins=1)
