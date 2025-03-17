# 金融情緒分析與Python應用

## 第一章：情緒指數的基礎概念

### 1-1 情緒分析概述
- 定義：情緒分析(sentiment analysis)是利用自然語言處理技術判斷文字中的情感傾向
- 應用目的：從非結構化文字中萃取市場情緒、投資洞見
- 核心價值：市場受情緒驅動，情緒波動往往領先價格變動
- 處理流程：資料蒐集 → 文字預處理 → 情緒分類 → 指數計算

### 1-2 情緒分析的類型
- 文件級分析：整篇文章的總體情緒（如新聞報導的正負面）
- 句子級分析：單句評論的情緒傾向（如推文情緒）
- 實體/方面級分析：針對特定目標的情緒（如對「獲利」「成長性」的評價）
- 細粒度情緒分析：區分詳細情緒類別（喜悅、憤怒、驚訝等）
- 情緒強度分析：評估情緒的強烈程度（強烈/輕微正負面等）

### 1-3 金融情緒指數特性
- 定義：量化投資人對市場或個股的情感/態度的數值指標
- 常見來源：社群媒體、新聞報導、分析師報告、公司公告
- 計算方式：將文字情緒分數加權平均，通常以-1(極負面)到1(極正面)表示
- 應用場景：風險預警、趨勢確認、逆勢交易訊號
- 代表性指標：恐懼與貪婪指數、VIX恐慌指數、社群情緒指標

### 1-4 金融情緒分析的挑戰
- 領域專業性：金融專業術語與行話（如「獲利預警」「健康修正」）
- 隱含情緒：市場報導通常措辭客觀，情緒表達含蓄
- 反諷與諷刺：「這檔股票穩穩發大財」可能是負面表達
- 多重目標：同一文字中對不同股票/指標的情緒可能不同
- 時效性強：市場情緒瞬息萬變，分析需即時性

## 第二章：自然語言處理與相關AI模型

### 2-1 NLP基礎技術
- 文字預處理：斷詞/分詞、去除停用詞、詞形還原
- 文字表示：詞袋模型(Bag-of-Words)、詞頻-逆文件頻率(TF-IDF)
- 特徵工程：n-gram建模、詞性標註、命名實體識別
- 基礎模型：字典法、機器學習分類(如SVM、隨機森林等)

### 2-2 詞典與規則方法
- 常用工具：VADER、TextBlob、SentiStrength
- 原理：基於情感詞典與語法規則計算情感分數
- 優點：速度快、無需訓練、解釋性強
- 局限：對語境、反諷敏感度低，難處理金融專業詞彙
- 範例：「台積電法說釋出謹慎展望」難以準確判斷

### 2-3 詞嵌入與Transformer革命
- 詞嵌入：Word2Vec、GloVe、FastText等將詞轉為語義向量
- Transformer架構：2017年提出，基於自注意力機制(Self-Attention)
- 優勢：捕捉長距離詞彙關係，理解上下文語境
- 架構特點：
  - 自注意力機制：同時處理所有詞彙，動態決定重要性
  - 多頭注意力：從不同角度理解文字
  - 位置編碼：保留詞序資訊

### 2-4 BERT與雙向模型
- BERT (2018)：Bidirectional Encoder Representations from Transformers
- 特點：雙向語境理解，預訓練+微調範式
- 預訓練任務：遮罩語言模型(MLM)、下一句預測(NSP)
- 金融領域變體：FinBERT、BloombergGPT專為財經文字優化
- 適用場景：金融新聞分類、盈餘報告情緒分析、分析師報告解讀

### 2-5 GPT與生成模型
- GPT (Generative Pre-trained Transformer)：自回歸語言模型
- 架構特點：僅使用Transformer解碼器，單向預測下一個詞
- 與BERT差異：生成vs.理解，單向vs.雙向
- 優勢：
  - 零樣本/少樣本學習能力強
  - 情感分析同時能提供解釋
  - 適應新語境與領域的能力佳
