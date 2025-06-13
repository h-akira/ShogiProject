from hads.shortcuts import render, redirect
from .forms import TagForm
import boto3
import datetime
from zoneinfo import ZoneInfo
import urllib.parse
from project.common import gen_code

MAIN_TABLE_NAME = "table-sgp-main"
TID_LENGTH = 8

def index(master, username):
    table = boto3.resource('dynamodb').Table(MAIN_TABLE_NAME)
    # 自分のタグ一覧を取得
    response = table.query(
        KeyConditionExpression=boto3.dynamodb.conditions.Key('pk').eq(f'tag#uname#{username}')
    )
    tags = [{'tname': item['tname'], 'tid': item['sk'].split('#')[1]} for item in response['Items']]
    context = {
        'username': username,
        'tags': tags
    }
    return render(master, 'tag/index.html', context)

def create(master, username):
    table = boto3.resource('dynamodb').Table(MAIN_TABLE_NAME)
    if master.request.method == 'POST':
        form = TagForm(**master.request.body)
        if not form.validate():
            return render(master, 'tag/create.html', {'form': form, 'error_message': 'タグ名を入力してください', 'username': username})
        tag_name = form.data['slug'].strip()
        now = datetime.datetime.now(ZoneInfo(master.settings.TIMEZONE)).strftime("%Y-%m-%d %H:%M:%S")
        tid = gen_code(8)
        table.put_item(Item={
            'pk': f'tag#uname#{username}',
            'sk': f'tid#{tid}',
            'clsi_sk': f'tname#{tag_name}',
            'tname': tag_name,
            'created': now,
            'latest_update': now
        })
        return redirect(master, 'tag:index', username=username)
    else:
        form = TagForm()
        return render(master, 'tag/create.html', {'form': form, 'username': username})

def edit(master, username, tid):
    table = boto3.resource('dynamodb').Table(MAIN_TABLE_NAME)
    # tidで既存タグを取得
    response = table.get_item(
        Key={
            'pk': f'tag#uname#{username}',
            'sk': f'tid#{tid}'
        }
    )
    tag_item = response.get('Item')
    tag_name = tag_item['tname'] if tag_item else ''
    if master.request.method == 'POST':
        form = TagForm(**master.request.body)
        if not form.validate():
            return render(master, 'tag/edit.html', {'form': form, 'error_message': 'タグ名を入力してください', 'username': username, 'tid': tid})
        new_tag_name = form.data['slug'].strip()
        now = datetime.datetime.now(ZoneInfo(master.settings.TIMEZONE)).strftime("%Y-%m-%d %H:%M:%S")
        # clsi_skとtnameを更新
        if tag_item:
            table.update_item(
                Key={'pk': tag_item['pk'], 'sk': tag_item['sk']},
                UpdateExpression="set clsi_sk=:clsi, tname=:tname, latest_update=:lu",
                ExpressionAttributeValues={
                    ':clsi': f'tname#{new_tag_name}',
                    ':tname': new_tag_name,
                    ':lu': now
                }
            )
        return redirect(master, 'tag:index', username=username)
    else:
        # GET: 既存タグ名をフォームにセット
        form = TagForm(slug=tag_name)
        return render(master, 'tag/edit.html', {'form': form, 'username': username, 'tid': tid})

def delete(master, username, tid):
    table = boto3.resource('dynamodb').Table(MAIN_TABLE_NAME)
    
    # まず、このタグが棋譜に付与されているかチェック
    kifu_tag_response = table.query(
        IndexName="SwapIndex",
        KeyConditionExpression=boto3.dynamodb.conditions.Key('sk').eq(f'tid#{tid}') & boto3.dynamodb.conditions.Key('pk').begins_with('tag#kid#')
    )
    
    if kifu_tag_response['Count'] > 0:
        # タグが棋譜に付与されている場合は、それらも削除
        for item in kifu_tag_response['Items']:
            table.delete_item(
                Key={
                    'pk': item['pk'],
                    'sk': item['sk']
                }
            )
    
    # タグ本体を削除
    table.delete_item(
        Key={
            'pk': f'tag#uname#{username}',
            'sk': f'tid#{tid}'
        }
    )
    
    return redirect(master, 'tag:index', username=username)
