class APIList:
    BASE_API_PATH = 'https://cdn-api.co-vin.in/api'
    GENERATE_OTP = ('post', BASE_API_PATH + '/v2/auth/generateMobileOTP')
    VALIDATE_OTP = ('post', BASE_API_PATH + '/v2/auth/validateMobileOtp')
    LIST_BENEFICIARIES = ('get', BASE_API_PATH + '/v2/appointment/beneficiaries')
    LIST_STATES = ('get', BASE_API_PATH + '/v2/admin/location/states')
    LIST_DISTRICTS = ('get', BASE_API_PATH + '/v2/admin/location/districts/{state_id}')
    SESSIONS_BY_DISTRICT = ('get', BASE_API_PATH + '/v2/appointment/sessions/calendarByDistrict')
    SCHEDULE_ANOINTMENT = ('post', BASE_API_PATH + '/v2/appointment/schedule')


PHONE_NUMBER = '***'

SLOT_CONFIG = {
    'state': "West Bengal",
    'districts': ['Hoogly', 'Howrah', 'Kolkata']
}

TWILIO_ACCOUNT_SID = "***"
TWILIO_AUTH_TOKEN = "***"

SECRET = "***"
