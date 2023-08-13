import requests
import re
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF, renderPM

from CowinHelper.api_list import APIList

captch_utl = APIList.GET_CAPTCHA


def refresh_captcha(headers):
    captcha_content = requests.post(captch_utl, headers=headers)

    with open('captcha.svg', 'w') as f:
        f.write(re.sub('(<path d=)(.*?)(fill=\"none\"/>)', '', captcha_content.json()['captcha']))

    drawing = svg2rlg('captcha.svg')
    renderPM.drawToFile(drawing, "captcha.png", fmt="PNG")
