import json
import subprocess
from typing import Any, Dict, List, Optional

from fastapi.logger import logger
from preview_generator.preview.builder.video__ffmpeg import VideoPreviewBuilderFFMPEG
from preview_generator.utils import ImgDims

TIMEOUT_SECONDS = 30


def run_tool(args: List[str]) -> bytes:
    try:
        completed = subprocess.run(args, capture_output=True, check=True, timeout=TIMEOUT_SECONDS)
    except subprocess.CalledProcessError as error:
        stderr = error.stderr.decode(errors='replace')
        logger.warning('%s failed on %s: %s', args[0], args[-1], stderr)
        raise
    return completed.stdout


def probe(file_path: str) -> Dict[str, Any]:
    output = run_tool(['ffprobe', '-show_format', '-show_streams', '-of', 'json', file_path])
    return json.loads(output)


class VideoPosterBuilder(VideoPreviewBuilderFFMPEG):
    """
    Preview a video with a single poster frame. Unlike its parent, it bounds
    ffprobe and ffmpeg with a timeout and probes the video when counting pages.
    """
    weight = VideoPreviewBuilderFFMPEG.weight + 1
    page_nb = 1

    def get_page_number(self, file_path: str, preview_name: str, cache_path: str, mimetype: Optional[str] = None) -> int:
        probe_data = probe(file_path)
        self.get_dims_from_ffmpeg_probe(probe_data)
        return self.page_nb

    def build_jpeg_preview(self, file_path: str, preview_name: str, cache_path: str, page_id: int, extension: str = '.jpg', size: Optional[ImgDims] = None, mimetype: str = '') -> None:
        size = size or self.default_size
        preview_path = f'{cache_path}{preview_name}{extension}'
        probe_data = probe(file_path)
        video_size = self.get_dims_from_ffmpeg_probe(probe_data)
        extraction_size = self._get_extraction_size(video_size, size)
        duration = float(probe_data['format'].get('duration', 0))
        frame_time = self._get_frame_time(0, self.page_nb, duration)
        scale = f'scale={extraction_size.width}:{extraction_size.height}'
        run_tool(['ffmpeg', '-nostdin', '-y', '-ss', str(frame_time), '-i', file_path, '-vf', scale, '-frames:v', '1', preview_path])
