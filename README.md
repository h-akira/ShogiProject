# ShogiProject
## 概要
将棋の棋譜の管理を管理するシステムです。
AIによる局面の解析機能も有しています。
このシステムは本リポジトリと
[ShogiProject_Analysis](https://github.com/h-akira/ShogiProject_Analysis)
の2つのリポジトリからなります。
また、Webアプリケーションフレームワークとして
[wambda](https://github.com/h-akira/wambda)
を使用しています。

## 構成
本システムはAWS上に構築され、構成図は下記の通りです。  
![structure](images/structure.png)  
赤枠と青枠に囲まれた部分はそれぞれのリポジトリに対応しており、SAMで展開されます。
それ以外の部分は別途構築します。

## 機能
- 棋譜登録
- 棋譜閲覧
- 棋譜編集
- 棋譜削除
- URLによる棋譜共有
- エクスプローラー
- AIによる局面解析
- 盤面からの棋譜入力（comming soon...）
- タグ（comming soon...）
- 棋譜公開（検討中）
- 棋譜閲覧権限設定（検討中）
- 局面検索（検討中）
- 将棋ウォーズ棋譜自動収集（検討中）
- 盤面からの棋譜編集（検討中）
