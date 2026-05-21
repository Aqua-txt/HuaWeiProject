"""Add realistic order data and adjust user creation times."""
import os, sys, uuid, random
from datetime import timedelta as dt_timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app import app
from models import db, User, Product, Order, beijing_now

test_ids = [f'2024302111{str(i+1).zfill(3)}' for i in range(12)]


_order_counter = 0
def make_order_no():
    global _order_counter
    _order_counter += 1
    return f"NO{int(beijing_now().timestamp()*1000)}{_order_counter:04d}{random.randint(10,99)}"


def main():
    with app.app_context():
        users = User.query.filter(User.student_id.in_(test_ids)).order_by(User.student_id).all()
        if len(users) != 12:
            print(f"ERROR: expected 12 users, found {len(users)}")
            return

        # --- 1. Adjust user creation times: spread over past 90 days ---
        now = beijing_now()
        for i, u in enumerate(users):
            # evenly spread: oldest ~90 days ago, newest ~2 days ago
            days_ago = 90 - (i * 7) + random.randint(-2, 2)
            days_ago = max(2, min(92, days_ago))
            u.created_at = now - dt_timedelta(days=days_ago)
        db.session.commit()
        print("Updated user creation times")

        # --- 2. Clear existing orders for test users ---
        test_user_ids = [u.id for u in users]
        from models import Review
        # delete reviews linked to these orders
        existing_orders = Order.query.filter(
            db.or_(Order.buyer_id.in_(test_user_ids), Order.seller_id.in_(test_user_ids))
        ).all()
        existing_order_ids = [o.id for o in existing_orders]
        if existing_order_ids:
            Review.query.filter(Review.order_id.in_(existing_order_ids)).delete(synchronize_session=False)
            for o in existing_orders:
                db.session.delete(o)
            db.session.commit()
            print(f"Cleared {len(existing_order_ids)} existing orders and their reviews")

        # --- 3. Create orders between users ---
        statuses = ['已完成', '已完成', '已完成', '已付款', '已付款', '待付款', '已退款']
        # weighted: mostly completed/paid transactions look realistic

        all_products = Product.query.filter(Product.seller_id.in_(test_user_ids)).all()
        # group products by seller
        seller_products = {}
        for p in all_products:
            seller_products.setdefault(p.seller_id, []).append(p)

        orders_created = 0
        # create 2-5 orders per user as buyer
        for buyer in users:
            buyer_products = [p for p in all_products if p.seller_id == buyer.id]
            buyer_products_ids = {p.id for p in buyer_products}

            # pick 2-5 other users to buy from
            other_sellers = [u for u in users if u.id != buyer.id]
            num_buys = random.randint(2, 5)
            sellers = random.sample(other_sellers, min(num_buys, len(other_sellers)))

            for seller in sellers:
                seller_prods = [p for p in all_products if p.seller_id == seller.id]
                if not seller_prods:
                    continue
                product = random.choice(seller_prods)

                status = random.choice(statuses)
                # order date between seller creation and now
                earliest = max(buyer.created_at, seller.created_at, product.created_at) + dt_timedelta(days=1)
                days_range = max(1, (now - earliest).days)
                order_date = earliest + dt_timedelta(days=random.randint(0, days_range))

                order = Order(
                    order_no=make_order_no(),
                    buyer_id=buyer.id,
                    seller_id=seller.id,
                    product_id=product.id,
                    amount=product.price,
                    status=status,
                    created_at=order_date,
                    updated_at=order_date,
                )

                if status == '已退款':
                    order.refund_status = '已退款'
                    order.refund_reason = random.choice([
                        '商品与描述不符', '不想要了', '买错了',
                    ])

                db.session.add(order)
                orders_created += 1

        db.session.commit()
        print(f"Created {orders_created} orders")

        # --- 4. Add reviews for completed orders ---
        completed = Order.query.filter(
            Order.buyer_id.in_(test_user_ids),
            Order.status == '已完成'
        ).all()

        comments_pool = [
            '卖家发货很快，商品质量好！',
            '沟通顺畅，物美价廉，好评。',
            '东西不错，就是包装有点简陋。',
            '性价比很高，推荐购买。',
            '跟描述一致，很满意。',
            '买家爽快，交易愉快。',
            '稍微有点使用痕迹但整体可以接受。',
            '不错，同学之间交易就是方便。',
        ]

        review_count = 0
        for order in completed:
            if random.random() > 0.8:
                continue

            cs = random.choices([5, 4, 3, 2, 1], weights=[45, 30, 18, 5, 2])[0]
            ds = random.choices([5, 4, 3, 2, 1], weights=[40, 32, 18, 7, 3])[0]
            ss = random.choices([5, 4, 3, 2, 1], weights=[42, 28, 20, 6, 4])[0]

            review = Review(
                order_id=order.id,
                reviewer_id=order.buyer_id,
                reviewee_id=order.seller_id,
                communication_score=cs,
                description_score=ds,
                speed_score=ss,
                comment=random.choice(comments_pool),
                created_at=order.created_at + dt_timedelta(days=random.randint(0, 3)),
            )
            db.session.add(review)
            review_count += 1

        db.session.commit()
        print(f"Created {review_count} reviews")

        # --- 5. Update user credit scores ---
        for u in users:
            seller_reviews = Review.query.filter_by(reviewee_id=u.id).all()
            if seller_reviews:
                avg = 0
                for r in seller_reviews:
                    overall = r.communication_score * 0.2 + r.description_score * 0.5 + r.speed_score * 0.3
                    avg += overall
                avg /= len(seller_reviews)
                u.credit_score = round(avg, 2)
                u.credit_count = len(seller_reviews)
            else:
                u.credit_score = 5.0
                u.credit_count = 0
        db.session.commit()
        print("Updated credit scores")

        # summary
        total_orders = Order.query.filter(
            db.or_(Order.buyer_id.in_(test_user_ids), Order.seller_id.in_(test_user_ids))
        ).count()
        total_reviews = Review.query.filter(
            db.or_(Review.reviewer_id.in_(test_user_ids), Review.reviewee_id.in_(test_user_ids))
        ).count()
        print(f"\nDone: {total_orders} orders, {total_reviews} reviews across 12 users")


if __name__ == '__main__':
    main()
