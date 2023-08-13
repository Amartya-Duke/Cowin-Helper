class APIList:
    BASE_API_PATH = 'https://cdn-api.co-vin.in/api'
    GENERATE_OTP = ('post', BASE_API_PATH + '/v2/auth/generateMobileOTP')
    # GENERATE_OTP = ('post', BASE_API_PATH + '/v2/auth/generateOTP')
    VALIDATE_OTP = ('post', BASE_API_PATH + '/v2/auth/confirmOtp')
    LIST_BENEFICIARIES = ('get', BASE_API_PATH + '/v4/appointment/beneficiaries')
    LIST_STATES = ('get', BASE_API_PATH + '/v2/admin/location/states')
    LIST_DISTRICTS = ('get', BASE_API_PATH + '/v2/admin/location/districts/{state_id}')
    SESSIONS_BY_DISTRICT = ('get', BASE_API_PATH + '/v2/appointment/sessions/calendarByDistrict')
    SESSIONS_BY_DISTRICT_PUBLIC = ('get', BASE_API_PATH + '/v2/appointment/sessions/public/calendarByDistrict')
    SCHEDULE_ANOINTMENT = ('post', BASE_API_PATH + '/v2/appointment/schedule')
    GET_CAPTCHA = ('post', BASE_API_PATH+'/v2/auth/getRecaptcha')
