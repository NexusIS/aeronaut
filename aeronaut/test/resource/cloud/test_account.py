from aeronaut.resource.cloud.account import Account, Role


class TestAccount:

    # =======
    # HELPERS
    # =======

    @property
    def xmlstr(self):
        return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
        <ns2:Account xmlns:ns2="http://oec.api.opsource.net/schemas/directory">
            <ns2:userName>user1</ns2:userName>
            <ns2:fullName>User Uno</ns2:fullName>
            <ns2:firstName>User</ns2:firstName>
            <ns2:lastName>Uno</ns2:lastName>
            <ns2:emailAddress>user.uno@nowhere.com</ns2:emailAddress>
            <ns2:department>Engineering</ns2:department>
            <ns2:customDefined1>DevOps</ns2:customDefined1>
            <ns2:customDefined2/>
            <ns2:orgId>9df77a7d-1234-4b44-8865-04303fe1e43b</ns2:orgId>
            <ns2:roles>
                <ns2:role>
                    <ns2:name>server</ns2:name>
                </ns2:role>
                <ns2:role>
                    <ns2:name>create image</ns2:name>
                </ns2:role>
                <ns2:role>
                    <ns2:name>storage</ns2:name>
                </ns2:role>
                <ns2:role>
                    <ns2:name>backup</ns2:name>
                </ns2:role>
            </ns2:roles>
        </ns2:Account>
        """

    # =====
    # TESTS
    # =====

    def test_account_attributes(self):
        account = Account(self.xmlstr)
        assert account.department == 'Engineering'
        assert account.email == 'user.uno@nowhere.com'
        assert account.first_name == 'User'
        assert account.full_name == 'User Uno'
        assert account.last_name == 'Uno'
        assert account.org_id == '9df77a7d-1234-4b44-8865-04303fe1e43b'
        assert account.username == 'user1'

        for role in account.roles:
            assert isinstance(role, Role)

        assert account.roles[0].name == 'server'
        assert account.roles[1].name == 'create image'
        assert account.roles[2].name == 'storage'
        assert account.roles[3].name == 'backup'
