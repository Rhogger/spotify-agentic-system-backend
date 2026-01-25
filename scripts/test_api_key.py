import os
import asyncio
from google import genai
from dotenv import load_dotenv

# Carrega variáveis do .env
load_dotenv()

API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    print("❌ Erro: GOOGLE_API_KEY não encontrada no .env")
    exit(1)

print(f"🔑 Testando API Key: {API_KEY[:5]}...{API_KEY[-4:]}")

# Lista de modelos para testar
# Nota: gemini-2.5 não é um nome padrão conhecido publicamente ainda,
# mas vamos testar conforme sua solicitação.
# Os nomes oficiais atuais costumam ser gemini-1.5-flash, gemini-1.5-pro, gemini-2.0-flash-exp
MODELS_TO_TEST = [
    "gemini-2.0-flash-exp",
    "gemini-2.5-flash-exp",
    "gemini-2.5-flash-preview",
    "gemini-3-flash-preview",
]


async def test_model(model_name):
    client = genai.Client(api_key=API_KEY)
    print(f"\n---------------------------------------------------")
    print(f"🤖 Testando modelo: {model_name}...")
    try:
        # Tenta uma requisição simples
        response = await client.aio.models.generate_content(
            model=model_name, contents="Responda com apenas uma palavra: Funcionou."
        )
        print(f"✅ SUCESSO! Resposta: {response.text}")
    except Exception as e:
        # Captura o erro e imprime de forma limpa
        print(f"❌ FALHA: {e}")


async def main():
    print("Iniciando testes de conectividade com Google GenAI...")
    for model in MODELS_TO_TEST:
        await test_model(model)
    print("\n---------------------------------------------------")
    print("Testes concluídos.")


if __name__ == "__main__":
    asyncio.run(main())
