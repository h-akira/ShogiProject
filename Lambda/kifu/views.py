from hads.shourtcuts import render
from hads.shourtcuts import login_required, redirect
from .forms import KifuForm
import random
import boto3
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key
import datetime
from zoneinfo import ZoneInfo

MAIN_TABLE_NAME = "table-sgp-main"
KID_LENGTH = 12
SHARE_CODE_LENGTH = 36

def _count_partition(table, pk_value):
  counter = 0
  last_evaluated_key = None
  while True:
    if last_evaluated_key:
      response = table.query(
        KeyConditionExpression=Key('pk').eq(pk_value),
        Select='COUNT',
        ExclusiveStartKey=last_evaluated_key
      )
    else:
      response = table.query(
        KeyConditionExpression=Key('pk').eq(pk_value),
        Select='COUNT'
      )
    counter += response['Count']
    last_evaluated_key = response.get('LastEvaluatedKey', None)
    if not last_evaluated_key:
      break
  return counter

def _gen_code(length):
  allow="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
  return ''.join(random.choice(allow) for i in range(length))

def _get_system_from_table(master):
  table = boto3.resource('dynamodb').Table(MAIN_TABLE_NAME)
  response = table.get_item(
    Key={
      "pk": "system",
      "sk": "none"
    }
  )
  if "Item" not in response:
    master.logger.warning("System item not found in DynamoDB")
    return {
      # "year_init": 2025,
      # "kifu_max_per_year": 3000,
      "kifu_max": 3000,
      "tag_max": 50
    }
  else:
    system = {}
    if "kifu_max" not in response["Item"]:
      master.logger.warning("kifu_max not found in system item")
      system["kifu_max"] = 3000
    else:
      system["kifu_max"] = response["Item"]["kifu_max"]
    if "tag_max" not in response["Item"]:
      master.logger.warning("tag_max not found in system item")
      system["tag_max"] = 50
    else:
      system["tag_max"] = response["Item"]["tag_max"]
    return system

def _slug_format_checker_return_error_message(slug: str):
  if len(slug) > 100:
    return "Slug is too long."
  if len(slug) == 0:
    return "Slug is empty."
  if slug[0] == "/":
    return "Slug cannot start with '/'."
  if "#" in slug:
    return "Slug cannot contain '#'."
  return None

def _check_slug_exists(table, username, slug):
  try:
    response = table.query(
      IndexName="CommonLSI",
      KeyConditionExpression=Key('pk').eq(f"kifu#uname#{username}") & Key('clsi_sk').eq(f"slug#{slug}")
    )
  except ClientError as e:
    raise e
  print(response)
  if response["Count"] > 1:
    raise Exception("Multiple items found with the same slug")
  elif response["Count"] == 1:
    return True
  else:
    return False

def _get_latest_update_items(table, username, limit=10):
  response = table.query(
    IndexName="LatestUpdateIndex",
    KeyConditionExpression=Key('pk').eq(f"kifu#uname#{username}"),
    ScanIndexForward=False,
    Limit=limit
  )
  return response["Items"]



@login_required
def delete(master, username, kid):
  if username != master.request.username:
    return redirect(master, "kifu:index", username=master.request.username)
  table = boto3.resource('dynamodb').Table(MAIN_TABLE_NAME)
  try:
    response = table.delete_item(
      Key={
        'pk': f"kifu#uname#{username}",
        'sk': f"kid#{kid}"
      },
      ConditionExpression=Key('pk').eq(f"kifu#uname#{username}") & Key('sk').eq(f"kid#{kid}")
    )
  except ClientError as e:
    master.logger.error(f"Failed to delete item: {e.response['Error']['Message']}")
  return redirect(master, "kifu:index", username=username)

@login_required
def index(master, username):
  if username != master.request.username:
    # 特定のユーザーには許可することもそのうち実装する
    return render(master, 'not_found.html')
  table = boto3.resource('dynamodb').Table(MAIN_TABLE_NAME)
  latest_update_items = _get_latest_update_items(table, username, limit=10)
  context = {
    'username': username,
    'latest_update_items': [
      {
        "kid": item["sk"].split("#")[1], 
        "slug": item["clsi_sk"].split("#")[1], 
        "latest_update": item["latest_update"]
      } for item in latest_update_items
    ]
  }
  return render(master, 'kifu/index.html', context)

@login_required
def detail(master, username, kid):
  if username != master.request.username:
    return render(master, 'not_found.html')
  table = boto3.resource('dynamodb').Table(MAIN_TABLE_NAME)
  response = table.get_item(
    Key={
      'pk': f"kifu#uname#{username}",
      'sk': f"kid#{kid}"
    }
  )
  if "Item" not in response:
    return render(master, 'not_found.html')
  else:
    item = response["Item"]
    context = {
      'username': username,
      'kid': kid,
      'slug': item["clsi_sk"].split("#")[1],
      'kifu': item["kifu"],
      'memo': item["memo"],
      'first_or_second': item["first_or_second"],
      'result': item["result"],
      'share': item["share"],
      'share_code': item["cgsi_pk"].split("#")[1],
      'public': item["public"],
      'created': item["created"],
      'latest_update': item["latest_update"]
    }
    return render(master, 'kifu/detail.html', context)


@login_required
def explorer(master, username):
  context = {
    'username': username
  }
  return render(master, 'kifu/explorer.html', context)

