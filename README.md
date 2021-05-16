# Cowin-Helper
This tool has been built using Co-WIN APIs  published 
<a href="https://apisetu.gov.in/public/marketplace/api/cowin">here</a>

Key features: 
- Authenticate using OTP
- Check for available slots (by district)
- Periodically check for slots-availability and notify via SMS once slot becomes available
- Auto-book slot. Booking slot requires captcha to be filled which requires a manual intervention, hence it cannot be automated.
However, this tool will open up a browser tab landing at Cowin portal immediately once slots become available. 
### Note
-  SMS functionality is provided by Twilio ( https://www.twilio.com/ )
