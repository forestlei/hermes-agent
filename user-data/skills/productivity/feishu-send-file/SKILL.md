---
name: feishu-send-file
description: 通过飞书API上传文件并发送到聊天，默认md转PDF发送
version: 2.0.0
author: Hermes Agent
metadata:
  hermes:
    tags: [Feishu, File-Upload, Messaging]
    category: productivity
    requires_toolsets: [terminal]
---

# 飞书发文件

通过飞书开放平台API上传文件并发送到指定聊天。**日报/报告默认转PDF发送。**

## 前置条件

- 飞书应用已开通 `im:resource` 权限（上传文件）
- 飞书应用已开通 `im:message:send_as_bot` 权限（发送消息）
- 凭据在配置文件中：`FEISHU_APP_ID` 和 `FEISHU_APP_SECRET`

## ⚠️ 凭据获取规则（必读！）

**execute_code沙箱没有环境变量！必须从配置文件读取！**

用 `_load_feishu_creds()` 辅助函数：
```python
def _load_feishu_creds():
    """从配置文件读取飞书凭据（沙箱安全）"""
    import os
    env_path = os.path.expanduser("~/.hermes/.env")
    app_id = app_secret = None
    with open(env_path) as f:
        for line in f:
            k = line.strip()
            if k.startswith("FEISHU_APP_ID="):
                app_id = k.split("=", 1)[1]
            elif k.startswith("FEISHU_APP_SECRET="):
                app_secret = k.split("=", 1)[1]
    return app_id, app_secret
```

## ⚠️ chat_id 获取规则（必读！）

**永远不要硬编码 chat_id！**

| 场景 | chat_id来源 |
|------|------------|
| 当前会话回复 | `HERMES_SESSION_CHAT_ID` 环境变量 |
| AI日报群 | `oc_6ed1cc645057da3bbe93c6120219a61e` — 仅在cron/日报场景使用 |
| Home频道 | `FEISHU_HOME_CHANNEL` 环境变量 |
| 用户指定 | 用户明确给出的chat_id |

**cron场景**：环境变量可能为空，此时按场景选择默认群。

## 默认发送流程：md → PDF → 飞书发文件

**日报/报告类内容必须转PDF发送，不要发纯文本！** 原因：飞书不支持.md预览，纯文本太长会被截断。

### 完整一键发送脚本（推荐）

