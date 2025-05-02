from wtforms import Form, BooleanField, StringField, validators, IntegerField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length

class KifuForm(Form):
  slug = StringField(
    render_kw={'style': 'width: 500px;'},
    validators=[DataRequired(), Length(min=1, max=127)]
  )
  public = BooleanField()
  kifu = TextAreaField(render_kw={'style': 'width: 300px; height: 200px;'})
  memo = TextAreaField(render_kw={'style': 'width: 100%; height: 200px;'})
  share = BooleanField()
  share_code = StringField(render_kw={'style': 'width: 500px;'})
  first_or_second = SelectField(
    choices=[('None', "---"), ('first', '先手'), ('second', '後手')]
    # validators=[Length(min=1, max=31)]
  )
  win_or_lose = SelectField(
    choices=[('None', "---"), ('win', '勝ち'), ('lose', '負け'), ('sennichite', '千日手'), ('jishogi','持将棋')]
    # validators=[Length(min=1, max=31)]
  )
