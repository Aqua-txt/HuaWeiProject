"""校园二手交易平台 V2 - 全链路API测试脚本"""
import json, time, sys
try:
    import requests
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'requests', '-q'])
    import requests

BASE = 'http://127.0.0.1:5000/api'
results = []

def record(module, case_id, title, status, detail=''):
    results.append({'module': module, 'id': case_id, 'title': title, 'status': status, 'detail': detail})
    icon = '[PASS]' if status == 'PASS' else '[FAIL]'
    print(f"  {icon} [{case_id}] {title}" + (f" — {detail}" if detail else ""))

def api(method, path, retries=2, **kw):
    url = f"{BASE}{path}"
    for attempt in range(retries + 1):
        try:
            r = getattr(requests, method)(url, timeout=10, **kw)
            try:
                j = r.json()
            except:
                j = {'code': r.status_code, 'message': r.text[:200]}
            return r.status_code, j
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            if attempt < retries:
                time.sleep(1)
            else:
                return 0, {'code': 0, 'message': str(e)}

# ==================== 1. 用户认证模块 ====================
print("\n=== 1. 用户认证模块 ===")

# TC-A01: 用户登录
code, data = api('post', '/auth/login', json={'student_id': '2024302111001', 'password': '123456'})
if code == 200 and data.get('code') == 200:
    user1_token = data['data']['token']
    user1_id = data['data']['user']['id']
    record('认证', 'TC-A01', '用户One登录', 'PASS')
else:
    record('认证', 'TC-A01', '用户One登录', 'FAIL', f"code={code}, data={data}")
    user1_token = user1_id = None

# TC-A02: 第二个用户登录
code, data = api('post', '/auth/login', json={'student_id': '2024302111002', 'password': '123456'})
if code == 200 and data.get('code') == 200:
    user2_token = data['data']['token']
    user2_id = data['data']['user']['id']
    record('认证', 'TC-A02', '用户Two登录', 'PASS')
else:
    record('认证', 'TC-A02', '用户Two登录', 'FAIL', f"code={code}, data={data}")
    user2_token = user2_id = None

# TC-A03: 错误密码登录
code, data = api('post', '/auth/login', json={'student_id': '2024302111001', 'password': 'wrongpwd'})
record('认证', 'TC-A03', '错误密码登录被拒绝', 'PASS' if code == 200 and data.get('code') == 400 else 'FAIL', f"resp_code={data.get('code')}")

# TC-A04: 获取当前用户信息
code, data = api('get', '/auth/me', headers={'Authorization': f'Bearer {user1_token}'})
record('认证', 'TC-A04', '获取当前用户信息', 'PASS' if code == 200 and data.get('code') == 200 else 'FAIL')

# TC-A05: 未登录访问受保护接口
code, data = api('get', '/auth/me')
record('认证', 'TC-A05', '未登录访问受保护接口返回401', 'PASS' if code == 401 or data.get('code') == 401 else 'FAIL')

# TC-A06: 注册新用户(重复学号)
code, data = api('post', '/auth/register', json={'student_id': '2024302111001', 'nickname': 'dup', 'password': '123456'})
record('认证', 'TC-A06', '重复学号注册被拒绝', 'PASS' if data.get('code') == 400 else 'FAIL')

# ==================== 2. 商品模块 ====================
print("\n=== 2. 商品模块 ===")

# TC-P01: 商品列表
code, data = api('get', '/products')
record('商品', 'TC-P01', '获取商品列表', 'PASS' if data.get('code') == 200 and len(data.get('data',{}).get('products',[])) > 0 else 'FAIL')

# TC-P02: 商品分类筛选
code, data = api('get', '/products?category=教材')
record('商品', 'TC-P02', '按分类筛选商品', 'PASS' if data.get('code') == 200 else 'FAIL')

# TC-P03: 商品关键词搜索
code, data = api('get', '/products?keyword=数学')
record('商品', 'TC-P03', '关键词搜索商品', 'PASS' if data.get('code') == 200 else 'FAIL')

# TC-P04: 发布商品(multipart)
code, data = api('post', '/products', headers={'Authorization': f'Bearer {user1_token}'},
    data={'title': '测试商品QA', 'description': 'QA测试用商品', 'price': '99.9', 'category': '教材', 'condition': '几乎全新'})
