from unittest.mock import patch
from connector_mock import Connector
from phantom.action_result import ActionResult
from sei.on_poll import on_poll

@patch('sei.get_events', return_value=["0000", '2021-08-01T00:00:01Z', ActionResult()])
def test_on_poll(mock_get_events):
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
                                    "persistenceTimestamp": '2020-08-01T00:00:01Z',
                                    "severity": "critical",
                                    "operationName" : "isolateFromNetwork",
                                    "status": "pending"
                                },
                                {
                                    "id": 1,
                                    "persistenceTimestamp": '2030-08-01T00:00:01Z',
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
    connector = Connector(config_connector)
    on_poll(connector, [])
    assert connector._state["isolated_devices"] == []
    assert connector._state["last_poll"] == '2021-08-01T00:00:01Z'
    assert connector._state["container_id"] == 0
