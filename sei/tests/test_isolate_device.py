from unittest.mock import MagicMock
#from unittest.mock import patch
from connector_mock import Connector
import sys
sys.modules['phantom.action_result'] = MagicMock()
sys.modules['phantom.app'] = MagicMock()
sys.modules['phantom'] = MagicMock()
sys.path.append('../phElements Security Center')
from sei.isolate_device import isolate_device

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

def test_isolate_device():
    connector = Connector(config_connector)
    assert isolate_device(connector, {"device_id": 1}) == 0