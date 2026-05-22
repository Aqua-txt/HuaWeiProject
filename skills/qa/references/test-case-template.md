# 测试用例模板 - 校园二手交易平台V2

> 所有测试用例基于代码实际实现设计，不设计与代码不符的场景。

## 用户认证模块 测试用例

### 功能测试

| 用例ID | 用例标题 | 前置条件 | 测试步骤 | 预期结果 | 优先级 | 状态 |
|--------|----------|----------|----------|----------|--------|------|
| TC-A01 | 用户登录(正确凭证) | 已注册用户 | POST /api/auth/login {student_id, password} | code=200, 返回JWT+用户信息 | P0 | 通过 |
| TC-A02 | 错误密码登录 | 已注册用户 | POST /api/auth/login 错误密码 | code=400, "学号或密码错误" | P0 | 通过 |
| TC-A03 | 获取当前用户信息 | 已登录 | GET /api/auth/me 携带Bearer token | code=200, 返回用户信息(含credit_score) | P0 | 通过 |
| TC-A04 | 未登录访问受保护接口 | 无 | GET /api/auth/me 无token | 返回401 | P0 | 通过 |
| TC-A05 | 重复学号注册被拒绝 | 学号已存在 | POST /api/auth/register 已有学号 | code=400, "该学号已注册" | P1 | 通过 |

### 边界值测试

| 用例ID | 测试项 | 边界值 | 预期结果 |
|--------|--------|--------|----------|
| BC-A01 | 学号长度 | 3位(<4位) | 注册失败 |
| BC-A02 | 学号长度 | 4位(最小有效) | 注册成功 |
| BC-A03 | 密码长度 | 5位(<6位) | 注册失败 |
| BC-A04 | 密码长度 | 6位(最小有效) | 注册成功 |

---

## 商品模块 测试用例

### 功能测试

| 用例ID | 用例标题 | 前置条件 | 测试步骤 | 预期结果 | 优先级 | 状态 |
|--------|----------|----------|----------|----------|--------|------|
| TC-P01 | 获取商品列表(分页) | 有商品数据 | GET /api/products?page=1&per_page=20 | code=200, 返回products+分页信息 | P0 | 通过 |
| TC-P02 | 按分类筛选商品 | 有商品数据 | GET /api/products?category=教材 | 仅返回教材类商品 | P0 | 通过 |
| TC-P03 | 关键词搜索 | 有商品数据 | GET /api/products?keyword=数学 | 返回标题或描述匹配的商品 | P0 | 通过 |
| TC-P04 | 按价格排序 | 有商品数据 | GET /api/products?sort=price_asc | 按价格升序返回 | P1 | 通过 |
| TC-P05 | 发布商品(multipart+图片) | 已登录 | POST /api/products 含title/price/category/images | 商品创建成功,状态=上架 | P0 | 通过 |
| TC-P06 | 商品详情(含卖家信用) | 有商品 | GET /api/products/{id} | 返回商品信息+seller_credit_score | P0 | 通过 |
| TC-P07 | 收藏/取消收藏(toggle) | 已登录 | POST /api/products/{id}/favorite | 切换收藏状态,返回is_favorited | P1 | 通过 |
| TC-P08 | 我的收藏列表 | 已登录 | GET /api/favorites | 返回收藏商品列表 | P1 | 通过 |

### 边界值测试

| 用例ID | 测试项 | 边界值 | 预期结果 | 代码实现 |
|--------|--------|--------|----------|----------|
| BC-P01 | 商品标题 | 超过100字 | 发布失败 | len(title)>100 校验 |
| BC-P02 | 价格下限 | 0或0.009 | 发布失败 | price<0.01 校验 |
| BC-P03 | 价格上限 | 100000 | 发布失败 | price>99999.99 校验 |
| BC-P04 | 图片数量 | 超过6张 | 拒绝上传 | len(image_files)>6 校验 |
| BC-P05 | 无图片 | 0张图片 | 发布失败,"请至少上传一张图片" | 业务要求 |

---

## 担保交易模块 测试用例

