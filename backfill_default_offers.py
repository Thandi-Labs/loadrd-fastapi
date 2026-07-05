"""One-off backfill: give every existing user the default offers they are missing.

Idempotent — matches on USSD code per user, so it can be re-run safely.

Usage:
    python backfill_default_offers.py            # show what would be inserted
    python backfill_default_offers.py --apply    # actually insert
"""
import sys

from database import SessionLocal
from models import Users, Offers, OfferCategory
from routers.users import DEFAULT_OFFERS


def backfill(apply: bool):
    db = SessionLocal()
    try:
        users = db.query(Users).all()
        total_inserted = 0

        for user in users:
            existing_ussds = {
                ussd for (ussd,) in
                db.query(Offers.ussd).filter(Offers.user_id == user.id).all()
            }
            missing = [o for o in DEFAULT_OFFERS
                       if o['ussd'] not in existing_ussds]

            if not missing:
                continue

            print(f"user {user.id} ({user.username}): adding {len(missing)} offer(s)")
            for offer in missing:
                print(f"    {offer['offer_name']} | {offer['ussd']} | KES {offer['amount']}")
                if apply:
                    db.add(Offers(
                        **offer,
                        active=True,
                        category=OfferCategory.DATA,
                        user_id=user.id,
                    ))
            total_inserted += len(missing)

        if apply:
            db.commit()
            print(f"\nDone: inserted {total_inserted} offer(s) for {len(users)} user(s).")
        else:
            print(f"\nDry run: would insert {total_inserted} offer(s) for {len(users)} user(s). "
                  f"Re-run with --apply to write.")
    finally:
        db.close()


if __name__ == '__main__':
    backfill(apply='--apply' in sys.argv)
