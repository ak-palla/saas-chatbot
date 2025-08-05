import { join } from "path";
import { readFileSync } from "fs";
import express from "express";
import serveStatic from "serve-static";
import shopify from "./shopify.js";
import productCreator from "./product-creator.js";
import PrivacyWebhookHandlers from "./privacy.js";

const PORT = parseInt(process.env.BACKEND_PORT || process.env.PORT, 10) || 3000;

const STATIC_PATH =
  process.env.NODE_ENV === "production"
    ? `${process.cwd()}/frontend/dist`
    : `${process.cwd()}/frontend/`;

const app = express();

// Set up Shopify authentication and webhook handling
app.get(shopify.config.auth.path, shopify.auth.begin());
app.get(
  shopify.config.auth.callbackPath,
  shopify.auth.callback(),
  shopify.redirectToShopifyOrAppRoot()
);
app.post(
  shopify.config.webhooks.path,
  shopify.processWebhooks({ webhookHandlers: PrivacyWebhookHandlers })
);

// If you are adding routes outside of the /api path, remember to
// also add a proxy rule for them in web/frontend/vite.config.js

app.use("/api/*", shopify.validateAuthenticatedSession());

app.use(express.json());

// Chatbot SaaS API endpoints
app.get("/api/chatbot/config", async (_req, res) => {
  try {
    const session = res.locals.shopify.session;
    
    // Get chatbot configuration for this shop
    const config = await getChatbotConfig(session.shop);
    
    res.status(200).json({
      success: true,
      config: config || {
        enabled: false,
        chatbotId: '',
        apiUrl: 'https://api.yourchatbot.com',
        theme: 'light',
        position: 'bottom-right',
        primaryColor: '#3b82f6',
        enableVoice: false,
        enableProductRecommendations: true,
        enableOrderTracking: true,
        showOnProductPages: true,
        showOnCartPage: true,
        showOnCheckoutPage: false
      }
    });
  } catch (error) {
    console.error('Error getting chatbot config:', error);
    res.status(500).json({ success: false, error: error.message });
  }
});

app.post("/api/chatbot/config", async (req, res) => {
  try {
    const session = res.locals.shopify.session;
    const config = req.body;
    
    // Validate required fields
    if (!config.chatbotId) {
      return res.status(400).json({ 
        success: false, 
        error: 'Chatbot ID is required' 
      });
    }
    
    // Save configuration
    await saveChatbotConfig(session.shop, config);
    
    // Install/update script tag if enabled
    if (config.enabled) {
      await installScriptTag(session, config);
    } else {
      await removeScriptTag(session);
    }
    
    res.status(200).json({ success: true });
  } catch (error) {
    console.error('Error saving chatbot config:', error);
    res.status(500).json({ success: false, error: error.message });
  }
});

app.post("/api/chatbot/test", async (req, res) => {
  try {
    const { chatbotId, apiUrl } = req.body;
    
    if (!chatbotId || !apiUrl) {
      return res.status(400).json({ 
        success: false, 
        error: 'Chatbot ID and API URL are required' 
      });
    }
    
    // Test connection to chatbot API
    const testUrl = `${apiUrl}/api/v1/widgets/public/${chatbotId}/config`;
    const response = await fetch(testUrl, { 
      method: 'GET',
      timeout: 10000 
    });
    
    if (response.ok) {
      res.status(200).json({ 
        success: true, 
        message: 'Connection successful' 
      });
    } else {
      res.status(400).json({ 
        success: false, 
        error: `Connection failed with status ${response.status}` 
      });
    }
  } catch (error) {
    console.error('Error testing chatbot connection:', error);
    res.status(500).json({ 
      success: false, 
      error: 'Connection test failed: ' + error.message 
    });
  }
});

app.get("/api/chatbot/analytics", async (req, res) => {
  try {
    const session = res.locals.shopify.session;
    const config = await getChatbotConfig(session.shop);
    
    if (!config || !config.chatbotId) {
      return res.status(400).json({ 
        success: false, 
        error: 'Chatbot not configured' 
      });
    }
    
    // Get analytics from chatbot API
    const analyticsUrl = `${config.apiUrl}/api/v1/widget-analytics/${config.chatbotId}/analytics/summary`;
    const response = await fetch(analyticsUrl, {
      headers: {
        'X-Shop-Domain': session.shop
      }
    });
    
    if (response.ok) {
      const analytics = await response.json();
      res.status(200).json({ success: true, analytics });
    } else {
      res.status(400).json({ 
        success: false, 
        error: 'Failed to fetch analytics' 
      });
    }
  } catch (error) {
    console.error('Error getting chatbot analytics:', error);
    res.status(500).json({ success: false, error: error.message });
  }
});

