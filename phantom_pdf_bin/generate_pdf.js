var page, system, fs, info, csrftoken, sessionid, categories,
    notification, data, address, output;

// Create a page object
page = require('webpage').create();

// Require the system module so I can read the command line arguments
system = require('system');

// Require the FileSystem module, so I can read the cookie file
fs = require('fs');

// Read the url and output file location from the command line argument
// Read the cookie file and split it by spaces
// Because the way I constructed this file, separate each field using spaces
address = system.args[1];
output = system.args[2];
cookie_file = system.args[3];
domain = system.args[4];
format = system.args[5]
orientation = system.args[6];

info = fs.read(cookie_file).split(' ');
csrftoken = info[0];
sessionid = info[1];

// Now we can add cookies into phantomjs, so when it renders the page, it
// will have the same permission and data as the current user
phantom.addCookie({'domain':domain, 'name':'csrftoken',
                   'value': csrftoken});
phantom.addCookie({'domain':domain, 'name':'sessionid',
                   'value': sessionid});


// Set the page size and orientation
page.paperSize = {
    format: format,
    orientation: orientation};

// Now we have everything settled, let's render the page
page.open(address, function (status) {
    if (status !== 'success') {
        // If PhantomJS failed to reach the address, print a message
        console.log('Unable to load the address!');
        phantom.exit();
    } else {
        // If we are here, it means we rendered page successfully
        // Use "evaluate" method of page object to manipulate the web page
        // Notice I am passing the data into the function, so I can use
        // them on the page
        page.evaluate(function(data) {
        }, data);

        // Now create the output file and exit PhantomJS
        page.render(output);
        phantom.exit();
    }
});
