from sqlmodel import Session, select

from app.models import Stock, User
from app.security import hash_password

# VULN: well-known, weak seed credentials (documented starter accounts for
# this training app, not real secrets) -- nosec B105 x3 below.
SEED_USERS = [
    {
        "email": "admin@stonksco.test",
        "username": "admin",
        "password": "admin123",  # nosec B105
        "role": "admin",
        "balance": 100_000.0,
    },
    {
        "email": "alice@stonksco.test",
        "username": "alice",
        "password": "password123",  # nosec B105
        "role": "user",
        "balance": 10_000.0,
    },
    {
        "email": "bob@stonksco.test",
        "username": "bob",
        "password": "hunter2",  # nosec B105
        "role": "user",
        "balance": 10_000.0,
    },
]

SEED_STOCKS = [
    ("AAPL", "Apple Inc.", 195.30),
    ("MSFT", "Microsoft Corp", 415.20),
    ("GOOG", "Alphabet Inc.", 142.10),
    ("AMZN", "Amazon.com Inc", 178.40),
    ("TSLA", "Tesla Inc", 248.50),
    ("NVDA", "NVIDIA Corp", 875.30),
    ("META", "Meta Platforms", 485.60),
    ("NFLX", "Netflix Inc", 610.75),
    ("AMD", "Advanced Micro Devices", 165.20),
    ("GME", "GameStop Corp", 21.75),
    ("DOGE", "Dogecoin Holdings Inc", 4.20),
    ("BB", "BlackBerry Ltd", 3.15),
    ("PLTR", "Palantir Technologies", 28.90),
    ("COIN", "Coinbase Global", 245.10),
]


def seed_initial_data(session: Session) -> None:
    """Seed demo users and stocks if the database is empty."""
    if session.exec(select(User)).first() is not None:
        return

    for spec in SEED_USERS:
        session.add(
            User(
                email=spec["email"],
                username=spec["username"],
                password_hash=hash_password(spec["password"]),
                role=spec["role"],
                balance=spec["balance"],
            ),
        )

    for ticker, name, price in SEED_STOCKS:
        session.add(Stock(ticker=ticker, name=name, price=price))

    session.commit()
