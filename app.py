from flask import Flask, request, jsonify
import requests
import json
import base64
import struct
import tempfile
import os
import sys
import importlib.util
from datetime import datetime
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import urllib3
import logging

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logging.getLogger('werkzeug').disabled = True
logging.getLogger('flask').disabled = True

app = Flask(__name__)

OAUTH_URL = "https://100067.connect.garena.com/oauth/guest/token/grant"
MAJOR_LOGIN_URL = "https://loginbp.ggblueshark.com/MajorLogin"

CLIENT_ID = "100067"
CLIENT_SECRET = "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3"

PROTO_KEY = b'Yg&tc%DEuh6%Zc^8'
PROTO_IV = b'6oyZDr22E3ychjM%'

BASE_HEADERS = {
    'User-Agent': "Dalvik/2.1.0 (Linux; U; Android 11; ASUS_Z01QD Build/PI)",
    'Connection': "Keep-Alive",
    'Accept-Encoding': "gzip",
    'Content-Type': "application/x-www-form-urlencoded",
    'Expect': "100-continue",
    'X-Unity-Version': "2018.4.11f1",
    'X-GA': "v1 1",
    'ReleaseVersion': "OB53"
}

MAJOR_LOGIN_REQ_B64 = "ChNNYWpvckxvZ2luUmVxLnByb3RvIvoKCgpNYWpvckxvZ2luEhIKCmV2ZW50X3RpbWUYAyABKAkSEQoJZ2FtZV9uYW1lGAQgASgJEhMKC3BsYXRmb3JtX2lkGAUgASgFEhYKDmNsaWVudF92ZXJzaW9uGAcgASgJEhcKD3N5c3RlbV9zb2Z0d2FyZRgIIAEoCRIXCg9zeXN0ZW1faGFyZHdhcmUYCSABKAkSGAoQdGVsZWNvbV9vcGVyYXRvchgKIAEoCRIUCgxuZXR3b3JrX3R5cGUYCyABKAkSFAoMc2NyZWVuX3dpZHRoGAwgASgNEhUKDXNjcmVlbl9oZWlnaHQYDSABKA0SEgoKc2NyZWVuX2RwaRgOIAEoCRIZChFwcm9jZXNzb3JfZGV0YWlscxgPIAEoCRIOCgZtZW1vcnkYECABKA0SFAoMZ3B1X3JlbmRlcmVyGBEgASgJEhMKC2dwdV92ZXJzaW9uGBIgASgJEhgKEHVuaXF1ZV9kZXZpY2VfaWQYEyABKAkSEQoJY2xpZW50X2lwGBQgASgJEhAKCGxhbmd1YWdlGBUgASgJEg8KB29wZW5faWQYFiABKAkSFAoMb3Blbl9pZF90eXBlGBcgASgJEhMKC2RldmljZV90eXBlGBggASgJEicKEG1lbW9yeV9hdmFpbGFibGUYGSABKAsyDS5HYW1lU2VjdXJpdHkSFAoMYWNjZXNzX3Rva2VuGB0gASgJEhcKD3BsYXRmb3JtX3Nka19pZBgeIAEoBRIaChJuZXR3b3JrX29wZXJhdG9yX2EYKSABKAkSFgoObmV0d29ya190eXBlX2EYKiABKAkSHAoUY2xpZW50X3VzaW5nX3ZlcnNpb24YOSABKAkSHgoWZXh0ZXJuYWxfc3RvcmFnZV90b3RhbBg8IAEoBRIiChpleHRlcm5hbF9zdG9yYWdlX2F2YWlsYWJsZRg9IAEoBRIeChZpbnRlcm5hbF9zdG9yYWdlX3RvdGFsGD4gASgFEiIKGmludGVybmFsX3N0b3JhZ2VfYXZhaWxhYmxlGD8gASgFEiMKG2dhbWVfZGlza19zdG9yYWdlX2F2YWlsYWJsZRhAIAEoBRIfChdnYW1lX2Rpc2tfc3RvcmFnZV90b3RhbBhBIAEoBRIlCh1leHRlcm5hbF9zZGNhcmRfYXZhaWxfc3RvcmFnZRhCIAEoBRIlCh1leHRlcm5hbF9zZGNhcmRfdG90YWxfc3RvcmFnZRhDIAEoBRIQCghsb2dpbl9ieRhJIAEoBRIUCgxsaWJyYXJ5X3BhdGgYSiABKAkSEgoKcmVnX2F2YXRhchhMIAEoBRIVCg1saWJyYXJ5X3Rva2VuGE0gASgJEhQKDGNoYW5uZWxfdHlwZRhOIAEoBRIQCghjcHVfdHlwZRhPIAEoBRIYChBjcHVfYXJjaGl0ZWN0dXJlGFEgASgJEhsKE2NsaWVudF92ZXJzaW9uX2NvZGUYUyABKAkSFAoMZ3JhcGhpY3NfYXBpGFYgASgJEh0KFXN1cHBvcnRlZF9hc3RjX2JpdHNldBhXIAEoDRIaChJsb2dpbl9vcGVuX2lkX3R5cGUYWCABKAUSGAoQYW5hbHl0aWNzX2RldGFpbBhZIAEoDBIUCgxsb2FkaW5nX3RpbWUYXCABKA0SFwoPcmVsZWFzZV9jaGFubmVsGF0gASgJEhIKCmV4dHJhX2luZm8YXiABKAkSIAoYYW5kcm9pZF9lbmdpbmVfaW5pdF9mbGFnGF8gASgNEg8KB2lmX3B1c2gYYSABKAUSDgoGaXNfdnBuGGIgASgFEhwKFG9yaWdpbl9wbGF0Zm9ybV90eXBlGGMgASgJEh0KFXByaW1hcnlfcGxhdGZvcm1fdHlwZRhkIAEoCSI1CgxHYW1lU2VjdXJpdHkSDwoHdmVyc2lvbhgGIAEoBRIUCgxoaWRkZW5fdmFsdWUYCCABKARiBnByb3RvMw=="

