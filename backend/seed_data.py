"""Reduce test data: keep only 3 products + 3 wanteds per test user."""
import os, sys, uuid, shutil, json, random
from datetime import timedelta as dt_timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app import app
from models import db, User, Product, Wanted, beijing_now

SOURCE_DIR = r"F:\Pictures"
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')

image_files = [f for f in os.listdir(SOURCE_DIR) if os.path.splitext(f)[1].lower() in {'.png','.jpg','.jpeg','.gif','.webp'}]

# only 3 per user
product_templates = [
    {"title": "高等数学（第七版）上下册", "category": "教材", "price": 25, "condition": "轻微使用痕迹", "desc": "考研用过，笔记较详细，无缺页。"},
    {"title": "罗技MX Master 3无线鼠标", "category": "数码", "price": 280, "condition": "轻微使用痕迹", "desc": "用了三个月，功能正常，配件齐全。"},
    {"title": "宿舍用迷你小风扇", "category": "生活", "price": 29, "condition": "几乎全新", "desc": "USB供电，三档风速，静音设计。"},
]

wanted_templates = [
    {"title": "求购二手大学英语四级真题", "category": "教材", "budget_min": 5, "budget_max": 20, "cond": "", "desc": "希望有真题和解析即可。"},
    {"title": "求购二手iPad（学习用）", "category": "数码", "budget_min": 500, "budget_max": 1500, "cond": "轻微使用痕迹", "desc": "支持Apple Pencil，屏幕无划痕。"},
    {"title": "求购瑜伽垫", "category": "生活", "budget_min": 15, "budget_max": 40, "cond": "", "desc": "宿舍健身用，厚度适中不硌手。"},
]

test_ids = [f'2024302111{str(i+1).zfill(3)}' for i in range(12)]


def copy_image(src_path):
    ext = os.path.splitext(src_path)[1].lower()
    new_name = f"{uuid.uuid4().hex}{ext}"
    shutil.copyfile(src_path, os.path.join(UPLOAD_DIR, new_name))
    return new_name


def main():
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    with app.app_context():
        users = User.query.filter(User.student_id.in_(test_ids)).order_by(User.student_id).all()
        user_ids = [u.id for u in users]

        # --- collect old images before deleting ---
        old_products = Product.query.filter(Product.seller_id.in_(user_ids)).all()
        old_images = set()
        for p in old_products:
            try:
                imgs = json.loads(p.images)
                for img in imgs:
                    old_images.add(img)
            except:
                pass

        # --- delete old records ---
        from models import WantedResponse
        # delete wanted responses linked to test users' wanteds
        test_wanted_ids = [w.id for w in Wanted.query.filter(Wanted.user_id.in_(user_ids)).all()]
        if test_wanted_ids:
            WantedResponse.query.filter(WantedResponse.wanted_id.in_(test_wanted_ids)).delete()
        WantedResponse.query.filter(WantedResponse.responder_id.in_(user_ids)).delete()
        wc = Wanted.query.filter(Wanted.user_id.in_(user_ids)).delete()
        pc = Product.query.filter(Product.seller_id.in_(user_ids)).delete()
        db.session.commit()
        print(f"Cleaned: {pc} products, {wc} wanteds")
        # keep images still used by other products (non-test users)
        remaining_imgs = set()
        all_products = Product.query.all()
        for p in all_products:
            try:
                for img in json.loads(p.images):
                    remaining_imgs.add(img)
            except:
                pass

        removed_imgs = 0
        for img in old_images:
            if img not in remaining_imgs:
                path = os.path.join(UPLOAD_DIR, img)
                if os.path.exists(path):
                    os.remove(path)
                    removed_imgs += 1
        print(f"Removed {removed_imgs} orphaned images")

        # --- create new ---
        total_p, total_w = 0, 0
        for user in users:
            for tmpl in product_templates:
                img = copy_image(os.path.join(SOURCE_DIR, random.choice(image_files)))
                price = round(tmpl["price"] * random.uniform(0.8, 1.3), 2)
                p = Product(
                    seller_id=user.id, title=tmpl["title"], description=tmpl["desc"],
                    price=price, category=tmpl["category"], condition=tmpl["condition"],
                    images=json.dumps([img]), status='上架',
                    created_at=beijing_now() - dt_timedelta(days=random.randint(1, 30)),
                )
                db.session.add(p)
                total_p += 1

            for tmpl in wanted_templates:
                bmin = round(tmpl["budget_min"] * random.uniform(0.8, 1.2))
                bmax = round(tmpl["budget_max"] * random.uniform(0.8, 1.2))
                if bmin > bmax:
                    bmin, bmax = bmax, bmin
                w = Wanted(
                    user_id=user.id, title=tmpl["title"], description=tmpl["desc"],
                    budget_min=bmin, budget_max=bmax, category=tmpl["category"],
                    desired_condition=tmpl["cond"], status='进行中',
                    created_at=beijing_now() - dt_timedelta(days=random.randint(1, 20)),
                )
                db.session.add(w)
                total_w += 1

        db.session.commit()
        print(f"Created: {total_p} products, {total_w} wanteds across {len(users)} users")


if __name__ == '__main__':
    main()
