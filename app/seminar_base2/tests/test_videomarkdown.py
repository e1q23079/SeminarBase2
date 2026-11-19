# VideoMarkdownのテスト
from django.test import TestCase
from ..lib.videomarkdown import convert_video_markdown


class VideoMarkdownTests(TestCase):
    """
    VideoMarkdownクラスのテストケース
    """

    def test_video_markdown_conversion(self):
        """
        VideoMarkdownの変換が正しく行われるかをテストする
        """
        input_content = "これはテストです。[video:](/media/video.mp4) これはテストです。"   # noqa: E501
        expected_output = 'これはテストです。<video src="/media/video.mp4" controls controlslist="nodownload"></video> これはテストです。'    # noqa: E501
        actual_output = convert_video_markdown(input_content)
        self.assertEqual(actual_output, expected_output)

    def test_video_markdown_conversion_with_double_slash(self):
        """
        URLが//で始まる場合、VideoMarkdownの変換が行われないことをテストする
        """
        input_content = "これはテストです。[video:](//media/video.mp4) これはテストです。"  # noqa: E501
        actual_output = convert_video_markdown(input_content)
        self.assertEqual(actual_output, input_content)

    def test_video_markdown_conversion_with_external_url(self):
        """
        URLが外部URLの場合、VideoMarkdownの変換が行われないことをテストする
        """
        input_content = "これはテストです。[video:](http://example.com/video.mp4) これはテストです。"   # noqa: E501
        actual_output = convert_video_markdown(input_content)
        self.assertEqual(actual_output, input_content)

    def test_video_markdown_conversion_with_no_video_tag(self):
        """
        VideoMarkdownのタグが含まれない場合、変換が行われないことをテストする
        """
        input_content = "これはテストです。ビデオタグはありません。"    # noqa: E501
        actual_output = convert_video_markdown(input_content)
        self.assertEqual(actual_output, input_content)

    def test_video_markdown_conversion_with_multiple_tags(self):
        """
        複数のVideoMarkdownタグが含まれる場合、すべてのタグが正しく変換されることをテストする
        """
        input_content = "これはテストです。[video:](/media/video1.mp4) これはテストです。[video:](/media/video2.mp4)"   # noqa: E501
        expected_output = 'これはテストです。<video src="/media/video1.mp4" controls controlslist="nodownload"></video> これはテストです。<video src="/media/video2.mp4" controls controlslist="nodownload"></video>'   # noqa: E501
        actual_output = convert_video_markdown(input_content)
        self.assertEqual(actual_output, expected_output)

    def test_video_markdown_conversion_with_escaped_url(self):
        """
        URLがエスケープされることをテストする
        """
        input_content = "これはテストです。[video:](/<script>alert('XSS')</script>/media/video with spaces.mp4) これはテストです。"  # noqa: E501
        expected_output = 'これはテストです。<video src="/&lt;script&gt;alert(&#x27;XSS&#x27;" controls controlslist="nodownload"></video></script>/media/video with spaces.mp4) これはテストです。'    # noqa: E501
        actual_output = convert_video_markdown(input_content)
        self.assertEqual(actual_output, expected_output)
