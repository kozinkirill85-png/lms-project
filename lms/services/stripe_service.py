import stripe
from django.conf import settings
from django.core.exceptions import ValidationError

stripe.api_key = settings.STRIPE_SECRET_KEY


class StripeService:
    """Сервис для взаимодействия с Stripe API"""

    @staticmethod
    def create_product(name: str, description: str = '') -> dict:
        """Создает продукт в Stripe"""
        try:
            product = stripe.Product.create(
                name=name,
                description=description,
            )
            return {
                'id': product.id,
                'name': product.name,
                'description': product.description,
            }
        except stripe.error.StripeError as e:
            raise ValidationError(f'Ошибка Stripe: {str(e)}')

    @staticmethod
    def create_price(product_id: str, amount: int, currency: str = 'rub') -> dict:
        """
        Создает цену в Stripe.
        amount указывается в копейках/центах (100 = 1 рубль/доллар)
        """
        try:
            price = stripe.Price.create(
                product=product_id,
                unit_amount=amount,  # В копейках!
                currency=currency,
            )
            return {
                'id': price.id,
                'product': price.product,
                'unit_amount': price.unit_amount,
                'currency': price.currency,
            }
        except stripe.error.StripeError as e:
            raise ValidationError(f'Ошибка Stripe: {str(e)}')

    @staticmethod
    def create_checkout_session(price_id: str, success_url: str, cancel_url: str, user_email: str = None) -> dict:
        """Создает сессию оплаты и возвращает ссылку на оплату"""
        try:
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price': price_id,
                    'quantity': 1,
                }],
                mode='payment',
                success_url=success_url,
                cancel_url=cancel_url,
                customer_email=user_email,
            )
            return {
                'id': session.id,
                'url': session.url,
                'status': session.status,
            }
        except stripe.error.StripeError as e:
            raise ValidationError(f'Ошибка Stripe: {str(e)}')

    @staticmethod
    def retrieve_session(session_id: str) -> dict:
        """Получает данные о сессии оплаты (для проверки статуса)"""
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            return {
                'id': session.id,
                'status': session.status,
                'payment_status': session.payment_status,
                'amount_total': session.amount_total,
                'currency': session.currency,
            }
        except stripe.error.StripeError as e:
            raise ValidationError(f'Ошибка Stripe: {str(e)}')
