from hads.shourtcuts import json_response
from hads.shourtcuts import login_required
from project.common import gen_code
import boto3
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key
import datetime
from zoneinfo import ZoneInfo
import json

MAIN_TABLE_NAME = "table-sgp-main"
AID_LENGTH = 8

@login_required
def submit(master):
  position = "lnsgkgsnl/1r5b1/p1pppp1p1/6p1p/9/2P6/PP1PPPPPP/1B5R1/LNSGKGSNL b - 1"
  sqs = boto3.client('sqs')
  ssm = boto3.client('ssm')
  QueueUrl=ssm.get_parameter(Name="/ShogiProject/SQS/Analysis/URL")["Parameter"]["Value"]
  # キュー内のメッセージの数が多ければ拒否
  response = sqs.get_queue_attributes(
    QueueUrl=QueueUrl,
    AttributeNames=['ApproximateNumberOfMessages']
  )
  if int(response['Attributes']['ApproximateNumberOfMessages']) > 5:
    return json_response(
      master, 
      {
        "submit": "reject",
        "aid": None
      }
    )
  # 直近の実行が一定以上なら拒否
  now = datetime.datetime.now(ZoneInfo(master.settings.TIMEZONE))
  now_str = now.strftime("%Y-%m-%d %H:%M:%S")
  ago_str = (now - datetime.timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")
  table = boto3.resource('dynamodb').Table(MAIN_TABLE_NAME)
  response = table.query(
    KeyConditionExpression=Key('pk').eq('analysis'),
    IndexName="CreatedIndex",
    ScanIndexForward=False,
    Limit=30,
  )
  if len(response["Items"]) == 30 and response["Items"][-1]["created"] > ago_str:
    return json_response(
      master, 
      {
        "submit": "reject",
        "aid": None
      }
    )
  # DynamoDBに登録
  expired = now + datetime.timedelta(hours=1)
  expired_int = int(expired.timestamp())
  aid = gen_code(AID_LENGTH)
  Item = {
    "pk": "analysis",
    "sk": f"aid#{aid}",
    "cgsi_pk": f"analysis#uname#{master.request.username}",
    "created": now_str,
    "status": "waiting",
    "response": None,
    "expired": expired_int
  }
  response = table.put_item(
    Item=Item
  )
  # SQSに送信
  data = {
    "username": master.request.username,
    "aid": aid,
    "position": position
  }
  message = json.dumps(data)
  response = sqs.send_message(
    QueueUrl=QueueUrl,
    MessageBody=message,
    MessageGroupId=data["username"],
    MessageDeduplicationId=data["aid"]
  )
  return json_response(
    master, 
    {
      "submit": "accept",
      "aid": aid
    }
  )

@login_required
def inquire(master, aid):
  response = {"hoge": "fuga"}
  return json_response(master, response)
