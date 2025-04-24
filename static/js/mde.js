/* EasyMDEの設定は画像アップロードに関わる部分に絞っています。 */
var _imageMaxSize = 1024 * 1024 * 2;  // 画像サイズは2MBまで
var _imageAccept = ['image/jpeg', 'image/png', 'image/gif', 'image/jpg'];  // JPEG,PNG,GIFを許可

/**
 * EasyMDEの初期化
 * @param elem エディタ対象エレメント(TextArea)
 * @return EasyMDEオブジェクト
 */
function initMDE(elem) {
  var mde = new EasyMDE({
    element: elem,
    uploadImage: true,
    hideIcons: ['image'],
    showIcons: ['upload-image'],
    imageUploadFunction: uploadImage,
    imageMaxSize: _imageMaxSize,
    imageAccept: _imageAccept,
  });
  return mde;
}

function uploadImage(file, onSuccess, onError) {
  // ファイルの検証(サイズ、タイプ)
  if (file.size === 0) {
    onError(constructErrorMessage(400));
    return;
  }
  if (username === '') {
    onError('ログインしてください');
    return;
  }
  if (file.size > _imageMaxSize) {
    onError(constructErrorMessage(413));
    return;
  }
  if (file.type) {
    var file_type = file.type.toLowerCase();
    if (!file_type.startsWith('image/')) {
      onError(constructErrorMessage(415));
      return;
    }
    if (_imageAccept && _imageAccept.length > 0) {
      if (_imageAccept.indexOf(file_type) === -1 && _imageAccept.indexOf('image/*') === -1) {
        onError(constructErrorMessage(415));
        return;
      }
    }
  } else {
    onError(constructErrorMessage(415));
    return;
  }

  // ファイルをBase64に変換して送信
  var reader = new FileReader();
  reader.onload = function(event) {
    var base64String = event.target.result.split(',')[1];
    var payload = JSON.stringify({
      fileName: file.name,
      fileType: file.type,
      data: base64String
    });
    // };
    $.ajax({
      url: '/storage/post/' + username, // 実際のエンドポイントに変更
      type: 'POST',
      contentType: 'application/json',
      data: payload,
    }).done(function(data, textStatus, jqXHR) {
      console.info('data: ' + data);
      // mde.codemirror.replaceSelection(`!`); // カーソル位置に挿入
      onSuccess(data.url);

      // EasyMDE本文に画像のMarkdownリンクを挿入
    }).fail(function(jqXHR, textStatus, errorThrown) {
      console.error('error: ' + jqXHR.status);
      onError(constructErrorMessage(jqXHR.status));
    });
  };
  reader.readAsDataURL(file); // ファイルをBase64エンコード
}
/**
 * エラー時の表示メッセージ生成
 * @param HTTPステータス
 * @return エラーメッセージ
 */
function constructErrorMessage(httpStatus) {
  var fileMsg = 'ファイル名: #image_name#\nファイルサイズ: #image_size#\n送信可能ファイルサイズ: #image_max_size#';
  switch (httpStatus) {
    case 400:	//noFileGiven
      return 'ファイルが指定されていません\n' + fileMsg;
    case 413:	//fileTooLarge
      return 'ファイルが送信可能サイズを超えています\n' + fileMsg;
    case 415:	//typeNotAllowed
      var types = getAllowedFileTypeStr();
      return '許可されないファイル形式です\n' + fileMsg + (types && types.length > 0 ? '\n送信可能ファイル形式: ' + types : '');
    case 500:	//internalServerError
      return 'サーバーで何らかのエラーが発生しました\n' + fileMsg;
    default:
      return '予期せぬエラーが発生しました\n' + fileMsg;
  }
}

/**
 * 許可されているファイル形式を返却
 * @return 許可されているファイル形式(カンマ区切り)
 */
function getAllowedFileTypeStr() {
  var str = '';
  if (_imageAccept && _imageAccept.length > 0) {
    for (var i = 0; i < _imageAccept.length; i++) {
      var sp = _imageAccept[i].split('/');
      str += i > 0 ? ', ' : '';
      str += sp[sp.length - 1];
    }
  }
  return str;
}
