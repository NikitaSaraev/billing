from flask import request, jsonify, Blueprint, current_app as app
from flask_jwt_extended import jwt_required, get_jwt_identity
from billing.models import WalletHistory, Wallet, EventEnum, User
from billing.extensions import db, apispec
from billing.wallet import helpers

blueprint = Blueprint("wallet", __name__, url_prefix="/wallet")


@blueprint.route('/add', methods=["POST"])
@jwt_required
def add_funds():
    funds = request.json.get('funds')
    if not helpers.validate_funds(funds):
        return jsonify({'message': 'validation failed'}), 400

    funds_to_add = float(funds)
    wallet = db.session.query(Wallet).filter_by(user_id=get_jwt_identity()).first()
    history = WalletHistory(wallet=wallet, event_type=EventEnum.addition, quantity=funds_to_add)
    wallet.current_value += funds_to_add
    db.session.add(wallet)
    db.session.add(history)
    db.session.commit()
    return jsonify({'message': 'funds added'}), 200


@blueprint.route('/transfer', methods=["POST"])
@jwt_required
def transfer_funds_by_name():
    funds = request.json.get('funds')
    uname = request.json.get('username')
    user = db.session.query(User).filter_by(username=uname).first()
    current_user = db.session.query(User).filter_by(id=get_jwt_identity()).first()

    if not all([helpers.validate_funds(funds), helpers.validate_user(user, current_user)]):
        return jsonify({'message': 'validation failed'}), 400

    funds_to_add = float(funds)
    wallet = db.session.query(Wallet).filter_by(user_id=get_jwt_identity()).with_for_update().first()
    if wallet.current_value < funds_to_add:
        db.session.rollback()
        return jsonify({'message': 'not enough funds'}), 406

    hist = WalletHistory(wallet=wallet, event_type=EventEnum.transfer, quantity=-funds_to_add)
    wallet.current_value -= funds_to_add
    wallet_to_add = user.wallet[0]
    add_hist = WalletHistory(wallet=wallet_to_add, event_type=EventEnum.transfer, quantity=funds_to_add)
    wallet_to_add.current_value += funds_to_add
    db.session.add(wallet)
    db.session.add(hist)
    db.session.add(add_hist)
    db.session.add(wallet_to_add)
    db.session.commit()
    return jsonify({'message': f'funds transferred to {uname}'}), 200


@blueprint.before_app_first_request
def register_views():
    apispec.spec.path(view=add_funds, app=app)
