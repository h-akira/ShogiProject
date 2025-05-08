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

def submit(master):
  response = {"hoge": "fuga"}
  return json_response(response)

def inquire(master, aid):
  response = {"hoge": "fuga"}
  return json_response(response)
