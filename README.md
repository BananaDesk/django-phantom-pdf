Django Phantom PDF
==================

A simple django app that takes the pain out of rendering PDFs from django views.

Quick start
-----------

1. Install node and phantomjs:

### On Mac OSX:

    brew install node npm
    npm install -g phantomjs

### On Ubuntu:

    apt-get install node npm
    sudo npm install -g phantomjs


2. Install django-phantom-pdf:

		pip install django-phantom-pdf

3. That's it, you can now start using it in your django views like so and rendering PDFs!

	    from phantom_pdf import render_to_pdf
    	from django.http import HttpResponse

	    def home(request):
    	    # If 'print=pdf' in GET params, then render the PDF!
        	if request.GET.get("print", None) == "pdf":
            	basename = 'output'  # `.pdf` will be appended to this string.
	            return render_to_pdf(request, basename)
                # If you want to change default format and orientation for this view
                # return render_to_pdf(request, basename, format='A3', orientation='portrait')
    	    else:
        	    return HttpResponse("Hello World!")

Advanced Use
------------

For more advanced use and control, you can set the following variables in your setting.
They are already set to sane defaults, so it's not necessary unless you are looking for
more fine grained control.

    PHANTOMJS_COOKIE_DIR = Directory where the temp cookies will be saved.
    PHANTOMJS_PDF_DIR = Directory where you want to the PDF to be saved temporarily.
    PHANTOMJS_BIN = Path to PhantomsJS binary.
    PHANTOMJS_GENERATE_PDF = Path to generate_pdf.js file.
    keep_pdf_files = Option to not delete the PDF file after rendering it.
    PHANTOMJS_FORMAT = Page size to use
    PHANTOMJS_ORIENTATION = How the page will be positioned when printing.
