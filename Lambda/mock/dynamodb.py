import boto3
import os

def set_data():
    """DynamoDBのモックデータを設定"""
    dynamodb = boto3.resource('dynamodb', region_name='ap-northeast-1')
    table_name = os.environ.get('DYNAMODB_TABLE', 'table-sgp-pro-main')

    # テーブル作成（存在しない場合のみ）
    try:
        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {'AttributeName': 'pk', 'KeyType': 'HASH'},
                {'AttributeName': 'sk', 'KeyType': 'RANGE'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'pk', 'AttributeType': 'S'},
                {'AttributeName': 'sk', 'AttributeType': 'S'},
                {'AttributeName': 'cgsi_pk', 'AttributeType': 'S'},
                {'AttributeName': 'clsi_sk', 'AttributeType': 'S'},
                {'AttributeName': 'created', 'AttributeType': 'S'},
                {'AttributeName': 'latest_access', 'AttributeType': 'S'},
                {'AttributeName': 'latest_update', 'AttributeType': 'S'}
            ],
            LocalSecondaryIndexes=[
                {
                    'IndexName': 'CreatedIndex',
                    'KeySchema': [
                        {'AttributeName': 'pk', 'KeyType': 'HASH'},
                        {'AttributeName': 'created', 'KeyType': 'RANGE'}
                    ],
                    'Projection': {
                        'ProjectionType': 'INCLUDE',
                        'NonKeyAttributes': ['clsi_sk', 'public', 'cgsi_pk']
                    }
                },
                {
                    'IndexName': 'CommonLSI',
                    'KeySchema': [
                        {'AttributeName': 'pk', 'KeyType': 'HASH'},
                        {'AttributeName': 'clsi_sk', 'KeyType': 'RANGE'}
                    ],
                    'Projection': {'ProjectionType': 'ALL'}
                },
                {
                    'IndexName': 'LatestAccessIndex',
                    'KeySchema': [
                        {'AttributeName': 'pk', 'KeyType': 'HASH'},
                        {'AttributeName': 'latest_access', 'KeyType': 'RANGE'}
                    ],
                    'Projection': {
                        'ProjectionType': 'INCLUDE',
                        'NonKeyAttributes': ['clsi_sk', 'public', 'cgsi_pk']
                    }
                },
                {
                    'IndexName': 'LatestUpdateIndex',
                    'KeySchema': [
                        {'AttributeName': 'pk', 'KeyType': 'HASH'},
                        {'AttributeName': 'latest_update', 'KeyType': 'RANGE'}
                    ],
                    'Projection': {
                        'ProjectionType': 'INCLUDE',
                        'NonKeyAttributes': ['clsi_sk', 'public', 'cgsi_pk']
                    }
                }
            ],
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'CommonGSI',
                    'KeySchema': [
                        {'AttributeName': 'cgsi_pk', 'KeyType': 'HASH'}
                    ],
                    'Projection': {'ProjectionType': 'ALL'}
                },
                {
                    'IndexName': 'SwapIndex',
                    'KeySchema': [
                        {'AttributeName': 'sk', 'KeyType': 'HASH'},
                        {'AttributeName': 'pk', 'KeyType': 'RANGE'}
                    ],
                    'Projection': {'ProjectionType': 'ALL'}
                }
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        table.wait_until_exists()
        print(f"Created table: {table_name}")
    except Exception as e:
        print(f"DynamoDB table creation error (may already exist): {e}")
        table = dynamodb.Table(table_name)

    # サンプルデータ投入
    items = [
        # システム設定
        {
            'pk': 'system',
            'sk': 'none',
            'kifu_max': 100,
            'tag_max': 50,
            'clsi_sk': 'system',
            'cgsi_pk': 'system',
            'created': '2023-12-01 00:00:00',
            'latest_update': '2023-12-01 00:00:00'
        },
        # サンプルユーザーの棋譜
        {
            'pk': 'kifu#uname#testuser',
            'sk': 'kid#testkifu001',
            'title': 'テスト棋譜1',
            'kifu': '手合割：平手\n先手：testuser\n後手：opponent\n手数----指手---------消費時間--\n   1 ７六歩(77)   (00:00/00:00:00)\n   2 ３四歩(33)   (00:00/00:00:00)\n   3 ２六歩(27)   (00:00/00:00:00)\n   4 ８四歩(83)   (00:00/00:00:00)\n   5 ２五歩(26)   (00:00/00:00:00)\n   6 ８五歩(84)   (00:00/00:00:00)\n   7 ７八金(69)   (00:00/00:00:00)\n   8 ３二金(41)   (00:00/00:00:00)\nまで8手で中断',
            'created': '2023-12-01 00:00:00',
            'latest_update': '2023-12-01 00:00:00',
            'clsi_sk': 'slug#テスト棋譜1',
            'cgsi_pk': 'scode#sharetest001',
            'share': False,
            'public': False,
            'memo': None,
            'result': None,
            'first_or_second': None
        },
        {
            'pk': 'kifu#uname#testuser',
            'sk': 'kid#testkifu002',
            'title': 'テスト棋譜2',
            'kifu': '手合割：平手\n先手：testuser\n後手：opponent2\n手数----指手---------消費時間--\n   1 ２六歩(27)   (00:00/00:00:00)\n   2 ８四歩(83)   (00:00/00:00:00)\n   3 ２五歩(26)   (00:00/00:00:00)\n   4 ８五歩(84)   (00:00/00:00:00)\n   5 ７八金(69)   (00:00/00:00:00)\n   6 ３二金(41)   (00:00/00:00:00)\nまで6手で中断',
            'created': '2023-12-02 00:00:00',
            'latest_update': '2023-12-02 00:00:00',
            'clsi_sk': 'slug#テスト棋譜2',
            'cgsi_pk': 'scode#sharetest002',
            'share': False,
            'public': False,
            'memo': None,
            'result': None,
            'first_or_second': None
        },
        # サンプルタグ
        {
            'pk': 'tag#uname#testuser',
            'sk': 'tid#testtag001',
            'tname': '初心者向け',
            'created': '2023-12-01 00:00:00',
            'latest_update': '2023-12-01 00:00:00',
            'clsi_sk': 'tname#初心者向け',
            'cgsi_pk': 'tag#uname#testuser#tid#testtag001'
        },
        {
            'pk': 'tag#uname#testuser', 
            'sk': 'tid#testtag002',
            'tname': '定跡',
            'created': '2023-12-01 00:00:00',
            'latest_update': '2023-12-01 00:00:00',
            'clsi_sk': 'tname#定跡',
            'cgsi_pk': 'tag#uname#testuser#tid#testtag002'
        },
        {
            'pk': 'tag#uname#testuser',
            'sk': 'tid#testtag003',
            'tname': '将棋ウォーズ',
            'created': '2023-12-01 00:00:00',
            'latest_update': '2023-12-01 00:00:00',
            'clsi_sk': 'tname#将棋ウォーズ',
            'cgsi_pk': 'tag#uname#testuser#tid#testtag003'
        },
        # タグと棋譜の関連付け
        {
            'pk': 'tag#kid#testkifu001',
            'sk': 'tid#testtag001',
            'tname': '初心者向け',
            'clsi_sk': 'tag#kid#testkifu001',
            'cgsi_pk': 'tag#kid#testkifu001#tid#testtag001',
            'latest_update': '2023-12-01 00:00:00'
        },
        {
            'pk': 'tag#kid#testkifu002',
            'sk': 'tid#testtag002',
            'tname': '定跡',
            'clsi_sk': 'tag#kid#testkifu002',
            'cgsi_pk': 'tag#kid#testkifu002#tid#testtag002',
            'latest_update': '2023-12-02 00:00:00'
        },
        # 共有用の棋譜データ
        {
            'pk': 'share#sharetest001',
            'sk': 'data',
            'kifu_id': 'testkifu001',
            'username': 'testuser',
            'title': 'テスト棋譜1',
            'clsi_sk': 'share#sharetest001',
            'cgsi_pk': 'share#sharetest001',
            'created': '2023-12-01 00:00:00',
            'latest_update': '2023-12-01 00:00:00'
        },
        {
            'pk': 'share#sharetest002',
            'sk': 'data',
            'kifu_id': 'testkifu002',
            'username': 'testuser',
            'title': 'テスト棋譜2',
            'clsi_sk': 'share#sharetest002',
            'cgsi_pk': 'share#sharetest002',
            'created': '2023-12-02 00:00:00',
            'latest_update': '2023-12-02 00:00:00'
        }
    ]
    
    for item in items:
        table.put_item(Item=item)
    print(f"Inserted {len(items)} items into {table_name}")