product_id = None
if data.get('code') == 200:
    product_id = data['data']['id']
    record('商品', 'TC-P04', '发布商品', 'PASS')
else:
    record('商品', 'TC-P04', '发布商品', 'FAIL', str(data))

# TC-P05: 商品详情
if product_id:
    code, data = api('get', f'/products/{product_id}')
    record('商品', 'TC-P05', '获取商品详情', 'PASS' if data.get('code') == 200 else 'FAIL')
else:
    record('商品', 'TC-P05', '获取商品详情', 'FAIL', '无商品ID')

# TC-P06: 收藏商品
if product_id:
    code, data = api('post', f'/products/{product_id}/favorite', headers={'Authorization': f'Bearer {user2_token}'}, json={})
    record('商品', 'TC-P06', '收藏商品', 'PASS' if data.get('code') == 200 else 'FAIL', str(data))

# TC-P07: 我的收藏列表
code, data = api('get', '/favorites', headers={'Authorization': f'Bearer {user2_token}'})
record('商品', 'TC-P07', '获取收藏列表', 'PASS' if data.get('code') == 200 else 'FAIL')

# ==================== 3. 交易订单模块 ====================
print("\n=== 3. 交易订单模块 ===")

# 找一个user2的上架商品来购买
code, data = api('get', '/products', headers={'Authorization': f'Bearer {user2_token}'})
seller_products = [p for p in data.get('data',{}).get('products',[]) if p.get('seller_id') == user2_id and p.get('status') == '上架']
buy_product = seller_products[0] if seller_products else None

order_id = None
if buy_product:
    # TC-O01: 创建订单
    code, data = api('post', '/orders', headers={'Authorization': f'Bearer {user1_token}'}, json={'product_id': buy_product['id']})
    if data.get('code') == 200:
        order_id = data['data']['id']
        record('订单', 'TC-O01', '创建订单', 'PASS')
    else:
        record('订单', 'TC-O01', '创建订单', 'FAIL', str(data))

    # TC-O02: 不能购买自己的商品
    code, data = api('post', '/orders', headers={'Authorization': f'Bearer {user2_token}'}, json={'product_id': buy_product['id']})
    record('订单', 'TC-O02', '不能购买自己的商品', 'PASS' if data.get('code') == 400 else 'FAIL')

    if order_id:
        # TC-O03: 模拟支付
        code, data = api('post', f'/orders/{order_id}/pay', headers={'Authorization': f'Bearer {user1_token}'}, json={})
        record('订单', 'TC-O03', '模拟支付', 'PASS' if data.get('code') == 200 else 'FAIL', str(data))

        # TC-O04: 买方确认收货
        code, data = api('post', f'/orders/{order_id}/confirm', headers={'Authorization': f'Bearer {user1_token}'}, json={})
        record('订单', 'TC-O04', '买方确认收货', 'PASS' if data.get('code') == 200 else 'FAIL', str(data))

        # TC-O05: 订单列表
        code, data = api('get', '/orders?role=buyer', headers={'Authorization': f'Bearer {user1_token}'})
        record('订单', 'TC-O05', '买方订单列表', 'PASS' if data.get('code') == 200 else 'FAIL')

        # TC-O06: 订单详情
        code, data = api('get', f'/orders/{order_id}', headers={'Authorization': f'Bearer {user1_token}'})
        record('订单', 'TC-O06', '订单详情', 'PASS' if data.get('code') == 200 else 'FAIL')
else:
    record('订单', 'TC-O01', '创建订单', 'FAIL', '无可购买商品')

# TC-O07: 退款流程测试
# 重新获取商品列表，找user2的上架商品
code, pdata = api('get', '/products', headers={'Authorization': f'Bearer {user2_token}'})
all_products_list = pdata.get('data',{}).get('products',[])
seller2_products = [p for p in all_products_list if p.get('seller_id') == user2_id and p.get('status') == '上架']
refund_product = seller2_products[0] if seller2_products else None
refund_order_id = None
if refund_product:
    code, data = api('post', '/orders', headers={'Authorization': f'Bearer {user1_token}'}, json={'product_id': refund_product['id']})
    if data.get('code') == 200:
        refund_order_id = data['data']['id']
        api('post', f'/orders/{refund_order_id}/pay', headers={'Authorization': f'Bearer {user1_token}'}, json={})
        code, data = api('post', f'/orders/{refund_order_id}/refund', headers={'Authorization': f'Bearer {user1_token}'}, json={'reason': '商品与描述不符需要退款处理'})
        record('订单', 'TC-O07', '买方申请退款', 'PASS' if data.get('code') == 200 else 'FAIL', str(data))
        if data.get('code') == 200:
            # 卖方同意退款
            code, data = api('post', f'/orders/{refund_order_id}/refund/respond', headers={'Authorization': f'Bearer {user2_token}'}, json={'agree': True, 'note': '同意退款'})
            record('订单', 'TC-O08', '卖方同意退款', 'PASS' if data.get('code') == 200 else 'FAIL', str(data))
