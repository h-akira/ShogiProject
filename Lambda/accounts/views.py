from wambda.shortcuts import render, redirect
from wambda.authenticate import login, signup, verify, MaintenanceOptionError, change_password, forgot_password, confirm_forgot_password
from .forms import LoginForm, SignupForm, VerifyForm, ChangePasswordForm, ForgotPasswordForm, ResetPasswordForm

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
        elif message_type == 'password_reset_success':
            context['message'] = 'パスワードリセットが完了しました'
    
    if master.request.method == 'POST' and form.validate():
        username = form.username.data
        password = form.password.data
        try:
            if login(master, username, password):
                return redirect(master, 'home')
            else:
                context['error'] = 'ログインに失敗しました'
                return render(master, 'accounts/login.html', context)
        except MaintenanceOptionError:
            context['error'] = '現在、メンテナンスのためログインできません。しばらくお待ちください。'
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
        except MaintenanceOptionError:
            context = {'form': form, 'error': '現在、メンテナンスのため新規登録を停止しております。ご迷惑をおかけして申し訳ございません。'}
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
    from wambda.authenticate import sign_out
    
    try:
        sign_out(master)  # 認証情報クリア + Cookie削除フラグ設定
        master.logger.debug("sign_out completed successfully")
    except Exception as e:
        master.logger.warning(f"Logout warning: {e}")
        # 例外が発生した場合も強制的にCookie削除
        master.request.auth = False
        master.request.username = None
        master.request.clean_cookie = True
        master.logger.debug("Forced cleanup after exception")
    
    # リダイレクト先URLをログ出力
    from wambda.shortcuts import reverse
    home_url = reverse(master, 'home')
    master.logger.debug(f"Redirecting to home URL: {home_url}")
    
    redirect_response = redirect(master, 'home')
    master.logger.debug(f"Redirect response: {redirect_response}")
    
    return redirect_response

def user_profile_view(master):
    if not master.request.auth:
        return redirect(master, 'accounts:login')
    
    # Get user email from Cognito if available
    email = None
    try:
        from wambda.authenticate import get_user_info
        user_info = get_user_info(master, master.request.username)
        if user_info:
            email = user_info.get('email')
    except Exception as e:
        master.logger.warning(f"Failed to get user email: {e}")
    
    context = {
        'username': master.request.username,
        'email': email
    }
    
    if master.request.method == 'GET':
        query_params = master.event.get('queryStringParameters') or {}
        message_type = query_params.get('message', '')
        
        if message_type == 'password_changed':
            context['message'] = 'パスワードが正常に変更されました'
    
    return render(master, 'accounts/user_profile.html', context)

def change_password_view(master):
    if not master.request.auth:
        return redirect(master, 'accounts:login')
    
    if master.request.method == 'POST':
        form = ChangePasswordForm(master.request.get_form_data())
    else:
        form = ChangePasswordForm()
    
    if master.request.method == 'POST' and form.validate():
        current_password = form.current_password.data
        new_password = form.new_password.data
        confirm_password = form.confirm_password.data
        
        if new_password != confirm_password:
            context = {'form': form, 'error': '新しいパスワードが一致しません'}
            return render(master, 'accounts/change_password.html', context)
        
        if change_password(master, master.request.username, current_password, new_password):
            from wambda.shortcuts import reverse
            profile_url = reverse(master, 'accounts:profile')
            return redirect(master, 'accounts:profile', query_params={
                'message': 'password_changed'
            })
        else:
            context = {'form': form, 'error': 'パスワード変更に失敗しました'}
            return render(master, 'accounts/change_password.html', context)
    
    return render(master, 'accounts/change_password.html', {'form': form})

def forgot_password_view(master):
    if master.request.method == 'POST':
        form = ForgotPasswordForm(master.request.get_form_data())
    else:
        form = ForgotPasswordForm()
    
    if master.request.method == 'POST' and form.validate():
        username = form.username.data
        if forgot_password(master, username):
            return redirect(master, 'accounts:reset_password', query_params={
                'username': username,
                'message': 'reset_code_sent'
            })
        else:
            context = {'form': form, 'error': 'パスワードリセット確認コード送信に失敗しました'}
            return render(master, 'accounts/forgot_password.html', context)
    
    return render(master, 'accounts/forgot_password.html', {'form': form})

def reset_password_view(master):
    if master.request.method == 'POST':
        form = ResetPasswordForm(master.request.get_form_data())
    else:
        form = ResetPasswordForm()
    
    context = {'form': form}
    
    if master.request.method == 'GET':
        query_params = master.event.get('queryStringParameters') or {}
        username = query_params.get('username', '')
        message_type = query_params.get('message', '')
        
        if username:
            form.username.data = username
        
        if message_type == 'reset_code_sent':
            context['message'] = 'パスワードリセット確認コードをメールで送信しました。'
    
    if master.request.method == 'POST' and form.validate():
        username = form.username.data
        confirmation_code = form.confirmation_code.data
        new_password = form.new_password.data
        confirm_password = form.confirm_password.data
        
        if new_password != confirm_password:
            context['error'] = 'パスワードが一致しません'
            return render(master, 'accounts/reset_password.html', context)
        
        if confirm_forgot_password(master, username, confirmation_code, new_password):
            return redirect(master, 'accounts:login', query_params={
                'message': 'password_reset_success'
            })
        else:
            context['error'] = 'パスワードリセットに失敗しました'
            return render(master, 'accounts/reset_password.html', context)
    
    return render(master, 'accounts/reset_password.html', context)