@login_required
def create(master, username):
  if master.request.method == 'POST':
    master.logger.info(master.request.body)
    table = boto3.resource('dynamodb').Table(MAIN_TABLE_NAME)
    now = datetime.datetime.now(ZoneInfo(master.settings.TIMEZONE))
    now_str = now.strftime("%Y-%m-%d %H:%M:%S")
    action = master.request.body["action"]
    form = KifuForm(**master.request.body)
    system = _get_system_from_table(master)
    if system["kifu_max"] < _count_partition(boto3.resource('dynamodb').Table(MAIN_TABLE_NAME), f"kifu#uname#{username}"):
      context = {
        "type": "create",
        "form": form,
        "error_message": "Kifu limit exceeded"
      }
      return render(master, 'kifu/edit.html', context)
    error_message = _slug_format_checker_return_error_message(form.data['slug'])
    if error_message is not None:
      context = {
        "type": "create",
        "form": form,
        "error_message": error_message
      }
      return render(master, 'kifu/edit.html', context)
    if _check_slug_exists(table, username, form.data['slug']):
      context = {
        "type": "create",
        "form": form,
        "error_message": "Slug already exists"
      }
      return render(master, 'kifu/edit.html', context)
    kid = _gen_code(KID_LENGTH)
    share_code = _gen_code(SHARE_CODE_LENGTH)
    Item = {
      "pk": f"kifu#uname#{username}",
      "sk": f"kid#{kid}",
      "cgsi_pk": f"scode#{share_code}",
      "clsi_sk": f"slug#{form.data['slug']}",
      "public": form.data['public'],
      "share": form.data['share'],
      "kifu": form.data['kifu'],
      "memo": form.data['memo'],
      "first_or_second": form.data['first_or_second'],
      "result": form.data['result'],
      "created": now_str,
      "latest_update": now_str
    }
    # Item["last_updated"] = datetime.datetime.now(ZoneInfo("Asia/Tokyo")).strftime("%Y-%m-%d %H:%M:%S")
    try:
      response = table.put_item(
        Item=Item
      )
      if action == "continue":
        context = {
          "type": "create",
          "form": form,
          "error_message": None
        }
        return redirect(master, "kifu:edit", username=username, kid=kid)
      elif action == "end":
        kid = Item["sk"].split("#")[1]
        return redirect(master, "kifu:detail", username=username, kid=kid)
      else:
        raise Exception("Invalid action")
    except ClientError as e:
      if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
        error_message = "Item with the same partition key and sort key already exists."
      else:
        import traceback
        error_message = traceback.format_exc()
      context = {
        "type": "create",
        "form": form,
        "error_message": error_message
      }
      return render(request, 'kifu/edit.html', context)
  elif master.request.method == 'GET':
    form = KifuForm()
    context = {
      "type": "create",
      "form": form,
      "error_message": None
    }
    return render(master, 'kifu/edit.html', context)
  else:
    raise Exception('Invalid request method')

def edit(master, username, kid):
  if username != master.request.username:
    return render(master, 'not_found.html')
  table = boto3.resource('dynamodb').Table(MAIN_TABLE_NAME)
  if master.request.method == 'POST':
    master.logger.info(master.request.body)
    now = datetime.datetime.now(ZoneInfo(master.settings.TIMEZONE))
    now_str = now.strftime("%Y-%m-%d %H:%M:%S")
    form = KifuForm(**master.request.body)
    action = master.request.body["action"]
    table.update_item(
      Key={
        'pk': f"kifu#uname#{username}",
        'sk': f"kid#{kid}"
      },
      UpdateExpression="set #clsi_sk=:cl, #kifu=:ki, #memo=:me, #first_or_second=:fi, #result=:re, #share=:sh, #public=:pu, #latest_update=:la",
      ExpressionAttributeNames={
        "#clsi_sk": "clsi_sk",
        "#kifu": "kifu",
        "#memo": "memo",
        "#first_or_second": "first_or_second",
        "#result": "result",
        "#share": "share",
        "#public": "public",
        "#latest_update": "lastest_update"
      },
      ExpressionAttributeValues={
        ':cl': f"slug#{form.data['slug']}",
        ':ki': form.data["kifu"],
        ':me': form.data["memo"],
        ':fi': form.data["first_or_second"],
        ':re': form.data["result"],
        ':sh': form.data["share"],
        ':pu': form.data["public"],
        ':la': now_str
      }
    )
    if action == "continue":
      context = {
        "type": "edit",
        "form": form,
        "error_message": None,
        "username": username,
        "kid": kid
      }
      return render(master, 'kifu/edit.html', context)
    elif action == "end":
      return redirect(master, "kifu:detail", username=username, kid=kid)
    else:
      raise Exception("Invalid action")
  elif master.request.method == 'GET':
    response = table.get_item(
      Key={
        'pk': f"kifu#uname#{username}",
        'sk': f"kid#{kid}"
      }
    )
    if "Item" not in response:
      return render(master, 'not_found.html')
    else:
      item = response["Item"]
      form = KifuForm(
        slug=item["clsi_sk"].split("#")[1],
        kifu=item["kifu"],
        memo=item["memo"],
        first_or_second=item["first_or_second"],
        result=item["result"],
        share=item["share"],
        public=item["public"]
      )
      context = {
        "type": "edit",
        "form": form,
        "error_message": None,
        "username": username,
        "kid": kid
      }
      return render(master, 'kifu/edit.html', context)





