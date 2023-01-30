from pyteal import *
from pyteal.ast.bytes import Bytes
from helpers import program


def approval_program():

    # locals
    local_opponent = Bytes("opponent")  # byteslice
    local_bet = Bytes("bet")  # uint64
    local_private_play = Bytes("private_play")  # byteslice
    local_play = Bytes("play")  # byteslice

    op_challenge = Bytes("challenge")
    op_accept = Bytes("accept")
    op_reveal = Bytes("reveal")

    # Subroutines 
    
    @Subroutine(TealType.none)
    def reset(account: Expr):
        return Seq(
            App.localPut(account, local_opponent, Bytes("")),
            App.localPut(account, local_bet, Int(0)),
            App.localPut(account, local_private_play, Bytes("")),
            App.localPut(account, local_play, Bytes("")),
        )


    @Subroutine(TealType.none)
    def create_challenge():
        return Reject()

    @Subroutine(TealType.none)
    def accept_challenge():
        return Reject()


    @Subroutine(TealType.none)
    def reveal():
        return Reject()

    return program.event(
        init=Approve(),
        opt_in=Seq(
            reset(Int(0)),
            Approve(),
        ),
        no_op=Seq(
            Cond(
                [
                    Txn.application_args[0] == op_challenge,
                    create_challenge(),
                ],
                [
                    Txn.application_args[0] == op_accept,
                    accept_challenge(),
                ],
                [
                    Txn.application_args[0] == op_reveal,
                    reveal(),
                ],
            ),
            Reject(),
        ),
    )


def clear_state_program():
    return Int(0)


if __name__ == "__main__":
    with open("vote_approval.teal", "w") as f:
        compiled = compileTeal(approval_program(), Mode.Application, version=6)
        f.write(compiled)

    with open("vote_clear_state.teal", "w") as f:
        compiled = compileTeal(clear_state_program(), Mode.Application, version=6)
        f.write(compiled)