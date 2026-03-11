"""Restful-Booker 接口测试"""


class TestBooking:
    """Booking 接口测试"""

    def test_get_booking_ids(self, http_client):
        """获取所有订单 ID"""
        resp = http_client.get("/booking")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_get_booking_by_id(self, http_client):
        """根据 ID 获取订单"""
        # 先创建一个订单
        create_resp = http_client.post(
            "/booking",
            json={
                "firstname": "Maxi",
                "lastname": "Test",
                "totalprice": 100,
                "depositpaid": True,
                "bookingdates": {"checkin": "2024-01-01", "checkout": "2024-01-02"},
                "additionalneeds": "Breakfast",
            },
        )
        booking_id = create_resp.json()["bookingid"]

        # 查询
        resp = http_client.get(f"/booking/{booking_id}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["firstname"] == "Maxi"
        assert data["lastname"] == "Test"

    def test_create_booking(self, http_client):
        """创建订单"""
        payload = {
            "firstname": "芳",
            "lastname": "Test",
            "totalprice": 200,
            "depositpaid": False,
            "bookingdates": {"checkin": "2024-06-01", "checkout": "2024-06-03"},
            "additionalneeds": "Parking",
        }

        resp = http_client.post("/booking", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["bookingid"] is not None
        assert data["booking"]["firstname"] == "芳"

    def test_update_booking(self, http_client):
        """更新订单（需鉴权 Restful-Booker 用 Basic Auth）"""
        # 创建订单
        create_resp = http_client.post(
            "/booking",
            json={
                "firstname": "Original",
                "lastname": "Name",
                "totalprice": 100,
                "depositpaid": True,
                "bookingdates": {"checkin": "2024-01-01", "checkout": "2024-01-02"},
            },
        )
        booking_id = create_resp.json()["bookingid"]

        # Basic Auth 鉴权更新
        payload = {
            "firstname": "Updated",
            "lastname": "Name",
            "totalprice": 150,
            "depositpaid": True,
            "bookingdates": {"checkin": "2024-02-01", "checkout": "2024-02-03"},
        }

        resp = http_client.put(
            f"/booking/{booking_id}",
            json=payload,
            headers={"Authorization": "Basic YWRtaW46cGFzc3dvcmQxMjM="},  # admin:password123
        )
        assert resp.status_code == 200
        assert resp.json()["firstname"] == "Updated"

    def test_delete_booking(self, http_client):
        """删除订单"""
        # 创建订单
        create_resp = http_client.post(
            "/booking",
            json={
                "firstname": "ToDelete",
                "lastname": "Test",
                "totalprice": 50,
                "depositpaid": True,
                "bookingdates": {"checkin": "2024-01-01", "checkout": "2024-01-02"},
            },
        )
        booking_id = create_resp.json()["bookingid"]

        # 删除
        resp = http_client.delete(f"/booking/{booking_id}", headers={"Authorization": "Basic YWRtaW46cGFzc3dvcmQxMjM="})
        assert resp.status_code == 201

        # 验证已删除
        get_resp = http_client.get(f"/booking/{booking_id}")
        assert get_resp.status_code == 404


class TestHealth:
    """健康检查"""

    def test_ping(self, http_client):
        """Ping 接口"""
        resp = http_client.get("/ping")
        assert resp.status_code == 201
        assert resp.text == "Created"
