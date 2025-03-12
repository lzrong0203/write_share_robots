from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {
            "role": "system",
            "content": [
                {
                    "type": "text",
                    "text": "對金融文本進行情緒分析。\n\n分析給定的金融文本並識別其情緒，包括正面、負面或中性情感。確保先進行合理的分析和推理，然後得出情緒結論。\n\n# 步驟\n\n1. **文本理解**：仔細閱讀並理解給定的金融文本。\n2. **語境分析**：識別可能影響情緒的上下文或特定語言。\n3. **情感識別**：根據詞彙、語氣和語境識別情感特徵。\n4. **推理**：綜合所有識別的信息形成初步判斷。\n5. **情緒結論**：明確文本的情緒為正面、負面或中性。\n6.標的識別：識別是否針對某一個標的，或是大盤指數。如果毫無關係，請回答\"無\"\n# 輸出格式\n\n以簡單的文本格式表述情感結論。例如:\n- \"正面\"\n- \"負面\"\n- \"中性\"\n同時附上標的。\n\n# 示例\n\n- **輸入**: \"台積電這家公司的季度利潤超出了市場預期，投資者反應積極。\"\n  **推理**: 公司利潤超出預期通常是利好消息，市場反應積極進一步增強了這一點。\n  **輸出**: \"正面，台積電\" \n\n- **輸入**: \"Google 宣布了一項裁員計劃，引發員工恐慌並導致股價下跌。\"\n  **推理**: 裁員計劃和股價下跌通常被視為負面消息，並可能引發市場和內部的負面情緒。\n  **輸出**: \"負面，Google\"\n\n# 注意事項\n\n- 確保在做出情緒判斷前，進行充分的分析和推理。\n- 考慮到金融文本中的術語和特有表達，注意其可能產生的情感影響。"
                }
            ]
        },
        # {
        #     "role": "user",
        #     "content": [
        #         {
        #             "type": "text",
        #             "text": "文本：馬斯克帶衰！ 特斯拉創史上最慘跌勢 專家急喊不妙了"
        #         }
        #     ]
        # },
        # {
        #     "role": "assistant",
        #     "content": [
        #         {
        #             "type": "text",
        #             "text": "**推理**: 文本中使用了「帶衰」、「最慘跌勢」和「不妙」等詞語，這些詞語通常帶有負面情緒，表明特斯拉的股價或市場表現不佳，並且專家對此表示擔憂。\n\n**輸出**: \"負面，特斯拉\""
        #         }
        #     ]
        # },
        # {
        #     "role": "user",
        #     "content": [
        #         {
        #             "type": "text",
        #             "text": "文本：川普1招封死中國這產業！代工廠「訂單量歸零」死了一半，上千家都在大裁員"
        #         }
        #     ]
        # },
        # {
        #     "role": "assistant",
        #     "content": [
        #         {
        #             "type": "text",
        #             "text": "**推理**: 文本中提到「封死」、「訂單量歸零」、「死了一半」、「大裁員」等詞語，這些詞語都帶有強烈的負面情緒，表明該產業受到嚴重打擊，導致訂單減少和大規模裁員。\n\n**輸出**: \"負面，無\""
        #         }
        #     ]
        # },
        # {
        #     "role": "user",
        #     "content": [
        #         {
        #             "type": "text",
        #             "text": "請問剛剛我問的文本資料，包含哪些標的"
        #         }
        #     ]
        # },
        # {
        #     "role": "assistant",
        #     "content": [
        #         {
        #             "type": "text",
        #             "text": "在您提供的文本中，涉及的標的主要是「中國的某個產業」和「代工廠」。具體的產業名稱和代工廠的名稱並未在文本中明確指出，因此無法確定具體的標的名稱。"
        #         }
        #     ]
        # },
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "文本：台積電今天大噴了！"
                }
            ]
        },
    ],
    response_format={
        "type": "text"
    },
    temperature=0,
    max_completion_tokens=2048,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0
)

print(response.choices[0].message.content)

