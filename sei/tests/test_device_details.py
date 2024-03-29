from connector_mock import Connector
from phantom.action_result import ActionResult
from sei.device_details import device_details

def test_device_details():
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
    action_result = ActionResult()
    connector = Connector(config_connector)
    device_details(connector, action_result, {"device_id": 1})
    assert action_result.get_data()[0] == { "isolate_queued" : True, "id": 0,
                                            "persistenceTimestamp": '2020-08-01T00:00:01Z',
                                            "severity": "critical",
                                            "operationName" : "isolateFromNetwork",
                                            "status": "pending"}