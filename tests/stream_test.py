"""stream unit test"""
import unittest
import json
from blocknative.stream import Stream as BNStream

EXAMPLE_TRANSACTION = """
{
    "timeStamp": "2021-11-12T16:52:27.107Z",
    "categoryCode": "activeAddress",
    "eventCode": "txConfirmed",
    "dappId": "super-secret-key",
    "blockchain": {
        "system": "ethereum",
        "network": "main"
    },
    "contractCall": {
        "contractType": "Uniswap V2: Router 2",
        "contractAddress": "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D",
        "methodName": "swapExactTokensForTokens",
        "params": {
            "amountIn": "5742316412",
            "amountOutMin": "5255365551676807280351",
            "path": [
                "0xdAC17F958D2ee523a2206206994597C13D831ec7",
                "0x6B175474E89094C44Da98b954EedeAC495271d0F",
                "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
                "0xE0aD1806Fd3E7edF6FF52Fdb822432e847411033"
            ],
            "to": "0x0088D85CE24a310b89B495d96F1B20f05647fE60",
            "deadline": "1636736022"
        }
    },
    "transaction": {
        "status": "confirmed",
        "monitorId": "Geth_1_B_PROD",
        "monitorVersion": "0.101.0",
        "timePending": "38129",
        "blocksPending": 2,
        "pendingTimeStamp": "2021-11-12T16:51:48.978Z",
        "pendingBlockNumber": 13602465,
        "hash": "0xd6f98c52a1cd7a4b39aeae5bd3919f699b7e0323d8fc2a91a9ba9163614cb9d7",
        "from": "0xE4f0f68B73D7c8ab9b7B96A3Fd1b079d5deAfD3F",
        "to": "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D",
        "value": "0",
        "gas": 274136,
        "nonce": 6,
        "blockHash": "0x15e55a7b4614e82893a1907d946a51094bb7f67b1bfc8a058378c6f3bab337f2",
        "blockNumber": 13602467,
        "v": "0x0",
        "r": "0x9b27c97a5d77b1f8b5dba5b440a063c3c441b8f9968adc65d6a14ebb9893334b",
        "s": "0x2411ca38c1ad896928d92e3bf561421077f4f999e250c01dfc18f0ecf08836a5",
        "input": "0x38ed1739000000000000000000000000000000000000000000000000000000015644cb7c00000000000000000000000000000000000000000000011ce4d9152148e176df00000000000000000000000000000000000000000000000000000000000000a00000000000000000000000000088d85ce24a310b89b495d96f1b20f05647fe6000000000000000000000000000000000000000000000000000000000618e9c160000000000000000000000000000000000000000000000000000000000000004000000000000000000000000dac17f958d2ee523a2206206994597c13d831ec70000000000000000000000006b175474e89094c44da98b954eedeac495271d0f000000000000000000000000c02aaa39b223fe8d0a0e5c4f27ead9083c756cc2000000000000000000000000e0ad1806fd3e7edf6ff52fdb822432e847411033",
        "gasPrice": "163234583488",
        "gasPriceGwei": 163,
        "gasUsed": "222957",
        "type": 2,
        "maxFeePerGas": "189659376996",
        "maxPriorityFeePerGas": "1500000000",
        "baseFeePerGas": "161734583488",
        "transactionIndex": 2,
        "asset": "",
        "blockTimeStamp": "2021-11-12T16:52:11.000Z",
        "watchedAddress": "0x7a250d5630b4cf539739df2c5dacb4c659f2488d",
        "direction": "incoming",
        "counterparty": "0xE4f0f68B73D7c8ab9b7B96A3Fd1b079d5deAfD3F"
    }
}"""

FLATTENED_EXAMPLE = """
{
  "status": "pending",
  "monitorId": "Geth_1_C2_PROD",
  "monitorVersion": "0.101.0",
  "pendingTimeStamp": "2021-11-12T18:38:17.016Z",
  "pendingBlockNumber": 13602948,
  "hash": "0x55e1843fb90fcd59f7c64ef1573d941929dc6b45862befef97e60c897dcb6d46",
  "from": "0x10418327aF39cb42c2B98673462B601D662CD088",
  "to": "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D",
  "value": "56016835900000000",
  "gas": 185079,
  "nonce": 2,
  "blockHash": "",
  "blockNumber": "",
  "v": "0x25",
  "r": "0xdd88a871c9061b0350845f6b97f8f15d73c764cac04bb51286a48c88aa19d237",
  "s": "0x13718ea2019dec0da8b330577dc68c02160b5587fd1775d70158237eb2b6d2e",
  "input": "0x7ff36ab50000000000000000000000000000000000000000000000001b0db954c83d5695000000000000000000000000000000000000000000000000000000000000008000000000000000000000000010418327af39cb42c2b98673462b601d662cd08800000000000000000000000000000000000000000000000000000000618ebb260000000000000000000000000000000000000000000000000000000000000002000000000000000000000000c02aaa39b223fe8d0a0e5c4f27ead9083c756cc20000000000000000000000008b3192f5eebd8579568a2ed41e6feb402f93f73f",
  "gasPrice": "125400000000",
  "gasPriceGwei": 125,
  "type": 0,
  "asset": "",
  "watchedAddress": "0x7a250d5630b4cf539739df2c5dacb4c659f2488d",
  "direction": "incoming",
  "counterparty": "0x10418327aF39cb42c2B98673462B601D662CD088",
  "eventCode": "txPool",
  "timeStamp": "2021-11-12T18:38:17.016Z",
  "system": "ethereum",
  "network": "main",
  "contractCall": {
    "contractType": "Uniswap V2: Router 2",
    "contractAddress": "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D",
    "methodName": "swapExactETHForTokens",
    "params": {
      "amountOutMin": "1949417987509147285",
      "path": "",
      "to": "0x10418327aF39cb42c2B98673462B601D662CD088",
      "deadline": "1636743974"
    }
  }
}
"""

class TestBlocknativeEventProperlyPackaged(unittest.TestCase):
    def test_fields_are_present_upon_flattening(self):
        """unit test"""
        expected = json.loads(FLATTENED_EXAMPLE)
        event = json.loads(EXAMPLE_TRANSACTION)
        stream = BNStream('')
        flattened = stream.flatten_event_to_transaction(event)
        self.assertIsNotNone(flattened)
        for k in expected.keys():
            self.assertTrue(k in flattened, "expected field: "+k)

        not_expected = ['transaction', 'blockchain', 'dappId']
        for k in not_expected:
            self.assertFalse(k in flattened, "Did not expect: "+k)


if __name__ == '__main__':
    unittest.main()
