from billing.models import User, Wallet


def test_wallet_add_funds(wallet_headers, client, db):
    rep = client.post('/wallet/add',
                      headers=wallet_headers,
                      json={'funds': -1}
                      )
    assert rep.status_code == 400
    funds_amount = 5
    rep = client.post('/wallet/add',
                      headers=wallet_headers,
                      json={'funds': funds_amount}
                      )

    assert rep.status_code == 200

    user = db.session.query(User).filter_by(username='w1').first()
    wallet = user.wallet[0]
    assert wallet.current_value == funds_amount
    assert len(wallet.history) == 1


def test_transfer_funds(wallet_headers, client, db):
    rep = client.post('/wallet/transfer',
                      headers=wallet_headers,
                      json={'funds': 1,
                            'username': 'w2'}
                      )
    assert rep.status_code == 400

    u = User(
        username='w2',
        email='w2@email.com',
        password='wallet'
    )
    w = Wallet(user=u)

    db.session.add(u)
    db.session.add(w)
    db.session.commit()

    rep = client.post('/wallet/transfer',
                      headers=wallet_headers,
                      json={'funds': 1,
                            'username': 'w2'}
                      )
    assert rep.status_code == 406

    wal = db.session.query(User).filter_by(username='w1').first().wallet[0]
    wal.current_value = 10
    db.session.add(wal)
    db.session.commit()

    rep = client.post('/wallet/transfer',
                      headers=wallet_headers,
                      json={'funds': 1,
                            'username': 'w2'}
                      )
    assert rep.status_code == 200
