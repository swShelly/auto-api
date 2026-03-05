"""Stripe API 接口测试"""
import pytest


class TestStripeCustomers:
    """Stripe Customer 接口测试"""
    
    def test_create_customer(self, stripe_client, stripe_api_key):
        """创建客户"""
        stripe_client.set_api_key(stripe_api_key)
        
        data = {
            "name": "张三",
            "email": "zhangsan@example.com",
            "description": "测试客户"
        }
        
        resp = stripe_client.post("/customers", data=data)
        
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "张三"
        assert data["email"] == "zhangsan@example.com"
        assert data["id"].startswith("cus_")  # Stripe ID 以 cus_ 开头
    
    def test_get_customer(self, stripe_client, stripe_api_key):
        """获取客户详情"""
        stripe_client.set_api_key(stripe_api_key)
        
        # 先创建
        create_resp = stripe_client.post("/customers", data={
            "name": "李四",
            "email": "lisi@example.com"
        })
        customer_id = create_resp.json()["id"]
        
        # 再查询
        resp = stripe_client.get(f"/customers/{customer_id}")
        
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "李四"
        assert data["id"] == customer_id
    
    def test_list_customers(self, stripe_client, stripe_api_key):
        """获取客户列表"""
        stripe_client.set_api_key(stripe_api_key)
        
        resp = stripe_client.get("/customers")
        
        assert resp.status_code == 200
        data = resp.json()
        assert "data" in data
        assert len(data["data"]) > 0


class TestStripeCharges:
    """Stripe Charge 接口测试"""
    
    def test_create_charge(self, stripe_client, stripe_api_key):
        """创建扣款"""
        stripe_client.set_api_key(stripe_api_key)
        
        # 先创建客户
        customer_resp = stripe_client.post("/customers", data={
            "email": "test@example.com"
        })
        customer_id = customer_resp.json()["id"]
        
        # 创建扣款
        data = {
            "amount": 2000,  # 20.00 美元（Stripe 用最小单位：分）
            "currency": "usd",
            "customer": customer_id,
            "description": "测试扣款"
        }
        
        resp = stripe_client.post("/charges", data=data)
        
        assert resp.status_code == 200
        data = resp.json()
        assert data["amount"] == 2000
        assert data["currency"] == "usd"
        assert data["status"] == "succeeded"
    
    def test_get_charge(self, stripe_client, stripe_api_key):
        """获取扣款详情"""
        stripe_client.set_api_key(stripe_api_key)
        
        # 先创建客户和扣款
        customer_resp = stripe_client.post("/customers", data={"email": "test2@example.com"})
        customer_id = customer_resp.json()["id"]
        
        charge_resp = stripe_client.post("/charges", data={
            "amount": 1000,
            "currency": "usd",
            "customer": customer_id
        })
        charge_id = charge_resp.json()["id"]
        
        # 查询扣款
        resp = stripe_client.get(f"/charges/{charge_id}")
        
        assert resp.status_code == 200
        assert resp.json()["id"] == charge_id


class TestStripePaymentIntents:
    """Stripe PaymentIntent 接口测试"""
    
    def test_create_payment_intent(self, stripe_client, stripe_api_key):
        """创建支付意向"""
        stripe_client.set_api_key(stripe_api_key)
        
        data = {
            "amount": 5000,  # 50.00 美元
            "currency": "usd",
            "payment_method_types[]": "card"
        }
        
        resp = stripe_client.post("/payment_intents", data=data)
        
        assert resp.status_code == 200
        data = resp.json()
        assert data["amount"] == 5000
        assert data["currency"] == "usd"
        assert data["status"] == "requires_payment_method"
        assert data["client_secret"] is not None
    
    def test_get_payment_intent(self, stripe_client, stripe_api_key):
        """获取支付意向"""
        stripe_client.set_api_key(stripe_api_key)
        
        # 先创建
        create_resp = stripe_client.post("/payment_intents", data={
            "amount": 3000,
            "currency": "usd"
        })
        intent_id = create_resp.json()["id"]
        
        # 查询
        resp = stripe_client.get(f"/payment_intents/{intent_id}")
        
        assert resp.status_code == 200
        assert resp.json()["id"] == intent_id


class TestStripeRefunds:
    """Stripe Refund 接口测试"""
    
    def test_create_refund(self, stripe_client, stripe_api_key):
        """创建退款"""
        stripe_client.set_api_key(stripe_api_key)
        
        # 先创建客户和扣款
        customer_resp = stripe_client.post("/customers", data={"email": "refund@example.com"})
        customer_id = customer_resp.json()["id"]
        
        charge_resp = stripe_client.post("/charges", data={
            "amount": 5000,
            "currency": "usd",
            "customer": customer_id,
            "capture": "false"  # 不立即扣款
        })
        charge_id = charge_resp.json()["id"]
        
        # 创建退款
        data = {
            "charge": charge_id,
            "amount": 1000  # 退 10 美元
        }
        
        resp = stripe_client.post("/refunds", data=data)
        
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "succeeded"
        assert data["amount"] == 1000
