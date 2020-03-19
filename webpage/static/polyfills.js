(function() {
    'use strict';

    // URLSearchParameters
    window.URLSearchParameters = function(querystring) {
        return (querystring || location.search).split('?').pop().split('&').reduce(function(acc, keyval) {
            var parts = keyval.split('=');
            var key = decodeURIComponent(parts[0]);
            var val = parts[1] ? decodeURIComponent(parts[1]) : true;
            acc[key] = val;
            return acc;
        }, {});
    };

    // Go to a certain URL, trigger reload if necessary
    window.goto = function(href) {
        window.open(href, '_top');
        if (window.location.pathname === href.split('#')[0]) {
            window.location.reload();
        }
    };

})();