# Cowin-Helper
This tool has been built using Co-WIN APIs  published 
<a href="https://apisetu.gov.in/public/marketplace/api/cowin">here</a>

Cowin exposes 2 types of APIs for checking slot availability - <i>Public</i> and <i>Protected</i>.

<i>Public APIs</i> does not require any authentication and the data is not real-time.
The official documentation quotes - "The appointment availability data is cached and may be upto 30 minutes old" 

To use the <i>Protected API</i>, user must be authenticated using OTP. The Auth token expires every 15mins or so hence a re-auth using OTP is required every time a request fails with status 401 (Unauthorized access). 

This tool lets you: 
- Configure slot check parameters.
- Authenticate using OTP
- Check for available slots (by district). The flag USE_PUBLIC_API at config.py acts as switch for using Public or Protected API.
- Periodically check for slots-availability and notify via SMS once slot becomes available
- Auto-book slot. Booking slot requires captcha to be filled which requires a manual intervention, hence it cannot be automated.
However, this tool will open up a browser tab landing at Cowin portal immediately once slots become available. 
### Note
-  SMS functionality is provided by Twilio ( https://www.twilio.com/ )
-  To use this feature, create a trial account at Twilio and set the following params in config.py: 
    
    TWILIO_ACCOUNT_SID
    
    TWILIO_AUTH_TOKEN
    
    TWILIO_SENDER_NUMBER
