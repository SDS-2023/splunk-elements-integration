from unittest.mock import MagicMock
from connector_mock import Connector
import sys
sys.modules['phantom.action_result'] = MagicMock()
sys.modules['phantom.app'] = MagicMock()
#sys.path.append('../phElements Security Center')
from sei.get_events import get_events

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

def test_get_events():
    connector = Connector(config_connector)
    result = get_events(connector, {"device_id": 1, "anchor": 0}, 2, '2022-08-01T00:00:01Z')
    assert result[:2] == ([
    {"name": 0, "label": "critical", "severity": 
    "critical",'artifact_type': 'event', 
    "data":{
                "id": 0,
                "persistenceTimestamp": 20,
                "severity": "critical",
                "operationName" : "isolateFromNetwork",
                "status": "pending"
            }, 
    "cef": {
                "id": 0,
                "persistenceTimestamp": 20,
                "severity": "critical",
                "operationName" : "isolateFromNetwork",
                "status": "pending"
            }, 
    "container_id": 2, 'run_automation': True},
    {"name": 1, "label": "critical", "severity": 
    "critical",'artifact_type': 'event', 
    "data":{
                "id": 1,
                "persistenceTimestamp": 30,
                "severity": "critical",
                "operationName" : "isolateFromNetwork",
                "status": "pending"
            }, 
    "cef": {
                "id": 1,
                "persistenceTimestamp": 30,
                "severity": "critical",
                "operationName" : "isolateFromNetwork",
                "status": "pending"
            }, 
    "container_id": 2, 'run_automation': True}
    ],20)