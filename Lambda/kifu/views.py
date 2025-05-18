from hads.shourtcuts import render
from hads.shourtcuts import login_required, redirect
from .forms import KifuForm
import boto3
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key
import datetime
from zoneinfo import ZoneInfo
from project.common import gen_code, encode_for_url, decode_from_url
import os

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
  if len(slug) > 4 and slug[-4:] == ".kif":
    return "'.kif' will be added automatically."
  return None

def _check_slug_exists(master, table, username, slug, allow_one=False):
  try:
    response = table.query(
      IndexName="CommonLSI",
      KeyConditionExpression=Key('pk').eq(f"kifu#uname#{username}") & Key('clsi_sk').eq(f"slug#{slug}")
    )
  except ClientError as e:
    raise e
  print(response)
  if response["Count"] > 1:
    master.logger.error(f"Multiple items found with the same slug: {slug}")
    return True
  elif response["Count"] == 1:
    if allow_one:
      return False
    else:
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
      'type' : "normal",
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

def share(master, share_code):
  table = boto3.resource('dynamodb').Table(MAIN_TABLE_NAME)
  response = table.query(
    IndexName="CommonGSI",
    KeyConditionExpression=Key('cgsi_pk').eq(f"scode#{share_code}")
  )
  if response["Count"] == 0:
    return render(master, 'not_found.html')
  elif response["Count"] > 1:
    return render(master, 'not_found.html')
  else:
    item = response["Items"][0]
    if not item["share"]:
      return render(master, 'not_found.html')
    context = {
      # 'username': item["pk"].split("#")[2],
      # 'kid': item["sk"].split("#")[1],
      # 'slug': item["clsi_sk"].split("#")[1],
      'type': "share",
      'share_code': item["cgsi_pk"].split("#")[1],
      'kifu': item["kifu"],
      'memo': item["memo"],
      'first_or_second': item["first_or_second"],
      'result': item["result"],
      'share': item["share"],
      'public': item["public"],
      'created': item["created"],
      'latest_update': item["latest_update"]
    }
    return render(master, 'kifu/detail.html', context)

@login_required
def explorer(master, username, slug_base64=None):
  if username != master.request.username:
    return render(master, 'not_found.html')
  table = boto3.resource('dynamodb').Table(MAIN_TABLE_NAME)
  init = "slug#"
  done_slug_list = []
  if slug_base64 is not None:
    init += decode_from_url(slug_base64)
    if init[-1] != "/":
      init += "/"
    done_slug_list = init[5:].split("/")
    if done_slug_list[-1] == "":
      done_slug_list.pop(-1)
  parent_folders_fullpath_base64 = []
  parent_folders_fullpath = ""
  for v in done_slug_list:
    parent_folders_fullpath = os.path.join(parent_folders_fullpath, v)
    parent_folders_fullpath_base64.append(encode_for_url(parent_folders_fullpath))
  parent_folders = [
    {
      "name": folder,
      "fullpath_base64": fullpath_base64
    } for folder, fullpath_base64 in zip(
      done_slug_list,
      parent_folders_fullpath_base64
    )
  ]
  rows_file = []
  folders = []
  folders_counter_dic = {}
  response = table.query(
    IndexName="CommonLSI",
    KeyConditionExpression=Key('pk').eq(f"kifu#uname#{username}") & Key('clsi_sk').begins_with(init)
  )
  for item in response["Items"]:
    remaining_slug = item["clsi_sk"][len(init):]
    if remaining_slug == "":
      continue
    remaining_slug_list = remaining_slug.split("/")
    if len(remaining_slug_list) == 1:
      rows_file.append(
        {
          "name": remaining_slug_list[0],
          "kid": item["sk"].split("#")[1],
        }
      )
    else:
      if remaining_slug_list[0] in folders:
        folders_counter_dic[remaining_slug_list[0]] += 1
      else:
        folders.append(remaining_slug_list[0])
        folders_counter_dic[remaining_slug_list[0]] = 1
  rows_folder = [
    {
      "name": folder,
      "counter": folders_counter_dic[folder],
      "fullpath_base64": encode_for_url(os.path.join(init[5:], folder))
    } for folder in folders
  ]
  context = {
    "username": username,
    "rows_file": rows_file,
    "rows_folder": rows_folder,
    "parent_folders": parent_folders
    # "folders": folders,
    # "floders_dic": floders_dic,
    # "base64_fullpath_folders": [
    #   encode_for_url(os.path.join(init[5:], f))  for f in folders
    # ],
    # "files": files,
    # "kids": kids
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
    if _check_slug_exists(master, table, username, form.data['slug']+".kif"):
      context = {
        "type": "create",
        "form": form,
        "error_message": "Slug already exists"
      }
      return render(master, 'kifu/edit.html', context)
    kid = gen_code(KID_LENGTH)
    share_code = gen_code(SHARE_CODE_LENGTH)
    Item = {
      "pk": f"kifu#uname#{username}",
      "sk": f"kid#{kid}",
      "cgsi_pk": f"scode#{share_code}",
      "clsi_sk": f"slug#{form.data['slug']}"+".kif",
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
    error_message = _slug_format_checker_return_error_message(form.data['slug'])
    if error_message is not None:
      context = {
        "type": "edit",
        "form": form,
        "error_message": error_message,
        "username": username,
        "kid": kid
      }
      return render(master, 'kifu/edit.html', context)
    if _check_slug_exists(master, table, username, form.data['slug']+".kif", allow_one=True):
      context = {
        "type": "edit",
        "form": form,
        "error_message": "Slug already exists",
        "username": username,
        "kid": kid
      }
      return render(master, 'kifu/edit.html', context)
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
        ':cl': f"slug#{form.data['slug']}"+".kif",
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
        slug=item["clsi_sk"].split("#")[1][:-4],
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





