from django.db.models import CharField, Model
from django_mysql.models import ListCharField

class Person(Model):
    name = CharField()
    post_nominals = ListCharField(
        base_field=CharField(max_length=10),
        size=6,
        max_length=(6 * 11) #6 * 10 character nominals, plus commas
    )
    