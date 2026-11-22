from django.utils.http import url_has_allowed_host_and_scheme


def is_valid_redirect_url(url, request):
    """
    リダイレクトURLが有効かどうかを判定します。
    :param url: リダイレクトURL
    :return: 有効な場合はTrue、無効な場合はFalse
    """
    if not url_has_allowed_host_and_scheme(
        url,
        allowed_hosts={request.get_host()}
    ):
        return '/'
    return url
