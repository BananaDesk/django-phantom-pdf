# -*- coding: utf-8 -*-

import os
import uuid
import urlparse
from subprocess import Popen, STDOUT, PIPE
from django.conf import settings
from django.http import HttpResponse


class RequestToPDF(object):
    """ Receive a request and return the PDF of the request.path """

    def __init__(self,
                 PHANTOMJS_COOKIE_DIR=None,
                 PHANTOMJS_PDF_DIR=None,
                 PHANTOMJS_BIN=None,
                 PHANTOMJS_GENERATE_PDF=None,
                 keep_pdf_files=False):
        self.keep_pdf_files = keep_pdf_files
        self.PHANTOMJS_COOKIE_DIR = PHANTOMJS_COOKIE_DIR
        self.PHANTOMJS_PDF_DIR = PHANTOMJS_PDF_DIR
        self.PHANTOMJS_BIN = PHANTOMJS_BIN
        self.PHANTOMJS_GENERATE_PDF = PHANTOMJS_GENERATE_PDF
        for phantomjs_attr_config in [
                'PHANTOMJS_COOKIE_DIR',
                'PHANTOMJS_PDF_DIR',
                'PHANTOMJS_BIN',
                'PHANTOMJS_GENERATE_PDF']:
            if not getattr(self, phantomjs_attr_config, None):
                value = getattr(settings, phantomjs_attr_config, None)
                if not value:
                    exc_msg = ''.join((
                        '{attr} is needed to be configured at settings.py or ',
                        'at RequestToPDF instance.'))
                    exc_msg = exc_msg.format(attr=phantomjs_attr_config)
                    raise Exception(exc_msg)
                setattr(self, phantomjs_attr_config, value)

    def _build_url(self, request):
        """ Build the url with protocol, domain and path """
        scheme, netloc, path, query, fragment = urlparse.urlsplit(
            request.build_absolute_uri())
        protocol = scheme
        domain = netloc
        return '{protocol}://{domain}{path}'.format(
            protocol=protocol,
            domain=domain,
            path=path)

    def _save_cookie_data(self, request):
        """ Save csrftoken and sessionid in file for authentication """
        cookie_file = '%s%s.cookie.txt' % (
            settings.PHANTOMJS_COOKIE_DIR, uuid.uuid1())
        with open(cookie_file, 'w+') as fh:
            cookie = ''.join((
                request.COOKIES.get('csrftoken', 'nocsrftoken'),
                ' ',
                request.COOKIES.get('sessionid', 'nosessionid')
            ))
            fh.write(cookie)
        return cookie_file

    def _set_source_file_name(self):
        """ Return the original source file of the pdf """
        return '%s%s.pdf' % (settings.PHANTOMJS_PDF_DIR, uuid.uuid1())

    def _return_response(self, file_src, basename):
        """ Read the generated pdf and return it with a response """
        try:
            # Open the file created by PhantomJS
            return_file = open(file_src, 'r')
        except IOError:
            exc_msg = "The PDF was not created. Check Site object's domain."
            raise Exception(exc_msg)
        response = HttpResponse(return_file,
                                mimetype='application/force-download'
                                )
        content_disposition = 'attachment; filename=%s.pdf' % (basename)
        response['Content-Disposition'] = content_disposition

        if not self.keep_pdf_files:  # remove generated pdf files
            os.remove(file_src)

        return response

    def request_to_pdf(self, request, basename):
        """ Receive request, basename and return a PDF in a HttpResponse """

        file_src = self._set_source_file_name()
        cookie_file = self._save_cookie_data(request)
        url = self._build_url(request)

        # Call phantomjs to generate the pdf
        # PhantomJS inject the domain in the cookie. If you are running Django
        # in localhost:8000
        # PhantomJS need to setup the domain like "localhost" without the port.
        domain = urlparse.urlsplit(
            request.build_absolute_uri()
        ).netloc.split(':')[0]
        pipe = Popen([
            settings.PHANTOMJS_BIN,
            settings.PHANTOMJS_GENERATE_PDF,
            url,
            file_src,
            cookie_file,
            domain], stdout=PIPE, stderr=STDOUT)
        output = pipe.stdout.read()

        # TODO: Remove this prints
        print '=' * 70
        print 'Converting pdf at %s...' % file_src
        print output
        print '=' * 70

        # Once the pdf is created, remove the cookie file
        os.remove(cookie_file)
        return self._return_response(file_src, basename)


def render_to_pdf(request, basename):
    request2pdf = RequestToPDF()
    response = request2pdf.request_to_pdf(request, basename)
    return response