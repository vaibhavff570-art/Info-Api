import asyncio
import time
import httpx
import json
from collections import defaultdict
from flask import Flask, request, jsonify
from flask_cors import CORS
from proto import FreeFire_pb2, main_pb2, AccountPersonalShow_pb2
from google.protobuf import json_format
from Crypto.Cipher import AES

G = bytes([89, 103, 38, 116, 99, 37, 68, 69, 117, 104, 54, 37, 90, 99, 94, 56])
F = bytes([54, 111, 121, 90, 68, 114, 50, 50, 69, 51, 121, 99, 104, 106, 77, 37])
REGNS = {"IND", "BR", "US", "SAC", "NA", "SG", "RU", "ID", "TW", "VN", "TH", "ME", "PK", "CIS", "BD", "EUROPE"}

FAHHHH = Flask(__name__)
CORS(FAHHHH)
TOKENS = defaultdict(dict)
UID_MEMORY = {}

def BmwNoNoBmvYas(d):
    l = AES.block_size - (len(d) % AES.block_size)
    return d + bytes([l] * l)

def BmwNoiNoiBmvYasYas(k, i, d):
    a = AES.new(k, AES.MODE_CBC, i)
    return a.encrypt(BmwNoNoBmvYas(d))

def PoI(b, mt):
    m = mt()
    m.ParseFromString(b)
    return m

async def QwE(jt, pt):
    json_format.ParseDict(json.loads(jt), pt)
    return pt.SerializeToString()

def AsD(reg):
    reg = reg.upper()
    if reg == "IND":
        return "uid=4940479833&password=BIBITGAMER13_A.-LJH-BY-UDJLO5"
    elif reg in {"BR", "US", "SAC", "NA"}:
        return "uid=4044223479&password=EB067625F1E2CB705C7561747A46D502480DC5D41497F4C90F3FDBC73B8082ED"
    else:
        return "uid=4108414251&password=E4F9C33BBEB23C0DA0AD7E60F63C8A05D6A878798E3CD32C4E2314C1EEFD4F72"

async def ZxV(acc):
    url = "https://ffmconnect.live.gop.garenanow.com/oauth/guest/token/grant"
    data = acc + "&response_type=token&client_type=2&client_secret=2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3&client_id=100067"
    async with httpx.AsyncClient(timeout=30.0) as cl:
        try:
            res = await cl.post(url, data=data, headers={'User-Agent': "Dalvik/2.1.0 (Linux; U; Android 13; CPH2095 Build/RKQ1.211119.001)", 'Connection': "Keep-Alive", 'Accept-Encoding': "gzip", 'Content-Type': "application/x-www-form-urlencoded"})
            d = res.json()
            return d.get("access_token", "0"), d.get("open_id", "0")
        except:
            return "0", "0"

async def Bmw(reg):
    try:
        acc = AsD(reg)
        token, oid = await ZxV(acc)
        if token == "0" or oid == "0":
            return
        body = json.dumps({"open_id": oid, "open_id_type": "4", "login_token": token, "orign_platform_type": "4"})
        pb = await QwE(body, FreeFire_pb2.LoginReq())
        enc = BmwNoiNoiBmvYasYas(G, F, pb)
        url = "https://loginbp.ggpolarbear.com/MajorLogin"
        async with httpx.AsyncClient(timeout=30.0) as cl:
            res = await cl.post(url, data=enc, headers={'User-Agent': "Dalvik/2.1.0 (Linux; U; Android 13; CPH2095 Build/RKQ1.211119.001)", 'Connection': "Keep-Alive", 'Accept-Encoding': "gzip", 'Content-Type': "application/octet-stream", 'Expect': "100-continue", 'X-Unity-Version': "2018.4.11f1", 'X-GA': "v1 1", 'ReleaseVersion': "OB53"})
            msg = json.loads(json_format.MessageToJson(PoI(res.content, FreeFire_pb2.LoginRes)))
            TOKENS[reg] = {
                'token': f"Bearer {msg.get('token','0')}",
                'region': msg.get('lockRegion','0'),
                'server': msg.get('serverUrl','0'),
                'expires': time.time() + 25200
            }
    except:
        pass

async def GaY():
    tasks = [Bmw(reg) for reg in REGNS]
    try:
        await asyncio.gather(*tasks, return_exceptions=True)
    except:
        for reg in REGNS:
            try:
                await Bmw(reg)
                await asyncio.sleep(1)
            except:
                continue

async def Gsu():
    while True:
        await asyncio.sleep(25200)
        await GaY()

async def RtY(reg):
    info = TOKENS.get(reg)
    if info and time.time() < info['expires']:
        return info['token'], info['region'], info['server']
    await Bmw(reg)
    info = TOKENS[reg]
    return info['token'], info['region'], info['server']

async def LoL(uid, unk, reg, ep):
    payload = await QwE(json.dumps({'a': uid, 'b': unk}), main_pb2.GetPlayerPersonalShow())
    data_enc = BmwNoiNoiBmvYasYas(G, F, payload)
    token, lock, server = await RtY(reg)
    async with httpx.AsyncClient(timeout=30.0) as cl:
        res = await cl.post(server+ep, data=data_enc, headers={'User-Agent': "Dalvik/2.1.0 (Linux; U; Android 13; CPH2095 Build/RKQ1.211119.001)", 'Connection': "Keep-Alive", 'Accept-Encoding': "gzip", 'Content-Type': "application/octet-stream", 'Expect': "100-continue", 'Authorization': token, 'X-Unity-Version': "2018.4.11f1", 'X-GA': "v1 1", 'ReleaseVersion': "OB53"})
        return json.loads(json_format.MessageToJson(PoI(res.content, AccountPersonalShow_pb2.AccountPersonalShowInfo)))

def HeHe(d):
    return d

@FAHHHH.route('/Bmw')
def OMG():
    uid = request.args.get('uid')
    if not uid:
        return jsonify({"error": "Please provide UID."}), 400
    
    if uid in UID_MEMORY:
        try:
            data = asyncio.run(LoL(uid, "7", UID_MEMORY[uid], "/GetPlayerPersonalShow"))
            data = HeHe(data)
            return json.dumps(data, indent=2, ensure_ascii=False), 200, {'Content-Type': 'application/json; charset=utf-8'}
        except:
            pass
    
    for reg in REGNS:
        try:
            data = asyncio.run(LoL(uid, "7", reg, "/GetPlayerPersonalShow"))
            UID_MEMORY[uid] = reg
            data = HeHe(data)
            return json.dumps(data, indent=2, ensure_ascii=False), 200, {'Content-Type': 'application/json; charset=utf-8'}
        except:
            continue
    
    return jsonify({"error": "UID not found in any region."}), 404

@FAHHHH.route('/refresh', methods=['GET','POST'])
def WTF():
    try:
        asyncio.run(GaY())
        return jsonify({'message':'Tokens refreshed for all regions.'}), 200
    except Exception as e:
        return jsonify({'error': f'Refresh failed: {e}'}), 500

async def xD():
    await GaY()
    asyncio.create_task(Gsu())

asyncio.run(xD())
FAHHHH.run(host='0.0.0.0', port=5000, debug=False)