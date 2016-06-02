# drop all db table
#./manage.py sqlclear packagename | ./manage.py dbshell

python manage.py migrate main # remove after fixing legacy "circle" import
python manage.py migrate
#python manage.py flush
#python manage.py createsuperuser

#python manage.py loaddata ./main/fixtures/sites.json
python manage.py loaddata ./main/fixtures/superuser.json
#
python manage.py loaddata ./main/fixtures/groups.json
python manage.py loaddata ./main/fixtures/data.json
python manage.py loaddata ./main/fixtures/transactions.json
#
#python manage.py loaddata ./main/fixtures/notifications.json # DEMO
#
#python manage.py collectstatic --dry-run --noinput

