#!/usr/bin/env python3
"""
Stripe Webhook Setup Script
Helps configure Stripe webhooks for production
"""

import stripe
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
if not stripe.api_key:
    print("❌ STRIPE_SECRET_KEY not found in environment")
    sys.exit(1)

print("🔧 Stripe Webhook Setup Tool")
print("=" * 40)

# Production webhook URL (update this)
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "https://api.yourdomain.com/api/v1/billing/webhooks/stripe")

def setup_webhooks():
    """Set up Stripe webhooks"""
    
    print(f"📡 Setting up webhook URL: {WEBHOOK_URL}")
    
    # Events to listen for
    events = [
        "customer.subscription.created",
        "customer.subscription.updated", 
        "customer.subscription.deleted",
        "invoice.payment_succeeded",
        "invoice.payment_failed",
        "checkout.session.completed",
        "customer.created",
        "customer.updated"
    ]
    
    try:
        # Create webhook endpoint
        webhook_endpoint = stripe.WebhookEndpoint.create(
            url=WEBHOOK_URL,
            enabled_events=events,
            description="Chatbot SaaS Platform Webhook"
        )
        
        print("✅ Webhook endpoint created successfully!")
        print(f"🆔 Webhook ID: {webhook_endpoint.id}")
        print(f"🔑 Webhook Secret: {webhook_endpoint.secret}")
        print(f"🎯 URL: {webhook_endpoint.url}")
        
        # Save webhook secret to .env file
        with open(".env", "a") as f:
            f.write(f"\n# Stripe Webhook Configuration\n")
            f.write(f"STRIPE_WEBHOOK_SECRET={webhook_endpoint.secret}\n")
            f.write(f"WEBHOOK_ENDPOINT_ID={webhook_endpoint.id}\n")
        
        print("\n📋 Webhook secret saved to .env file")
        print("\n🎯 Next steps:")
        print("1. Copy the webhook secret to your production .env")
        print("2. Test the webhook with Stripe CLI")
        print("3. Monitor webhook events in Stripe Dashboard")
        
    except stripe.error.StripeError as e:
        print(f"❌ Stripe error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

def list_webhooks():
    """List existing webhooks"""
    try:
        webhooks = stripe.WebhookEndpoint.list()
        
        if not webhooks.data:
            print("📭 No webhooks found")
            return
            
        print("\n📋 Existing webhooks:")
        for webhook in webhooks.data:
            print(f"  🆔 {webhook.id}")
            print(f"  🎯 {webhook.url}")
            print(f"  📅 Created: {webhook.created}")
            print(f"  ✅ Enabled: {webhook.enabled}")
            print(f"  📊 Events: {len(webhook.enabled_events)}")
            print("-" * 40)
            
    except Exception as e:
        print(f"❌ Error listing webhooks: {e}")

def delete_webhook(webhook_id):
    """Delete a webhook"""
    try:
        stripe.WebhookEndpoint.delete(webhook_id)
        print(f"✅ Webhook {webhook_id} deleted")
    except Exception as e:
        print(f"❌ Error deleting webhook: {e}")

def main():
    """Main CLI interface"""
    
    print("Choose an action:")
    print("1. Setup new webhook")
    print("2. List existing webhooks")
    print("3. Delete webhook")
    print("4. Exit")
    
    choice = input("\nEnter choice (1-4): ").strip()
    
    if choice == "1":
        setup_webhooks()
    elif choice == "2":
        list_webhooks()
    elif choice == "3":
        webhook_id = input("Enter webhook ID to delete: ").strip()
        if webhook_id:
            confirm = input(f"Are you sure you want to delete {webhook_id}? (y/N): ").strip()
            if confirm.lower() == "y":
                delete_webhook(webhook_id)
    elif choice == "4":
        print("👋 Goodbye!")
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    main()