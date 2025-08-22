from hads.shortcuts import json_response
from hads.shortcuts import login_required
from project.common import gen_code
import boto3
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key
import datetime
from zoneinfo import ZoneInfo
import json
from project.common import Shogi
import os

MAIN_TABLE_NAME = os.environ.get('DYNAMODB_TABLE', 'table-sgp-pro-main')
AID_LENGTH = 8

@login_required
def submit(master):
  master.logger.info(f"event: {master.event}")
  master.logger.info(f"submit: {master.request.body}")
  body = json.loads(master.event["body"])
  if master.request.method != "POST":
    master.logger.error("Invalid request method")
    return json_response(
      master, 
      {
        "submit": "reject",
        "aid": None
      }
    )
  # position = master.request.body.get("position")
  position = body.get("position")
  if position is None:
    master.logger.error("Position not found")
    return json_response(
      master, 
      {
        "submit": "reject",
        "aid": None
      }
    )
  if position.startswith("position sfen "):
    position = position.replace("position sfen ","")
    # position = "lnsgkgsnl/1r5b1/p1pppp1p1/6p1p/9/2P6/PP1PPPPPP/1B5R1/LNSGKGSNL b - 1"
  else:
    master.logger.error("Invalid position format")
    return json_response(
      master,
      {
        "submit": "reject",
        "aid": None
      }
    )
  import os
  
  sqs = boto3.client('sqs')
  
  # 環境変数からキュー名を取得（デフォルトはsqs-sgp-analysis.fifo）
  queue_name = os.environ.get('SQS_QUEUE_NAME', 'sqs-sgp-analysis.fifo')
  
  # アカウントIDを動的取得
  sts = boto3.client('sts')
  account_id = sts.get_caller_identity()['Account']
  
  # SQS URLを動的生成
  region = os.environ.get('AWS_REGION', 'ap-northeast-1')
  QueueUrl = f"https://sqs.{region}.amazonaws.com/{account_id}/{queue_name}"
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
  table = boto3.resource('dynamodb').Table(MAIN_TABLE_NAME) 
  response = table.get_item(
    Key={
      "pk": "analysis",
      "sk": f"aid#{aid}"
    }
  )
  if response.get("Item") is None:
    return json_response(
      master, 
      {
        "status": None,
        "message": "Not found"
      }
    )
  if response["Item"]["cgsi_pk"] != f"analysis#uname#{master.request.username}":
    return json_response(
      master, 
      {
        "status": None,
        "message": "Not found"
      }
    )
  if response["Item"]["status"] == "waiting":
    return json_response(
      master, 
      {
        "status": "running",
        "message": None
      }
    )
  elif response["Item"]["status"] == "successed":
    return json_response(
      master, 
      {
        "status": "successed",
        "message": _response2message(json.loads(response["Item"]["response"]))
      }
    )
  else:
    return json_response(
      master, 
      {
        "status": "failed",
        "message": "解析に失敗しました。"
      }
    )

def _response2message(response:dict):
  shogi = Shogi(response["position"])
  count = shogi.count
  message_rows = [f"=== {count-1}手目 ==="]
  for i in range(1,11):
    if str(i) in response["result"].keys():
      shogi = Shogi(response["position"])
      turn = shogi.turn
      count = shogi.count
      kifu_jp_list = shogi.moves_by_sfen_moves(
        response["result"][str(i)]["pv"].split(" "),
        return_kifu_jp_list=True
      )
      score = response["result"][str(i)]["score"]
      if score[0] != "#":
        if turn == "w":
          score = str(-int(score))
        if score[0] != "-":
          score = "+" + score
      row = f"""\
候補手{i}
評価値: {score}
手順　: {' '.join(kifu_jp_list)}"""
      message_rows.append(row)
    else:
      break
  return "\n".join(message_rows)



  return json_response(master, response)
