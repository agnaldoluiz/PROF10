from flask import current_app
from flask_wtf import FlaskForm
from wtforms.validators import (
	DataRequired, 
	Required,
	Length,
	Regexp,
	EqualTo
	)
from wtforms import (
	TextAreaField,
	TextField,
	IntegerField, 
	PasswordField,
	BooleanField,
	ValidationError,
	SubmitField,
	StringField
)

class UniqueUser(object):
	def __init__(self, message = "User Exists"):
		self.message = message
	#to do: validate uniqueness checking the database


validators = {
	'email': [
		Required(),
		#UniqueUser(message = 'Email address already exists')
	],
	'password': [
		Required(),
		Length(min = 6, max = 50),
		EqualTo('confirm', message = 'Password must match'),
		Regexp(r'[A-Za-z0-9@#$%^&+=]',
			message = 'Password contains invalid characters')
	],

	'text': [
		Required()
	]
}

class RegisterForm(FlaskForm):
	email = TextField('Email', validators['email'])
	password = PasswordField('Password', validators['password'],)
	confirm = PasswordField('Confirm Password')


class ProfessorForm(FlaskForm):
	first_name = TextField('First Name', validators['text'])
	last_name = TextField('Last Name', validators['text'])
	department = TextField('Department', validators['text'])
	college = TextField('College')
	add_professor = SubmitField('add_professor')

class PostForm(FlaskForm):
	post = TextAreaField('post', validators = [Required()])
	teaching = IntegerField('teaching', validators = [Required()])
	material = IntegerField('material', validators = [Required()])
	participation = IntegerField('participation', validators = [Required()])
	# Do not count for rating
	difficulty = IntegerField('difficulty', validators = [Required()])
	# Attendance
	attendance = BooleanField('attendance', validators = [Required()], default = False)
	subject = TextField('subject', validators = [Required()])

class CollegeForm(FlaskForm):
	college_name = TextField('college_name', validators = [DataRequired()])
	college_acronym = TextField('college_acronym', validators = [DataRequired()])
	state = TextField('state', validators = [DataRequired()])
	add_college = SubmitField('add_college')

class SearchForm(FlaskForm):
    search = StringField('search', validators=[DataRequired()])


