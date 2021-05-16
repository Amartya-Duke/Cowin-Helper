USE_PUBLIC_API = False
PHONE_NUMBER = '***'
BROWSER_PATH = '"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" %s'  # it will be used to open a browser tab pointing to cowin for registration, if slots becomes available

SLOT_CONFIG = {
    'min_age': 18,
    'weeks': 6,
    'dose_no': 1,
    'state': "West Bengal",
    'districts': ['Hoogly', 'Howrah', 'Kolkata']  # should be ordered in choice of preference
}

TWILIO_ACCOUNT_SID = "***"
TWILIO_AUTH_TOKEN = "***"
TWILIO_SENDER_NUMBER = "***"

SECRET = "***"