- 應用：情緒判斷、財報摘要、市場評論生成

### 2-6 開源大型語言模型
- LLaMA (Meta)：高效能開源大型語言模型
- 優勢：可本地部署、避免API成本、保護資料隱私
- 微調方法：LoRA (Low-Rank Adaptation)參數高效微調
- 金融領域應用：可針對本地市場特色進行優化
- 部署考量：計算資源需求、推論速度、維護成本

## 第三章：社群討論、重大訊息與新聞報導的情緒指數

### 3-1 社群媒體情緒分析
- 主要平台：X(Twitter)、Reddit、PTT、Dcard等
- 文字特點：
  - 非正式語言、口語化表達
  - 大量表情符號、縮寫、俚語
  - 文字極短且雜訊多
  - 諷刺與反諷常見
- 挑戰：
  - 語言多變性（新詞、流行語）
  - 表情符號語義（😂→正面、😡→負面）
  - 即時性要求高
- 優勢：反映散戶情緒、即時市場反應、趨勢早期訊號

### 3-2 社群文字處理技術
- 資料蒐集：平台API、爬蟲技術、第三方資料服務
- 特殊預處理：
  - 表情符號映射（轉換為文字情感值）
  - 縮寫展開（如LOL→laughing out loud）
  - 錯別字修正、標準化處理
- 差異化權重設計：
  - 發言者影響力（如PageRank演算法）
  - 歷史準確度加權
  - 社交網絡中心度
- 時間衰減函數：指數衰減控制資訊時效性

### 3-3 新聞報導情緒分析
- 來源類型：財經媒體、公司公告、分析師報告
- 文字特點：
  - 語言正式、結構性強
  - 情感表達隱晦、措辭客觀
  - 包含豐富背景資訊
  - 涉及多個實體與事件
- 挑戰：
  - 媒體立場偏誤
  - 專業術語理解
  - 隱含情緒辨識
- 優勢：雜訊少、資訊價值高、覆蓋面廣

### 3-4 重大訊息與公告分析
- 類型：財報、重大交易、管理層變動、產品發布
- 特點：
  - 高度結構化、正式語言
  - 與市場預期比較至關重要
  - 情緒反應常與預期背離
- 分析技術：
  - 比較分析（與預期、歷史資料對比）
  - 關鍵指標提取
  - 異常表述識別
- 事件研究法：分析公告前後的情緒變化

### 3-5 多來源情緒融合
- 權重策略：
  - 來源可信度加權
  - 資訊新鮮度（時間衰減）
  - 文字品質評分
- 跨市場情緒傳導：
  - VAR模型捕捉市場間情緒連動性
  - 主要市場情緒領先指標（美股→台股）
  - 跨域情緒溢出效應
- 綜合情緒指標：技術指標與情緒指標融合

### 3-6 台灣市場情緒分析案例
- 特色平台：PTT Stock、台股論壇、財經討論區
- 台灣市場專有詞彙：「摸頭」、「長紅」、「填息」等
- 中文處理挑戰：
  - 無空格斷詞（使用jieba等工具）
  - 繁簡體混用
  - 地域性表達與俚語
- 整合策略：台股技術面+基本面+情緒面多維分析

## 第四章：ChatGPT與Python API

### 4-1 ChatGPT基本概念
- 定義：基於GPT架構的對話型AI
- 核心能力：文字理解、生成、摘要、分析
- 優勢：
  - 理解語境能力強
  - 處理複雜指令
  - 掌握廣泛領域知識（含金融）
  - 多語言支援
- 限制：
  - 知識截止日期
  - 幻覺（虛構內容）
  - 模型推理不透明

### 4-2 OpenAI API概述
- API結構：端點、模型、參數
- 主要模型：
  - GPT-4：最強大，準確度高但成本高
  - GPT-3.5 Turbo：平衡效能與成本
  - 其他專用模型：嵌入、編輯等
- 關鍵參數：
  - temperature：創造性控制（0最確定性）
  - max_tokens：控制回應長度
  - presence/frequency penalties：避免重複
