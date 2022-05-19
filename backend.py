from fastapi import FastAPI
from typing import Optional,List
from databases import Database
from fastapi.params import Query
from pydantic import BaseModel
import pandas as pd
import json
from fastapi.middleware.cors import CORSMiddleware
from cloudtx_api import add_baby_monitor_data_to_cloud
app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class IP(BaseModel):
    ip_address: str
    mac_address: str

class STATUS(BaseModel):
    status : str
    mac_address : str

class AI_PRED(BaseModel):
    sleeping_state: Optional[str] = None
    max_ai_stat: Optional[str] = None
    current_ai_stat: Optional[str] = None
    b_stat: str
    t_start: str
    t_save: str
    breathing_pause: int
    mac_address: str
    fa1: float
    fa2: float
    fb1: float
    fb2: float
    max_amp: float
    periodic: int
    peak1_bin: float
    Br_freq_rpm: float
    sd_peak1_bin: float
    sd_whole: float
    nic_features:List[int]
    entropy:float
    new_breathing_pause:int
    breathing_pause_time:int
    Br_rate_1100:float
database = Database('postgresql://rohit:raybaby@34.203.100.53:5432/qr_codes')



@app.on_event("startup")
async def startup():
    await database.connect()



@app.get("/qr_code/")
async def get_container_info(qr_code: str):
    query = "SELECT mac_id FROM qr_mapping where qr = %r"%(qr_code)
    out = pd.DataFrame(await database.fetch_all(query=query))
    if len(out):
        return out.to_dict()['mac_id'][0]
    else:
        return {}

@app.get("/app_status/")
async def get_app_status(mac_id: str):
    query = "SELECT app_status FROM app_status where mac_id = %r"%(mac_id)
    out = pd.DataFrame(await database.fetch_all(query=query))
    if len(out):
        return out.to_dict()['app_status'][0]
    else:
        return "0"

@app.post("/ip_mapping/")
async def insert_ip(ip: IP):
    ip = json.loads(ip.json())
    ip['ip_address'] = ip['ip_address'].replace('-','.')
    query_to_check_mapping = """
            SELECT mac_id from ip_mapping
            WHERE mac_id = '%s'
            """%(ip['mac_address'])
    out = pd.DataFrame(await database.fetch_all(query=query_to_check_mapping))
    if len(out):
        query = """
                UPDATE ip_mapping
                set ip_address = '%s'
                where mac_id = '%s' """%(ip['ip_address'],ip['mac_address'])
        await database.execute(query=query)
    else:
        query = "INSERT INTO ip_mapping(mac_id, ip_address) VALUES ('%s','%s')"%(ip['mac_address'],ip['ip_address'])
        await database.execute(query=query)
    return True

@app.post("/raybaby_app_status/")
async def insert_ip(raybaby_status: STATUS):
    raybaby_status = json.loads(raybaby_status.json())
    query_to_check_mapping = """
            SELECT mac_id from app_status
            WHERE mac_id = '%s'
            """%(raybaby_status['mac_address'])
    out = pd.DataFrame(await database.fetch_all(query=query_to_check_mapping))
    if len(out):
        query = """
                UPDATE app_status
                set app_status = '%s'
                where mac_id = '%s' """%(raybaby_status['status'],raybaby_status['mac_address'])
        await database.execute(query=query)
    else:
        query = "INSERT INTO app_status (mac_id, app_status) VALUES ('%s','%s')"%(raybaby_status['mac_address'],raybaby_status['status'])
        await database.execute(query=query)
    return True

@app.post("/ai_pred/")
async def insert_ip(body: AI_PRED):
    body = body.dict()
    return add_baby_monitor_data_to_cloud(body)
@app.get("/mac_id_ip_mapping/")
async def get_ip_address(mac_id: str):
    query = "SELECT ip_address FROM ip_mapping where mac_id = '%s'"%(mac_id)
    out = pd.DataFrame(await database.fetch_all(query=query))
    if len(out):
        return out.to_dict()['ip_address'][0]
    else:
        return {}