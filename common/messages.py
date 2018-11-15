class Messages(object):
    AUTH_REQUEST = "hi here is the payment information"
    AUTH_RESPONSE = "cool, here is my certificate"
    AUTH_DATA = "everything is good"

    TRANSACTION_VERIFIED = "Transaction verified!"


class ErrorMessages(object):
    INVALID_CARD = "Invalid Card ID"
    INVALID_AUTH_REQUEST = 'unknown authrequest'
    MISMATCH_DIGEST = "message went wrong during transmission, hashes don't match"

    FAILED_CONNECT_BANK = "Can't communicate with issue banker"
    FAILED_CONNECT_GATEWAY = "Can't communicate with gateway"
    FAILED_BANKING_AUTHORIZE = "Failed to authorize with bank"
    FAILED_RENEW_CERTIFICATE = "{} Failed to renew certificate"

    FAILED_VERIFY_DATA = "Data went wrong during transmission, failed to verify signature"
    FAILED_VERIFY_TRANSACTION = "the otp does not matches"
    TRANSACTION_FAILED = "Transaction Failed!"
