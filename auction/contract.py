from pyteal import *
from beaker import *


class Auction(Application):

    # Global state 

    
    # 2 Global Bytes 
    # owner : address 
    owner = ApplicationStateValue(stack_type=TealType.bytes)
    # highest_bidder : address
    highest_bidder = ApplicationStateValue(stack_type=TealType.bytes)

    # 2 Global Ints 
    # highest_bid : uint64
    highest_bid = ApplicationStateValue(stack_type=TealType.uint64)
    # bid_end : uint64 
    auction_end = ApplicationStateValue(stack_type=TealType.uint64)


    # 1. Create the auction contract
     
    @create # this decorator tells Beaker this function .. 
    def create(self):
        return Seq(
            self.owner.set(Txn.sender()), # Person who initialize & sender() returns the Pyteal expression 
            self.highest_bidder.set(Bytes("")), 
            self.highest_bid.set(Int(0)),
            self.bid_end.set(Int(0))
        )


    # 2. Start_auction 

    #  * Length : duration of the auction *
    @external 
    def start_auction(self, payment: abi.PaymentTransaction, length : abi.Uint64, start_price: abi.Uint64):  
        # fund the contract with 0.1 ALGO = 0.1 * 10^6 microalgos = 100 000 microalgos
        # set the bid_end to a certain time
        # fix a bid start amount 
        payment = payment.get()
        return Seq(
            Assert(payment.receiver() == Global.current_application_address()),  # Checking that payment is made to this contract 
            Assert(payment.amount() == Int(100_000)),
            # set the bid_end 
            self.bid_end.set(Global.latest_timestamp() + length.get() ),
            self.highest_bid.set(start_price.get())
        )
    
    # 3. Handle incoming bids 

    @internal(TealType.none)
    # Pay back to user if not highest bid 

    def pay(self, receiver: Expr, amount: Expr):
        return Seq(
            InnerTxnBuilder.Begin(),
            InnerTxnBuilder.SetFields(
                {
                    TxnField.type_enum: TxnType.Payment,
                    TxnField.receiver: receiver, 
                    TxnField.amount : amount,
                    TxnField.fee : Int(0),
                }
            ),
            InnerTxnBuilder.Submit(),
        )


    @external 
    def bidding(self, payment: abi.PaymentTransaction):
        payment = payment.get()

        return Seq(
            Assert(Global.latest_timestamp() < self.auction_end.get()),
            # Verifying payment transaction 
            Assert(payment.amount() > self.highest_bid.get()),
            Assert(Txn.sender() == payment.sender()),
            # Return previous bid 
            If(self.highest_bidder.get() != Bytes("") , self.pay(self.highest_bidder.get(), self.highest_bid.get())),
            # Set global state
            self.highest_bidder.set(payment.sender()),
            self.highest_bid.set(payment.amount()),
        )


    # 3. End_auction 



