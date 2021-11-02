import unittest
import json
from blocknative.exceptions import InvalidAPIKeyError
from blocknative.utils import raise_error_on_status

class TestMethodRaiseErrorOnStatus(unittest.TestCase):
  error_payload = {
    'version': 0, 'serverVersion': '0.122.2', 'timeStamp': '2021-11-02T18:06:57.295Z', 'connectionId': 'XX-XX-XX-XX', 'status': 'error', 'raw': '{"timeStamp": "2021-11-02T18:06:51.655854", "dappId": "", "version": "1", "blockchain": {"system": "ethereum", "network": "main"}, "categoryCode": "initialize", "eventCode": "checkDappId"}', 'event': {'timeStamp': '2021-11-02T18:06:51.655854', 'dappId': '', 'version': '1', 'blockchain': {'system': 'ethereum', 'network': 'main'}, 'categoryCode': 'initialize', 'eventCode': 'checkDappId'}, 'reason': ' is not a valid API key'
  }

  status_but_no_reason = {
    'version': 0, 'serverVersion': '0.122.2', 'timeStamp': '2021-11-02T18:06:57.295Z', 'connectionId': 'XX-XX-XX-XX', 'status': 'ok', 'raw': '{"timeStamp": "2021-11-02T18:06:51.655854", "dappId": "", "version": "1", "blockchain": {"system": "ethereum", "network": "main"}, "categoryCode": "initialize", "eventCode": "checkDappId"}', 'event': {'timeStamp': '2021-11-02T18:06:51.655854', 'dappId': '', 'version': '1', 'blockchain': {'system': 'ethereum', 'network': 'main'}, 'categoryCode': 'initialize', 'eventCode': 'checkDappId'}, 
  }

  status_okay = {
    'version': 0, 'serverVersion': '0.122.2', 'timeStamp': '2021-11-02T18:06:57.295Z', 'connectionId': 'XX-XX-XX-XX', 'status': 'ok', 'raw': '{"timeStamp": "2021-11-02T18:06:51.655854", "dappId": "", "version": "1", "blockchain": {"system": "ethereum", "network": "main"}, "categoryCode": "initialize", "eventCode": "checkDappId"}', 'event': {'timeStamp': '2021-11-02T18:06:51.655854', 'dappId': '', 'version': '1', 'blockchain': {'system': 'ethereum', 'network': 'main'}, 'categoryCode': 'initialize', 'eventCode': 'checkDappId'}, 
  }



  def test_raise_error_for_error_payload(self):
    with self.assertRaises(InvalidAPIKeyError) as context:
      raise_error_on_status(self.error_payload)
    self.assertTrue('is not a valid API key' in context.exception.args)

  def test_no_error_raise_for_no_reason(self):
    raise_error_on_status(self.status_but_no_reason)

  def test_no_error_status_okay(self):
    raise_error_on_status(self.status_okay)


if __name__ == '__main__':
  unittest.main()
