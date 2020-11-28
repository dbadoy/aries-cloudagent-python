from asynctest import TestCase as AsyncTestCase
from asynctest import mock as async_mock

from ....core.in_memory import InMemoryProfile
from ....messaging.request_context import RequestContext

from .. import routes as test_module


# TODO: Add tests
class TestJSONLDRoutes(AsyncTestCase):
    async def setUp(self):
        self.session = InMemoryProfile.test_session()
        self.did_info = await self.session.wallet.create_local_did()
        self.context = RequestContext(self.session.profile)
        self.app = {
            "request_context": self.context,
        }

    async def test_verify_credential(self):
        mock_request = async_mock.MagicMock(
            app=self.app,
            json=async_mock.CoroutineMock(
                return_value={  # posted json
                    "verkey": (
                        # pulled from the did:key in example
                        "5yKdnU7ToTjAoRNDzfuzVTfWBH38qyhE1b9xh4v8JaWF"
                    ),
                    "doc": {
                        "@context": [
                            "https://www.w3.org/2018/credentials/v1",
                            "https://www.w3.org/2018/credentials/examples/v1",
                        ],
                        "id": "http://example.gov/credentials/3732",
                        "type": ["VerifiableCredential", "UniversityDegreeCredential"],
                        "issuer": (
                            "did:key:z6MkjRagNiMu91DduvCvgEsqLZDVzrJzFrwahc4tXLt9DoHd"
                        ),
                        "issuanceDate": "2020-03-10T04:24:12.164Z",
                        "credentialSubject": {
                            "id": (
                                "did:key:"
                                "z6MkjRagNiMu91DduvCvgEsqLZDVzrJzFrwahc4tXLt9DoHd"
                            ),
                            "degree": {
                                "type": "BachelorDegree",
                                "name": "Bachelor of Science and Arts",
                            },
                        },
                        "proof": {
                            "type": "Ed25519Signature2018",
                            "created": "2020-04-10T21:35:35Z",
                            "verificationMethod": (
                                "did:key:"
                                "z6MkjRagNiMu91DduvCvgEsqLZDVzrJzFrwahc"
                                "4tXLt9DoHd#z6MkjRagNiMu91DduvCvgEsqLZD"
                                "VzrJzFrwahc4tXLt9DoHd"
                            ),
                            "proofPurpose": "assertionMethod",
                            "jws": (
                                "eyJhbGciOiJFZERTQSIsImI2NCI6ZmFsc2UsImNyaX"
                                "QiOlsiYjY0Il19..l9d0YHjcFAH2H4dB9xlWFZQLUp"
                                "ixVCWJk0eOt4CXQe1NXKWZwmhmn9OQp6YxX0a2Lffe"
                                "gtYESTCJEoGVXLqWAA"
                            ),
                        },
                    },
                }
            ),
        )

        with async_mock.patch.object(test_module.web, "json_response") as mock_response:
            result = await test_module.verify(mock_request)
            assert result == mock_response.return_value
            mock_response.assert_called_once_with({"valid": True})  # expected response

    async def test_sign_credential(self):
        mock_request = async_mock.MagicMock(
            app=self.app,
            json=async_mock.CoroutineMock(
                return_value={  # posted json
                    "verkey": self.did_info.verkey,
                    "doc": {
                        "credential": {
                            "@context": [
                                "https://www.w3.org/2018/credentials/v1",
                                "https://www.w3.org/2018/credentials/examples/v1",
                            ],
                            "id": "http://example.gov/credentials/3732",
                            "type": [
                                "VerifiableCredential",
                                "UniversityDegreeCredential",
                            ],
                            "issuer": (
                                "did:key:"
                                "z6MkjRagNiMu91DduvCvgEsqLZDVzrJzFrwahc4tXLt9DoHd"
                            ),
                            "issuanceDate": "2020-03-10T04:24:12.164Z",
                            "credentialSubject": {
                                "id": (
                                    "did:key:"
                                    "z6MkjRagNiMu91DduvCvgEsqLZDVzrJzFrwahc4tXLt9DoHd"
                                ),
                                "degree": {
                                    "type": "BachelorDegree",
                                    "name": u"Bachelor of Encyclopædic Arts",
                                },
                            },
                        },
                        "options": {
                            "type": "Ed25519Signature2018",
                            "created": "2020-04-10T21:35:35Z",
                            "verificationMethod": (
                                "did:key:"
                                "z6MkjRagNiMu91DduvCvgEsqLZDVzrJzFrwahc4tXLt9DoHd#"
                                "z6MkjRagNiMu91DduvCvgEsqLZDVzrJzFrwahc4tXLt9DoHd"
                            ),
                            "proofPurpose": "assertionMethod",
                        },
                    },
                }
            ),
        )

        with async_mock.patch.object(test_module.web, "json_response") as mock_response:
            result = await test_module.sign(mock_request)
            assert result == mock_response.return_value
            mock_response.assert_called_once()
            assert "signed_doc" in mock_response.call_args[0][0]
            assert "error" not in mock_response.call_args[0][0]
