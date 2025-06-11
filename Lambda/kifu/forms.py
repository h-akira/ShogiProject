from wtforms import Form, BooleanField, StringField, validators, IntegerField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length

class KifuForm(Form):
  slug = StringField(
    render_kw={'style': 'width: 500px;'},
    validators=[DataRequired(), Length(min=1, max=127)]
  )
  kifu = TextAreaField(render_kw={'style': 'width: 300px; height: 200px;'})
  memo = TextAreaField(render_kw={'style': 'width: 100%; height: 200px;'})
  share = BooleanField()
  first_or_second = SelectField(
    choices=[('none', "---"), ('first', '先手'), ('second', '後手')]
    # validators=[Length(min=1, max=31)]
  )
  result = SelectField(
    choices=[('none', "---"), ('win', '勝ち'), ('lose', '負け'), ('sennichite', '千日手'), ('jishogi','持将棋')]
    # validators=[Length(min=1, max=31)]
  )
  tags = StringField(
    render_kw={'style': 'width: 100%;'},
    description='カンマ区切りで複数タグを入力できます',
    validators=[Length(max=255)]
  )
