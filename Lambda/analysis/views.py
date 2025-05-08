from hads.shourtcuts import json_response
from hads.shourtcuts import login_required
from project.common import gen_code
import boto3
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key
import datetime
from zoneinfo import ZoneInfo

MAIN_TABLE_NAME = "table-sgp-main"
AID_LENGTH = 8

@login_required
def submit(master):
  table = boto3.resource('dynamodb').Table(MAIN_TABLE_NAME)
  response = table.query(
    KeyConditionExpression=Key('pk').eq('analysis'),
    IndexName="CreatdIndex",
    ScanIndexForward=False
  )
  master.logger.info(f"response: {response}")
  now = datetime.datetime.now(ZoneInfo(master.settings.TIMEZONE))
  now_str = now.strftime("%Y-%m-%d %H:%M:%S")
  expired = now + datetime.timedelta(hours=1)
  expired_int = int(expired.timestamp())
  Item = {
    "pk": "analysis",
    "sk": f"aid#{gen_code(AID_LENGTH)}",
    "cgsi_pk": f"analysis#uname#{master.request.username}",
    "created": now_str,
    "status": "waiting",
    "response": None,
    "expired": expired_int
  }
  response = table.put_item(
    Item=Item
  )
  return json_response(response)

@login_required
def inquire(master, aid):
  response = {"hoge": "fuga"}
  return json_response(response)
