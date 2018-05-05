from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import Student


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ('id', 'username', 'password', 'email', 'grade', 'college', 'department', 'major', 'not_recommends')
        extra_kwargs = {
            'email': {'required': True, 'allow_null': False, 'allow_blank': False}
        }

    def get_field_value(self, data, key):
        if key in data:
            return data[key]
        if self.instance:
            return getattr(self.instance, key)
        return None

    def validate(self, data):
        # college, department, major belonging validations
        errors = []
        college = self.get_field_value(data, 'college')
        department = self.get_field_value(data, 'department')
        major = self.get_field_value(data, 'major')
        if department is not None:
            if college and department and college.id != department.college_id:
                errors.append('The department must belong to the college')
            if major is not None:
                if department and major and department.id != major.department_id:
                    errors.append('The major must belong to the department')
        if errors:
            raise ValidationError(errors)

        # password hashing
        if 'password' not in data:
            # password not changed
            return data
        tmp_user = User(username=data['username'], email=data['email'])
        validate_password(data['password'], user=tmp_user)
        data['password'] = make_password(data['password'])
        return data
