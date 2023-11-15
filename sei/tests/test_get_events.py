from connector_mock import Connector
from sei.get_events import get_events

def test_get_events():
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
    result = get_events(connector, {"device_id": 1, "anchor": 0}, 2, '2022-08-01T00:00:01Z')
    assert result[:2] == ([
    {"name": 0, "label": "critical", "severity": 
    "critical",'artifact_type': 'event', 
    "data":{
                "id": 0,
                "persistenceTimestamp": '2020-08-01T00:00:01Z',
                "severity": "critical",
                "operationName" : "isolateFromNetwork",
                "status": "pending"
            }, 
    "cef": {
                "id": 0,
                "persistenceTimestamp": '2020-08-01T00:00:01Z',
                "severity": "critical",
                "operationName" : "isolateFromNetwork",
                "status": "pending"
            }, 
    "container_id": 2, 'run_automation': True},
    {"name": 1, "label": "critical", "severity": 
    "critical",'artifact_type': 'event', 
    "data":{
                "id": 1,
                "persistenceTimestamp": '2030-08-01T00:00:01Z',
                "severity": "critical",
                "operationName" : "isolateFromNetwork",
                "status": "pending"
            }, 
    "cef": {
                "id": 1,
                "persistenceTimestamp": '2030-08-01T00:00:01Z',
                "severity": "critical",
                "operationName" : "isolateFromNetwork",
                "status": "pending"
            }, 
    "container_id": 2, 'run_automation': True}
    ], '2020-08-01T00:00:01Z')

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
                    "items": None,
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
    result = get_events(connector, {"device_id": 1, "anchor": 0}, 2, '2010-08-01T00:00:01Z')
    assert result[:2] == ([], '2010-08-01T00:00:01Z')