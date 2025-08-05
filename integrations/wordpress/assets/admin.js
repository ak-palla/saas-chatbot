jQuery(document).ready(function($) {
    // Initialize color picker
    $('.color-picker').wpColorPicker();
    
    // Test connection functionality
    $('#test-connection').on('click', function() {
        var $button = $(this);
        var originalText = $button.text();
        
        // Get form values
        var chatbotId = $('#chatbot_id').val();
        var apiUrl = $('#api_url').val();
        
        if (!chatbotId || !apiUrl) {
            alert('Please enter both Chatbot ID and API URL before testing.');
            return;
        }
        
        // Show loading state
        $button.text('Testing...').prop('disabled', true);
        
        // Make AJAX request
        $.ajax({
            url: chatbot_ajax.ajax_url,
            type: 'POST',
            data: {
                action: 'chatbot_test_connection',
                chatbot_id: chatbotId,
                api_url: apiUrl,
                nonce: chatbot_ajax.nonce
            },
            success: function(response) {
                if (response.success) {
                    alert('✅ ' + response.data);
                } else {
                    alert('❌ ' + response.data);
                }
            },
            error: function() {
                alert('❌ Connection test failed. Please try again.');
            },
            complete: function() {
                $button.text(originalText).prop('disabled', false);
            }
        });
    });
    
    // Form validation
    $('form').on('submit', function() {
        var chatbotId = $('#chatbot_id').val();
        var apiUrl = $('#api_url').val();
        
        if (!chatbotId) {
            alert('Please enter a Chatbot ID.');
            $('#chatbot_id').focus();
            return false;
        }
        
        if (!apiUrl) {
            alert('Please enter an API URL.');
            $('#api_url').focus();
            return false;
        }
        
        // Validate URL format
        var urlPattern = /^https?:\/\/.+/;
        if (!urlPattern.test(apiUrl)) {
            alert('Please enter a valid API URL (must start with http:// or https://).');
            $('#api_url').focus();
            return false;
        }
        
        return true;
    });
    
    // Real-time preview updates
    function updatePreview() {
        var theme = $('#theme').val();
        var position = $('#position').val();
        var color = $('#primary_color').val();
        
        // Update preview if it exists
        var $preview = $('.chatbot-preview');
        if ($preview.length) {
            $preview.removeClass('theme-light theme-dark theme-auto')
                   .addClass('theme-' + theme);
            
            $preview.removeClass('pos-bottom-right pos-bottom-left pos-top-right pos-top-left')
                   .addClass('pos-' + position);
            
            $preview.find('.preview-bubble').css('background-color', color);
        }
    }
    
    // Bind preview updates
    $('#theme, #position').on('change', updatePreview);
    $('#primary_color').on('change', updatePreview);
    
    // Initialize preview
    updatePreview();
    
    // Help tooltips
    $('.help-tooltip').on('mouseenter', function() {
        var tooltip = $(this).data('tooltip');
        if (tooltip) {
            $(this).attr('title', tooltip);
        }
    });
    
    // Advanced settings toggle
    $('.advanced-toggle').on('click', function() {
        var $target = $($(this).data('target'));
        $target.slideToggle();
        $(this).find('.dashicons').toggleClass('dashicons-arrow-down dashicons-arrow-up');
    });
    
    // Copy shortcode functionality
    $('.copy-shortcode').on('click', function() {
        var shortcode = $(this).data('shortcode');
        
        // Create temporary input
        var $temp = $('<input>');
        $('body').append($temp);
        $temp.val(shortcode).select();
        document.execCommand('copy');
        $temp.remove();
        
        // Show feedback
        var $button = $(this);
        var originalText = $button.text();
        $button.text('Copied!');
        setTimeout(function() {
            $button.text(originalText);
        }, 2000);
    });
    
    // Widget preview functionality
    function initWidgetPreview() {
        var $preview = $('.widget-preview-container');
        if (!$preview.length) return;
        
        var config = {
            chatbotId: $('#chatbot_id').val(),
            baseUrl: $('#api_url').val(),
            theme: $('#theme').val(),
            position: $('#position').val(),
            primaryColor: $('#primary_color').val(),
            enableVoice: $('#enable_voice').is(':checked'),
            autoOpen: $('#auto_open').is(':checked')
        };
        
        // Update preview with current settings
        $preview.html(generatePreviewHTML(config));
    }
    
    function generatePreviewHTML(config) {
        var bubbleStyle = 'background-color: ' + config.primaryColor + ';';
        var positionClass = 'preview-' + config.position;
        var themeClass = 'preview-theme-' + config.theme;
        
        return '<div class="widget-preview ' + positionClass + ' ' + themeClass + '">' +
               '<div class="preview-bubble" style="' + bubbleStyle + '">' +
               '<span class="preview-icon">💬</span>' +
               '</div>' +
               '<div class="preview-window">' +
               '<div class="preview-header" style="' + bubbleStyle + '">' +
               '<span>Chat with us</span>' +
               '<span class="preview-close">×</span>' +
               '</div>' +
               '<div class="preview-messages">' +
               '<div class="preview-message bot">' +
               '<div class="preview-avatar">🤖</div>' +
               '<div class="preview-text">Hello! How can I help you today?</div>' +
               '</div>' +
               '</div>' +
               '<div class="preview-input">' +
               '<input type="text" placeholder="Type your message..." disabled>' +
               (config.enableVoice ? '<button class="preview-voice">🎤</button>' : '') +
               '</div>' +
               '</div>' +
               '</div>';
    }
    
    // Update preview when settings change
    $('#chatbot_id, #api_url, #theme, #position, #primary_color, #enable_voice, #auto_open').on('change input', function() {
        setTimeout(initWidgetPreview, 100);
    });
    
    // Initialize preview on load
    initWidgetPreview();
    
    // Tab functionality for settings
    $('.nav-tab').on('click', function(e) {
        e.preventDefault();
        
        var $tab = $(this);
        var target = $tab.attr('href');
        
        // Update active tab
        $('.nav-tab').removeClass('nav-tab-active');
        $tab.addClass('nav-tab-active');
        
        // Show target content
        $('.tab-content').hide();
        $(target).show();
    });
    
    // Initialize first tab
    $('.nav-tab:first').click();
    
    // Settings import/export
    $('#export-settings').on('click', function() {
        var settings = {
            chatbot_id: $('#chatbot_id').val(),
            api_url: $('#api_url').val(),
            theme: $('#theme').val(),
            position: $('#position').val(),
            primary_color: $('#primary_color').val(),
            enable_voice: $('#enable_voice').is(':checked'),
            auto_open: $('#auto_open').is(':checked')
        };
        
        var dataStr = JSON.stringify(settings, null, 2);
        var dataBlob = new Blob([dataStr], {type: 'application/json'});
        
        var link = document.createElement('a');
        link.href = URL.createObjectURL(dataBlob);
        link.download = 'chatbot-settings.json';
        link.click();
    });
    
    $('#import-settings').on('change', function(e) {
        var file = e.target.files[0];
        if (!file) return;
        
        var reader = new FileReader();
        reader.onload = function(e) {
            try {
                var settings = JSON.parse(e.target.result);
                
                // Apply settings
                $('#chatbot_id').val(settings.chatbot_id || '');
                $('#api_url').val(settings.api_url || '');
                $('#theme').val(settings.theme || 'light');
                $('#position').val(settings.position || 'bottom-right');
                $('#primary_color').val(settings.primary_color || '#3b82f6').trigger('change');
                $('#enable_voice').prop('checked', settings.enable_voice || false);
                $('#auto_open').prop('checked', settings.auto_open || false);
                
                alert('Settings imported successfully!');
                initWidgetPreview();
                
            } catch (error) {
                alert('Error importing settings: Invalid file format.');
            }
        };
        reader.readAsText(file);
    });
    
    // Performance optimization: Debounce preview updates
    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
    
    const debouncedPreviewUpdate = debounce(initWidgetPreview, 300);
    
    // Replace immediate preview updates with debounced version
    $('#chatbot_id, #api_url, #theme, #position, #primary_color, #enable_voice, #auto_open').off('change input').on('change input', debouncedPreviewUpdate);
});
