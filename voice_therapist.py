import os
import wave
import pyaudio
from openai import OpenAI
import config

# 初始化 OpenAI 客户端
client = OpenAI(api_key=config.OPENAI_API_KEY)

# 录音参数
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
WAVE_OUTPUT_FILENAME = "recording.wav"

messages = [{"role": "system", "content": 'You are a therapist. Respond to all input in 25 words or less.'}]

def record_audio():
    """录制音频"""
    p = pyaudio.PyAudio()

    # 选择默认输入设备
    default_input_device_info = p.get_default_input_device_info()
    default_input_device_index = default_input_device_info['index']

    stream = p.open(format=FORMAT,
                   channels=CHANNELS,
                   rate=RATE,
                   input=True,
                   input_device_index=default_input_device_index,
                   frames_per_buffer=CHUNK,
                   start=False)  # 先不开始录音

    print("\n按回车键开始录音...")
    input()
    
    # 开始录音
    stream.start_stream()
    print("正在录音...（再次按回车键结束）")
    
    frames = []
    recording = True
    
    while recording:
        try:
            # 添加错误处理
            try:
                data = stream.read(CHUNK, exception_on_overflow=False)
                frames.append(data)
            except OSError as e:
                if e.errno == -9981:  # Input overflow
                    continue
                else:
                    raise e
            
            # 非阻塞方式检查输入
            import sys
            import select
            
            if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
                line = input()
                recording = False
        except KeyboardInterrupt:
            recording = False
        except Exception as e:
            print(f"录音时发生错误: {str(e)}")
            recording = False

    print("录音结束")
    stream.stop_stream()
    stream.close()
    p.terminate()

    if len(frames) == 0:
        print("没有录到任何音频，请重试")
        return False

    # 保存录音文件
    try:
        wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()
        return True
    except Exception as e:
        print(f"保存音频文件时发生错误: {str(e)}")
        return False

def process_audio():
    """处理音频并获取回复"""
    global messages
    
    try:
        # 转录音频
        print("正在转录音频...")
        audio_file = open(WAVE_OUTPUT_FILENAME, "rb")
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )
        print(f"您说: {transcript.text}")

        # 发送到 GPT 获取回复
        messages.append({"role": "user", "content": transcript.text})
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages
        )

        # 获取回复
        ai_response = response.choices[0].message.content
        messages.append({"role": "assistant", "content": ai_response})
        print(f"AI 回复: {ai_response}")

        # 语音播放回复
        os.system(f'say "{ai_response}"')

    except Exception as e:
        print(f"错误: {str(e)}")
    finally:
        # 清理音频文件
        audio_file.close()
        if os.path.exists(WAVE_OUTPUT_FILENAME):
            os.remove(WAVE_OUTPUT_FILENAME)

def main():
    print("欢迎使用 AI 治疗师！")
    print("使用说明:")
    print("1. 按回车键开始录音")
    print("2. 再次按回车键结束录音")
    print("3. 输入 'q' 并按回车键退出程序")
    
    while True:
        command = input("\n按回车开始新的对话，或输入 'q' 退出程序: ")
        if command.lower() == 'q':
            print("\n感谢使用！再见！")
            break
            
        if record_audio():
            process_audio()
        else:
            print("录音失败，请重试")

if __name__ == "__main__":
    main() 