### 功能测试

| 用例ID | 用例标题 | 前置条件 | 测试步骤 | 预期结果 | 优先级 | 状态 |
|--------|----------|----------|----------|----------|--------|------|
| TC-O01 | 创建订单(商品自动下架) | 买方登录+商品上架 | POST /api/orders {product_id} | 订单创建,status=待付款,商品status=已下架 | P0 | 通过 |
| TC-O02 | 不能购买自己商品 | 卖方登录 | POST /api/orders 自己的商品id | code=400, "不能购买自己的商品" | P0 | 通过 |
| TC-O03 | 模拟支付 | 订单待付款 | POST /api/orders/{id}/pay | status=已付款,生成Payment记录(pay_type=wechat) | P0 | 通过 |
| TC-O04 | 买方确认收货 | 订单已付款 | POST /api/orders/{id}/confirm | status=已完成,buyer_confirmed_at更新 | P0 | 通过 |
| TC-O05 | 取消订单 | 订单待付款 | POST /api/orders/{id}/cancel | status=已取消,商品重新上架 | P0 | 通过 |
| TC-O06 | 买方申请退款 | 订单已付款 | POST /api/orders/{id}/refund {reason>=10字} | status=退款中,refund_status=待处理 | P0 | 通过 |
| TC-O07 | 卖方同意退款 | 退款中 | POST refund/respond {agree:true} | status=已退款,生成退款Payment(pay_type=wechat_refund) | P0 | 通过 |
| TC-O08 | 卖方拒绝退款升级仲裁 | 退款中 | POST refund/respond {agree:false} | status=管理员仲裁,refund_status=已拒绝 | P0 | 通过 |
| TC-O09 | 买方订单列表 | 有订单 | GET /api/orders?role=buyer | 返回buyer视角订单 | P1 | 通过 |
| TC-O10 | 卖方订单列表 | 有订单 | GET /api/orders?role=seller | 返回seller视角订单 | P1 | 通过 |
| TC-O11 | 订单详情(含支付记录) | 有订单 | GET /api/orders/{id} | 返回订单信息+payments列表 | P1 | 通过 |

### 异常测试

| 用例ID | 异常场景 | 测试步骤 | 预期结果 |
|--------|----------|----------|----------|
| EC-O01 | 对已付款订单再次支付 | POST pay 对status=已付款订单 | code=400, "订单已支付"或"订单状态不正确" |
| EC-O02 | 操作不存在的订单 | POST confirm 不存在的order_id | code=404, "订单不存在" |
| EC-O03 | 卖方操作买方专属动作 | 卖方POST confirm 买方订单 | code=403, "无权操作" |
| EC-O04 | 已有未完成订单重复购买 | 同一商品再次create(已有待付款/已付款) | code=400, "该商品已有未完成订单" |
| EC-O05 | 退款原因不足10字 | POST refund reason="太短" | code=400, "退款原因至少10个字" |

---

## 信用评价模块 测试用例

### 功能测试

| 用例ID | 用例标题 | 前置条件 | 测试步骤 | 预期结果 | 优先级 | 状态 |
|--------|----------|----------|----------|----------|--------|------|
| TC-R01 | 评价已完成订单(三维打分) | 订单已完成 | POST /api/reviews {order_id, communication/description/speed 1-5, comment} | 评价成功,overall=沟通*0.2+相符*0.5+速度*0.3 | P0 | 通过 |
| TC-R02 | 重复评价被拒绝 | 同一订单已评价 | POST /api/reviews 同一order_id | code=400, "已评价过该订单" | P0 | 通过 |
| TC-R03 | 检查可评价状态 | 已完成订单 | GET /api/orders/{id}/reviewable | 返回reviewable=true/false+reason | P0 | 通过 |
| TC-R04 | 获取评价列表 | 有评价 | GET /api/reviews?reviewee_id=X | 返回被评价者的评价列表 | P1 | 通过 |

### 边界值测试

