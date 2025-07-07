import openai
from typing import Dict, Optional
from app.config import settings
import logging
logger = logging.getLogger(__name__)
class WhatsAppAIAgent:
def __init__(self):
openai.api_key = settings.OPENAI_API_KEY
self.conversation_templates = {
"initial": """Olá {customer_name}, tudo bem?\n\n😊\n\nNotamos que você deixou um item no carrinho em nossa loja:\n\n🧺 Produto: {product_name}\n💰 Valor: R$ {product_price:.2f}\n📦 Quantidade: {quantity}\n👇\n\nEsse item ainda está disponível, e podemos reservar para você por tempo limitado.\nFinalize seu pedido agora e garanta seu produto antes que acabe!\n\n🔗 Finalizar compra: {checkout_url}\nPosso te ajudar com alguma dúvida?""",
"follow_up": """Oi {customer_name}!\n\n😊\n\nVi que você ainda não finalizou sua compra do produto: {product_name}\nPosso te ajudar com alguma dúvida? Estou aqui para esclarecer qualquer coisa sobre:\n• Forma de pagamento\n• Prazo de entrega\n• Características do produto\nSe precisar de qualquer informação, é só me chamar!\n"discount": """Olá {customer_name}!\n\n🎉\n\n💬""",\n\nTenho uma oferta especial para você:\n**10% OFF** no seu carrinho!\n\n🧺 Produto: {product_name}\n💰 Valor original: R$ {product_price:.2f}\n🎯 Valor com desconto: R$ {discounted_price:.2f}\nUse o código: VOLTA10\nVálido por apenas 2 horas!\n\n⏰\n\n🔗 Finalizar com desconto: {checkout_url}?discount=VOLTA10"""
}

def generate_template_message(self, message_type: str, cart_data: Dict) -> str:
"""Generate message from template"""
template = self.conversation_templates.get(message_type, "")
if message_type == "discount":
cart_data["discounted_price"] = cart_data["product_price"] * 0.9
return template.format(**cart_data)
def generate_contextual_response(self, customer_message: str, cart_context: Dict) -> str:
"""Generate AI response based on customer message and cart context"""
try:
system_prompt = f"""Você é um atendente virtual gentil e empático de uma loja online\nbrasileira especializada em produtos plásticos e utensílios domésticos.\nContexto do carrinho abandonado:\n- Cliente: {cart_context.get("customer_name", "Cliente")}\n- Produto: {cart_context.get("product_name", "Produto")}\n- Valor: R$ {cart_context.get("product_price", 0):.2f}\n- Quantidade: {cart_context.get("quantity", 1)}\nDiretrizes:\n1. Responda sempre em português brasileiro\n2. Seja gentil, empático e natural\n3. Foque em converter a venda sem ser insistente\n4. Use emojis quando apropriado\n5. Ofereça ajuda para objeções comuns (preço, frete, dúvidas)\n6. Se o cliente demonstrar interesse, forneça o link: {cart_context.get("checkout_url", "")}\n7. Mantenha respostas concisas (máximo 3 linhas)\nMensagem do cliente: "{customer_message}"\nResponda como um atendente humano responderia:"""
response = openai.ChatCompletion.create(
model="gpt-3.5-turbo",
messages=[
{"role": "system", "content": system_prompt},\n{"role": "user", "content": customer_message}\n],
max_tokens=150,
temperature=0.7
)
ai_response = response.choices[0].message.content.strip()
logger.info(f"AI response generated successfully")
return ai_response
except Exception as e:
logger.error(f"Error generating AI response: {e}")
return "Desculpe, estou com dificuldades técnicas no momento. Você pode finalizar\nsua compra através do link que enviei anteriormente. Se precisar de ajuda, entre em contato\nconosco!"
def analyze_message_intent(self, message: str) -> str:
"""Analyze customer message to determine intent"""
message_lower = message.lower()
# Simple intent classification\nif any(word in message_lower for word in ["sim", "ok", "quero", "vou comprar",\n"finalizar"]):\nreturn "positive"\nelif any(word in message_lower for word in ["não", "nao", "depois", "mais tarde"]):\nreturn "negative"\nelif any(word in message_lower for word in ["frete", "entrega", "prazo"]):\nreturn "shipping_question"\nelif any(word in message_lower for word in ["preço", "preco", "valor", "desconto"]):\nreturn "price_question"\nelif any(word in message_lower for word in ["produto", "qualidade", "tamanho"]):\nreturn "product_question"\nelse:\nreturn "general"