- 計費模式：基於輸入/輸出tokens計費

### 4-3 環境準備與API設置
```python
# 安裝必要套件
!pip install openai requests pandas matplotlib numpy

# 設置API金鑰（環境變數為佳）
import os
import openai

# 方法1：從環境變數取得（推薦）
openai.api_key = os.getenv("OPENAI_API_KEY")

# 方法2：直接設置（不適合正式環境）
# openai.api_key = "your-api-key-here"

# 測試連線
response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello!"}
    ]
)
print(response.choices[0].message['content'])
```

### 4-4 基本API呼叫
```python
def query_gpt(prompt, system_msg="", model="gpt-3.5-turbo"):
    """基本GPT查詢函式"""
    messages = []
    
    # 加入系統訊息（如果提供）
    if system_msg:
        messages.append({"role": "system", "content": system_msg})
    
    # 加入使用者訊息
    messages.append({"role": "user", "content": prompt})
    
    # API呼叫
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0,  # 對於情緒分析，低溫度確保一致性
        max_tokens=500
    )
    
    return response.choices[0].message['content']

# 測試情緒分析
news = "台積電Q4財報優於市場預期，營收創新高，但2023年展望保守。"
system_msg = "你是一位專業的金融情緒分析師，專門分析財經新聞的情緒傾向。"
prompt = f"分析以下新聞的情緒傾向（正面/負面/中性）並解釋原因：\n\n{news}"

result = query_gpt(prompt, system_msg)
print(result)
```

### 4-5 金融專業提示工程
- 系統訊息優化：定義分析師角色與專業背景
- 提示設計核心要素：
  - 任務明確化：情緒、強度、理由
  - 輸出格式控制：結構化JSON便於解析
  - 提供分析框架與標準
  - 包含少樣本示例（few-shot learning）
- 範例提示模板：

```python
# 專業金融情緒分析系統提示
SYSTEM_PROMPT = """
你是一位資深金融分析師，專精於情緒分析。請分析以下財經文字的情緒傾向：
1. 將情緒評分為-1.0（極負面）到1.0（極正面）之間的數值
2. 給出0-100%的信心度評分
3. 列出支持你分析的關鍵詞或句子
4. 考慮金融專業術語的實際含義（如"獲利預警"為負面）
5. 以JSON格式返回結果：{"score": 數值, "confidence": 百分比, "key_factors": [因素列表]}
"""

# 帶範例的提示模板（few-shot）
FEW_SHOT_EXAMPLES = """
範例1:
"台積電宣布加速3奈米量產，客戶需求強勁"
{"score": 0.8, "confidence": 90, "key_factors": ["加速量產", "需求強勁"]}

範例2:
"某公司營收下滑15%，但虧損幅度優於預期"
{"score": -0.3, "confidence": 75, "key_factors": ["營收下滑", "優於預期"]}
"""
```

## 第五章：使用GPT API取得情緒指數

### 5-1 情緒分析流程設計
- 整體工作流：
  - 資料蒐集：新聞API、社群爬蟲
  - 預處理：清洗、分割、格式化
  - API分析：批次處理、解析結果
  - 指數計算：加權、平滑、正規化
- 系統架構考量：
  - 擴展性：支援多股票、多來源
  - 效率：批次處理策略、成本優化
  - 可靠性：錯誤處理、重試機制
  - 合規性：資料隱私與使用條款

### 5-2 採集財經文字資料
```python
import requests
import pandas as pd
from datetime import datetime, timedelta

# 從新聞API取得特定公司新聞
def get_company_news(company, days=7, api_key="your_newsapi_key"):
    """取得公司相關新聞"""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    url = f"https://newsapi.org/v2/everything?q={company}&from={start_date.strftime('%Y-%m-%d')}&to={end_date.strftime('%Y-%m-%d')}&sortBy=popularity&apiKey={api_key}"
    
    response = requests.get(url)
    if response.status_code == 200:
        news_data = response.json()
        articles = news_data.get('articles', [])
        return pd.DataFrame(articles)
    else:
        print(f"錯誤: {response.status_code}")
        return pd.DataFrame()
    
# 從PTT股板爬取討論（簡化版）
def scrape_ptt_stock(stock_id, pages=3):
    """爬取PTT股票版特定股票的討論"""
    import requests
    from bs4 import BeautifulSoup
    
    posts = []
    # 實際實作中需添加爬蟲邏輯
    # ...
    
    return pd.DataFrame(posts)
```

