from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import uuid

# User Models
class User(BaseModel):
    user_id: str
    email: str
    name: str
    picture: str
    credits: int = 10000  # Free credits for new users
    credits_used: int = 0
    created_at: datetime
    updated_at: datetime

class UserSession(BaseModel):
    session_id: str
    user_id: str
    session_token: str
    expires_at: datetime
    created_at: datetime

# Auth Models
class UserRegister(BaseModel):
    email: str
    password: str
    name: str

class UserLogin(BaseModel):
    email: str
    password: str

class SessionRequest(BaseModel):
    session_id: str

class SessionResponse(BaseModel):
    user: User
    session_token: str

class LoginResponse(BaseModel):
    user: User
    session_token: str
    message: str

# Conversation Models
class Conversation(BaseModel):
    conversation_id: str
    user_id: str
    title: str
    model: str = "gpt-4o"
    forked_from: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class ConversationListItem(BaseModel):
    conversation_id: str
    title: str
    model: str
    updated_at: datetime
    message_count: int
    forked_from: Optional[str] = None

class ConversationCreate(BaseModel):
    title: str = "Nueva Conversación"
    model: str = "gpt-4o"
    fork_from: Optional[str] = None

# Message Models
class Message(BaseModel):
    message_id: str
    conversation_id: str
    user_id: str
    role: str  # "user" or "assistant"
    content: str
    tokens_used: int = 0
    model: str = "gpt-4o"
    edited: bool = False
    original_content: Optional[str] = None
    timestamp: datetime

class MessageCreate(BaseModel):
    content: str
    
class MessageEdit(BaseModel):
    content: str

class MessageResponse(BaseModel):
    user_message: Message
    assistant_message: Message
    tokens_used: int
    credits_remaining: int

class AIModel(BaseModel):
    model_id: str
    name: str
    provider: str
    description: str
    popular: bool

# Credits Models
class CreditBalance(BaseModel):
    credits: int
    credits_used: int

class CreditPackage(BaseModel):
    package_id: str
    name: str
    credits: int
    price: float
    currency: str = "usd"
    popular: bool = False
    bonus: int = 0
    base_credits: Optional[int] = None

class CheckoutRequest(BaseModel):
    package_id: Optional[str] = None
    custom_amount: Optional[float] = None
    promo_code: Optional[str] = None
    origin_url: str

# Payment Models
class PaymentTransaction(BaseModel):
    transaction_id: str
    user_id: str
    stripe_session_id: str
    package_id: str
    amount: float
    currency: str
    credits: int
    promo_code: Optional[str] = None
    discount: float = 0
    status: str  # "pending", "completed", "failed"
    payment_status: str  # "unpaid", "paid"
    processed: bool = False
    created_at: datetime
    updated_at: datetime

class TransactionHistory(BaseModel):
    transaction_id: str
    amount: float
    credits: int
    status: str
    created_at: datetime