MAJOR_LOGIN_RES_B64 = "ChNNYWpvckxvZ2luUmVzLnByb3RvInwKDU1ham9yTG9naW5SZXMSEwoLYWNjb3VudF91aWQYASABKAQSDgoGcmVnaW9uGAIgASgJEg0KBXRva2VuGAggASgJEgsKA3VybBgKIAEoCRIRCgl0aW1lc3RhbXAYFSABKAMSCwoDa2V5GBYgASgMEgoKAml2GBcgASgMYgZwcm90bzM="

def load_protobuf_classes():
    classes = {}
    temp_dir = tempfile.mkdtemp()
    
    req_code = '''
# -*- coding: utf-8 -*-
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
import base64
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(base64.b64decode("''' + MAJOR_LOGIN_REQ_B64 + '''"))
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'MajorLoginReq_pb2', _globals)
'''
    
    res_code = '''
# -*- coding: utf-8 -*-
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
import base64
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(base64.b64decode("''' + MAJOR_LOGIN_RES_B64 + '''"))
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'MajorLoginRes_pb2', _globals)
'''
    
    req_path = os.path.join(temp_dir, 'MajorLoginReq_pb2.py')
    with open(req_path, 'w') as f:
        f.write(req_code)
    spec = importlib.util.spec_from_file_location("MajorLoginReq_pb2", req_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["MajorLoginReq_pb2"] = module
    spec.loader.exec_module(module)
    classes['MajorLogin'] = module.MajorLogin
    classes['GameSecurity'] = module.GameSecurity
    
    res_path = os.path.join(temp_dir, 'MajorLoginRes_pb2.py')
    with open(res_path, 'w') as f:
        f.write(res_code)
    spec = importlib.util.spec_from_file_location("MajorLoginRes_pb2", res_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["MajorLoginRes_pb2"] = module
    spec.loader.exec_module(module)
    classes['MajorLoginRes'] = module.MajorLoginRes
    
    return classes

try:
    PB = load_protobuf_classes()
    MajorLogin = PB['MajorLogin']
    GameSecurity = PB['GameSecurity']
    MajorLoginRes = PB['MajorLoginRes']
except Exception as e:
    print(f"[✗] Failed to load protobuf classes: {e}")
    print("[*] Make sure you have protobuf installed: pip install protobuf")
    sys.exit(1)

def encrypt_proto(payload_bytes):
    cipher = AES.new(PROTO_KEY, AES.MODE_CBC, PROTO_IV)
    padded = pad(payload_bytes, AES.block_size)
    return cipher.encrypt(padded)

def decrypt_proto(encrypted_bytes):
    try:
        cipher = AES.new(PROTO_KEY, AES.MODE_CBC, PROTO_IV)
        decrypted = unpad(cipher.decrypt(encrypted_bytes), AES.block_size)
        return decrypted
    except Exception as e:
        return None

def generate_access_token(uid, password):
    headers = {
        "Host": "100067.connect.garena.com",
        "User-Agent": "GarenaMSDK/5.5.2P3(SM-A515F;Android 12;en-US;IND;)",
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "close"
    }
    data = {
        "uid": uid, "password": password, "response_type": "token",
        "client_type": "2", "client_secret": CLIENT_SECRET, "client_id": CLIENT_ID
    }
    try:
        response = requests.post(OAUTH_URL, headers=headers, data=data, timeout=30, verify=False)
        if response.status_code == 200:
            resp_data = response.json()
            return resp_data.get("open_id"), resp_data.get("access_token"), None
        elif response.status_code == 429:
            return None, None, "Rate limited (429) - Too many requests"
        else:
            try:
                error_data = response.json()
                return None, None, f"HTTP {response.status_code}: {error_data}"
            except:
                return None, None, f"HTTP {response.status_code}: {response.text}"
    except requests.exceptions.Timeout:
        return None, None, "Request timeout"
    except Exception as e:
        return None, None, str(e)

def build_major_login_message(open_id, access_token):
    major_login = MajorLogin()
    major_login.event_time = str(datetime.now())[:-7]
    major_login.game_name = "free fire"
    major_login.platform_id = 1
    major_login.client_version = "1.123.1"
    major_login.system_software = "Android OS 9 / API-28 (PQ3B.190801.10101846/G9650ZHU2ARC6)"
    major_login.system_hardware = "Handheld"
    major_login.telecom_operator = "Verizon"
    major_login.network_type = "WIFI"
    major_login.screen_width = 1920
    major_login.screen_height = 1080
    major_login.screen_dpi = "280"
    major_login.processor_details = "ARM64 FP ASIMD AES VMH | 2865 | 4"
    major_login.memory = 3003
    major_login.gpu_renderer = "Adreno (TM) 640"
    major_login.gpu_version = "OpenGL ES 3.1 v1.46"
    major_login.unique_device_id = "Google|34a7dcdf-a7d5-4cb6-8d7e-3b0e448a0c57"
    major_login.client_ip = "223.191.51.89"
    major_login.language = "en"
    major_login.open_id = open_id
    major_login.open_id_type = "4"
    major_login.device_type = "Handheld"
    major_login.memory_available.version = 55
    major_login.memory_available.hidden_value = 81
    major_login.access_token = access_token
    major_login.platform_sdk_id = 1
    major_login.network_operator_a = "Verizon"
    major_login.network_type_a = "WIFI"
    major_login.client_using_version = "7428b253defc164018c604a1ebbfebdf"
    major_login.external_storage_total = 36235
    major_login.external_storage_available = 31335
    major_login.internal_storage_total = 2519
    major_login.internal_storage_available = 703
    major_login.game_disk_storage_available = 25010
    major_login.game_disk_storage_total = 26628
    major_login.external_sdcard_avail_storage = 32992
    major_login.external_sdcard_total_storage = 36235
    major_login.login_by = 3
    major_login.library_path = "/data/app/com.dts.freefireth-YPKM8jHEwAJlhpmhDhv5MQ==/lib/arm64"
    major_login.reg_avatar = 1
    major_login.library_token = "5b892aaabd688e571f688053118a162b|/data/app/com.dts.freefireth-YPKM8jHEwAJlhpmhDhv5MQ==/base.apk"
    major_login.channel_type = 3
    major_login.cpu_type = 2
    major_login.cpu_architecture = "64"
    major_login.client_version_code = "2019118695"
    major_login.graphics_api = "OpenGLES2"
    major_login.supported_astc_bitset = 16383
    major_login.login_open_id_type = 4
    major_login.analytics_detail = b"FwQVTgUPX1UaUllDDwcWCRBpWA0FUgsvA1snWlBaO1kFYg=="
    major_login.loading_time = 13564
    major_login.release_channel = "android"
    major_login.extra_info = "KqsHTymw5/5GB23YGniUYN2/q47GATrq7eFeRatf0NkwLKEMQ0PK5BKEk72dPflAxUlEBir6Vtey83XqF593qsl8hwY="
    major_login.android_engine_init_flag = 110009
    major_login.if_push = 1
    major_login.is_vpn = 1
    major_login.origin_platform_type = "4"
    major_login.primary_platform_type = "4"
    return major_login.SerializeToString()

def major_login(open_id, access_token):
    proto_payload = build_major_login_message(open_id, access_token)
    encrypted_payload = encrypt_proto(proto_payload)
    try:
        response = requests.post(MAJOR_LOGIN_URL, data=encrypted_payload, headers=BASE_HEADERS, timeout=30, verify=False)
        if response.status_code == 200:
            response_data = response.content
            if len(response_data) % 16 == 0:
                decrypted_response = decrypt_proto(response_data)
                if decrypted_response:
                    res = MajorLoginRes()
                    res.ParseFromString(decrypted_response)
                    return True, {
                        'account_uid': res.account_uid,
                        'region': res.region,
                        'token': res.token,
                        'url': res.url,
                        'timestamp': res.timestamp,
                        'key': res.key.hex() if res.key else None,
                        'iv': res.iv.hex() if res.iv else None
                    }
            try:
                res = MajorLoginRes()
                res.ParseFromString(response_data)
                if res.token:
                    return True, {
                        'account_uid': res.account_uid,
                        'region': res.region,
                        'token': res.token,
                        'url': res.url,
                        'timestamp': res.timestamp,
                        'key': res.key.hex() if res.key else None,
                        'iv': res.iv.hex() if res.iv else None
                    }
            except:
                pass
            return False, f"Could not parse response. Length: {len(response_data)}"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
    except requests.exceptions.Timeout:
        return False, "Request timeout"
    except Exception as e:
        return False, str(e)

@app.route('/Bmw', methods=['GET'])
def process():
    uid = request.args.get('uid')
    password = request.args.get('password')
    
    if not uid or not password:
        return jsonify({
            "status": "error",
            "message": "Missing required parameters: uid and password",
            "Api": "http://3.108.219.42:5001/Bmw?uid={uid}&password={pass}"
        }), 400
    
    open_id, access_token, error = generate_access_token(uid, password)
    
    if error:
        return jsonify({
            "status": "error",
            "message": f"Authentication failed: {error}",
            "uid": uid
        }), 401
    
    success, login_response = major_login(open_id, access_token)
    
    if not success:
        return jsonify({
            "status": "error",
            "message": f"Account Is Banned Or Wrong Uid Pass Check Again",
            "uid": uid,
            "open_id": open_id,
            "access_token": access_token
        }), 500
    
    jwt_token = login_response.get('token')
    
    return jsonify({
        "status": "success",
        "uid": uid,
        "open_id": open_id,
        "access_token": access_token,
        "jwt_token": jwt_token,
        "account_uid": login_response.get('account_uid'),
        "region": login_response.get('region'),
        "timestamp": login_response.get('timestamp'),
        "base_url": login_response.get('url')
    })

if __name__ == '__main__':
    import sys
    cli = sys.modules['flask.cli']
    cli.show_server_banner = lambda *x: None
    app.run(host='0.0.0.0', port=5001, debug=False)