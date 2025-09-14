from wambda.shortcuts import render, redirect
from .forms import TagForm
import boto3
import datetime
from zoneinfo import ZoneInfo
import urllib.parse
from project.common import gen_code
import os

MAIN_TABLE_NAME = os.environ.get('DYNAMODB_TABLE', 'table-sgp-pro-main')
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
        form_data = master.request.get_form_data()
        form = TagForm(form_data)
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
        form_data = master.request.get_form_data()
        form = TagForm(form_data)
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

def detail(master, username, tid):
    table = boto3.resource('dynamodb').Table(MAIN_TABLE_NAME)
    
    # タグ情報を取得
    tag_response = table.get_item(
        Key={
            'pk': f'tag#uname#{username}',
            'sk': f'tid#{tid}'
        }
    )
    
    if 'Item' not in tag_response:
        return render(master, 'not_found.html')
    
    tag_item = tag_response['Item']
    
    # このタグが付与されている棋譜一覧を取得
    kifu_tag_response = table.query(
        IndexName="SwapIndex",
        KeyConditionExpression=boto3.dynamodb.conditions.Key('sk').eq(f'tid#{tid}') & boto3.dynamodb.conditions.Key('pk').begins_with('tag#kid#')
    )
    
    # 棋譜の詳細情報を取得
    kifu_list = []
    for item in kifu_tag_response['Items']:
        kid = item['pk'].split('#')[2]  # tag#kid#{kid} から kid を取得
        
        # 棋譜の詳細を取得
        kifu_response = table.get_item(
            Key={
                'pk': f'kifu#uname#{username}',
                'sk': f'kid#{kid}'
            }
        )
        
        if 'Item' in kifu_response:
            kifu_item = kifu_response['Item']
            kifu_list.append({
                'kid': kid,
                'slug': kifu_item['clsi_sk'].split('#')[1],
                'latest_update': kifu_item['latest_update'],
                'created': kifu_item['created']
            })
    
    # 最終更新日でソート
    kifu_list.sort(key=lambda x: x['latest_update'], reverse=True)
    
    context = {
        'username': username,
        'tid': tid,
        'tag_name': tag_item['tname'],
        'tag_created': tag_item.get('created', ''),
        'tag_latest_update': tag_item.get('latest_update', ''),
        'kifu_list': kifu_list,
        'kifu_count': len(kifu_list)
    }
    
    return render(master, 'tag/detail.html', context)
