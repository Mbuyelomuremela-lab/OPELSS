import os
import pathlib
os.environ['DATABASE_URL'] = 'sqlite:///' + str(pathlib.Path('instance/app.db').resolve())
import app as app_module
app_obj = app_module.create_app()
client = app_obj.test_client()
with client.session_transaction() as sess:
    sess['_user_id'] = '1'
    sess['_fresh'] = True
    sess['user_id'] = 1
resp = client.get('/assets/?category=&status=Slow&lab_id=&province_id=')
print('status', resp.status_code)
print(resp.get_data(as_text=True)[:8000])
