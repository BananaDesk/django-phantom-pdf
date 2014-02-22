# -*- coding: utf-8 -*-

import os
import uuid
import urlparse
import phantom_pdf_bin
from subprocess import Popen, STDOUT, PIPE

from django.conf import settings
from django.http import HttpResponse


# Path to generate_pdf.js file. Its distributed with this django product.
GENERATE_PDF_JS = os.path.join(os.path.dirname(phantom_pdf_bin.__file__), 'generate_pdf.js')
PHANTOM_ROOT_DIR = '/tmp/phantom_pdf'
DEFAULT_SETTINGS = dict(
    PHANTOMJS_COOKIE_DIR=os.path.join(PHANTOM_ROOT_DIR, 'cookies'),
    PHANTOMJS_PDF_DIR=os.path.join(PHANTOM_ROOT_DIR, 'pdfs'),
    PHANTOMJS_BIN='phantomjs'
)


class RequestToPDF(object):
    """Class for rendering a requested page to a PDF."""

    def __init__(self,
                 PHANTOMJS_COOKIE_DIR=None,
                 PHANTOMJS_PDF_DIR=None,
                 PHANTOMJS_BIN=None,
                 PHANTOMJS_GENERATE_PDF=GENERATE_PDF_JS,
                 keep_pdf_files=False,
                 ):
        """Arguments:
            PHANTOMJS_COOKIE_DIR = Directory where the temp cookies will be saved.
            PHANTOMJS_PDF_DIR = Directory where you want to the PDF to be saved temporarily.
            PHANTOMJS_BIN = Path to PhantomsJS binary.
            PHANTOMJS_GENERATE_PDF = Path to generate_pdf.js file.
            keep_pdf_files = Option to not delete the PDF file after rendering it.
        """
        self.keep_pdf_files = keep_pdf_files
        self.PHANTOMJS_COOKIE_DIR = PHANTOMJS_COOKIE_DIR
        self.PHANTOMJS_PDF_DIR = PHANTOMJS_PDF_DIR
        self.PHANTOMJS_BIN = PHANTOMJS_BIN
        self.PHANTOMJS_GENERATE_PDF = PHANTOMJS_GENERATE_PDF
        for attr in [
                'PHANTOMJS_COOKIE_DIR',
                'PHANTOMJS_PDF_DIR',
                'PHANTOMJS_BIN',
                'PHANTOMJS_GENERATE_PDF']:
            if not getattr(self, attr, None):
                value = getattr(settings, attr, None)
                if not value:
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

    def _set_source_file_name(self):
        """Return the original source filename of the pdf."""
        return ''.join((
            os.path.join(
                self.PHANTOMJS_PDF_DIR, str(uuid.uuid1())
            ), '.pdf'
        ))

    def _return_response(self, file_src, basename):
        """Read the generated pdf and return it in a django HttpResponse."""
        try:
            # Open the file created by PhantomJS
            return_file = open(file_src, 'r')
        except IOError:
            exc_msg = "The PDF was not created. Enable debug at RequestToPDF instance."
            raise Exception(exc_msg)

        response = HttpResponse(
            return_file,
            mimetype='application/force-download'
        )
        content_disposition = 'attachment; filename=%s.pdf' % (basename)
        response['Content-Disposition'] = content_disposition

        if not self.keep_pdf_files:  # remove generated pdf files
            os.remove(file_src)

        return response

    def request_to_pdf(self, request, basename):
        """Receive request, basename and return a PDF in an HttpResponse."""

        file_src = self._set_source_file_name()
        cookie_file = self._save_cookie_data(request)
        url = self._build_url(request)

        domain = urlparse.urlsplit(
            request.build_absolute_uri()
        ).netloc.split(':')[0]
        Popen([
            self.PHANTOMJS_BIN,
            self.PHANTOMJS_GENERATE_PDF,
            url,
            file_src,
            cookie_file,
            domain], stdout=PIPE, stderr=STDOUT)

        # Once the pdf is created, remove the cookie file.
        os.remove(cookie_file)
        return self._return_response(file_src, basename)


def render_to_pdf(request, basename):
    """Helper function for rendering a request to pdf.
    Arguments:
        request = django request.
        basename = string to use for your pdf's filename.
    """
    request2pdf = RequestToPDF()
    response = request2pdf.request_to_pdf(request, basename)
    return response

