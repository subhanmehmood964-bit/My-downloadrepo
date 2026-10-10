from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import yt_dlp

app = FastAPI()

class ExtractRequest(BaseModel):
    url: str

@app.post("/extract")
def extract_media(req: ExtractRequest):
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(req.url, download=False)
            
            formats = []
            for f in info.get('formats', []):
                if f.get('vcodec') != 'none':
                    formats.append({
                        'type': 'video',
                        'quality': f.get('format_note') or f"{f.get('height')}p",
                        'ext': f.get('ext'),
                        'url': f.get('url')
                    })
                elif f.get('acodec') != 'none' and f.get('vcodec') == 'none':
                    formats.append({
                        'type': 'audio',
                        'quality': f"{int(f.get('abr', 128))}kbps MP3",
                        'ext': 'mp3',
                        'url': f.get('url')
                    })

            return {
                'title': info.get('title'),
                'thumbnail': info.get('thumbnail'),
                'platform': info.get('extractor_key'),
                'formats': formats
            }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