| 用例ID | 测试项 | 边界值 | 预期结果 | 代码实现 |
|--------|--------|--------|----------|----------|
| BC-R01 | 评分下限 | 0 | 评价失败 | score<1 校验 |
| BC-R02 | 评分上限 | 6 | 评价失败 | score>5 校验 |
| BC-R03 | 评价文字长度 | >200字 | 评价失败 | len(comment)>200 校验 |
| BC-R04 | 7天有效期 | 交易完成8天后 | 评价失败,"评价已过期" | order.updated_at+7天 |

### 异常测试

| 用例ID | 异常场景 | 测试步骤 | 预期结果 |
|--------|----------|----------|----------|
| EC-R01 | 评价未完成订单 | POST reviews 对status=已付款订单 | code=400, "只能评价已完成的订单" |
| EC-R02 | 非交易参与方评价 | 无关用户POST reviews | code=403, "无权评价" |

---

## 举报模块 测试用例

### 功能测试

| 用例ID | 用例标题 | 前置条件 | 测试步骤 | 预期结果 | 优先级 | 状态 |
|--------|----------|----------|----------|----------|--------|------|
| TC-RP01 | 提交举报(4种类型) | 已登录+有商品 | POST /api/reports {product_id, report_type, description>=10字} | 举报成功,product.report_count+1 | P0 | 通过 |
| TC-RP02 | 重复举报同一商品被拒 | 已举报同一商品 | POST /api/reports 同product_id | code=400, "你已举报过该商品" | P0 | 通过 |
| TC-RP03 | 举报描述不足10字 | 已登录 | POST /api/reports description="太短" | code=400, "举报描述至少10个字" | P0 | 通过 |
| TC-RP04 | 我的举报列表 | 有举报 | GET /api/reports | 返回当前用户的举报列表 | P1 | 通过 |

### 边界值测试

| 用例ID | 测试项 | 边界值 | 预期结果 |
|--------|--------|--------|----------|
| BC-RP01 | 举报类型 | 非法类型"spam" | code=400, "无效的举报类型" |
| BC-RP02 | 描述长度 | 恰好10字 | 举报成功 |

---

## 求购专区 测试用例

### 功能测试

| 用例ID | 用例标题 | 前置条件 | 测试步骤 | 预期结果 | 优先级 | 状态 |
|--------|----------|----------|----------|----------|--------|------|
| TC-W01 | 发布求购 | 已登录 | POST /api/wanteds {title,desc,budget_min,max,category,condition} | 求购创建,status=进行中 | P0 | 通过 |
| TC-W02 | 求购列表(分类筛选) | 有数据 | GET /api/wanteds?category=教材 | 按分类过滤,分页返回 | P0 | 通过 |
| TC-W03 | 求购详情(含推荐商品) | 有求购 | GET /api/wanteds/{id} | 返回详情+responses+recommended_products | P0 | 通过 |
| TC-W04 | 响应求购(报价+留言) | 非求购者登录 | POST /api/wanteds/{id}/responses {price_offer, message} | 响应成功 | P0 | 通过 |
| TC-W05 | 不能响应自己求购 | 求购者登录 | POST responses自己求购 | code=400, "不能响应自己的求购" | P1 | 通过 |
| TC-W06 | 求购响应列表 | 有响应 | GET /api/wanteds/{id}/responses | 返回响应列表(含responder信息) | P1 | 通过 |
| TC-W07 | 关闭求购 | 求购者登录 | PUT /api/wanteds/{id} {status:"已关闭"} | status=已关闭 | P1 | 通过 |
| TC-W08 | 响应已关闭求购被拒 | 求购已关闭 | POST responses | code=400, "求购已关闭" | P1 | 通过 |

### 边界值测试

| 用例ID | 测试项 | 边界值 | 预期结果 | 代码实现 |
|--------|--------|--------|----------|----------|
| BC-W01 | 预算min>max | budget_min=100,max=10 | code=400, "预算范围无效" | min>max 校验 |
| BC-W02 | 标题长度 | >100字 | code=400 | len(title)>100 校验 |

---

## 管理后台 测试用例

### 功能测试

