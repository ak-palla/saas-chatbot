# Chatbot SaaS Widget

A production-ready, embeddable chatbot widget for the Chatbot SaaS Platform. This widget can be easily integrated into any website to provide AI-powered chat functionality with voice support.

## Features

- **🤖 AI Chat**: Text-based conversations with your custom chatbot
- **🎤 Voice Support**: Speech-to-text and text-to-speech capabilities
- **📱 Responsive Design**: Works on desktop, tablet, and mobile
- **🎨 Customizable**: Full theming and styling support
- **⚡ Real-time**: WebSocket-based real-time messaging
- **🔒 Secure**: Secure authentication and data handling
- **📦 Lightweight**: Optimized for fast loading

## Quick Start

### Method 1: Embed Script (Recommended)

Add this script to your website's `<head>` section:

```html
<script src="https://cdn.jsdelivr.net/npm/@chatbot-saas/widget@latest/dist/embed.js"
        data-chatbot-id="your-chatbot-id"
        data-base-url="https://api.yourchatbot.com"
        data-primary-color="#3b82f6"
        data-bot-name="Your Assistant"
        data-enable-voice="true"></script>
```

### Method 2: Manual Initialization

```html
<!-- Add the widget script -->
<script src="https://cdn.jsdelivr.net/npm/@chatbot-saas/widget@latest/dist/widget.umd.js"></script>

<!-- Initialize the widget -->
<script>
  ChatbotSaaS.init({
    chatbotId: 'your-chatbot-id',
    baseUrl: 'https://api.yourchatbot.com',
    theme: 'light',
    position: 'bottom-right',
    primaryColor: '#3b82f6',
    botName: 'Your Assistant',
    enableVoice: true
  });
</script>
```

### Method 3: NPM Installation

```bash
npm install @chatbot-saas/widget
```

```javascript
import ChatbotWidget from '@chatbot-saas/widget';

const widget = new ChatbotWidget({
  chatbotId: 'your-chatbot-id',
  baseUrl: 'https://api.yourchatbot.com',
  theme: 'light',
  // ... other options
});
```

## Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `chatbotId` | string | - | **Required** - Your chatbot's unique ID |
| `baseUrl` | string | `https://api.yourchatbot.com` | API base URL |
| `theme` | string | `light` | Theme: `light`, `dark`, `auto` |
| `position` | string | `bottom-right` | Widget position: `bottom-right`, `bottom-left`, `top-right`, `top-left` |
| `primaryColor` | string | `#3b82f6` | Primary brand color |
| `greeting` | string | `Hello! How can I help you today?` | Welcome message |
| `botName` | string | `Assistant` | Chatbot name |
| `showAvatar` | boolean | `true` | Show avatars in chat |
| `enableVoice` | boolean | `false` | Enable voice features |
| `maxWidth` | number | `400` | Maximum widget width (px) |
| `maxHeight` | number | `600` | Maximum widget height (px) |
| `zIndex` | number | `999999` | CSS z-index |
| `autoOpen` | boolean | `false` | Auto-open widget on load |

## API Methods

### Global Methods

```javascript
// Initialize widget
ChatbotSaaS.init(config);

// Control widget
ChatbotSaaS.open();
ChatbotSaaS.close();
ChatbotSaaS.toggle();

// Send messages programmatically
ChatbotSaaS.sendMessage('Hello, bot!');
ChatbotSaaS.addMessage('Custom message', 'user');

// Destroy widget
ChatbotSaaS.destroy();
```

### Data Attributes (HTML)

You can configure the widget using HTML data attributes:

```html
<script src="...embed.js"
        data-chatbot-id="your-chatbot-id"
        data-primary-color="#ff6b6b"
        data-position="bottom-left"
        data-enable-voice="true"
        data-auto-open="true"></script>
```

## Styling

The widget uses CSS custom properties for easy customization:

```css
:root {
  --chatbot-primary-color: #3b82f6;
  --chatbot-background: #ffffff;
  --chatbot-text-color: #1f2937;
  --chatbot-border-radius: 12px;
  --chatbot-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
}
```

## Browser Support

- Chrome 80+
- Firefox 75+
- Safari 13+
- Edge 80+
- Mobile browsers (iOS Safari, Chrome Mobile)

## Security

- HTTPS only (production)
- CORS configured
- Input sanitization
- XSS protection
- Rate limiting

## Development

### Build from source

```bash
cd frontend/saas-chatbot/src/widget
npm install
npm run build
```

### Local development

```bash
npm run dev
```

## Troubleshooting

### Common Issues

1. **Widget not appearing**: Check console for errors, verify chatbotId
2. **CORS errors**: Ensure baseUrl is correct and CORS is configured
3. **Voice not working**: Check browser permissions for microphone access
4. **Styling issues**: Verify CSS is not being overridden by site styles

### Debug Mode

Enable debug logging by adding `data-debug="true"` to the script tag.

## Examples

### Basic Usage

```html
<!DOCTYPE html>
<html>
<head>
    <title>My Website</title>
</head>
<body>
    <!-- Your content -->
    
    <!-- Chatbot Widget -->
    <script src="https://cdn.jsdelivr.net/npm/@chatbot-saas/widget@latest/dist/embed.js"
            data-chatbot-id="your-chatbot-id"
            data-base-url="https://api.yourchatbot.com"></script>
</body>
</html>
```

### Advanced Configuration

```html
<script>
  ChatbotSaaS.init({
    chatbotId: 'your-chatbot-id',
    baseUrl: 'https://api.yourchatbot.com',
    theme: 'dark',
    position: 'bottom-left',
    primaryColor: '#8b5cf6',
    botName: 'Support Assistant',
    greeting: 'Hi! I\'m here to help with any questions.',
    enableVoice: true,
    autoOpen: true,
    maxWidth: 500,
    maxHeight: 700
  });
</script>
```

## License

MIT License - See LICENSE file for details.