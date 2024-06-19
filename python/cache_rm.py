import shutil
import os

# Hugging Face 캐시 디렉토리 경로
cache_dir = os.path.expanduser('~/.cache/huggingface/hub/models--Falconsai--text_summarization')
# cache_dir = os.path.expanduser('~/.cache/huggingface/hub/models--jordiclive--flan-t5-3b-summarizer')

# 캐시 디렉토리 삭제
if os.path.exists(cache_dir):
    shutil.rmtree(cache_dir)
    print(f"Deleted cache directory: {cache_dir}")
else:
    print(f"Cache directory does not exist: {cache_dir}")
