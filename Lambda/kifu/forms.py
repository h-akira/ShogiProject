from wtforms import Form, BooleanField, StringField, validators, IntegerField, TextAreaField
from wtforms.validators import DataRequired, Length

class KifuForm(Form):
  slug = StringField(
    render_kw={'style': 'width: 500px;'},
    validators=[DataRequired(), Length(min=1, max=127)]
  )
  public = BooleanField()
  kifu = TextAreaField()
  memo = TextAreaField()
  share = BooleanField()
  share_code = StringField(render_kw={'style': 'width: 500px;'})
  first_or_second = StringField(
    validators=[Length(min=1, max=31)]
  )
  win_or_lose = StringField(
    validators=[Length(min=1, max=31)]
  )
