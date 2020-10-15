#!/bin/bash

export UTS_USERNAME=
export UTS_PASSWORD=

export CAS_LOGIN_URL=https://utslogin.nlm.nih.gov/cas/login
export CAS_LOGOUT_URL=https://utslogin.nlm.nih.gov:443/cas/logout

export DOWNLOAD_URL=$1
export BROWSER_USER_AGENT="Firefox/18.0"
export COOKIE_FILE=uts-cookie.txt
export NLM_CACERT=uts.nlm.nih.gov.crt

if [ $# -eq 0 ]; then echo "Usage: curl-uts-downloads.sh  download_url "
                      echo "  e.g.   curl-uts-download.sh https://download.nlm.nih.gov/umls/kss/rxnorm/RxNorm_full_current.zip"
                      echo "         curl-uts-download.sh https://download.nlm.nih.gov/umls/kss/rxnorm/RxNorm_weekly_current.zip"
   exit
fi

# Remove old uts auth cookie if exists
if [ -f uts-cookie.txt ]; then
    rm uts-cookie.txt
fi

#echo "Go the UTS login page and get the UTS Auth cookie with CAS ticket.."

curl -L -A $BROWSER_USER_AGENT -H Connection:keep-alive -H Expect: -H Accept-Language:en-us --cacert $NLM_CACERT -k -b $COOKIE_FILE  -c $COOKIE_FILE -O $CAS_LOGIN_URL

nonce=`grep "execution" login | awk -F"\"" '{print $6}'`

curl -s -A $BROWSER_USER_AGENT -b $COOKIE_FILE -H Connection:keep-alive -H Expect: -H Accept-Language:en-us -H Referer:$CAS_LOGIN_URL -d "service=$DOWNLOAD_URL&username=$UTS_USERNAME&password=$UTS_PASSWORD&_eventId=submit&submit=LOGIN&execution=$nonce" --cacert $NLM_CACERT -k -c $COOKIE_FILE  -O $CAS_LOGIN_URL

echo 'Now get the download'
curl -L -A $BROWSER_USER_AGENT -H Connection:keep-alive -H Expect: -H Accept-Language:en-us --cacert $NLM_CACERT -k -b $COOKIE_FILE -O $DOWNLOAD_URL

#echo "Now log out.."
curl -s -L -A $BROWSER_USER_AGENT -H Connection:keep-alive -H Expect: -H Accept-Language:en-us --cacert $NLM_CACERT -k -b $COOKIE_FILE $CAS_LOGOUT_URL

#echo "cleaning up .."
if [ -f login ]; then
    rm login
	fi
if [ -f logout ]; then
    rm logout
fi
