from unittest.mock import MagicMock
from connector_mock import Connector
import sys
sys.modules['phantom.action_result'] = MagicMock()
sys.modules['phantom.app'] = MagicMock()
sys.modules['phantom'] = MagicMock()
sys.path.append('../phElements Security Center')
from sei.device_details import device_details

config_connector = {
    "timestamp": "2022-08-01T00:00:01Z",
    "state":{
            "last_poll": "poll",
            "isolated_devices": [],
            "container_id": 0
            },
    "client_id": 123,
    "client_secret": 321,
    "base_url": "https://api.com",
    "response": {
                    "items":[
                                {
                                    "id": 0,
                                    "persistenceTimestamp": 20,
                                    "severity": "critical",
                                    "operationName" : "isolateFromNetwork",
                                    "status": "pending"
                                },
                                {
                                    "id": 1,
                                    "persistenceTimestamp": 30,
                                    "severity": "critical",
                                    "operationName" : "isolateFromNetwork",
                                    "status": "pending"
                                }
                            ],
                    "organizationId": 333,
                    "nextAnchor": None,
                    "access_token" : "1111",
                    "multistatus" : [
                                {
                                    "status": 202,
                                    "target": "target1"
                                }
                            ]
                    },
    "message": "Message"
}

def test_device_details():
    connector = Connector(config_connector)
    assert device_details(connector, {"device_id": 1}) == 0