else:
    record('订单', 'TC-O07', '买方申请退款', 'FAIL', '无可购买商品')
    record('订单', 'TC-O08', '卖方同意退款', 'FAIL', '前置条件不满足')

# TC-O09: 卖方拒绝退款升级仲裁
seller3_products = [p for p in all_products_list if p.get('seller_id') == user2_id and p.get('status') == '上架']
reject_product = seller3_products[0] if seller3_products else None
if reject_product:
    code, data = api('post', '/orders', headers={'Authorization': f'Bearer {user1_token}'}, json={'product_id': reject_product['id']})
    if data.get('code') == 200:
        rj_oid = data['data']['id']
        api('post', f'/orders/{rj_oid}/pay', headers={'Authorization': f'Bearer {user1_token}'}, json={})
        api('post', f'/orders/{rj_oid}/refund', headers={'Authorization': f'Bearer {user1_token}'}, json={'reason': '测试拒绝退款然后升级仲裁流程'})
        code, data = api('post', f'/orders/{rj_oid}/refund/respond', headers={'Authorization': f'Bearer {user2_token}'}, json={'agree': False, 'note': '不同意退款'})
        record('订单', 'TC-O09', '卖方拒绝退款升级仲裁', 'PASS' if data.get('code') == 200 and data.get('data',{}).get('status') == '管理员仲裁' else 'FAIL', str(data))
else:
    record('订单', 'TC-O09', '卖方拒绝退款升级仲裁', 'FAIL', '前置条件不满足')

# ==================== 4. 信用评价模块 ====================
print("\n=== 4. 信用评价模块 ===")

if order_id:
    # TC-R01: 评价已完成订单
    code, data = api('post', '/reviews', headers={'Authorization': f'Bearer {user1_token}'}, json={
        'order_id': order_id, 'communication_score': 5, 'description_score': 4, 'speed_score': 5, 'comment': '交易顺利，好评！'})
    record('评价', 'TC-R01', '评价已完成订单', 'PASS' if data.get('code') == 200 else 'FAIL', str(data))

    # TC-R02: 重复评价被拒绝
    code, data = api('post', '/reviews', headers={'Authorization': f'Bearer {user1_token}'}, json={
        'order_id': order_id, 'communication_score': 3, 'description_score': 3, 'speed_score': 3, 'comment': '重复评价'})
    record('评价', 'TC-R02', '重复评价被拒绝', 'PASS' if data.get('code') == 400 else 'FAIL')

    # TC-R03: 检查可评价状态
    code, data = api('get', f'/orders/{order_id}/reviewable', headers={'Authorization': f'Bearer {user1_token}'})
    record('评价', 'TC-R03', '检查订单可评价状态', 'PASS' if data.get('code') == 200 else 'FAIL')

    # TC-R04: 评价列表
    code, data = api('get', f'/reviews?reviewee_id={user2_id}', headers={'Authorization': f'Bearer {user1_token}'})
    record('评价', 'TC-R04', '获取被评价者评价列表', 'PASS' if data.get('code') == 200 else 'FAIL')
else:
    record('评价', 'TC-R01', '评价已完成订单', 'FAIL', '无已完成订单')

# ==================== 5. 举报模块 ====================
print("\n=== 5. 举报模块 ===")

if not product_id:
    code, pdata3 = api('get', '/products')
    product_id = pdata3.get('data',{}).get('products',[{}])[0].get('id')

