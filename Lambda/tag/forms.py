from wtforms import Form, StringField
from wtforms.validators import DataRequired, Length

class TagForm(Form):
  slug = StringField(
    render_kw={'style': 'width: 500px;'},
    validators=[DataRequired(), Length(min=1, max=127)]
  )
