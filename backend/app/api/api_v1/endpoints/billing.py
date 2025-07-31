"""
Stripe billing and subscription management endpoints
Handles webhooks, subscription management, and usage limits
"""

import logging
import stripe
from fastapi import APIRouter, HTTPException, status, Depends, Request
from typing import Dict, Any

from app.core.config import settings
from app.core.supabase_auth import get_current_user_supabase
from app.core.database import get_supabase

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Initialize Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

router = APIRouter()


@router.post("/webhooks/stripe")
async def stripe_webhook(request: Request):
    """
    Handle Stripe webhooks for subscription events
    
    Events handled:
    - customer.subscription.created
    - customer.subscription.updated  
    - customer.subscription.deleted
    - invoice.payment_succeeded
    - invoice.payment_failed
    """
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')
    
    try:
        # Verify webhook signature
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        logger.error("❌ Invalid Stripe webhook payload")
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        logger.error("❌ Invalid Stripe webhook signature")
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    # Handle the event
    event_type = event['type']
    logger.info(f"📡 Processing Stripe webhook: {event_type}")
    
    supabase = get_supabase()
    
    try:
        if event_type == 'customer.subscription.created':
            await _handle_subscription_created(event['data']['object'], supabase)
        
        elif event_type == 'customer.subscription.updated':
            await _handle_subscription_updated(event['data']['object'], supabase)
        
        elif event_type == 'customer.subscription.deleted':
            await _handle_subscription_deleted(event['data']['object'], supabase)
        
        elif event_type == 'invoice.payment_succeeded':
            await _handle_payment_succeeded(event['data']['object'], supabase)
        
        elif event_type == 'invoice.payment_failed':
            await _handle_payment_failed(event['data']['object'], supabase)
        
        logger.info(f"✅ Successfully processed webhook: {event_type}")
        
    except Exception as e:
        logger.error(f"💥 Error processing webhook {event_type}: {str(e)}")
        raise HTTPException(status_code=500, detail="Webhook processing failed")
    
    return {"status": "success"}


async def _handle_subscription_created(subscription: Dict[str, Any], supabase):
    """Handle new subscription creation"""
    customer_id = subscription['customer']
    subscription_id = subscription['id']
    
    # Map Stripe price IDs to subscription tiers
    price_to_tier = {
        'price_basic': 'basic',
        'price_pro': 'pro', 
        'price_enterprise': 'enterprise'
    }
    
    tier = price_to_tier.get(subscription['items']['data'][0]['price']['id'], 'free')
    
    # Update user subscription
    supabase.table("users").update({
        "subscription_tier": tier,
        "stripe_customer_id": customer_id,
        "stripe_subscription_id": subscription_id,
        "subscription_status": "active"
    }).eq("stripe_customer_id", customer_id).execute()


async def _handle_subscription_updated(subscription: Dict[str, Any], supabase):
    """Handle subscription updates (tier changes, renewals)"""
    customer_id = subscription['customer']
    
    price_to_tier = {
        'price_basic': 'basic',
        'price_pro': 'pro',
        'price_enterprise': 'enterprise'
    }
    
    tier = price_to_tier.get(subscription['items']['data'][0]['price']['id'], 'free')
    status = subscription['status']
    
    supabase.table("users").update({
        "subscription_tier": tier,
        "subscription_status": status
    }).eq("stripe_customer_id", customer_id).execute()


async def _handle_subscription_deleted(subscription: Dict[str, Any], supabase):
    """Handle subscription cancellation/downgrade to free"""
    customer_id = subscription['customer']
    
    supabase.table("users").update({
        "subscription_tier": "free",
        "subscription_status": "canceled"
    }).eq("stripe_customer_id", customer_id).execute()


async def _handle_payment_succeeded(invoice: Dict[str, Any], supabase):
    """Handle successful payment"""
    customer_id = invoice['customer']
    
    supabase.table("users").update({
        "subscription_status": "active"
    }).eq("stripe_customer_id", customer_id).execute()


async def _handle_payment_failed(invoice: Dict[str, Any], supabase):
    """Handle failed payment"""
    customer_id = invoice['customer']
    
    supabase.table("users").update({
        "subscription_status": "past_due"
    }).eq("stripe_customer_id", customer_id).execute()