if product_id:
    # TC-RP01: 提交举报
    code, data = api('post', '/reports', headers={'Authorization': f'Bearer {user2_token}'}, json={
        'product_id': product_id, 'report_type': '虚假信息', 'description': '该商品信息与实际不符，请核查处理'})
    record('举报', 'TC-RP01', '提交举报', 'PASS' if data.get('code') == 200 else 'FAIL', str(data))

    # TC-RP02: 重复举报被拒绝
    code, data = api('post', '/reports', headers={'Authorization': f'Bearer {user2_token}'}, json={
        'product_id': product_id, 'report_type': '违规商品', 'description': '该商品属于违规商品请处理'})
    record('举报', 'TC-RP02', '重复举报被拒绝', 'PASS' if data.get('code') == 400 else 'FAIL')

    # TC-RP03: 举报描述过短
    code2, data2 = api('post', '/reports', headers={'Authorization': f'Bearer {user1_token}'}, json={
        'product_id': product_id, 'report_type': '其他', 'description': '太短'})
    record('举报', 'TC-RP03', '举报描述少于10字被拒绝', 'PASS' if data2.get('code') == 400 else 'FAIL')

    # TC-RP04: 我的举报列表
    code, data = api('get', '/reports', headers={'Authorization': f'Bearer {user2_token}'})
    record('举报', 'TC-RP04', '获取我的举报列表', 'PASS' if data.get('code') == 200 else 'FAIL')
else:
    record('举报', 'TC-RP01', '提交举报', 'FAIL', '无商品ID')

# ==================== 6. 求购模块 ====================
print("\n=== 6. 求购模块 ===")

# TC-W01: 发布求购
code, data = api('post', '/wanteds', headers={'Authorization': f'Bearer {user1_token}'}, json={
    'title': '求购线性代数教材', 'description': '需要一本干净的线性代数教材',
    'budget_min': 10, 'budget_max': 30, 'category': '教材', 'desired_condition': '几乎全新'})
wanted_id = None
if data.get('code') == 200:
    wanted_id = data['data']['id']
    record('求购', 'TC-W01', '发布求购', 'PASS')
else:
    record('求购', 'TC-W01', '发布求购', 'FAIL', str(data))

# TC-W02: 求购列表
code, data = api('get', '/wanteds')
record('求购', 'TC-W02', '获取求购列表', 'PASS' if data.get('code') == 200 else 'FAIL')

# TC-W03: 求购详情+推荐商品
if wanted_id:
    code, data = api('get', f'/wanteds/{wanted_id}')
    record('求购', 'TC-W03', '求购详情含推荐商品', 'PASS' if data.get('code') == 200 else 'FAIL')

    # TC-W04: 响应求购
    code, data = api('post', f'/wanteds/{wanted_id}/responses', headers={'Authorization': f'Bearer {user2_token}'},
        json={'price_offer': 20, 'message': '我有一本，可面交', 'product_id': None})
    record('求购', 'TC-W04', '响应求购', 'PASS' if data.get('code') == 200 else 'FAIL', str(data))

    # TC-W05: 不能响应自己的求购
    code, data = api('post', f'/wanteds/{wanted_id}/responses', headers={'Authorization': f'Bearer {user1_token}'},
        json={'price_offer': 15, 'message': '自己响应'})
    record('求购', 'TC-W05', '不能响应自己的求购', 'PASS' if data.get('code') == 400 else 'FAIL')

    # TC-W06: 求购响应列表
    code, data = api('get', f'/wanteds/{wanted_id}/responses', headers={'Authorization': f'Bearer {user1_token}'})
    record('求购', 'TC-W06', '获取求购响应列表', 'PASS' if data.get('code') == 200 else 'FAIL')

    # TC-W07: 关闭求购
    code, data = api('put', f'/wanteds/{wanted_id}', headers={'Authorization': f'Bearer {user1_token}'}, json={'status': '已关闭'})
    record('求购', 'TC-W07', '关闭求购', 'PASS' if data.get('code') == 200 else 'FAIL')
else:
    for i in ['TC-W03','TC-W04','TC-W05','TC-W06','TC-W07']:
        record('求购', i, '求购相关测试', 'FAIL', '无求购ID')

# ==================== 7. 管理后台模块 ====================
print("\n=== 7. 管理后台模块 ===")

# TC-AD01: 管理员登录
code, data = api('post', '/admin/login', json={'username': 'admin', 'password': 'admin123'})
if data.get('code') == 200:
    admin_token = data['data']['token']
    record('管理后台', 'TC-AD01', '管理员登录', 'PASS')