### 5-3 文字預處理與優化
```python
def preprocess_for_gpt(text, max_length=3000):
    """預處理文字以供GPT分析"""
    # 基本清洗
    text = text.replace('\n', ' ').replace('\r', ' ')
    text = ' '.join(text.split())  # 移除多餘空格
    
    # 截斷過長文字（避免超出token限制）
    if len(text) > max_length:
        text = text[:max_length] + "..."
    
    return text

# 分割過長文字
def chunk_long_text(text, chunk_size=3000, overlap=200):
    """將長文字分割為較小區塊，保留上下文重疊"""
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        if end < len(text) and end - start < chunk_size:
            # 尋找句子邊界
            sentence_end = text.rfind('. ', start, end) + 1
            if sentence_end > start:
                end = sentence_end
        
        chunks.append(text[start:end])
        start = end - overlap if end < len(text) else end
    
    return chunks
```

### 5-4 情緒分析提示設計
```python
def create_sentiment_prompt(text, company_name=None):
    """建立情緒分析提示"""
    system_msg = """你是一位專業金融分析師，專精於情緒分析。分析文字的情緒傾向，並返回以下JSON格式：
{
  "sentiment_score": 情緒分數（-1到1，負面到正面），
  "confidence": 信心水準（0到1），
  "key_factors": [支持這一評分的關鍵因素]
}"""

    if company_name:
        prompt = f"分析以下文字對{company_name}的情緒傾向:\n\n{text}"
    else:
        prompt = f"分析以下財經文字的整體情緒傾向:\n\n{text}"
    
    return system_msg, prompt

# 多類別情緒分析提示
def create_advanced_sentiment_prompt(text):
    """建立細分情緒類別的分析提示"""
    system_msg = """你是一位專業金融分析師，專精於多維度情緒分析。分析文字並返回以下JSON格式：
{
  "overall_score": 總體情緒（-1到1），
  "dimensions": {
    "growth": 成長前景評分（-1到1），
    "risk": 風險評估（-1到1），
    "management": 管理層評價（-1到1）
  },
  "emotions": {
    "optimism": 樂觀程度（0到1），
    "fear": 恐懼程度（0到1），
    "confidence": 信心程度（0到1）
  },
  "key_sentences": [關鍵句子列表]
}"""

    prompt = f"進行多維度情緒分析:\n\n{text}"
    return system_msg, prompt
```

### 5-5 API呼叫與結果處理
```python
import json
import time
import openai

def analyze_sentiment_with_gpt(text, company_name=None, model="gpt-3.5-turbo"):
    """使用GPT進行情緒分析"""
    system_msg, prompt = create_sentiment_prompt(text, company_name)
    
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": prompt}
            ],
            temperature=0,
            max_tokens=250
        )
        
        # 解析JSON回應
        response_text = response.choices[0].message['content']
        
        # 處理非標準JSON輸出（清理並解析）
        response_text = response_text.strip()
        if response_text.startswith("```json"):
            response_text = response_text.replace("```json", "").replace("```", "")
        
        sentiment_data = json.loads(response_text)
        return sentiment_data
    
    except Exception as e:
        print(f"分析情緒時發生錯誤: {e}")
        time.sleep(2)  # 速率限制處理
        return {"sentiment_score": None, "confidence": None, "key_factors": []}