| 用例ID | 用例标题 | 前置条件 | 测试步骤 | 预期结果 | 优先级 | 状态 |
|--------|----------|----------|----------|----------|--------|------|
| TC-AD01 | 管理员登录 | admin已初始化 | POST /api/admin/login {username,password} | 返回admin JWT(role=admin) | P0 | 通过 |
| TC-AD02 | 普通token无法访问admin | 普通用户token | GET /api/admin/reports 普通token | 返回403, "需要管理员权限" | P0 | 通过 |
| TC-AD03 | 管理端举报列表(全部) | 管理员登录 | GET /api/admin/reports | 返回所有用户举报(非仅本人) | P0 | 通过 |
| TC-AD04 | 下架商品处理举报 | 有待处理举报 | POST /admin/reports/{id}/handle {action:"takedown"} | product.status=已下架, report.status=已处理 | P0 | 通过 |
| TC-AD05 | 驳回举报 | 有待处理举报 | POST handle {action:"reject"} | report.status=已驳回 | P1 | 通过 |
| TC-AD06 | 封禁用户 | 管理员登录 | PUT /admin/users/{id}/ban {is_banned:true} | user.is_banned=true | P1 | 通过 |
| TC-AD07 | 管理端商品列表(搜索) | 管理员登录 | GET /api/admin/products?keyword=xxx | 返回匹配商品 | P1 | 通过 |
| TC-AD08 | 数据看板 | 管理员登录 | GET /api/admin/dashboard | 返回overview+30天trend+category_distribution | P1 | 通过 |
| TC-AD09 | 错误管理员密码 | 无 | POST /api/admin/login 错误密码 | code=400 | P1 | 通过 |

---

## 聊天系统 测试用例

### 功能测试

| 用例ID | 用例标题 | 前置条件 | 测试步骤 | 预期结果 | 优先级 | 状态 |
|--------|----------|----------|----------|----------|--------|------|
| TC-C01 | 获取会话列表(含未读数) | 已登录 | GET /api/conversations | 返回会话列表+last_message+unread_count | P0 | 通过 |
| TC-C02 | 创建会话(需product_id+seller_id) | 买方登录+有商品 | POST /api/conversations {product_id, seller_id} | 会话创建,同一买家+商品去重 | P0 | 通过 |
| TC-C03 | 不能和自己聊天 | 卖方登录 | POST /api/conversations {seller_id=自己id} | code=400, "不能和自己聊天" | P0 | 通过 |
| TC-C04 | 发送消息 | 有会话 | POST /conversations/{id}/messages {content} | 消息发送成功 | P0 | 通过 |
| TC-C05 | 获取消息列表 | 有会话 | GET /conversations/{id}/messages | 返回消息列表 | P1 | 通过 |
| TC-C06 | 未读消息数 | 已登录 | GET /api/unread-count | 返回未读数量 | P1 | 通过 |

---

## 安全测试用例

| 用例ID | 安全测试项 | 测试要点 | 预期结果 | 优先级 |
|--------|------------|----------|----------|--------|
| SC-001 | SQL注入 | 登录接口输入 ' OR '1'='1 | 请求被拒绝(code=400),SQLAlchemy ORM参数化查询 | P0 |
| SC-002 | XSS跨站脚本 | 求购标题输入&lt;script&gt;alert(1)&lt;/script&gt; | 内容安全存储,前端Vue3自动转义不执行 | P0 |
| SC-003 | 越权操作 | 用A用户token操作B用户订单/评价 | 返回403, "无权操作" | P0 |
| SC-004 | 未授权访问 | 无token访问受保护接口 | 返回401 | P0 |
| SC-005 | 管理接口鉴权隔离 | 普通token访问/admin接口 | 返回403, "需要管理员权限" | P0 |
| SC-006 | 重复操作防护 | 重复评价/重复举报 | UniqueConstraint拦截,返回400 | P1 |
| SC-007 | 密码哈希存储 | 检查数据库password_hash字段 | Werkzeug generate_password_hash,非明文 | P1 |