```python
from hermes_tools import terminal
import json, os

def _load_feishu_creds():
    env_path = os.path.expanduser("~/.hermes/.env")
    app_id = app_secret = None
    with open(env_path) as f:
        for line in f:
            k = line.strip()
            if k.startswith("FEISHU_APP_ID="):
                app_id = k.split("=", 1)[1]
            elif k.startswith("FEISHU_APP_SECRET="):
                app_secret = k.split("=", 1)[1]
    return app_id, app_secret

def _get_chat_id(chat_id=None):
    if chat_id is None:
        chat_id = os.environ.get("HERMES_SESSION_CHAT_ID")
    if not chat_id:
        chat_id = "oc_6ed1cc645057da3bbe93c6120219a61e"
    return chat_id

def _get_token():
    app_id, app_secret = _load_feishu_creds()
    payload = json.dumps({"app_id": app_id, "app_secret": app_secret})
    r = terminal(f"""curl -s -X POST 'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal' -H 'Content-Type: application/json' -d '{payload}'""")
    return json.loads(r['output'])['tenant_access_token']

def feishu_send_report(md_path, chat_id=None):
    """日报/报告发送：md→PDF→飞书发文件，一步到位"""
    chat_id = _get_chat_id(chat_id)
    
    # md→HTML→PDF
    import markdown
    with open(md_path) as f:
        md_content = f.read()
    html_body = markdown.markdown(md_content, extensions=["tables", "fenced_code"])
    html_full = f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<style>
body {{ font-family: "PingFang SC","Microsoft YaHei","Noto Sans CJK SC",sans-serif; 
       margin: 40px; line-height: 1.8; color: #333; font-size: 14px; }}
h1 {{ color: #1a1a2e; border-bottom: 2px solid #e94560; padding-bottom: 8px; }}
h2 {{ color: #16213e; border-left: 4px solid #e94560; padding-left: 10px; margin-top: 30px; }}
h3 {{ color: #0f3460; }}
table {{ border-collapse: collapse; width: 100%; margin: 10px 0; }}
th, td {{ border: 1px solid #ddd; padding: 8px 12px; text-align: left; font-size: 13px; }}
th {{ background-color: #1a1a2e; color: white; }}
tr:nth-child(even) {{ background-color: #f8f8f8; }}
blockquote {{ border-left: 4px solid #e94560; margin: 10px 0; padding: 10px 15px; background: #fff5f5; }}
a {{ color: #e94560; text-decoration: none; }}
</style></head><body>{html_body}</body></html>"""
    
    base = os.path.splitext(md_path)[0]
    html_path, pdf_path = base + ".html", base + ".pdf"
    with open(html_path, "w") as f:
        f.write(html_full)
    
    r = terminal(f"weasyprint {html_path} {pdf_path} 2>&1")
    if r['exit_code'] != 0:
        raise RuntimeError(f"PDF conversion failed: {r['output'][:200]}")
    
    # 上传+发送
    token = _get_token()
    pdf_name = os.path.basename(pdf_path)
    r2 = terminal(f"""curl -s -X POST 'https://open.feishu.cn/open-apis/im/v1/files' -H 'Authorization: Bearer {token}' -F 'file_type=pdf' -F 'file_name={pdf_name}' -F 'file=@{pdf_path}'""")
    upload_data = json.loads(r2['output'])
    if upload_data.get('code') != 0:
        raise RuntimeError(f"Upload failed: {upload_data}")
    file_key = upload_data['data']['file_key']
    
    content_str = json.dumps({"file_key": file_key})
    body = json.dumps({"receive_id": chat_id, "msg_type": "file", "content": content_str})
    r3 = terminal(f"""curl -s -X POST 'https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id' -H 'Authorization: Bearer {token}' -H 'Content-Type: application/json' -d '{body}'""")
    send_data = json.loads(r3['output'])
    if send_data.get('code') != 0:
        raise RuntimeError(f"Send failed: {send_data}")
    return send_data

def feishu_send_file(file_path, file_name=None, chat_id=None):
    """发送任意文件到飞书"""
    chat_id = _get_chat_id(chat_id)
    if file_name is None:
        file_name = os.path.basename(file_path)
    
    ext = os.path.splitext(file_name)[1].lower()
    file_type_map = {'.pdf':'pdf','.doc':'doc','.docx':'docx','.xls':'xls',
                     '.xlsx':'xlsx','.ppt':'ppt','.pptx':'pptx','.mp4':'mp4','.opus':'opus'}
    file_type = file_type_map.get(ext, 'stream')
    
    token = _get_token()
    r2 = terminal(f"""curl -s -X POST 'https://open.feishu.cn/open-apis/im/v1/files' -H 'Authorization: Bearer {token}' -F 'file_type={file_type}' -F 'file_name={file_name}' -F 'file=@{file_path}'""")
    file_key = json.loads(r2['output'])['data']['file_key']
    
    content_str = json.dumps({"file_key": file_key})
    body = json.dumps({"receive_id": chat_id, "msg_type": "file", "content": content_str})
    r3 = terminal(f"""curl -s -X POST 'https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id' -H 'Authorization: Bearer {token}' -H 'Content-Type: application/json' -d '{body}'""")
    return json.loads(r3['output'])

def feishu_send_text(text, chat_id=None):
    """发送文本消息到飞书群"""
    chat_id = _get_chat_id(chat_id)
    token = _get_token()
    
    body = json.dumps({"receive_id": chat_id, "msg_type": "text", "content": json.dumps({"text": text})})
    r2 = terminal(f"""curl -s -X POST 'https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id' -H 'Authorization: Bearer {token}' -H 'Content-Type: application/json' -d '{body}'""")
    return json.loads(r2['output'])
```

## User Preference: Always Send Files Directly
- **不要只给文件路径**——用户无法打开服务器上的路径，必须通过飞书API直接发送文件
- 生成报告后，立即调用发送流程，不要只告诉用户"文件已保存到/path"
- 即使是临时报告/调研结果，也应主动发送

## Pitfalls

- **execute_code沙箱没有环境变量**——必须从配置文件读取凭据，不能用`os.environ.get()`
- **chat_id绝对不能硬编码**——优先从`HERMES_SESSION_CHAT_ID`获取，cron场景fallback到日报群
- **content 字段必须双重转义**——它是 JSON 字符串而非 JSON 对象
- **file_type=stream 是万能类型**——非标准文件都用 stream
- **token 有效期2小时**——保险起见每次操作前获取新的
- **应用必须在目标群中**——bot 需要是群成员才能发消息
- **.md 文件飞书不支持预览**——必须转PDF后再发
- **中文文件名可能乱码**——建议用英文文件名
- **weasyprint已安装在venv中**——可直接调用，无需安装
- **⚠️ weasyprint PDF转换经常失败**——中文内容+复杂表格时尤其容易crash（font渲染、CSS属性不支持等）。Fallback方案：用 `file_type=stream` 直接发送.md文件，虽然飞书不能预览但至少用户能下载打开。优先尝试PDF，失败后立即fallback到stream