# 批次處理新聞項
def process_news_batch(news_df, company_name, max_items=None):
    """批次處理新聞文章"""
    results = []
    
    # 限制處理項目數（如果指定）
    if max_items:
        news_df = news_df.head(max_items)
    
    for i, row in news_df.iterrows():
        print(f"處理項目 {i+1}/{len(news_df)}")
        content = row.get('content', '') or row.get('description', '')
        
        if not content:
            continue
            
        processed_text = preprocess_for_gpt(content)
        sentiment = analyze_sentiment_with_gpt(processed_text, company_name)
        
        # 添加元資料
        sentiment['date'] = row.get('publishedAt', datetime.now().isoformat())
        sentiment['title'] = row.get('title', '')
        sentiment['source'] = row.get('source', {}).get('name', '')
        sentiment['url'] = row.get('url', '')
        
        results.append(sentiment)
        
        # 避免API限制
        time.sleep(1)
    
    return pd.DataFrame(results)
```

### 5-6 情緒指數建構
```python
import numpy as np
import matplotlib.pyplot as plt

def calculate_sentiment_index(sentiment_df, decay_factor=0.2):
    """計算時間加權情緒指數"""
    # 確保有時間資料
    if 'date' not in sentiment_df.columns or sentiment_df.empty:
        print("資料缺少日期資訊或為空")
        return pd.Series()
    
    # 轉換日期為datetime
    sentiment_df['date'] = pd.to_datetime(sentiment_df['date'])
    
    # 排序
    sentiment_df = sentiment_df.sort_values('date')
    
    # 計算時間權重（較新 = 更重要）
    max_date = sentiment_df['date'].max()
    sentiment_df['days_old'] = (max_date - sentiment_df['date']).dt.total_seconds() / (60*60*24)
    sentiment_df['time_weight'] = np.exp(-decay_factor * sentiment_df['days_old'])
    
    # 應用權重（包括信心度）
    sentiment_df['weighted_score'] = sentiment_df['sentiment_score'] * sentiment_df.get('confidence', 1) * sentiment_df['time_weight']
    
    # 按日計算加權平均
    daily_sentiment = sentiment_df.groupby(sentiment_df['date'].dt.date)['weighted_score'].mean()
    
    return daily_sentiment

# 視覺化情緒指數
def plot_sentiment_index(sentiment_index, stock_symbol):
    """繪製情緒指數趨勢圖"""
    plt.figure(figsize=(12, 6))
    plt.plot(sentiment_index.index, sentiment_index.values, 'b-', linewidth=2)
    plt.axhline(y=0, color='r', linestyle='--', alpha=0.3)
    plt.fill_between(sentiment_index.index, 0, sentiment_index.values, 
                     where=(sentiment_index.values > 0), color='green', alpha=0.2)
    plt.fill_between(sentiment_index.index, 0, sentiment_index.values, 
                     where=(sentiment_index.values < 0), color='red', alpha=0.2)
    
    plt.title(f'{stock_symbol} 情緒指數趨勢', fontsize=15)
    plt.xlabel('日期')
    plt.ylabel('加權情緒分數')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    # 添加均線
    if len(sentiment_index) > 3:
        sentiment_index.rolling(window=3).mean().plot(
            color='orange', linestyle='-.', label='3日均線')
        plt.legend()
    
    return plt
```

### 5-7 多股票綜合分析
```python
def batch_sentiment_analysis(stock_list, days=7, api_key=None):
    """批次分析多支股票的新聞情緒"""
    all_sentiment_data = {}
    
    for stock in stock_list:
        print(f"處理 {stock}...")
        news = get_company_news(stock, days=days, api_key=api_key)
        
        if news.empty:
            print(f"未找到 {stock} 的新聞")
            continue
        
        # 處理新聞
        stock_sentiment = process_news_batch(news, stock, max_items=10)
        
        # 計算該股票的指數
        if not stock_sentiment.empty and 'sentiment_score' in stock_sentiment:
            try:
                all_sentiment_data[stock] = calculate_sentiment_index(stock_sentiment)
            except Exception as e:
                print(f"計算 {stock} 指數時出錯: {e}")
    
    return all_sentiment_data

