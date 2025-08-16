from hads.shortcuts import render, redirect
from hads.authenticate import login, signup, verify, MaintenanceOptionError
from .forms import LoginForm, SignupForm, VerifyForm

def login_view(master):
    if master.request.method == 'POST':
        form = LoginForm(master.request.get_form_data())
    else:
        form = LoginForm()
    
    context = {'form': form}
    
    # URLパラメータからメッセージを取得
    if master.request.method == 'GET':
        query_params = master.event.get('queryStringParameters') or {}
        message_type = query_params.get('message', '')
        
        # メッセージ設定
        if message_type == 'verify_success':
            context['message'] = 'メールアドレスの確認が完了しました'
    
    if master.request.method == 'POST' and form.validate():
        username = form.username.data
        password = form.password.data
        try:
            if login(master, username, password):
                return redirect(master, 'home')
            else:
                context['error'] = 'ログインに失敗しました'
                return render(master, 'accounts/login.html', context)
        except MaintenanceOptionError as e:
            context['error'] = str(e)
            return render(master, 'accounts/login.html', context)
    
    return render(master, 'accounts/login.html', context)

def signup_view(master):
    if master.request.method == 'POST':
        form = SignupForm(master.request.get_form_data())
    else:
        form = SignupForm()
    
    if master.request.method == 'POST' and form.validate():
        username = form.username.data
        email = form.email.data
        password = form.password.data
        try:
            if signup(master, username, email, password):
                # サインアップ成功後は/accounts/verifyにリダイレクトし、ユーザー名をクエリパラメータで渡す
                return redirect(master, 'accounts:verify', query_params={
                    'username': username,
                    'message': 'signup_success'
                })
            else:
                context = {'form': form, 'error': 'サインアップに失敗しました'}
                return render(master, 'accounts/signup.html', context)
        except MaintenanceOptionError as e:
            context = {'form': form, 'error': str(e)}
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
            # verify成功後は/accounts/loginにリダイレクトしてメッセージを表示
            return redirect(master, 'accounts:login', query_params={
                'message': 'verify_success'
            })
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