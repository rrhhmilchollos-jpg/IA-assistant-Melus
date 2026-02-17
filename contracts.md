# Assistant Melus - Contracts & Implementation Plan

## API Contracts

### Authentication APIs

#### POST /api/auth/session
- **Purpose**: Exchange session_id for session_token
- **Input**: `{ "session_id": "string" }`
- **Output**: `{ "user": {...}, "session_token": "string" }`
- **Action**: Creates/updates user, creates session, sets httpOnly cookie

#### GET /api/auth/me
- **Purpose**: Get current authenticated user
- **Headers**: Authorization: Bearer {token} OR Cookie: session_token
- **Output**: `{ "user_id": "string", "email": "string", "name": "string", "picture": "string", "credits": number }`
- **Error**: 401 if not authenticated

#### POST /api/auth/logout
- **Purpose**: Logout user
- **Action**: Deletes session from DB, clears cookie

### Chat APIs

#### GET /api/conversations
- **Purpose**: Get all conversations for authenticated user
- **Output**: `[{ "conversation_id": "string", "title": "string", "updated_at": "datetime", "message_count": number }]`

#### POST /api/conversations
- **Purpose**: Create new conversation
- **Output**: `{ "conversation_id": "string", "title": "Nueva Conversación", "created_at": "datetime" }`

#### DELETE /api/conversations/{conversation_id}
- **Purpose**: Delete a conversation and all its messages

#### GET /api/conversations/{conversation_id}/messages
- **Purpose**: Get all messages in a conversation
- **Output**: `[{ "message_id": "string", "role": "user|assistant", "content": "string", "timestamp": "datetime", "tokens_used": number }]`

#### POST /api/conversations/{conversation_id}/messages
- **Purpose**: Send message and get AI response
- **Input**: `{ "content": "string" }`
- **Output**: `{ "user_message": {...}, "assistant_message": {...}, "tokens_used": number, "credits_remaining": number }`
- **Process**:
  1. Check user has enough credits
  2. Save user message to DB
  3. Call OpenAI GPT-4o using Emergent LLM Key
  4. Save assistant response to DB
  5. Deduct credits from user
  6. Return both messages

### Credits & Payments APIs

#### GET /api/credits
- **Purpose**: Get user's current credit balance
- **Output**: `{ "credits": number, "credits_used": number }`

#### GET /api/credits/packages
- **Purpose**: Get available credit packages
- **Output**: `[{ "package_id": "string", "name": "string", "credits": number, "price": number, "currency": "usd" }]`

#### POST /api/credits/checkout
- **Purpose**: Create Stripe checkout session
- **Input**: `{ "package_id": "string", "origin_url": "string" }`
- **Output**: `{ "checkout_url": "string", "session_id": "string" }`
- **Action**: Creates payment_transaction record with status "pending"

#### GET /api/credits/checkout/status/{session_id}
- **Purpose**: Check payment status and add credits
- **Output**: `{ "status": "string", "payment_status": "string", "credits_added": number }`
- **Action**: If paid and not processed, add credits to user

#### POST /api/webhook/stripe
- **Purpose**: Handle Stripe webhooks
- **Action**: Process payment events asynchronously

## Database Schema

### users
```json
{
  "user_id": "user_abc123",
  "email": "user@example.com",
  "name": "User Name",
  "picture": "https://...",
  "credits": 10000,
  "credits_used": 0,
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### user_sessions
```json
{
  "session_id": "sess_abc123",
  "user_id": "user_abc123",
  "session_token": "token_...",
  "expires_at": "datetime",
  "created_at": "datetime"
}
```

### conversations
```json
{
  "conversation_id": "conv_abc123",
  "user_id": "user_abc123",
  "title": "Conversation title",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### messages
```json
{
  "message_id": "msg_abc123",
  "conversation_id": "conv_abc123",
  "user_id": "user_abc123",
  "role": "user | assistant",
  "content": "Message content",
  "tokens_used": 150,
  "timestamp": "datetime"
}
```

### payment_transactions
```json
{
  "transaction_id": "txn_abc123",
  "user_id": "user_abc123",
  "stripe_session_id": "cs_...",
  "package_id": "basic",
  "amount": 10.00,
  "currency": "usd",
  "credits": 500000,
  "status": "pending | completed | failed",
  "payment_status": "unpaid | paid",
  "processed": false,
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

## Credit Packages

```python
CREDIT_PACKAGES = {
    "starter": {
        "name": "Starter",
        "credits": 100000,
        "price": 5.00,
        "popular": False
    },
    "basic": {
        "name": "Básico",
        "credits": 500000,
        "price": 10.00,
        "popular": True
    },
    "pro": {
        "name": "Pro",
        "credits": 2000000,
        "price": 29.00,
        "popular": False
    },
    "unlimited": {
        "name": "Unlimited",
        "credits": 10000000,
        "price": 99.00,
        "popular": False
    }
}
```

## Token to Credits Conversion
- 1 token consumed from OpenAI = 1 credit deducted
- New users get 10,000 free credits (~6-8 messages with GPT-4o)

## Frontend Changes from Mock

### Remove Mock Data
- Delete `/app/frontend/src/mock/mockData.js`
- Remove all mock imports from components

### Add API Integration
- Create `/app/frontend/src/api/client.js` for API calls
- Create `/app/frontend/src/context/AuthContext.jsx` for auth state
- Add protected routes

### Add New Pages/Components
- `/login` - Login page with Google OAuth button
- `/dashboard` - Main chat interface (protected)
- `/pricing` - Credit packages page
- `/success` - Payment success page
- `AuthCallback.jsx` - Handle OAuth callback

### Update App.js
- Add routing for all pages
- Wrap app with AuthContext
- Add ProtectedRoute component

## Implementation Flow

### Phase 1: Backend Setup
1. Install emergentintegrations library
2. Add environment variables (EMERGENT_LLM_KEY, STRIPE_API_KEY)
3. Create database models (Pydantic)
4. Implement authentication endpoints
5. Implement chat endpoints with OpenAI integration
6. Implement credits & payment endpoints

### Phase 2: Frontend Integration
1. Remove all mock data
2. Create API client utility
3. Implement AuthContext
4. Create login page with OAuth
5. Create AuthCallback component
6. Update chat interface to use real APIs
7. Add credit balance display
8. Create pricing page
9. Implement payment flow

### Phase 3: Testing
1. Test authentication flow
2. Test chat functionality
3. Test credit deduction
4. Test payment flow
5. Test edge cases (no credits, expired session, etc.)

## Security Considerations
- All chat endpoints require authentication
- Payment amounts defined server-side only
- Session tokens expire after 7 days
- Prevent duplicate credit additions for same payment
- Rate limiting on API endpoints (future)
