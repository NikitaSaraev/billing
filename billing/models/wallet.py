import enum

from billing.extensions import db


class Wallet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, unique=True)
    current_value = db.Column(db.Float, default=0.0)

    user = db.relationship("User", lazy="joined", back_populates="wallet")
    history = db.relationship("WalletHistory", back_populates="wallet",  cascade="all,delete")


class EventEnum(enum.IntEnum):
    addition = 1
    transfer = 2


class WalletHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    wallet_id = db.Column(db.Integer, db.ForeignKey("wallet.id"), nullable=False)
    event_type = db.Column(db.Enum(EventEnum), nullable=False)
    quantity = db.Column(db.Float, nullable=False)

    wallet = db.relationship("Wallet", back_populates="history")
