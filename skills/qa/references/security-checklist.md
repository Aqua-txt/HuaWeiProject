# 安全测试检查清单 - 校园二手交易平台V2

> 基于代码实际实现评估，不假设未实现的安全机制。

## 1. 注入攻击测试

| 序号 | 测试项 | 测试方法 | 检查点 | 结果 |
|------|--------|----------|--------|------|
| 1.1 | SQL注入 | 登录接口输入 `' OR '1'='1` | SQLAlchemy ORM参数化查询,注入返回业务错误 | 通过 |
| 1.2 | XSS跨站脚本 | 求购/评价输入 `<script>alert(1)</script>` | 后端安全存储,Vue3模板自动转义,脚本不执行 | 通过 |
| 1.3 | 命令注入 | 输入 `; ls`、`&& whoami` | Python Flask无系统命令调用,无风险 | 通过(不适用) |

## 2. 认证授权测试

| 序号 | 测试项 | 测试方法 | 检查点 | 结果 |
|------|--------|----------|--------|------|
| 2.1 | 未授权访问 | 无token访问 /api/auth/me | 返回401 | 通过 |
| 2.2 | 普通用户权限绕过 | 普通token访问 /api/admin/* | JWT payload.role!=admin,返回403 | 通过 |
| 2.3 | 越权操作 | A用户token操作B用户订单/评价 | 各接口校验buyer_id/seller_id,返回403 | 通过 |
| 2.4 | admin/init接口 | POST /api/admin/init | 仅admin表为空时可调用,已有admin后返回400 | 通过(设计如此) |

## 3. 数据安全测试

| 序号 | 测试项 | 测试方法 | 检查点 | 结果 |
|------|--------|----------|--------|------|
| 3.1 | 密码加密存储 | 查看数据库password_hash字段 | Werkzeug generate_password_hash(pbkdf2:sha256) | 通过 |
| 3.2 | JWT机制 | 检查认证流程 | 用户JWT(user_id)/管理员JWT(admin_id,role=admin)双通道 | 通过 |
| 3.3 | JWT有效期 | 检查config JWT_EXPIRATION_HOURS | 72小时,过期返回401 ExpiredSignatureError | 通过 |

## 4. 接口安全测试

| 序号 | 测试项 | 测试方法 | 检查点 | 结果 |
|------|--------|----------|--------|------|
| 4.1 | API认证机制 | 无token访问受保护接口 | login_required装饰器返回401 | 通过 |
| 4.2 | 重复操作防护 | 重复评价/举报 | UniqueConstraint(order_id,reviewer_id) / (reporter_id,product_id) | 通过 |
| 4.3 | 购买自己商品 | 卖方购买自己商品 | 代码校验product.seller_id!=buyer_id | 通过 |
| 4.4 | 重复购买防护 | 对同一商品已有未完成订单 | 代码查询待付款/已付款订单存在则拒绝 | 通过 |

## 5. 安全说明

- **无CSRF Token**：项目使用JWT Bearer Token(非Cookie)认证，CSRF攻击面天然不存在，无需额外CSRF防护
- **无频率限制**：校园内网使用，风险低，后续可加Flask-Limiter
- **HTTP传输**：开发环境HTTP，生产环境需配置HTTPS
