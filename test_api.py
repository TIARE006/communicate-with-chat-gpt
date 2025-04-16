from openai import OpenAI
import config
import sys

# 初始化 OpenAI 客户端
client = OpenAI(api_key=config.OPENAI_API_KEY)

def test_api_connection():
    print("正在测试 API 连接...")
    print("使用的 API key:", config.OPENAI_API_KEY[:10] + "..." if config.OPENAI_API_KEY else "未设置")
    
    try:
        # 尝试发送一个简单的请求
        print("发送测试请求...")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello"}]
        )
        print("API 连接成功！")
        print("响应:", response.choices[0].message.content)
        return True
    except Exception as e:
        print("API 连接失败！")
        print("错误类型:", type(e).__name__)
        print("错误信息:", str(e))
        if hasattr(e, 'response'):
            print("响应状态码:", e.response.status_code)
            print("响应内容:", e.response.text)
        return False

if __name__ == "__main__":
    test_api_connection() 