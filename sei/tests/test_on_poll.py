from unittest.mock import MagicMock
from unittest.mock import patch
from connector_mock import Connector
from connector_mock import ActionResult
import sys
sys.modules['phantom.action_result'] = MagicMock()
sys.modules['phantom.app'] = MagicMock()
sys.path.append('../phElements Security Center')
from sei.on_poll import on_poll
    
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

action_result = ActionResult()

@patch('sei.get_events', return_value=["0000", 0, action_result])
def test_on_poll(mock_get_events):
    connector = Connector(config_connector)
    assert on_poll(connector, None) == 1
