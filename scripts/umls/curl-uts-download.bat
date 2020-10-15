@echo off

IF "%1"=="" goto usage

REM  NOTE: Avoid using '%' in the URL,username and password.
REM        '%' is a metacharacter in windows batch files. It is used for parameter substitution, e.g. %1. 
REM        If you need to use it(as a literal '%') you need to use '%%' in the  command. 

SET CAS_LOGIN_URL=https://utslogin.nlm.nih.gov/cas/login
SET CAS_LOGOUT_URL=https://utslogin.nlm.nih.gov:443/cas/logout 

SET DOWNLOAD_URL=%1

SET UTS_USERNAME=
SET UTS_PASSWORD=

SET BROWSER_USER_AGENT="Mozilla/5.0 (Windows NT 5.1; rv:18.0) Gecko/2010 0101 Firefox/18.0"
SET COOKIE_FILE=uts-cookie.txt
SET NLM_CACERT=uts.nlm.nih.gov.crt
SET CURL_HOME=
SET CURL_COMMAND=%CURL_HOME%\curl -s

if "%2"=="verbose" SET CURL_COMMAND=%CURL_HOME%\curl -v

rem Remove old uts auth cookie
del uts-cookie.txt login logout token.txt

rem echo Go the UTS login page and get the UTS Auth cookie with CAS ticket..

%CURL_COMMAND%  -L -A %BROWSER_USER_AGENT% -H Connection:keep-alive -H Expect: -H Accept-Language:en-us --cacert %NLM_CACERT% -k -b %COOKIE_FILE%  -c %COOKIE_FILE% -O %CAS_LOGIN_URL%

call jrepl_cas.bat

for /f %%G in (token.txt) do set NONCE=%%G

%CURL_COMMAND% -L -A %BROWSER_USER_AGENT% -H Connection:keep-alive -H Expect: -H Accept-Language:en-us -b %COOKIE_FILE% -d "username=%UTS_USERNAME%&password=%UTS_PASSWORD%&_eventId=submit&submit=LOGIN&execution=%NONCE%" --cacert %NLM_CACERT% -k -c %COOKIE_FILE%  -O %CAS_LOGIN_URL%

echo  Now download the file ..

%CURL_COMMAND% -L -A %BROWSER_USER_AGENT% -H Connection:keep-alive -H Expect: -H Accept-Language:en-us --cacert %NLM_CACERT% -k -b %COOKIE_FILE% -O %DOWNLOAD_URL%


rem "Logging out.."
%CURL_COMMAND% -L -A %BROWSER_USER_AGENT% -H Connection:keep-alive -H Expect: -H Accept-Language:en-us --cacert %NLM_CACERT% -k -b %COOKIE_FILE% -O %CAS_LOGOUT_URL%

echo cleaning up ...
del login logout token.txt

rem "File has been downloaded"
goto END

:USAGE
echo Usage: curl-uts-download.bat download_url [verbose]
echo e.g.   curl-uts-download.bat https://download.nlm.nih.gov/umls/kss/rxnorm/RxNorm_full_current.zip
echo        curl-uts-download.bat https://download.nlm.nih.gov/umls/kss/rxnorm/RxNorm_weekly_current.zip
            
goto END

:END