# 市場綜合情緒指數
def calculate_market_sentiment(sentiment_dict, weights=None):
    """計算市場綜合情緒指數"""
    # 股票列表
    stocks = list(sentiment_dict.keys())
    
    if not stocks:
        return pd.Series()
    
    # 預設等權重
    if weights is None:
        weights = {stock: 1/len(stocks) for stock in stocks}
    
    # 確保所有股票資料具有相同的日期索引
    all_dates = set()
    for stock in stocks:
        all_dates.update(sentiment_dict[stock].index)
    all_dates = sorted(list(all_dates))
    
    # 建立市場指數
    market_sentiment = pd.Series(0, index=all_dates)
    
    # 加權計算
    for stock in stocks:
        # 重新索引以對齊日期
        stock_sentiment = sentiment_dict[stock].reindex(all_dates).fillna(0)
        market_sentiment += stock_sentiment * weights.get(stock, 1/len(stocks))
    
    return market_sentiment
```

## 第六章：金融情緒分析的現在與未來

### 6-1 當前產業應用
- 主要應用場景：
  - 量化交易：情緒因子納入多因子模型
  - 風險管理：情緒異常作為風險預警
  - 投資研究：輔助基本面與技術面分析
  - 市場監控：即時監測市場情緒波動
- 業界領導者：
  - Bloomberg GPT：專為金融領域優化的LLM
  - RavenPack：專業新聞情緒資料提供商
  - MarketPsych：社群媒體情緒指數
  - 投資銀行自建系統

### 6-2 多模態情緒分析
- 超越純文字：整合圖像、音訊、影片
- 應用場景：
  - 分析財報影片中CEO表情與語調
  - 解讀財經節目主持人情緒變化
  - 評估投資人電話會議中的語氣
  - 分析財經圖表與文字的結合解讀
- 技術架構：
  - 視覺Transformer (ViT) 處理圖像
  - 與LLM結合的多模態融合層
  - 跨模態注意力機制

### 6-3 即時情緒交易系統
- 系統架構：
  - 資料層：多源資料蒐集與整合
  - 分析層：情緒分析與訊號生成
  - 策略層：訊號過濾與交易決策
  - 執行層：委託管理與風險控制
- 關鍵技術：
  - 流處理框架（Kafka、Flink）
  - 低延遲API呼叫策略
  - 訊號檢驗與過濾演算法
  - 風險限制機制

### 6-4 先進AI技術應用
- 因果推論：
  - 識別情緒與市場關係的因果機制
  - 處理混淆變數（如：重大事件）
  - 建構反事實情境分析
- 強化學習：
  - 自適應情緒閾值調整
  - 多週期訊號最佳化
  - 市場狀態感知的策略選擇
- 可解釋AI：
  - 情緒判斷根據視覺化
  - 因子影響力分解
  - 決策路徑追蹤

### 6-5 道德考量與挑戰
- 市場操縱風險：
  - 情緒分析可能被用於市場操縱
  - 假新聞放大效應
  - 高頻情緒交易的系統性風險
- 資訊不對稱：
  - 大型機構優勢擴大
  - 散戶投資人的資料壁壘
  - 演算法透明度問題
- 監管環境：
  - 情緒分析相關法規不完善
  - 跨司法管轄區的法遵挑戰
  - 隱私保護與資料使用平衡

### 6-6 未來發展方向
- 個性化情緒分析：
  - 投資人風格客製化
  - 個人風險偏好適配
  - 情緒反應模式識別
- 跨資產情緒溢出：
  - 股票→債券→商品情緒傳導
  - 產業間情緒關聯網路
  - 全球市場情緒連動性
- 先進技術整合：
  - 聯邦學習實現隱私保護
  - 量子運算加速情緒處理
  - 大規模知識圖譜增強情緒理解
- 台灣市場特色：
  - 台灣市場情緒指數在地化
  - A股與港股情緒同步性研究
  - 兩岸三地金融術語整合