from io import BytesIO
from PIL import Image as PilImage
from django.core.files.base import ContentFile
from django.views.static import directory_index, was_modified_since
from rest_framework import exceptions

from rest_framework.permissions import BasePermission

import mimetypes
import posixpath
from pathlib import Path

from django.http import FileResponse, Http404, HttpResponseNotModified
from django.utils._os import safe_join
from django.utils.http import http_date
from django.utils.translation import gettext as _


def secure_serve(request, path, document_root=None, show_indexes=False):
    # only auth user can see image(url)
    if not bool(request.user and request.user.is_authenticated):
        raise exceptions.AuthenticationFailed

    path = posixpath.normpath(path).lstrip("/")
    fullpath = Path(safe_join(document_root, path))
    if fullpath.is_dir():
        if show_indexes:
            return directory_index(path, fullpath)
        raise Http404(_("Directory indexes are not allowed here."))
    if not fullpath.exists():
        raise Http404(_("“%(path)s” does not exist") % {"path": fullpath})
    # Respect the If-Modified-Since header.
    statobj = fullpath.stat()
    if not was_modified_since(
            request.META.get("HTTP_IF_MODIFIED_SINCE"), statobj.st_mtime
    ):
        return HttpResponseNotModified()
    content_type, encoding = mimetypes.guess_type(str(fullpath))
    content_type = content_type or "application/octet-stream"
    response = FileResponse(fullpath.open("rb"), content_type=content_type)
    response.headers["Last-Modified"] = http_date(statobj.st_mtime)
    if encoding:
        response.headers["Content-Encoding"] = encoding
    return response


def create_exist_image(image, convert, ext='png', quality=95):
    ext = 'jpeg' if ext.lower() == 'jpg' else ext
    filename = str(image).split('/')[-1].split('.')

    with PilImage.open(image) as image:
        buff_image = BytesIO()
        binary_image = image.convert(convert)
        binary_image.save(buff_image, ext, quality=quality)

        return ContentFile(buff_image.getvalue(), f'{filename}-binary.{ext}')
