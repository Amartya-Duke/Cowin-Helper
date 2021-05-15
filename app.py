import datetime
import hashlib
import time

import requests
from twilio.rest import Client

from CowinHelper.config import APIList, PHONE_NUMBER, SLOT_CONFIG, TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, SECRET


class Session:
    def __init__(self, session_id, date, center_name, district, vaccine_type, slots_available):
        self.session_id = session_id
        self.date = date
        self.center_name = center_name
        self.district = district
        self.vaccine_type = vaccine_type
        self.slots_available = slots_available

    def __str__(self):
        return "{center_name},{district}, slots available({slots}),{vaccine} on {date}".format(date=self.date,
                                                                                               center_name=self.center_name,
                                                                                               district=self.district,
                                                                                               slots=self.slots_available,
                                                                                               vaccine=self.vaccine_type)


class CowinHelper:
    def __init__(self, mobile_number):
        self.mobile_number = mobile_number
        self.available_sessions = []
        self.token = ""
        self.headers = {'Content-type': 'application/json',
                        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
                        'origin': "https://selfregistration.cowin.gov.in",
                        "referer": "https://selfregistration.cowin.gov.in/"}

    def make_request(self, request_type, api_path, payload=None, params={}):
        response = requests.request(request_type, api_path, json=payload,
                                    headers=self.headers, params=params)

        if response.status_code != 200:
            raise Exception("Request failed with status {}".format(response.status_code))

        return response.json()

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

        self.token = response['token']
        self.headers['Authorization'] = 'Bearer ' + self.token
        print(self.token)
        print("Authenticated")

    def list_beneficiaries(self):
        if not self.token:
            print("Authentication required. Retrying authentication")
            retries = 5
            while retries:
                try:
                    self.authenticate()
                    break
                except:
                    time.sleep(20)
                    retries -= 1
            else:
                print("Unable to authenticate")
                return
        request_type, api_path = APIList.LIST_BENEFICIARIES
        response = self.make_request(request_type, api_path)
        print(response)
        print(response.json())

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
                    center_name = center['name']
                    for session in center['sessions']:
                        if session['available_capacity_dose{}'.format(dose)] == 0:
                            continue
                        vaccine = session['vaccine']
                        date = session['date']
                        session_id = session['session_id']
                        available_session_list.append(Session(session_id, date, center_name, district_id, vaccine,
                                                              session['available_capacity_dose{}'.format(dose)]))
        self.available_sessions = available_session_list

    def notify(self):
        if not self.available_sessions:
            return False
        print("Sessions available:")
        account_sid = TWILIO_ACCOUNT_SID
        auth_token = TWILIO_AUTH_TOKEN
        client = Client(account_sid, auth_token)

        body = "Sessions available: {total} \n".format(total=len(self.available_sessions))
        for session in self.available_sessions:
            print(str(session))
            body += str(session)
            body += '\n'

        message = client.messages \
            .create(
            body=body,
            from_='+12105987550',
            to="+91" + str(PHONE_NUMBER)
        )

        print(message.sid)
        return True

    def book_slot(self, session):
        if not self.available_sessions:
            return

    def run_periodically(self, interval_in_mins):
        run_count = 1
        while True:
            print("Run count: {}".format(run_count))
            self.search_available_slots(state=SLOT_CONFIG['state'], districts=SLOT_CONFIG['districts'],
                                        min_age_limit=SLOT_CONFIG['min_age'], dose=SLOT_CONFIG['dose'],
                                        weeks=SLOT_CONFIG['weeks'])
            is_notified = self.notify()
            if is_notified:
                break
            run_count += 1
            time.sleep(interval_in_mins * 60)


if __name__ == '__main__':
    helper = CowinHelper(PHONE_NUMBER)
    helper.authenticate()
    # helper.list_beneficiaries()
    # sessions = helper.search_available_slots(state=SLOT_CONFIG['state'], districts=SLOT_CONFIG['districts'], min_age_limit=45, weeks=6)
    # helper.notify()
    # helper.book_slot()

    helper.run_periodically(interval_in_mins=0.1)
