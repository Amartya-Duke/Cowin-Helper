USE_PUBLIC_API = False
PHONE_NUMBER = '***'
BROWSER_PATH = '"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" %s'  # it will be used to open a browser tab pointing to cowin for registration, if slots becomes available

AUTO_READ_OTP = True  # requires OTP server is running and the server is notified once OTP arrives at phone
OTP_UTILS = {
    "SERVER_HOST": "",
    "SERVER_PORT": 9002,
    "OTP_STORE_PATH": "C:\\Users\\Amartya\\OneDrive\\Desktop\\CoWINOtp.txt"
}

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
