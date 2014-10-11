What
=====

jQuery plugin to transform unobtrusively a checkbox in a Toggle switch button "à la iOS". The checkbox is simply hidden (absolutized and moved far to the left) and updated by the button, so submitting the form will have exactly the same effect as if you had not applied the plugin on your checkboxes. **Accessibility** is then also maintained because you act on the original checkbox, which means you can use the spacebar to toggle.

Demo
=====

[http://jsfiddle.net/seboulba/PC4aN/9/](http://jsfiddle.net/seboulba/PC4aN/9/)

Why
===

* ability to use the text I want in the button. So you can have whatever text you want for each side. **The width of the wider text will be applied on both sides**.
* text can be set in the html markup, not in JS

Usage
======
In your html:

    <input name="foo" type="checkbox" class="iToggle" data-label-on="yes" data-label-off="no"/>

Put whatever you want for both labels.

In your JS (when page ready):

    $('input[type=checkbox]').iToggle({speed: 100});


These are the options with their default values:

    // speed of animation
    speed: 70

    // labels when no label attribute given
    defaultOnLabel: 'yes'
    defaultOffLabel: 'no'

You can also define <strong>application-wide</strong> options like this:

    $.fn.iToggle.defaultOptions = {
        defaultOffLabel: 'man',
        defaultOnLabel: 'woman'
    };

You will also need the CSS. You can use the provided stylesheet or modify it to suit your needs.

Requirements
=============

  * jQuery v1.7+

Compatibility
==============

Tested on:

  * Chrome v20
  * Firefox v12
  * IE7-8
