"""
认证服务
"""
import random
import string
from datetime import datetime, timedelta
from flask import current_app
from .. import redis_client

class AuthService:
    """认证服务类"""

    @staticmethod
    def generate_sms_code():
        """
        生成6位短信验证码
        """
        return ''.join(random.choices(string.digits, k=6))

    @staticmethod
    def send_sms_code(phone, sms_type='login'):
        """
        发送短信验证码
        注意：这里是模拟发送，实际项目中需要集成短信服务商API
        """
        try:
            # 生成验证码
            code = AuthService.generate_sms_code()

            # 存储到Redis，5分钟过期
            key = f"sms:{phone}:{sms_type}"
            redis_client.setex(key, 300, code)

            # 模拟发送短信（禁止将真实验证码写入日志）
            print(f"[SMS] 发送验证码到 {phone} (类型: {sms_type})")

            # 实际项目中调用短信服务商API，如：
            # response = requests.post('https://api.sms-provider.com/send', json={
            #     'phone': phone,
            #     'message': f'您的验证码是: {code}，5分钟内有效'
            # })

            return True, "验证码发送成功"

        except Exception as e:
            print(f"[SMS] 发送失败: {str(e)}")
            return False, "验证码发送失败"

    @staticmethod
    def verify_sms_code(phone, code, sms_type='login'):
        """
        验证短信验证码
        """
        try:
            key = f"sms:{phone}:{sms_type}"
            stored_code = redis_client.get(key)

            if not stored_code:
                return False

            # 验证成功后删除验证码
            if str(stored_code) == str(code):
                redis_client.delete(key)
                return True

            return False

        except Exception as e:
            print(f"[SMS] 验证失败: {str(e)}")
            return False

    @staticmethod
    def get_sms_code_remaining_time(phone, sms_type='login'):
        """
        获取短信验证码剩余有效时间（秒）
        """
        try:
            key = f"sms:{phone}:{sms_type}"
            ttl = redis_client.ttl(key)
            return max(0, ttl)
        except Exception:
            return 0

    @staticmethod
    def blacklist_token(token, expires_in=3600):
        """
        将令牌加入黑名单
        """
        try:
            key = f"blacklist:{token}"
            redis_client.setex(key, expires_in, '1')
            return True
        except Exception as e:
            print(f"[TOKEN] 黑名单添加失败: {str(e)}")
            return False

    @staticmethod
    def is_token_blacklisted(token):
        """
        检查令牌是否在黑名单中
        """
        try:
            key = f"blacklist:{token}"
            return redis_client.exists(key)
        except Exception as e:
            print(f"[TOKEN] 黑名单检查失败: {str(e)}")
            return False

