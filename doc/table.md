# テーブル設計
本システムではDynamoDBを使用する。
1つのテーブルに全てのデータを格納するため、
Keyの先頭に
「kifu#」や「tag#」をつけることで
データの種類を区別する。
<table border="1">
  <thead>
    <tr>
      <th colspan="4">列種別</th>
      <th>Partition Key</th>
      <th>Sort Key</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
    <tr>
      <th colspan="4">列名</th>
      <th>pk</th>
      <th>sk</th>
      <th>cgsi_pk</th>
      <th>clsi_sk</th>
      <th>kifu</th>
      <th>first_or_second</th>
      <th>result</th>
      <th>memo</th>
      <th>public</th>
      <th>share</th>
      <th>created</th>
      <th>latest_access</th>
      <th>latest_update</th>
      <th>kifu_max</th>
      <th>tag_max</th>
      <th>status</th>
      <th>response</th>
      <th>expired</th>
    </tr>
    <tr>
      <th>IndexType</th>
      <th>IndexName</th>
      <th>ProjectionType</th>
      <th>IndexDescription\DataType</th>
      <th>文字列</th>
      <th>文字列</th>
      <th>文字列</th>
      <th>文字列</th>
      <th>文字列</th>
      <th>文字列</th>
      <th>文字列</th>
      <th>文字列</th>
      <th>真偽</th>
      <th>真偽</th>
      <th>文字列</th>
      <th>文字列</th>
      <th>文字列</th>
      <th>数値</th>
      <th>数値</th>
      <th>文字列</th>
      <th>文字列</th>
      <th>数値</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>GSI</td>
      <td>SwapIndex</td>
      <td>all</td>
      <td>IDからの取得及び重複チェック要。pkの開始文字列指定のためskが必要。</td>
      <td>Sort Key</td>
      <td>Partition Key</td>
      <td>all</td>
      <td>all</td>
      <td>all</td>
      <td>all</td>
      <td>all</td>
      <td>all</td>
      <td>all</td>
      <td>all</td>
      <td>all</td>
      <td>all</td>
      <td>all</td>
      <td>all</td>
      <td>all</td>
      <td>all</td>
      <td>all</td>
      <td>all</td>
    </tr>
    <tr>
      <td>GSI</td>
      <td>CommonGSI</td>
      <td>all</td>
      <td>シェアコードからの取得とタグ-タグ名ペアの重複チェック。</td>
      <td>primary</td>
      <td>primary</td>
      <td>Partition Key</td>
      <td>all</td>
      <td>all</td>
      <td>all</td>
      <td>all</td>
      <td>all</td>
      <td>all</td>
      <td>all</td>
      <td>all</td>
      <td>all</td>
      <td>all</td>
      <td>all</td>
      <td>all</td>
      <td>all</td>
      <td>all</td>
      <td>all</td>
    </tr>
    <tr>
      <td>LSI</td>
      <td>CommonLSI</td>
      <td>include</td>
      <td>Slugからの取得及び重複チェック、それとタグ-タグ名ペアの重複チェック用。</td>
      <td>Partition Key</td>
      <td>primary</td>
      <td></td>
      <td>Sort Key</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <td>LSI</td>
      <td>CreatedIndex</td>
      <td>include</td>
      <td>棋譜とタグの作成日でのソート用</td>
      <td>Partition Key</td>
      <td>primary</td>
      <td>include</td>
      <td>include</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td>include</td>
      <td>Sord Key</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <td>LSI</td>
      <td>LatestAccessIndex</td>
      <td>include</td>
      <td>棋譜とタグの最終アクセス日でのソート用</td>
      <td>Partition Key</td>
      <td>primary</td>
      <td>include</td>
      <td>include</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td>include</td>
      <td></td>
      <td>Sort Key</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <td>LSI</td>
      <td>LatestUpdateIndex</td>
      <td>include</td>
      <td>棋譜とタグの最終更新日でのソート用</td>
      <td>Partition Key</td>
      <td>primary</td>
      <td>include</td>
      <td>include</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td>include</td>
      <td></td>
      <td></td>
      <td>Sort Key</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <td>ExampleNumber</td>
      <td colspan="3">ExampleDescription</td>
      <td colspan="18">ExampleValue</td>
    </tr>
    <tr>
      <td>例1</td>
      <td colspan="3">棋譜。一番多くなる。棋譜の数が多くなると一つのPartitionに偏るので、将来的にPartitionを分割することを検討する</td>
      <td>kifu#uname#h-akira</td>
      <td>kid#fdsaj9d9s0</td>
      <td>kifu#scode#lkihofkwif4tF</td>
      <td>slug#社団戦/2025/鈴木</td>
      <td>略</td>
      <td>firtst</td>
      <td>sennichite</td>
      <td>あああいいいううう</td>
      <td>TRUE</td>
      <td>TRUE</td>
      <td>2025-12-31 11:11:31</td>
      <td>2025-12-31 11:11:31</td>
      <td>2025-12-31 11:11:31</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <td>例2</td>
      <td colspan="3">ユーザーの設定。全ユーザーが一つのPartitionに偏るとユーザー数増加時に性能が落ちるため、将来的にPartitionを分割することを検討する</td>
      <td>users</td>
      <td>uname#h-akira</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <td>例3</td>
      <td colspan="3">システムの設定用。現時点で用途未確定。</td>
      <td>system</td>
      <td>none</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td>3000</td>
      <td>50</td>
      <td></td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <td>例5</td>
      <td colspan="3">タグの保持者、id、名前の組</td>
      <td>tag#uname#h-akira</td>
      <td>tid#jko2kdl</td>
      <td></td>
      <td>tname#四間飛車</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td>2025-12-31 11:11:31</td>
      <td>2025-12-31 11:11:31</td>
      <td>2025-12-31 11:11:31</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <td>例6</td>
      <td colspan="3">棋譜につけるタグ。棋譜からの検索とタグ名からの検索とユーザーネームからの検索の3つに対応する。</td>
      <td>tag#kid#fdsaj9d9s1</td>
      <td>tid#jko2kdl</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <td>例7</td>
      <td colspan="3">特定の棋譜へのアクセスを許可されたユーザー</td>
      <td>kallowed#kid#fdsaj9d9s1</td>
      <td>uname#h-akira2</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <td>例8</td>
      <td colspan="3">全ての棋譜へのアクセスを許可されたユーザー</td>
      <td>uallowed#uname#h-akira</td>
      <td>uname#h-akira2</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <td>例9</td>
      <td colspan="3">解析結果・制限</td>
      <td>analysis</td>
      <td>aid#fdjsklfadf</td>
      <td>analysis#uname#h-akira</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td>2025-12-31 11:11:31</td>
      <td></td>
      <td></td>
      <td></td>
      <td></td>
      <td>waiting/successed/error</td>
      <td>略</td>
      <td>1234567890</td>
    </tr>
    <tr>
      <td colspan="4">（列幅調整用）</td>
      <td>____________________________</td>
      <td>____________________________</td>
      <td>____________________________</td>
      <td>____________________________</td>
      <td>__________________</td>
      <td>__________________</td>
      <td>__________________</td>
      <td>__________________</td>
      <td>__________________</td>
      <td>__________________</td>
      <td>__________________</td>
      <td>__________________</td>
      <td>__________________</td>
      <td>__________________</td>
      <td>__________________</td>
      <td>__________________</td>
      <td>__________________</td>
      <td>__________________</td>
    </tr>
  </tbody>
</table>
