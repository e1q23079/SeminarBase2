import re
import html


def _replace_video_markdown(match: re.Match[str]) -> str:
    """
    url を受け取り、ビデオタグに変換する関数
    """
    url = match.group(1)
    if url.startswith("/") and not url.startswith("//"):
        url = html.escape(url)
        return f'<video src="{url}" controls controlslist="nodownload"></video>'    # noqa: E501
    return match.group(0)


def convert_video_markdown(content):
    """
    ビデオタグを変換する関数
    """
    return re.sub(
        r'\[video:\]\((.*?)\)',
        _replace_video_markdown,
        content
    )
