from dataclasses import dataclass

import grpc

from xpring.proto.account_info_pb2 import AccountInfo
from xpring.proto.get_fee_request_pb2 import GetFeeRequest
from xpring.proto.get_account_info_request_pb2 import GetAccountInfoRequest
from xpring.proto.payment_pb2 import Payment as PaymentProtobuf
from xpring.proto.transaction_pb2 import Transaction as TransactionProtobuf
from xpring.proto.signed_transaction_pb2 import SignedTransaction as SignedTransactionProtobuf
from xpring.proto.submit_signed_transaction_request_pb2 import SubmitSignedTransactionRequest
from xpring.proto.xrp_amount_pb2 import XRPAmount as XrpAmountProtobuf
from xpring.proto.xrp_ledger_pb2_grpc import XRPLedgerAPIStub
from xpring.types import Address, Amount, SignedTransaction, XrpAmount
from xpring.wallet import Wallet


@dataclass
class Account:
    balance: int
    sequence: int
    previous_txn_id: str
    previous_txn_lgr_seq: int


class Client:

    def __init__(self, grpc_client: XRPLedgerAPIStub):
        self.grpc_client = grpc_client

    @classmethod
    def from_url(cls, grpc_url: str = 'grpc.xpring.tech:80'):
        channel = grpc.insecure_channel(grpc_url)
        grpc_client = XRPLedgerAPIStub(channel)
        return cls(grpc_client)

    def _get_account_info(self, address: str) -> AccountInfo:
        request = GetAccountInfoRequest(address=address)
        return self.grpc_client.GetAccountInfo(request)

    def get_account_info(self, address: str) -> Account:
        response = self._get_account_info(address)
        return Account(
            int(response.balance.drops),
            int(response.sequence),
            response.previous_affecting_transaction_id,
            int(response.previous_affecting_transaction_ledger_version),
        )

    def get_balance(self, address: str) -> int:
        response = self._get_account_info(address)
        return int(response.balance.drops)

    def _get_fee(self) -> str:
        request = GetFeeRequest()
        return self.grpc_client.GetFee(request).amount.drops

    def get_fee(self) -> int:
        return int(self._get_fee())

    def submit(self, signed_transaction: SignedTransaction) -> None:
        # TODO: Diagnose fields ignored by the limited transaction protobuf.
        transaction = signed_transaction.transaction
        amount = transaction['Amount']
        if isinstance(amount, XrpAmount):
            amount_protobuf = XrpAmountProtobuf(drops=amount)
        else:
            raise NotImplementedError('FiatAmountProtobuf')
        payment_protobuf = PaymentProtobuf(
            xrp_amount=amount_protobuf, destination=transaction['Destination']
        )
        fee_protobuf = XrpAmountProtobuf(drops=transaction['Fee'])
        transaction_protobuf = TransactionProtobuf(
            account=transaction['Account'],
            fee=fee_protobuf,
            sequence=transaction['Sequence'],
            payment=payment_protobuf,
            signing_public_key_hex=signed_transaction.public_key.hex().upper(),
            last_ledger_sequence=transaction['LastLedgerSequence'],
        )
        signed_transaction_protobuf = SignedTransactionProtobuf(
            transaction=transaction_protobuf,
            transaction_signature_hex=signed_transaction.signature.hex().upper(
            ),
        )
        request = SubmitSignedTransactionRequest(
            signed_transaction=signed_transaction_protobuf
        )
        self.grpc_client.SubmitSignedTransaction(request)

    def send(
        self, wallet: Wallet, destination: Address, amount: Amount
    ) -> None:
        if isinstance(amount, int):
            # Let users pass XRP amounts as `int`s.
            amount = str(amount)
        account = self.get_account_info(wallet.address)
        transaction = {
            'Account': wallet.address,
            'Amount': amount,
            'Destination': destination,
            'Fee': str(self.get_fee()),
            'Sequence': account.sequence + 1,
            # TODO: Is there some way to make this optional or choose a better
            # number?
            'LastLedgerSequence': account.previous_txn_lgr_seq + 100000,
        }
        signed_transaction = wallet.sign_transaction(transaction)
        self.submit(signed_transaction)
