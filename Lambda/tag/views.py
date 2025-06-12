from hads.shortcuts import render, redirect
from .forms import TagForm
import boto3
import datetime
from zoneinfo import ZoneInfo

MAIN_TABLE_NAME = "table-sgp-main"
TID_LENGTH = 8

def index(master, username):
    context = {
        'username': username
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
        tid = tag_name  # タグ名をtidとして使う（重複管理は省略）
        table.put_item(Item={
            'pk': f'tag#uname#{username}',
            'sk': f'tname#{tag_name}',
            'tname': tag_name,
            'created': now,
            'latest_update': now
        })
        return redirect(master, 'tag:index', username=username)
    else:
        form = TagForm()
        return render(master, 'tag/create.html', {'form': form, 'username': username})