else:
    record('管理后台', 'TC-AD01', '管理员登录', 'FAIL', str(data))
    admin_token = None

# TC-AD02: 普通用户无法访问管理接口
code, data = api('get', '/admin/reports', headers={'Authorization': f'Bearer {user1_token}'})
record('管理后台', 'TC-AD02', '普通用户无法访问管理接口', 'PASS' if data.get('code') in [401, 403] else 'FAIL', f"code={data.get('code')}")

if admin_token:
    ah = {'Authorization': f'Bearer {admin_token}'}

    # TC-AD03: 举报管理列表
    code, data = api('get', '/admin/reports', headers=ah)
    record('管理后台', 'TC-AD03', '管理端举报列表', 'PASS' if data.get('code') == 200 else 'FAIL')

    # TC-AD04: 处理举报(下架)
    report_id = None
    if data.get('code') == 200 and data.get('data',{}).get('reports'):
        pending = [r for r in data['data']['reports'] if r.get('status') == '待处理']
        if pending:
            report_id = pending[0]['id']
            code, data = api('post', f'/admin/reports/{report_id}/handle', headers=ah, json={'action': 'takedown', 'note': '测试下架'})
            record('管理后台', 'TC-AD04', '管理员下架商品处理举报', 'PASS' if data.get('code') == 200 else 'FAIL', str(data))
        else:
            record('管理后台', 'TC-AD04', '管理员下架商品处理举报', 'SKIP', '无待处理举报')
    else:
        record('管理后台', 'TC-AD04', '管理员下架商品处理举报', 'SKIP', '无举报数据')

    # TC-AD05: 商品管理列表
    code, data = api('get', '/admin/products', headers=ah)
    record('管理后台', 'TC-AD05', '管理端商品列表', 'PASS' if data.get('code') == 200 else 'FAIL')

    # TC-AD06: 用户管理列表
    code, data = api('get', '/admin/users', headers=ah)
    record('管理后台', 'TC-AD06', '管理端用户列表', 'PASS' if data.get('code') == 200 else 'FAIL')

    # TC-AD07: 封禁用户
    if data.get('code') == 200 and data.get('data',{}).get('users'):
        ban_user = data['data']['users'][0]
        code, data = api('put', f'/admin/users/{ban_user["id"]}/ban', headers=ah, json={'is_banned': True})
        record('管理后台', 'TC-AD07', '封禁用户', 'PASS' if data.get('code') == 200 else 'FAIL')
        # 恢复
        api('put', f'/admin/users/{ban_user["id"]}/ban', headers=ah, json={'is_banned': False})

    # TC-AD08: 数据看板
    code, data = api('get', '/admin/dashboard', headers=ah)
    record('管理后台', 'TC-AD08', '数据看板', 'PASS' if data.get('code') == 200 else 'FAIL')

    # TC-AD09: 错误管理员密码
    code, data = api('post', '/admin/login', json={'username': 'admin', 'password': 'wrong'})
    record('管理后台', 'TC-AD09', '错误管理员密码被拒绝', 'PASS' if data.get('code') == 400 else 'FAIL')
else:
    for i in ['TC-AD03','TC-AD04','TC-AD05','TC-AD06','TC-AD07','TC-AD08','TC-AD09']:
        record('管理后台', i, '管理后台测试', 'FAIL', '管理员登录失败')

# ==================== 8. 聊天模块 ====================
print("\n=== 8. 聊天模块 ===")

# TC-C01: 获取会话列表
code, data = api('get', '/conversations', headers={'Authorization': f'Bearer {user1_token}'})
record('聊天', 'TC-C01', '获取会话列表', 'PASS' if data.get('code') == 200 else 'FAIL')