// Product recommendations endpoint
app.get("/api/products/recommendations", async (req, res) => {
  try {
    const session = res.locals.shopify.session;
    const { query, limit = 5 } = req.query;
    
    const client = new shopify.api.clients.Graphql({ session });
    
    const productsQuery = `
      query getProducts($first: Int!, $query: String) {
        products(first: $first, query: $query) {
          edges {
            node {
              id
              title
              handle
              description
              images(first: 1) {
                edges {
                  node {
                    url
                    altText
                  }
                }
              }
              priceRange {
                minVariantPrice {
                  amount
                  currencyCode
                }
              }
              variants(first: 1) {
                edges {
                  node {
                    id
                    availableForSale
                  }
                }
              }
            }
          }
        }
      }
    `;
    
    const response = await client.query({
      data: {
        query: productsQuery,
        variables: {
          first: parseInt(limit),
          query: query || null
        }
      }
    });
    
    const products = response.body.data.products.edges.map(edge => ({
      id: edge.node.id,
      title: edge.node.title,
      handle: edge.node.handle,
      description: edge.node.description,
      image: edge.node.images.edges[0]?.node.url,
      price: edge.node.priceRange.minVariantPrice.amount,
      currency: edge.node.priceRange.minVariantPrice.currencyCode,
      available: edge.node.variants.edges[0]?.node.availableForSale,
      url: `https://${session.shop}/products/${edge.node.handle}`
    }));
    
    res.status(200).json({ success: true, products });
  } catch (error) {
    console.error('Error getting product recommendations:', error);
    res.status(500).json({ success: false, error: error.message });
  }
});

// Order tracking endpoint
app.get("/api/orders/:orderNumber", async (req, res) => {
  try {
    const session = res.locals.shopify.session;
    const { orderNumber } = req.params;
    
    const client = new shopify.api.clients.Graphql({ session });
    
    const orderQuery = `
      query getOrder($query: String!) {
        orders(first: 1, query: $query) {
          edges {
            node {
              id
              name
              processedAt
              fulfillmentStatus
              financialStatus
              totalPrice {
                amount
                currencyCode
              }
              shippingAddress {
                city
                province
                country
              }
              fulfillments {
                trackingInfo {
                  number
                  url
                }
                status
              }
            }
          }
        }
      }
    `;
    
    const response = await client.query({
      data: {
        query: orderQuery,
        variables: {
          query: `name:${orderNumber}`
        }
      }
    });
    
    const orders = response.body.data.orders.edges;
    if (orders.length === 0) {
      return res.status(404).json({ 
        success: false, 
        error: 'Order not found' 
      });
    }
    
    const order = orders[0].node;
    res.status(200).json({ 
      success: true, 
      order: {
        id: order.id,
        number: order.name,
        status: order.fulfillmentStatus,
        financialStatus: order.financialStatus,
        total: order.totalPrice.amount,
        currency: order.totalPrice.currencyCode,
        processedAt: order.processedAt,
        tracking: order.fulfillments.map(f => ({
          number: f.trackingInfo?.number,
          url: f.trackingInfo?.url,
          status: f.status
        }))
      }
    });
  } catch (error) {
    console.error('Error getting order:', error);
    res.status(500).json({ success: false, error: error.message });
  }
});

app.use(productCreator);

app.use(shopify.cspHeaders());
app.use(serveStatic(STATIC_PATH, { index: false }));

app.use("/*", shopify.ensureInstalledOnShop(), async (_req, res, _next) => {
  return res
    .status(200)
    .set("Content-Type", "text/html")
    .send(readFileSync(join(STATIC_PATH, "index.html")));
});

// Helper functions
async function getChatbotConfig(shop) {
  // In a real app, this would query your database
  // For now, return mock data or implement your storage logic
  return null;
}

async function saveChatbotConfig(shop, config) {
  // In a real app, this would save to your database
  // Implement your storage logic here
  console.log(`Saving config for shop ${shop}:`, config);
}

async function installScriptTag(session, config) {
  try {
    const client = new shopify.api.clients.Rest({ session });
    
    // Remove existing script tag first
    await removeScriptTag(session);
    
    // Create new script tag
    const scriptTag = {
      script_tag: {
        event: 'onload',
        src: `${config.apiUrl}/widget/embed.js?shop=${session.shop}&chatbot=${config.chatbotId}`,
        display_scope: 'all'
      }
    };
    
    await client.post({
      path: 'script_tags',
      data: scriptTag
    });
    
    console.log(`Installed script tag for shop ${session.shop}`);
  } catch (error) {
    console.error('Error installing script tag:', error);
    throw error;
  }
}

async function removeScriptTag(session) {
  try {
    const client = new shopify.api.clients.Rest({ session });
    
    // Get existing script tags
    const response = await client.get({
      path: 'script_tags'
    });
    
    // Find and remove chatbot script tags
    const scriptTags = response.body.script_tags || [];
    for (const tag of scriptTags) {
      if (tag.src && tag.src.includes('chatbot')) {
        await client.delete({
          path: `script_tags/${tag.id}`
        });
      }
    }
    
    console.log(`Removed script tags for shop ${session.shop}`);
  } catch (error) {
    console.error('Error removing script tag:', error);
    // Don't throw error for removal failures
  }
}

app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
