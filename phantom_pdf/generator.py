# -*- coding: utf-8 -*-

import logging
from subprocess import Popen, STDOUT, PIPE
import os
import phantom_pdf_bin
import urlparse
import uuid

from django.conf import settings
from django.http import HttpResponse


logger = logging.getLogger(__name__)


# Path to generate_pdf.js file. Its distributed with this django product.
GENERATE_PDF_JS = os.path.join(os.path.dirname(phantom_pdf_bin.__file__),
                               'generate_pdf.js')
PHANTOM_ROOT_DIR = '/tmp/phantom_pdf'
DEFAULT_SETTINGS = dict(
    PHANTOMJS_COOKIE_DIR=os.path.join(PHANTOM_ROOT_DIR, 'cookies'),
    PHANTOMJS_GENERATE_PDF=GENERATE_PDF_JS,
    PHANTOMJS_PDF_DIR=os.path.join(PHANTOM_ROOT_DIR, 'pdfs'),
    PHANTOMJS_BIN='phantomjs',
    PHANTOMJS_FORMAT='A4',
    PHANTOMJS_ORIENTATION='landscape',
    KEEP_PDF_FILES=False,
)


class RequestToPDF(object):
    """Class for rendering a requested page to a PDF."""

    def __init__(self,
                 PHANTOMJS_COOKIE_DIR=None,
                 PHANTOMJS_PDF_DIR=None,
                 PHANTOMJS_BIN=None,
                 PHANTOMJS_GENERATE_PDF=None,
                 KEEP_PDF_FILES=None):
        """Arguments:
            PHANTOMJS_COOKIE_DIR = Directory where the temp cookies will be saved.
            PHANTOMJS_PDF_DIR = Directory where you want to the PDF to be saved temporarily.
            PHANTOMJS_BIN = Path to PhantomsJS binary.
            PHANTOMJS_GENERATE_PDF = Path to generate_pdf.js file.
            KEEP_PDF_FILES = Option to not delete the PDF file after rendering it.
        """
        self.PHANTOMJS_COOKIE_DIR = PHANTOMJS_COOKIE_DIR
        self.PHANTOMJS_PDF_DIR = PHANTOMJS_PDF_DIR
        self.PHANTOMJS_BIN = PHANTOMJS_BIN
        self.PHANTOMJS_GENERATE_PDF = PHANTOMJS_GENERATE_PDF
        self.KEEP_PDF_FILES = KEEP_PDF_FILES

        for attr in [
                'PHANTOMJS_COOKIE_DIR',
                'PHANTOMJS_PDF_DIR',
                'PHANTOMJS_BIN',
                'PHANTOMJS_GENERATE_PDF',
                'KEEP_PDF_FILES']:

            if getattr(self, attr, None) is None:
                value = getattr(settings, attr, None)
                if value is None:
                    value = DEFAULT_SETTINGS[attr]
                setattr(self, attr, value)

        assert os.path.isfile(self.PHANTOMJS_BIN), \
            "%s doesnt exist, read the docs for more info." % self.PHANTOMJS_BIN
        for dir_ in [self.PHANTOMJS_COOKIE_DIR, self.PHANTOMJS_PDF_DIR]:
            if not os.path.isdir(dir_):
                os.makedirs(dir_)

    def _build_url(self, request):
        """Build the url for the request."""
        scheme, netloc, path, query, fragment = urlparse.urlsplit(
            request.build_absolute_uri())
        protocol = scheme
        domain = netloc
        return '{protocol}://{domain}{path}'.format(
            protocol=protocol,
            domain=domain,
            path=path)

    def _save_cookie_data(self, request):
        """Save csrftoken and sessionid in a cookie file for authentication."""
        cookie_file = ''.join((
            os.path.join(
                self.PHANTOMJS_COOKIE_DIR, str(uuid.uuid1())
            ), '.cookie.txt'
        ))
        with open(cookie_file, 'w+') as fh:
            cookie = ''.join((
                request.COOKIES.get('csrftoken', 'nocsrftoken'),
                ' ',
                request.COOKIES.get('sessionid', 'nosessionid')
            ))
            fh.write(cookie)
        return cookie_file

    def _set_source_file_name(self, basename=str(uuid.uuid1())):
        """Return the original source filename of the pdf."""
        return ''.join((os.path.join(self.PHANTOMJS_PDF_DIR, basename), '.pdf'))

    def _return_response(self, file_src, basename):
        """Read the generated pdf and return it in a django HttpResponse."""
        # Open the file created by PhantomJS
        return_file = None
        with open(file_src, 'rb') as f:
            return_file = f.readlines()

        response = HttpResponse(
            return_file,
            content_type='application/pdf'
        )
        content_disposition = 'attachment; filename=%s.pdf' % (basename)
        response['Content-Disposition'] = content_disposition

        if not self.KEEP_PDF_FILES:  # remove generated pdf files
            os.remove(file_src)

        return response

    def request_to_pdf(self, request, basename,
                       format=DEFAULT_SETTINGS['PHANTOMJS_FORMAT'],
                       orientation=DEFAULT_SETTINGS['PHANTOMJS_ORIENTATION']):
        """Receive request, basename and return a PDF in an HttpResponse."""

        file_src = self._set_source_file_name(basename=basename)
        try:
            os.remove(file_src)
            logger.info("Removed already existing file: %s", file_src)
        except OSError:
            pass

        cookie_file = self._save_cookie_data(request)
        url = self._build_url(request)

        domain = urlparse.urlsplit(
            request.build_absolute_uri()
        ).netloc.split(':')[0]

        # Some servers have SSLv3 disabled, leave
        # phantomjs connect with others than SSLv3
        ssl_protocol = "--ssl-protocol=ANY"
        try:
            phandle = Popen([
                self.PHANTOMJS_BIN,
                ssl_protocol,
                self.PHANTOMJS_GENERATE_PDF,
                url,
                file_src,
                cookie_file,
                domain,
                format,
                orientation
            ], close_fds=True, stdout=PIPE, stderr=STDOUT)
            phandle.communicate()

        finally:
            # Make sure we remove the cookie file.
            os.remove(cookie_file)

        return self._return_response(file_src, basename)


def render_to_pdf(request, basename,
                  format=DEFAULT_SETTINGS['PHANTOMJS_FORMAT'],
                  orientation=DEFAULT_SETTINGS['PHANTOMJS_ORIENTATION']):
    """Helper function for rendering a request to pdf.
    Arguments:
        request = django request.
        basename = string to use for your pdf's filename.
        format = the page size to be applied; default if not given.
        orientation = the page orientation to use; default if not given.
    """
    request2pdf = RequestToPDF()
    response = request2pdf.request_to_pdf(request, basename, format=format,
                                          orientation=orientation)
    return response