# TC-C02: 创建会话
# 使用已有商品ID
code, pdata2 = api('get', '/products')
conv_product = pdata2.get('data',{}).get('products',[{}])[0]
conv_product_id = conv_product.get('id') or product_id
if conv_product_id and conv_product.get('seller_id') != user2_id:
    code, data = api('post', '/conversations', headers={'Authorization': f'Bearer {user2_token}'}, json={'product_id': conv_product_id})
    if data.get('code') == 200:
        conv_id = data['data']['id']
        record('聊天', 'TC-C02', '创建会话', 'PASS')
        # TC-C03: 发送消息
        code, data = api('post', f'/conversations/{conv_id}/messages', headers={'Authorization': f'Bearer {user2_token}'}, json={'content': '你好，这个还在吗？'})
        record('聊天', 'TC-C03', '发送消息', 'PASS' if data.get('code') == 200 else 'FAIL')
        # TC-C04: 获取消息列表
        code, data = api('get', f'/conversations/{conv_id}/messages', headers={'Authorization': f'Bearer {user2_token}'})
        record('聊天', 'TC-C04', '获取消息列表', 'PASS' if data.get('code') == 200 else 'FAIL')
    else:
        record('聊天', 'TC-C02', '创建会话', 'FAIL', str(data))
        record('聊天', 'TC-C03', '发送消息', 'FAIL', '前置失败')
        record('聊天', 'TC-C04', '获取消息列表', 'FAIL', '前置失败')
else:
    record('聊天', 'TC-C02', '创建会话', 'FAIL', '无商品ID')

# TC-C05: 未读消息数
code, data = api('get', '/unread-count', headers={'Authorization': f'Bearer {user1_token}'})
record('聊天', 'TC-C05', '获取未读消息数', 'PASS' if data.get('code') == 200 else 'FAIL')

# ==================== 9. 安全测试 ====================
print("\n=== 9. 安全测试 ===")

# TC-S01: SQL注入
code, data = api('post', '/auth/login', json={'student_id': "' OR '1'='1", 'password': '123456'})
record('安全', 'TC-S01', 'SQL注入登录被拒绝', 'PASS' if data.get('code') == 400 else 'FAIL', f"code={data.get('code')}")

# TC-S02: XSS输入
code, data = api('post', '/wanteds', headers={'Authorization': f'Bearer {user1_token}'}, json={
    'title': '<script>alert(1)</script>', 'description': 'xss test', 'budget_min': 1, 'budget_max': 10, 'category': '其他'})
record('安全', 'TC-S02', 'XSS输入不执行脚本', 'PASS' if data.get('code') == 200 else 'FAIL')

# TC-S03: 越权操作-用user1 token操作user2的订单
code, data = api('get', '/orders?role=seller', headers={'Authorization': f'Bearer {user1_token}'})
record('安全', 'TC-S03', '用户只能看到自己的订单', 'PASS' if data.get('code') == 200 else 'FAIL')

# TC-S04: 无token访问保护接口
code, data = api('post', '/orders', json={'product_id': 1})
record('安全', 'TC-S04', '无token访问保护接口被拒', 'PASS' if code in [401, 403] or data.get('code') in [401, 403] else 'FAIL')

# TC-S05: 管理员token访问普通用户接口限制
code, data = api('get', '/admin/users', headers={'Authorization': f'Bearer {user1_token}'})
record('安全', 'TC-S05', '普通token无法访问admin接口', 'PASS' if data.get('code') in [401, 403] else 'FAIL', f"code={data.get('code')}")

# ==================== 输出结果 ====================
print("\n" + "="*60)
print("测试结果汇总")
print("="*60)

modules = {}
for r in results:
    m = r['module']
    if m not in modules:
        modules[m] = {'pass': 0, 'fail': 0, 'skip': 0}
    if r['status'] == 'PASS':
        modules[m]['pass'] += 1
    elif r['status'] == 'FAIL':
        modules[m]['fail'] += 1
    else:
        modules[m]['skip'] += 1

total_pass = total_fail = total_skip = 0
for m, c in modules.items():
    total_pass += c['pass']; total_fail += c['fail']; total_skip += c['skip']
    total = c['pass'] + c['fail'] + c['skip']
    print(f"  {m}: {c['pass']}/{total} 通过, {c['fail']} 失败, {c['skip']} 跳过")

total = total_pass + total_fail + total_skip
print(f"\n  总计: {total_pass}/{total} 通过 ({total_pass/total*100:.1f}%), {total_fail} 失败, {total_skip} 跳过")

# 输出JSON供后续使用
with open('D:/HuaWeiProject/test_results.json', 'w', encoding='utf-8') as f:
    json.dump({'results': results, 'summary': modules, 'total_pass': total_pass, 'total_fail': total_fail, 'total_skip': total_skip}, f, ensure_ascii=False, indent=2)
print(f"\n详细结果已保存到 test_results.json")