@router.get("/subscription")
async def get_subscription_info(current_user: dict = Depends(get_current_user_supabase)):
    """Get user's current subscription information"""
    supabase = get_supabase()
    
    user_id = current_user["id"]
    
    # Get user subscription details
    response = supabase.table("users").select(
        "subscription_tier", "subscription_status", "stripe_customer_id"
    ).eq("id", user_id).execute()
    
    if not response.data:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_data = response.data[0]
    
    # Get subscription limits based on tier
    tier_limits = {
        "free": {
            "chatbots": 1,
            "documents": 5,
            "messages_per_month": 100,
            "voice_minutes_per_month": 10
        },
        "basic": {
            "chatbots": 5,
            "documents": 50,
            "messages_per_month": 1000,
            "voice_minutes_per_month": 60
        },
        "pro": {
            "chatbots": 20,
            "documents": 500,
            "messages_per_month": 10000,
            "voice_minutes_per_month": 300
        },
        "enterprise": {
            "chatbots": 100,
            "documents": 5000,
            "messages_per_month": 100000,
            "voice_minutes_per_month": 1000
        }
    }
    
    tier = user_data.get("subscription_tier", "free")
    
    return {
        "tier": tier,
        "status": user_data.get("subscription_status", "active"),
        "limits": tier_limits.get(tier, tier_limits["free"]),
        "stripe_customer_id": user_data.get("stripe_customer_id")
    }


@router.get("/usage")
async def get_usage_stats(current_user: dict = Depends(get_current_user_supabase)):
    """Get current usage statistics for the user"""
    supabase = get_supabase()
    
    user_id = current_user["id"]
    
    # Count chatbots
    chatbots_count = supabase.table("chatbots").select("count", count="exact").eq("user_id", user_id).execute()
    
    # Count documents
    documents_count = supabase.table("documents").select("count", count="exact").eq("uploaded_by", user_id).execute()
    
    # Count messages (this month)
    from datetime import datetime, timedelta
    start_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    messages_count = supabase.table("messages").select("count", count="exact").eq("user_id", user_id).gte("created_at", start_of_month.isoformat()).execute()
    
    return {
        "chatbots": chatbots_count.count if hasattr(chatbots_count, 'count') else 0,
        "documents": documents_count.count if hasattr(documents_count, 'count') else 0,
        "messages_this_month": messages_count.count if hasattr(messages_count, 'count') else 0
    }


@router.post("/create-checkout-session")
async def create_checkout_session(
    price_id: str,
    current_user: dict = Depends(get_current_user_supabase)
):
    """Create Stripe checkout session for subscription upgrade"""
    supabase = get_supabase()
    
    user_id = current_user["id"]
    user_email = current_user["email"]
    
    try:
        # Check if user already has Stripe customer ID
        response = supabase.table("users").select("stripe_customer_id").eq("id", user_id).execute()
        user_data = response.data[0]
        
        customer_id = user_data.get("stripe_customer_id")
        
        if not customer_id:
            # Create new Stripe customer
            customer = stripe.Customer.create(
                email=user_email,
                metadata={"user_id": user_id}
            )
            customer_id = customer.id
            
            # Update user with customer ID
            supabase.table("users").update({
                "stripe_customer_id": customer_id
            }).eq("id", user_id).execute()
        
        # Create checkout session
        checkout_session = stripe.checkout.Session.create(
            customer=customer_id,
            payment_method_types=['card'],
            line_items=[{
                'price': price_id,
                'quantity': 1,
            }],
            mode='subscription',
            success_url=f"{settings.ALLOWED_HOSTS[0]}/dashboard/billing?success=true",
            cancel_url=f"{settings.ALLOWED_HOSTS[0]}/dashboard/billing?canceled=true",
            metadata={
                "user_id": user_id
            }
        )
        
        return {"session_id": checkout_session.id, "url": checkout_session.url}
        
    except Exception as e:
        logger.error(f"💥 Error creating checkout session: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create checkout session")


@router.post("/create-portal-session")
async def create_portal_session(current_user: dict = Depends(get_current_user_supabase)):
    """Create Stripe customer portal session"""
    supabase = get_supabase()
    
    user_id = current_user["id"]
    
    try:
        response = supabase.table("users").select("stripe_customer_id").eq("id", user_id).execute()
        user_data = response.data[0]
        
        customer_id = user_data.get("stripe_customer_id")
        if not customer_id:
            raise HTTPException(status_code=404, detail="No Stripe customer found")
        
        portal_session = stripe.billing_portal.Session.create(
            customer=customer_id,
            return_url=f"{settings.ALLOWED_HOSTS[0]}/dashboard/billing"
        )
        
        return {"url": portal_session.url}
        
    except Exception as e:
        logger.error(f"💥 Error creating portal session: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create portal session")