"""
微信支付工具
"""
import time
import uuid
import json
from flask import current_app
import requests
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
import base64

class WeChatPayService:
    """微信支付服务"""

    @staticmethod
    def get_config():
        """获取微信支付配置"""
        return {
            'app_id': current_app.config.get('WECHAT_APP_ID'),
            'mch_id': current_app.config.get('WECHAT_MCH_ID'),
            'private_key': current_app.config.get('WECHAT_PRIVATE_KEY'),
            'serial_no': current_app.config.get('WECHAT_SERIAL_NO')
        }

    @staticmethod
    def load_private_key(private_key_str):
        """
        加载私钥
        """
        try:
            # 如果是字符串格式，需要处理
            if isinstance(private_key_str, str):
                # 移除PEM头尾
                private_key_str = private_key_str.replace('-----BEGIN PRIVATE KEY-----', '')
                private_key_str = private_key_str.replace('-----END PRIVATE KEY-----', '')
                private_key_str = private_key_str.replace('\n', '').replace('\r', '')

                # base64解码
                private_key_bytes = base64.b64decode(private_key_str)
                private_key_str = private_key_bytes.decode('utf-8')

            private_key = serialization.load_pem_private_key(
                private_key_str.encode(),
                password=None
            )
            return private_key
        except Exception as e:
            raise Exception(f"私钥加载失败: {str(e)}")

    @staticmethod
    def sign_data(data, private_key):
        """
        使用私钥签名数据
        """
        try:
            signature = private_key.sign(
                data.encode('utf-8'),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return base64.b64encode(signature).decode('utf-8')
        except Exception as e:
            raise Exception(f"数据签名失败: {str(e)}")

    @staticmethod
    def create_prepay_order(order_data):
        """
        创建预支付订单
        """
        try:
            config = WeChatPayService.get_config()

            # 构建请求数据
            timestamp = str(int(time.time()))
            nonce_str = str(uuid.uuid4()).replace('-', '')

            request_data = {
                'appid': config['app_id'],
                'mchid': config['mch_id'],
                'description': order_data.get('description', '电池租售订单'),
                'out_trade_no': order_data['out_trade_no'],
                'notify_url': order_data.get('notify_url', 'https://your-domain.com/api/v1/payment/notify'),
                'amount': {
                    'total': int(order_data['total_amount'] * 100),  # 转换为分
                    'currency': 'CNY'
                }
            }

            # 添加可选字段
            if order_data.get('payer_openid'):
                request_data['payer'] = {
                    'openid': order_data['payer_openid']
                }

            # 序列化请求数据
            json_data = json.dumps(request_data, separators=(',', ':'))

            # 构建签名字符串
            signature_str = f'POST\n/v3/pay/transactions/jsapi\n{timestamp}\n{nonce_str}\n{json_data}\n'

            # 加载私钥并签名
            private_key = WeChatPayService.load_private_key(config['private_key'])
            signature = WeChatPayService.sign_data(signature_str, private_key)

            # 构建请求头
            headers = {
                'Authorization': f'WECHATPAY2-SHA256-RSA2048 mchid="{config["mch_id"]}",nonce_str="{nonce_str}",timestamp="{timestamp}",serial_no="{config["serial_no"]}",signature="{signature}"',
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'User-Agent': 'battery-saas/1.0.0'
            }

            # 发送请求
            url = 'https://api.mch.weixin.qq.com/v3/pay/transactions/jsapi'
            response = requests.post(url, data=json_data, headers=headers, timeout=30)

            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'prepay_id': result.get('prepay_id'),
                    'data': result
                }
            else:
                return {
                    'success': False,
                    'message': f'创建预支付订单失败: {response.text}'
                }

        except Exception as e:
            return {
                'success': False,
                'message': f'创建预支付订单异常: {str(e)}'
            }

    @staticmethod
    def generate_pay_params(prepay_id):
        """
        生成前端支付参数
        """
        try:
            config = WeChatPayService.get_config()

            timestamp = str(int(time.time()))
            nonce_str = str(uuid.uuid4()).replace('-', '')

            # 构建签名字符串
            signature_str = f'{config["app_id"]}\n{timestamp}\n{nonce_str}\nprepay_id={prepay_id}\n'

            # 加载私钥并签名
            private_key = WeChatPayService.load_private_key(config['private_key'])
            pay_sign = WeChatPayService.sign_data(signature_str, private_key)

            return {
                'success': True,
                'data': {
                    'appId': config['app_id'],
                    'timeStamp': timestamp,
                    'nonceStr': nonce_str,
                    'package': f'prepay_id={prepay_id}',
                    'signType': 'RSA',
                    'paySign': pay_sign
                }
            }

        except Exception as e:
            return {
                'success': False,
                'message': f'生成支付参数失败: {str(e)}'
            }

    @staticmethod
    def refund_order(refund_data):
        """
        申请退款
        """
        try:
            config = WeChatPayService.get_config()

            # 构建请求数据
            timestamp = str(int(time.time()))
            nonce_str = str(uuid.uuid4()).replace('-', '')

            request_data = {
                'out_trade_no': refund_data['out_trade_no'],
                'out_refund_no': refund_data['out_refund_no'],
                'amount': {
                    'refund': int(refund_data['refund_amount'] * 100),  # 转换为分
                    'total': int(refund_data['total_amount'] * 100),
                    'currency': 'CNY'
                }
            }

            # 序列化请求数据
            json_data = json.dumps(request_data, separators=(',', ':'))

            # 构建签名字符串
            signature_str = f'POST\n/v3/refund/domestic/refunds\n{timestamp}\n{nonce_str}\n{json_data}\n'

            # 加载私钥并签名
            private_key = WeChatPayService.load_private_key(config['private_key'])
            signature = WeChatPayService.sign_data(signature_str, private_key)

            # 构建请求头
            headers = {
                'Authorization': f'WECHATPAY2-SHA256-RSA2048 mchid="{config["mch_id"]}",nonce_str="{nonce_str}",timestamp="{timestamp}",serial_no="{config["serial_no"]}",signature="{signature}"',
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'User-Agent': 'battery-saas/1.0.0'
            }

            # 发送请求
            url = 'https://api.mch.weixin.qq.com/v3/refund/domestic/refunds'
            response = requests.post(url, data=json_data, headers=headers, timeout=30)

            if response.status_code in [200, 202]:
                result = response.json()
                return {
                    'success': True,
                    'refund_id': result.get('refund_id'),
                    'data': result
                }
            else:
                return {
                    'success': False,
                    'message': f'申请退款失败: {response.text}'
                }

        except Exception as e:
            return {
                'success': False,
                'message': f'申请退款异常: {str(e)}'
            }

    @staticmethod
    def query_order(out_trade_no):
        """
        查询订单
        """
        try:
            config = WeChatPayService.get_config()

            timestamp = str(int(time.time()))
            nonce_str = str(uuid.uuid4()).replace('-', '')

            # 构建签名字符串
            signature_str = f'GET\n/v3/pay/transactions/out-trade-no/{out_trade_no}\n{timestamp}\n{nonce_str}\n\n'

            # 加载私钥并签名
            private_key = WeChatPayService.load_private_key(config['private_key'])
            signature = WeChatPayService.sign_data(signature_str, private_key)

            # 构建请求头
            headers = {
                'Authorization': f'WECHATPAY2-SHA256-RSA2048 mchid="{config["mch_id"]}",nonce_str="{nonce_str}",timestamp="{timestamp}",serial_no="{config["serial_no"]}",signature="{signature}"',
                'Accept': 'application/json',
                'User-Agent': 'battery-saas/1.0.0'
            }

            # 发送请求
            url = f'https://api.mch.weixin.qq.com/v3/pay/transactions/out-trade-no/{out_trade_no}'
            response = requests.get(url, headers=headers, timeout=30)

            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'data': result
                }
            else:
                return {
                    'success': False,
                    'message': f'查询订单失败: {response.text}'
                }

        except Exception as e:
            return {
                'success': False,
                'message': f'查询订单异常: {str(e)}'
            }

    @staticmethod
    def verify_notification_signature(headers, body):
        """
        验证回调通知签名
        注意：当前项目未集成微信支付平台证书，无法安全验签时必须拒绝处理
        """
        try:
            required_headers = [
                'Wechatpay-Timestamp',
                'Wechatpay-Nonce',
                'Wechatpay-Signature',
                'Wechatpay-Serial'
            ]
            missing = [header for header in required_headers if not headers.get(header)]
            if missing:
                return {
                    'success': False,
                    'message': f"缺少签名头: {', '.join(missing)}"
                }

            return {
                'success': False,
                'message': '当前环境未配置微信支付平台证书，拒绝处理未验签回调'
            }

        except Exception as e:
            return {
                'success': False,
                'message': f'签名验证失败: {str(e)}'
            }
