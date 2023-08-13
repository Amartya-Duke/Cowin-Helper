# Cowin-Helper
This tool has been built using Co-WIN APIs  published 
<a href="https://apisetu.gov.in/public/marketplace/api/cowin">here</a>

Cowin exposes 2 types of APIs for checking slot availability - <i>Public</i> and <i>Protected</i>.

<i>Public APIs</i> does not require any authentication and the data is not real-time.
The official documentation quotes - "The appointment availability data is cached and may be upto 30 minutes old" 

To use the <i>Protected API</i>, user must be authenticated using OTP. The Auth token expires every 15mins or so hence a re-auth using OTP is required every time a request fails with status 401 (Unauthorized access). 

This tool lets you: 
- Configure slot check parameters.
- Authenticate using OTP and Auto read OTP.
- Check for available slots (by district). The flag USE_PUBLIC_API at config.py acts as switch for using Public or Protected API.
- Periodically check for slots-availability and notify via SMS once slot becomes available. <i>(Using Protected API requires re-auth every 15mins)</i>
- Auto-book slot. Booking slot requires captcha to be filled which requires a manual intervention, hence it cannot be automated.
However, this tool will open up a browser tab landing at Cowin portal immediately once slots become available. 

To use the auto read OTP feature:
 - set the flag AUTO_READ_OTP to True in config.py
 - give a file path where OTP will ge stored in OTP_UTILS in config.py
 - start the OTP server (otp_utils/otp_server.py)
 - setup the Shortcuts app (on iphone) or IFTTT app (on android) to make a POST api call to OTP server once OTP arrives at phone
    - payload should be as follows:
    {
        "otp": "OTP message from CoWin"
    }

### Note
-  SMS functionality is provided by Twilio ( https://www.twilio.com/ )
-  To use this feature, create a trial account at Twilio and set the following params in config.py: 
    
    TWILIO_ACCOUNT_SID
    
    TWILIO_AUTH_TOKEN
    
    TWILIO_SENDER_NUMBER




https://github.com/amartya-s/Cowin-Helper/assets/13063884/4b4ad60b-73f4-4aae-9057-bd4a4025d25c

