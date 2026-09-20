from __future__ import annotations
import json, os, sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
sys.path.insert(0,str(Path(__file__).resolve().parent))
from content_generator import choose_book_link, generate_post
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'output'
def main():
    max_chars=int(os.getenv('POST_MAX_CHARS','2850')); link=choose_book_link(); post,meta=generate_post(link,max_chars); OUT.mkdir(parents=True,exist_ok=True)
    date_key=datetime.now(ZoneInfo('Asia/Kolkata')).strftime('%Y-%m-%d')
    (OUT/f'{date_key}.md').write_text(post+'\n',encoding='utf-8'); (OUT/'latest.txt').write_text(post+'\n',encoding='utf-8'); (OUT/'metadata.json').write_text(json.dumps(meta,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(post); print(f'Generated {len(post)} characters | Topic: {meta["topic"]} | Question bank: {meta["question_bank_size"]}')
if __name__=='__main__': main()
