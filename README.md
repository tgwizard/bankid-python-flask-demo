# BankID Python Flask Demo

For the fun of it. If you're doing this for real, https://github.com/hbldh/pybankid/ seems like a nice library.

Links:

 - BankID website: https://www.bankid.com
 - Development and test resources: https://www.bankid.com/bankid-i-dina-tjanster/rp-info


View the WSDL (using HTTPie):

```
http --verify=BankID_TEST_ROOT.ca \
    --cert FPTestcert2_20150818_102329.pem \
    --cert-key FPTestcert2_20150818_102329.key \
    https://appapi2.test.bankid.com/rp/v4?wsdl
```


## Develop

Requires Python 3.6.

```bash
make setup
make install
```


## Run

```bash
make serve
```


## Screenshots

<img src="https://github.com/tgwizard/bankid-python-flask-demo/blob/master/screenshots/auth_2.png" width="500">
