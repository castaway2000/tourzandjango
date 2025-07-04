/**
 * jquery.slimmenu.js
 * http://adnantopal.github.io/slimmenu/
 * Author: @adnantopal
 * Copyright 2013, Adnan Topal (atopal.com)
 * Licensed under the MIT license.
 */
;(function ( $, window, document, undefined )
{
    var pluginName = "slimmenu",
        defaults =
        {
            resizeWidth: '768',
            collapserTitle: 'Main Menu',
            animSpeed: 'medium',
            easingEffect: null,
            indentChildren: false,
            childrenIndenter: '&nbsp;&nbsp;',
            logo: '<div class="navbar-header">'+
                        '<div class="navbar-brand no-padding">'+
                            '<a class="navbar-brand navbar-logo" href="/">'+
                                '<span>'+
                                    '<img src="/static/img/tourzan_logo_white.jpg" class="navbar-logo"'+
                                     'alt="Tourzan logo" title="Tourzan logo" />'+
                                '</span>'+
                            '</a>'+
                            '<div class="pull-left navbar-logo-text">'+
                                '<a href="/">Tourzan</a>'+
                            '</div>'+
                        '</div>'+
                    '</div>'
        };

    function Plugin( element, options )
    {
        this.element = element;
        this.$elem = $(this.element);
        this.options = $.extend( {}, defaults, options );
        this.init();
    }

    Plugin.prototype = {

        init: function()
        {
            var $options = this.options,
                $menu = this.$elem,
                $collapser = '<div class="slimmenu-menu-collapser">' +
                    ''+$options.logo+'' +
                    '<div class="slimmenu-collapse-button"><span class="slimmenu-icon-bar">' +
                    '</span><span class="slimmenu-icon-bar"></span>' +
                    '<span class="slimmenu-icon-bar"></span>' +
                    '</div></div>',
                $menu_collapser;

            $menu.before($collapser);
            $menu_collapser = $menu.prev('.slimmenu-menu-collapser');

            $menu.on('click', '.slimmenu-sub-collapser', function(e)
            {
                e.preventDefault();
                e.stopPropagation();

                var $parent_li = $(this).closest('li');

                if ($(this).hasClass('expanded'))
                {
                    $(this).removeClass('expanded');
                    $(this).find('i').addClass('fa fa-angle-down');
                    $parent_li.find('>ul').slideUp($options.animSpeed, $options.easingEffect);
                }
                else
                {
                    $(this).addClass('expanded');
                    $(this).find('i').removeClass('fa-angle-down').addClass('fa fa-angle-up');
                    $parent_li.find('>ul').slideDown($options.animSpeed, $options.easingEffect);
                }
            });

            $menu_collapser.on('click', '.slimmenu-collapse-button', function(e)
            {
                e.preventDefault();
                $menu.slideToggle($options.animSpeed, $options.easingEffect);
            });

            this.resizeMenu({ data: { el: this.element, options: this.options } });
            $(window).on('resize', { el: this.element, options: this.options }, this.resizeMenu);
        },

        resizeMenu: function(event)
        {
            var $window = $(window),
                $options = event.data.options,
                $menu = $(event.data.el),
                $menu_collapser = $('body').find('.slimmenu-menu-collapser');

            $menu.find('li').each(function()
            {
                if ($(this).has('ul').length)
                {
                    $(this).addClass('slimmenu-sub-menu');
                    if ($(this).has('.slimmenu-sub-collapser').length)
                    {
                        $(this).children('.slimmenu-sub-collapser i').addClass('fa fa-angle-down');
                    }
                    else
                    {
                        $(this).append('<span class="slimmenu-sub-collapser"><i class="fa fa-angle-down"></i></span>');
                    }
                }

                $(this).children('ul').hide();
                $(this).find('.slimmenu-sub-collapser').removeClass('expanded').children('i').addClass('fa fa-angle-down');
            });

            if ($options.resizeWidth >= $window.width() || $('body').hasClass('touch'))
            {
                if ($options.indentChildren)
                {
                    $menu.find('ul').each(function()
                    {
                        var $depth = $(this).parents('ul').length;
                        if (!$(this).children('li').children('a').has('i').length)
                        {
                            $(this).children('li').children('a').prepend(Plugin.prototype.indent($depth, $options));
                        }
                    });
                }

                $menu.find('li').has('ul').off('mouseenter mouseleave');
                $menu.addClass('slimmenu-collapsed').hide();
                $menu_collapser.show();
            }
            else
            {
                $menu.find('li').has('ul').on('mouseenter', function()
                {
                    $(this).find('>ul').stop().slideDown($options.animSpeed, $options.easingEffect);
                })
                .on('mouseleave', function()
                {
                    $(this).find('>ul').stop().slideUp($options.animSpeed, $options.easingEffect);
                });

                $menu.find('li > a > i').remove();
                $menu.removeClass('slimmenu-collapsed').show();
                $menu_collapser.hide();
            }
        },

        indent: function(num, options)
        {
            var $indent = '';
            for (var i=0; i < num; i++)
            {
                $indent += options.childrenIndenter;
            }
            return '<i>'+$indent+'</i>';
        }
    };

    $.fn[pluginName] = function ( options )
    {
        return this.each(function ()
        {
            if (!$.data(this, "plugin_" + pluginName))
            {
                $.data(this, "plugin_" + pluginName,
                new Plugin( this, options ));
            }
        });
    };

})( jQuery, window, document );