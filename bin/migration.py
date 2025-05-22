#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Created: 2025-05-22 20:50:03

import sys
import os
import glob
import boto3
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key
import datetime
from zoneinfo import ZoneInfo
import chardet
sys.path.append(
  os.path.join(
    os.path.dirname(
      os.path.abspath(__file__)
    ),
    "../Lambda"
  )
)
from project.common import gen_code

MAIN_TABLE_NAME = "table-sgp-main"
KID_LENGTH = 12
SHARE_CODE_LENGTH = 36

def parse_args():
  import argparse
  parser = argparse.ArgumentParser(description="""\

""", formatter_class = argparse.ArgumentDefaultsHelpFormatter)
  parser.add_argument("--version", action="version", version='%(prog)s 0.0.1')
  parser.add_argument("-p", "--profile", metavar="profile", help="output file")
  parser.add_argument("-r", "--region", metavar="region", default="ap-northeast-1", help="AWS region")
  parser.add_argument("-o", "--output", metavar="output-file", default="999_旧DropBox", help="output file")
  parser.add_argument("-u", "--username", metavar="username", required=True, help="username")
  parser.add_argument("-t", "--timezone", metavar="timezone", default="Asia/Tokyo", help="timezone")
  parser.add_argument("root", metavar="input-root", help="root of the input files")
  options = parser.parse_args()
  return options

def _check_slug_exists(table, username, slug):
  try:
    response = table.query(
      IndexName="CommonLSI",
      KeyConditionExpression=Key('pk').eq(f"kifu#uname#{username}") & Key('clsi_sk').eq(f"slug#{slug}")
    )
  except ClientError as e:
    raise e
  if response["Count"] >= 1:
    return True
  else:
    return False

def main():
  options = parse_args()
  if options.profile is None:
    session = boto3.Session()
  else:
    session = boto3.Session(profile_name=options.profile)
  table = session.resource('dynamodb', region_name=options.region).Table(MAIN_TABLE_NAME)
  # root以下のファイルを再起的に取得
  files = glob.glob(os.path.join(options.root, "**", "*.kif"), recursive=True)
  for i, file in enumerate(files):
    if i <= 10:
      continue
    # rootからの相対パスを取得
    relpath = os.path.relpath(file, options.root)
    slug = os.path.join(options.output, relpath)
    # print(relpath)
    kid = gen_code(KID_LENGTH)
    share_code = gen_code(SHARE_CODE_LENGTH)
    now = datetime.datetime.now(ZoneInfo(options.timezone))
    now_str = now.strftime("%Y-%m-%d %H:%M:%S")
    try:
      with open(file, "r", encoding="utf-8") as f:
        kifu = f.read()
      print(f"Detected encoding: utf-8")
    except UnicodeDecodeError:
      try:
        with open(file, "r", encoding="shift-jis") as f:
          kifu = f.read()
        # print(f"Detected encoding: shift-jis")
      except UnicodeDecodeError:
        try:
          with open(file, "r", encoding="euc-jp") as f:
            kifu = f.read()
          print(f"Detected encoding: euc-jp")
        except UnicodeDecodeError:
          try:
            with open(file, "r", encoding="iso-2022-jp") as f:
              kifu = f.read()
            print(f"Detected encoding: iso-2022-jp")
          except UnicodeDecodeError:
            print(f"Error: Failed to decode {file} with utf-8, shift-jis, euc-jp, iso-2022-jp")
            continue
    Item = {
      "pk": f"kifu#uname#{options.username}",
      "sk": f"kid#{kid}",
      "cgsi_pk": f"scode#{share_code}",
      "clsi_sk": f"slug#{slug}",
      "public": False,
      "share": False,
      "kifu": kifu,
      "memo": None,
      "first_or_second": None,
      "result": None,
      "created": now_str,
      "latest_update": now_str
    }
    if _check_slug_exists(table, options.username, slug):
      print(f"Error: slug already exists: {slug}")
      continue
    try:
      response = table.put_item(
        Item=Item
      )
    except Exception as e:
      import traceback
      print(f"Error writing {file}: {e}")
      traceback.print_exc()
      continue

if __name__ == '__main__':
  main()
