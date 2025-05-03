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

@login_required
def index(master, username):
  context = {
    'username': username
  }
  return render(master, 'kifu/index.html', context)

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
      return render(master, 'kifu/create.html', context)
    error_message = _slug_format_checker_return_error_message(form.data['slug'])
    if error_message is not None:
      context = {
        "type": "create",
        "form": form,
        "error_message": error_message
      }
      return render(master, 'kifu/create.html', context)
    if _check_slug_exists(table, username, form.data['slug']):
      context = {
        "type": "create",
        "form": form,
        "error_message": "Slug already exists"
      }
      return render(master, 'kifu/create.html', context)
    Item = {
      "pk": f"kifu#uname#{username}",
      "sk": f"kid#{_gen_code(KID_LENGTH)}",
      "cgsi_pk": f"scode#{_gen_code(SHARE_CODE_LENGTH)}",
      "clsi_sk": f"slug#{form.data['slug']}",
      "public": form.data['public'],
      "share": form.data['share'],
      "kifu": form.data['kifu'],
      "memo": form.data['memo'],
      "first_or_second": form.data['first_or_second'],
      "result": form.data['result']
    }
    # Item["last_updated"] = datetime.datetime.now(ZoneInfo("Asia/Tokyo")).strftime("%Y-%m-%d %H:%M:%S")
    table = boto3.resource('dynamodb').Table(MAIN_TABLE_NAME)



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
        return render(master, 'kifu/create.html', context)
      elif action == "end":
        kid = Item["sk"].split("#")[1]
        # 暫定
        return redirect(master, "kifu:index", username=username)
      else:
        raise Exception("Invalid action")
    except ClientError as e:
      if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
        error_message = "Item with the same partition key and sort key already exists."
      else:
        import traceback
        error_message = traceback.format_exc()
      # form = PageForm(data=Item)
      context = {
        "type": "create",
        "form": form,
        "error_message": error_message
      }
      return render(request, 'kifu/create.html', context)
  elif master.request.method == 'GET':
    form = KifuForm()
    context = {
      "type": "create",
      "form": form,
      "error_message": None
    }
    return render(master, 'kifu/create.html', context)
  else:
    raise Exception('Invalid request method')
