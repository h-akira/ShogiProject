from hads.shortcuts import render, redirect
from hads.authenticate import login, signup, verify
from .forms import LoginForm, SignupForm, VerifyForm

def login_view(master):
    if master.request.method == 'POST':
        form = LoginForm(master.request.get_form_data())
    else:
        form = LoginForm()
    
    if master.request.method == 'POST' and form.validate():
        username = form.username.data
        password = form.password.data
        if login(master, username, password):
            return redirect(master, 'home')
        else:
            context = {'form': form, 'error': 'ログインに失敗しました'}
            return render(master, 'accounts/login.html', context)
    
    return render(master, 'accounts/login.html', {'form': form})

def signup_view(master):
    if master.request.method == 'POST':
        form = SignupForm(master.request.get_form_data())
    else:
        form = SignupForm()
    
    if master.request.method == 'POST' and form.validate():
        username = form.username.data
        email = form.email.data
        password = form.password.data
        if signup(master, username, email, password):
            # サインアップ成功後は/accounts/verifyにリダイレクトし、ユーザー名をクエリパラメータで渡す
            from hads.shortcuts import reverse
            verify_url = reverse(master, 'accounts:verify') + f'?username={username}&message=signup_success'
            return {
                'statusCode': 302,
                'headers': {
                    'Location': verify_url
                }
            }
        else:
            context = {'form': form, 'error': 'サインアップに失敗しました'}
            return render(master, 'accounts/signup.html', context)
    
    return render(master, 'accounts/signup.html', {'form': form})

def verify_view(master):
    if master.request.method == 'POST':
        form = VerifyForm(master.request.get_form_data())
    else:
        form = VerifyForm()
    
    context = {'form': form}
    
    # URLパラメータからユーザー名とメッセージを取得
    if master.request.method == 'GET':
        query_params = master.event.get('queryStringParameters') or {}
        username = query_params.get('username', '')
        message_type = query_params.get('message', '')
        
        if username:
            form.username.data = username
        
        # メッセージ設定
        if message_type == 'signup_success':
            context['message'] = 'サインアップが完了しました。確認コードをメールで送信しました。'
    
    if master.request.method == 'POST' and form.validate():
        username = form.username.data
        code = form.code.data
        if verify(master, username, code):
            login_form = LoginForm()
            login_context = {
                'form': login_form,
                'message': 'メールアドレスの確認が完了しました'
            }
            return render(master, 'accounts/login.html', login_context)
        else:
            context['error'] = '確認に失敗しました'
            return render(master, 'accounts/verify.html', context)
    
    return render(master, 'accounts/verify.html', context)

def logout_view(master):
    from hads.authenticate import sign_out
    
    try:
        sign_out(master)  # 認証情報クリア + Cookie削除フラグ設定
        master.logger.info("sign_out completed successfully")
    except Exception as e:
        master.logger.warning(f"Logout warning: {e}")
        # 例外が発生した場合も強制的にCookie削除
        master.request.auth = False
        master.request.username = None
        master.request.clean_cookie = True
        master.logger.info("Forced cleanup after exception")
    
    # リダイレクト先URLをログ出力
    from hads.shortcuts import reverse
    home_url = reverse(master, 'home')
    master.logger.info(f"Redirecting to home URL: {home_url}")
    
    redirect_response = redirect(master, 'home')
    master.logger.info(f"Redirect response: {redirect_response}")
    
    return redirect_response