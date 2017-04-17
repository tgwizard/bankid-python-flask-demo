from requests import Session
from zeep import Client, Transport

import os.path

from zeep.exceptions import Fault

TEST_WSDL_URL = 'https://appapi2.test.bankid.com/rp/v4?wsdl'
TEST_CLIENT_CERT_PUBKEY_PATH = os.path.join(
    os.path.dirname(__file__), '../FPTestcert2_20150818_102329.pem',
)
TEST_CLIENT_CERT_PRIVKEY_PATH = os.path.join(
    os.path.dirname(__file__), '../FPTestcert2_20150818_102329.key',
)
TEST_ROOT_CA_PATH = os.path.join(
    os.path.dirname(__file__), '../BankID_TEST_ROOT.ca',
)


session = Session()
session.verify = TEST_ROOT_CA_PATH
session.cert = (TEST_CLIENT_CERT_PUBKEY_PATH, TEST_CLIENT_CERT_PRIVKEY_PATH)

BANKID_CLIENT = Client(TEST_WSDL_URL, transport=Transport(session=session))


def authenticate(pid: str):
    assert len(pid) == 12
    r = BANKID_CLIENT.service.Authenticate(
        personalNumber=pid,
        requirementAlternatives=[
            {
                'requirement': {
                    'condition': [
                        {
                            'key': 'CertificatePolicies',
                            'value': '1.2.3.4.*',
                        },
                    ],
                },
            },
        ],
    )
    order_ref = r['orderRef']
    auto_start_token = r['autoStartToken']
    return order_ref, auto_start_token


class UserCancelled(Exception):
    pass


def get_status(order_ref) -> dict:
    assert len(order_ref) > 32

    try:
        r = BANKID_CLIENT.service.Collect(order_ref)
    except Fault as e:
        if e.message == 'USER_CANCEL':
            raise UserCancelled()
        raise

    print(r)
    user_info = None
    if r['userInfo']:
        user_info = {
            'given_name': r['userInfo']['givenName'],
            'surname': r['userInfo']['surname'],
            'name': r['userInfo']['name'],
            'personal_number': r['userInfo']['personalNumber'],
            'not_before': r['userInfo']['notBefore'].isoformat(),
            'not_after': r['userInfo']['notAfter'].isoformat(),
            'ip_address': r['userInfo']['ipAddress'],
        }
    return {
        'progress_status': r['progressStatus'],
        'signature': r['signature'],
        'user_info': user_info,
        'ocsp_response': r['ocspResponse'],
    }
