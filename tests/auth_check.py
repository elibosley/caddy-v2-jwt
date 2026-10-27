import base64
import hashlib
import hmac
import http.client
import json
import os
from pathlib import Path
import secrets
import subprocess
import time
import urllib.error
import urllib.request

import sys
import tempfile

scratch = tempfile.TemporaryDirectory(prefix='caddy-auth-check-')
directory = Path(scratch.name)
config = r"""
{
    security {
        authorization policy all_users_policy {
            allow group Admin SuperUser Downloader User
            set auth url http://localhost/login
            set access_token cookie name sso_access_token
            crypto key verify {env.JWT_TOKEN_SECRET}
        }
        authorization policy downloader_users_policy {
            allow group Admin SuperUser Downloader
            set auth url http://localhost/login
            set access_token cookie name sso_access_token
            crypto key verify {env.JWT_TOKEN_SECRET}
        }
        authorization policy admin_users_policy {
            allow group Admin SuperUser
            set auth url http://localhost/login
            set access_token cookie name sso_access_token
            crypto key verify {env.JWT_TOKEN_SECRET}
        }
    }
}
:8080 {
    route /user {
        authorize with all_users_policy
        respond "authorized" 200
    }
    route /downloader {
        authorize with downloader_users_policy
        respond "authorized" 200
    }
    route /admin {
        authorize with admin_users_policy
        respond "authorized" 200
    }
}
"""
(directory / 'Caddyfile').write_text(config)
secret = secrets.token_urlsafe(40)
(directory / 'runtime.env').write_text('JWT_TOKEN_SECRET=' + secret + '\n')
image = sys.argv[1]
name = 'caddy-auth-check-' + secrets.token_hex(5)
created = False

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl): return None

def encode(obj):
    return base64.urlsafe_b64encode(json.dumps(obj, separators=(',', ':')).encode()).rstrip(b'=').decode()

def token(group='Admin', expired=False, bad=False, unsigned=False):
    now = int(time.time())
    header = encode({'alg': 'none' if unsigned else 'HS256', 'typ': 'JWT'})
    payload = encode({'iss': 'Organizr', 'aud': 'Organizr', 'sub': 'auth-check',
                      'name': 'auth-check', 'email': 'auth-check@example.invalid',
                      'group': group, 'groupID': 0, 'userID': 0,
                      'iat': now-7200 if expired else now-5,
                      'exp': now-3600 if expired else now+120, 'jti': secrets.token_hex(8)})
    unsigned_data = header + '.' + payload
    signature = '' if unsigned else base64.urlsafe_b64encode(hmac.new(
        (secret+'wrong' if bad else secret).encode(), unsigned_data.encode(), hashlib.sha256).digest()).rstrip(b'=').decode()
    return unsigned_data + '.' + signature

try:
    p = subprocess.run(['docker','run','-d','--platform','linux/amd64','--name',name,
        '-p','127.0.0.1::8080','--env-file',str(directory/'runtime.env'),
        '--mount','type=bind,src='+str(directory/'Caddyfile')+',dst=/etc/caddy/Caddyfile,readonly',
        image],capture_output=True,text=True,check=True)
    created = True
    port = subprocess.run(['docker','port',name,'8080/tcp'],capture_output=True,text=True,check=True).stdout.strip().rsplit(':',1)[1]
    opener = urllib.request.build_opener(NoRedirect)
    def request(route, jwt=None):
        headers = {'Cookie': 'sso_access_token='+jwt} if jwt else {}
        req = urllib.request.Request('http://127.0.0.1:'+port+route,headers=headers)
        try:
            with opener.open(req,timeout=5) as r:return r.status
        except urllib.error.HTTPError as r:return r.code
    # Bounded readiness for this newly created local test container.
    for n in range(20):
        try: request('/user');break
        except (urllib.error.URLError, http.client.RemoteDisconnected, ConnectionResetError):
            if n==19:raise
            time.sleep(.2)
    results = {}
    for group, allowed in [('Admin',{'/user','/downloader','/admin'}),
                           ('Downloader',{'/user','/downloader'}),('User',{'/user'}),('Guest',set())]:
        jwt = token(group)
        for route in ['/user','/downloader','/admin']:
            status = request(route,jwt)
            expected = status==200 if route in allowed else status in (302,401,403)
            results[group+route] = status
            assert expected, (group,route,status)
    for label,jwt in [('missing',None),('tampered',token(bad=True)),
                      ('expired',token(expired=True)),('unsigned',token(unsigned=True))]:
        status=request('/admin',jwt);results[label]=status
        assert status in (302,401,403),(label,status)
    assert len(results) == 16
    print('Passed 16 role, signature, expiration, and missing-token checks.')
except Exception:
    if created:
        logs=subprocess.run(['docker','logs',name],capture_output=True,text=True)
        print(logs.stdout+logs.stderr, file=sys.stderr)
    raise
finally:
    if created:
        subprocess.run(['docker','rm','-f',name],capture_output=True,check=True)
    (directory/'runtime.env').unlink(missing_ok=True)

    scratch.cleanup()
