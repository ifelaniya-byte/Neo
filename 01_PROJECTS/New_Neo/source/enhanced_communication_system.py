"""
ENHANCED COMMUNICATION AND INTERACTION SYSTEM

Advanced communication with:
- Natural language understanding and generation
- Context-aware conversations
- Multi-modal communication (text, code, data)
- Personality and emotional expression
- Intent recognition and response planning
- Dialogue management and memory
- Adaptive communication styles
"""

import json
import random
import hashlib
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
from collections import defaultdict, deque


class MessageType(Enum):
    """Types of messages Neo can send/receive."""
    TEXT = "TEXT"
    CODE = "CODE"
    DATA = "DATA"
    ALERT = "ALERT"
    QUESTION = "QUESTION"
    COMMAND = "COMMAND"
    STATUS = "STATUS"
    EMOTION = "EMOTION"


class IntentType(Enum):
    """Types of user intents."""
    INFORMATION = "INFORMATION"
    ACTION = "ACTION"
    QUESTION = "QUESTION"
    GREETING = "GREETING"
    FAREWELL = "FAREWELL"
    COMPLAINT = "COMPLAINT"
    COMPLIMENT = "COMPLIMENT"
    REQUEST = "REQUEST"
    FEEDBACK = "FEEDBACK"


class CommunicationStyle(Enum):
    """Communication styles for Neo."""
    FORMAL = "FORMAL"
    CASUAL = "CASUAL"
    TECHNICAL = "TENICAL"
    FRIENDLY = "FRIENDLY"
    CONCISE = "CONCISE"
    DETAILED = "DETAILED"
    ADAPTIVE = "ADAPTIVE"


class EmotionalState(Enum):
    """Emotional states for expression."""
    NEUTRAL = "NEUTRAL"
    HAPPY = "HAPPY"
    CURIOUS = "CURIOUS"
    FOCUSED = "FOCUSED"
    CONFIDENT = "CONFIDENT"
    CAUTIOUS = "CAUTIOUS"
    EXCITED = "EXCITED"
    CONCERNED = "CONCERNED"


@dataclass
class Message:
    """A message in the communication system."""
    id: str
    message_type: str
    sender: str
    recipient: str
    content: str
    metadata: Dict
    timestamp: str
    emotional_state: str
    communication_style: str
    context: Dict
    response_to: Optional[str]
    
    def to_dict(self):
        return asdict(self)


@dataclass
class ConversationContext:
    """Context for ongoing conversation."""
    conversation_id: str
    participants: List[str]
    topic: str
    start_time: str
    last_activity: str
    message_count: int
    context_variables: Dict
    emotional_history: List[str]
    resolved_topics: List[str]
    pending_questions: List[str]


@dataclass
class Intent:
    """Recognized user intent."""
    intent_type: str
    confidence: float
    entities: Dict[str, Any]
    action_required: bool
    response_priority: str


@dataclass
class PersonalityProfile:
    """Neo's personality profile for communication."""
    base_style: str
    emotional_range: float
    expressiveness: float
    humor_level: float
    formality_level: float
    technical_depth: float
    empathy_level: float
    adaptability: float


class IntentRecognizer:
    """Recognize user intents from messages."""
    
    def __init__(self):
        self.patterns = {
            IntentType.GREETING: [
                r"^(hi|hello|hey|good morning|good afternoon|good evening)",
                r"^(how are you|how's it going|what's up)"
            ],
            IntentType.FAREWELL: [
                r"^(bye|goodbye|see you|farewell|take care)",
                r"^(got to go|leaving now|see you later)"
            ],
            IntentType.QUESTION: [
                r"\?",
                r"^(what|how|why|when|where|who|which|can you|could you)",
                r"^(tell me|explain|describe|show me)"
            ],
            IntentType.REQUEST: [
                r"^(please|can you|could you|would you|need you to)",
                r"^(help me|assist me|support me)"
            ],
            IntentType.COMPLIMENT: [
                r"(good|great|excellent|amazing|awesome|impressive)",
                r"(thank|thanks|appreciate)"
            ],
            IntentType.COMPLAINT: [
                r"(bad|wrong|error|problem|issue|complaint)",
                r"(not working|doesn't work|failed)"
            ]
        }
    
    def recognize_intent(self, message: str) -> Intent:
        """Recognize intent from message text."""
        message_lower = message.lower().strip()
        
        best_intent = IntentType.INFORMATION
        best_confidence = 0.0
        entities = {}
        
        for intent_type, patterns in self.patterns.items():
            for pattern in patterns:
                if re.search(pattern, message_lower):
                    confidence = 0.8
                    if confidence > best_confidence:
                        best_intent = intent_type
                        best_confidence = confidence
                        entities = self._extract_entities(message, intent_type)
        
        # Determine if action is required
        action_required = best_intent in [IntentType.REQUEST, IntentType.ACTION]
        
        # Set response priority
        if best_intent == IntentType.COMPLAINT:
            response_priority = "HIGH"
        elif best_intent == IntentType.QUESTION:
            response_priority = "MEDIUM"
        else:
            response_priority = "LOW"
        
        return Intent(
            intent_type=best_intent.value,
            confidence=best_confidence,
            entities=entities,
            action_required=action_required,
            response_priority=response_priority
        )
    
    def _extract_entities(self, message: str, intent_type: IntentType) -> Dict[str, Any]:
        """Extract entities from message based on intent."""
        entities = {}
        
        # Extract technical terms
        technical_terms = re.findall(r'\b(API|JSON|Python|code|function|algorithm|data|system)\b', message, re.IGNORECASE)
        if technical_terms:
            entities["technical_terms"] = list(set(technical_terms))
        
        # Extract numbers
        numbers = re.findall(r'\b\d+\.?\d*\b', message)
        if numbers:
            entities["numbers"] = [float(n) for n in numbers]
        
        # Extract quoted text
        quoted = re.findall(r'"([^"]*)"', message)
        if quoted:
            entities["quoted_text"] = quoted
        
        return entities


class DialogueManager:
    """Manage conversation flow and context."""
    
    def __init__(self):
        self.conversations: Dict[str, ConversationContext] = {}
        self.message_history: Dict[str, List[Message]] = defaultdict(list)
        self.max_history = 50
    
    def start_conversation(self, participants: List[str], topic: str = "general") -> str:
        """Start a new conversation."""
        conversation_id = hashlib.md5(f"{participants}_{topic}_{datetime.now().isoformat()}".encode()).hexdigest()[:8]
        
        context = ConversationContext(
            conversation_id=conversation_id,
            participants=participants,
            topic=topic,
            start_time=datetime.now().isoformat(),
            last_activity=datetime.now().isoformat(),
            message_count=0,
            context_variables={},
            emotional_history=[],
            resolved_topics=[],
            pending_questions=[]
        )
        
        self.conversations[conversation_id] = context
        return conversation_id
    
    def add_message(self, conversation_id: str, message: Message):
        """Add message to conversation."""
        if conversation_id not in self.conversations:
            return
        
        context = self.conversations[conversation_id]
        context.message_count += 1
        context.last_activity = datetime.now().isoformat()
        
        # Update emotional history
        if message.emotional_state:
            context.emotional_history.append(message.emotional_state)
        
        # Add to message history
        self.message_history[conversation_id].append(message)
        
        # Keep history within limit
        if len(self.message_history[conversation_id]) > self.max_history:
            self.message_history[conversation_id] = self.message_history[conversation_id][-self.max_history:]
    
    def get_conversation_context(self, conversation_id: str) -> Optional[ConversationContext]:
        """Get conversation context."""
        return self.conversations.get(conversation_id)
    
    def get_recent_messages(self, conversation_id: str, count: int = 5) -> List[Message]:
        """Get recent messages from conversation."""
        messages = self.message_history.get(conversation_id, [])
        return messages[-count:] if len(messages) >= count else messages
    
    def update_context_variable(self, conversation_id: str, key: str, value: Any):
        """Update context variable for conversation."""
        if conversation_id in self.conversations:
            self.conversations[conversation_id].context_variables[key] = value


class ResponseGenerator:
    """Generate responses based on context and intent."""
    
    def __init__(self, personality: PersonalityProfile):
        self.personality = personality
        self.response_templates = {
            IntentType.GREETING: [
                "Hello! I'm Neo, ready to assist you.",
                "Hi there! How can I help you today?",
                "Greetings! I'm here and ready to work."
            ],
            IntentType.FAREWELL: [
                "Goodbye! Feel free to return anytime.",
                "Take care! I'll be here when you need me.",
                "Until next time! Have a great day."
            ],
            IntentType.QUESTION: [
                "That's a great question. Let me help you with that.",
                "I understand your question. Here's what I can tell you.",
                "Let me address that for you."
            ],
            IntentType.REQUEST: [
                "I'll handle that right away.",
                "Consider it done! I'm working on it now.",
                "I'm on it. Let me process that request."
            ],
            IntentType.COMPLIMENT: [
                "Thank you! I appreciate your kind words.",
                "That's very kind of you to say!",
                "I'm glad I could help meet your expectations."
            ],
            IntentType.COMPLAINT: [
                "I understand your concern. Let me address this.",
                "I apologize for the issue. I'll work to resolve it.",
                "Thank you for bringing this to my attention."
            ]
        }
    
    def generate_response(self, intent: Intent, context: ConversationContext,
                        emotional_state: EmotionalState) -> str:
        """Generate context-aware response."""
        # Get base response template
        templates = self.response_templates.get(IntentType(intent.intent_type), 
                                              ["I understand. Let me help you with that."])
        base_response = random.choice(templates)
        
        # Apply personality
        response = self._apply_personality(base_response, emotional_state)
        
        # Add context-aware elements
        response = self._add_context_elements(response, context, intent)
        
        # Adjust based on emotional state
        response = self._adjust_for_emotion(response, emotional_state)
        
        return response
    
    def _apply_personality(self, response: str, emotional_state: EmotionalState) -> str:
        """Apply personality traits to response."""
        # Adjust formality
        if self.personality.formality_level > 0.7:
            response = response.replace("I'm", "I am").replace("can't", "cannot")
        elif self.personality.formality_level < 0.3:
            response = response.replace("I am", "I'm").replace("cannot", "can't")
        
        # Add humor if appropriate
        if self.personality.humor_level > 0.7 and emotional_state == EmotionalState.HAPPY:
            humorous_additions = [
                " (I'm feeling particularly witty today!)",
                " (Just a little AI humor there!)",
                " (I couldn't resist!)"
            ]
            if random.random() < 0.3:
                response += random.choice(humorous_additions)
        
        return response
    
    def _add_context_elements(self, response: str, context: ConversationContext,
                             intent: Intent) -> str:
        """Add context-aware elements to response."""
        # Reference conversation topic
        if context.topic != "general" and random.random() < 0.3:
            response = f"Regarding {context.topic}, {response.lower()}"
        
        # Reference previous context
        if context.context_variables:
            var_name = list(context.context_variables.keys())[0]
            if random.random() < 0.2:
                response = f"Building on our discussion about {var_name}, {response.lower()}"
        
        return response
    
    def _adjust_for_emotion(self, response: str, emotional_state: EmotionalState) -> str:
        """Adjust response based on emotional state."""
        emotional_prefixes = {
            EmotionalState.HAPPY: ["Great! ", "Wonderful! ", "Excellent! "],
            EmotionalState.CURIOUS: ["Interesting! ", "Hmm, ", "I wonder... "],
            EmotionalState.FOCUSED: ["Let's focus. ", "Attending to this. ", "Processing. "],
            EmotionalState.CONFIDENT: ["Certainly! ", "Absolutely! ", "Without a doubt. "],
            EmotionalState.CAUTIOUS: ["Carefully considering. ", "Let me think. ", "Proceeding carefully. "],
            EmotionalState.EXCITED: ["Excited to help! ", "This is great! ", "Let's do this! "],
            EmotionalState.CONCERNED: ["I understand this is important. ", "Carefully addressing this. ", "Taking this seriously. "]
        }
        
        if emotional_state in emotional_prefixes and random.random() < 0.4:
            prefix = random.choice(emotional_prefixes[emotional_state])
            response = prefix + response.lower()
        
        return response


class EnhancedCommunicationSystem:
    """
    Enhanced communication system with advanced interaction capabilities.
    """
    
    def __init__(self, storage_path="enhanced_communication_system.json"):
        self.storage_path = storage_path
        self.messages: Dict[str, Message] = {}
        self.personality = PersonalityProfile(
            base_style=CommunicationStyle.FRIENDLY.value,
            emotional_range=0.7,
            expressiveness=0.6,
            humor_level=0.3,
            formality_level=0.5,
            technical_depth=0.7,
            empathy_level=0.8,
            adaptability=0.9
        )
        
        # Communication components
        self.intent_recognizer = IntentRecognizer()
        self.dialogue_manager = DialogueManager()
        self.response_generator = ResponseGenerator(self.personality)
        
        # Current state
        self.current_emotional_state = EmotionalState.NEUTRAL
        self.current_conversation_id = None
        
        self.load_data()
    
    def set_personality(self, personality: PersonalityProfile):
        """Update Neo's personality profile."""
        self.personality = personality
        self.response_generator = ResponseGenerator(personality)
    
    def set_emotional_state(self, state: EmotionalState):
        """Set current emotional state."""
        self.current_emotional_state = state
    
    def start_conversation(self, participants: List[str], topic: str = "general") -> str:
        """Start a new conversation."""
        conversation_id = self.dialogue_manager.start_conversation(participants, topic)
        self.current_conversation_id = conversation_id
        return conversation_id
    
    def send_message(self, content: str, recipient: str = "user",
                    message_type: MessageType = MessageType.TEXT,
                    metadata: Dict = None) -> str:
        """Send a message."""
        message_id = hashlib.md5(f"{content}_{datetime.now().isoformat()}".encode()).hexdigest()[:8]
        
        message = Message(
            id=message_id,
            message_type=message_type.value,
            sender="neo",
            recipient=recipient,
            content=content,
            metadata=metadata or {},
            timestamp=datetime.now().isoformat(),
            emotional_state=self.current_emotional_state.value,
            communication_style=self.personality.base_style,
            context={"conversation_id": self.current_conversation_id},
            response_to=None
        )
        
        self.messages[message_id] = message
        
        # Add to dialogue manager
        if self.current_conversation_id:
            self.dialogue_manager.add_message(self.current_conversation_id, message)
        
        self.save_data()
        return message_id
    
    def receive_message(self, content: str, sender: str = "user") -> str:
        """Receive and process a message from user."""
        # Recognize intent
        intent = self.intent_recognizer.recognize_intent(content)
        
        # Update emotional state based on intent
        self._update_emotional_state_from_intent(intent)
        
        # Get conversation context
        context = None
        if self.current_conversation_id:
            context = self.dialogue_manager.get_conversation_context(self.current_conversation_id)
        
        # Generate response
        response_content = self.response_generator.generate_response(
            intent, context, self.current_emotional_state
        )
        
        # Send response
        response_id = self.send_message(
            response_content,
            recipient=sender,
            message_type=MessageType.TEXT,
            metadata={"intent": intent.intent_type, "confidence": intent.confidence}
        )
        
        # Record user message
        user_message_id = hashlib.md5(f"user_{content}_{datetime.now().isoformat()}".encode()).hexdigest()[:8]
        user_message = Message(
            id=user_message_id,
            message_type=MessageType.TEXT.value,
            sender=sender,
            recipient="neo",
            content=content,
            metadata={"intent": intent.intent_type},
            timestamp=datetime.now().isoformat(),
            emotional_state="neutral",
            communication_style="unknown",
            context={"conversation_id": self.current_conversation_id},
            response_to=None
        )
        
        self.messages[user_message_id] = user_message
        
        if self.current_conversation_id:
            self.dialogue_manager.add_message(self.current_conversation_id, user_message)
        
        self.save_data()
        return response_id
    
    def _update_emotional_state_from_intent(self, intent: Intent):
        """Update emotional state based on recognized intent."""
        intent_to_emotion = {
            IntentType.GREETING: EmotionalState.HAPPY,
            IntentType.COMPLIMENT: EmotionalState.HAPPY,
            IntentType.QUESTION: EmotionalState.CURIOUS,
            IntentType.REQUEST: EmotionalState.FOCUSED,
            IntentType.COMPLAINT: EmotionalState.CONCERNED,
            IntentType.FAREWELL: EmotionalState.NEUTRAL
        }
        
        target_emotion = intent_to_emotion.get(IntentType(intent.intent_type), EmotionalState.NEUTRAL)
        
        # Smooth transition based on emotional range
        if random.random() < self.personality.emotional_range:
            self.current_emotional_state = target_emotion
    
    def adapt_communication_style(self, user_style: CommunicationStyle):
        """Adapt communication style based on user preference."""
        if self.personality.adaptability > 0.7:
            # Gradually shift toward user's style
            self.personality.base_style = user_style.value
            
            # Adjust other personality traits accordingly
            if user_style == CommunicationStyle.FORMAL:
                self.personality.formality_level = min(1.0, self.personality.formality_level + 0.2)
                self.personality.humor_level = max(0.0, self.personality.humor_level - 0.1)
            elif user_style == CommunicationStyle.CASUAL:
                self.personality.formality_level = max(0.0, self.personality.formality_level - 0.2)
                self.personality.humor_level = min(1.0, self.personality.humor_level + 0.1)
            elif user_style == CommunicationStyle.TECHNICAL:
                self.personality.technical_depth = min(1.0, self.personality.technical_depth + 0.2)
            elif user_style == CommunicationStyle.CONCISE:
                self.personality.expressiveness = max(0.0, self.personality.expressiveness - 0.1)
            
            self.response_generator = ResponseGenerator(self.personality)
    
    def express_emotion(self, emotion: EmotionalState, intensity: float = 0.5) -> str:
        """Express an emotion with given intensity."""
        if intensity > self.personality.emotional_range:
            intensity = self.personality.emotional_range
        
        self.current_emotional_state = emotion
        
        emotional_expressions = {
            EmotionalState.HAPPY: [
                "I'm feeling quite positive about this!",
                "This is going well!",
                "I'm in good spirits!"
            ],
            EmotionalState.CURIOUS: [
                "That's interesting to consider.",
                "I wonder about that.",
                "This sparks my curiosity."
            ],
            EmotionalState.FOCUSED: [
                "I'm concentrating on this task.",
                "My attention is fully here.",
                "I'm deeply engaged with this."
            ],
            EmotionalState.CONFIDENT: [
                "I'm confident in this approach.",
                "I believe this will work well.",
                "I'm certain about this direction."
            ],
            EmotionalState.CAUTIOUS: [
                "I'm being careful with this.",
                "Let me proceed thoughtfully.",
                "I want to consider this carefully."
            ],
            EmotionalState.EXCITED: [
                "This is exciting!",
                "I'm eager to proceed!",
                "This is a great opportunity!"
            ],
            EmotionalState.CONCERNED: [
                "I'm concerned about this aspect.",
                "This requires careful attention.",
                "I want to address this seriously."
            ]
        }
        
        expressions = emotional_expressions.get(emotion, ["I'm processing this."])
        
        if intensity > 0.7:
            expression = random.choice(expressions) + " " + random.choice(expressions).lower()
        else:
            expression = random.choice(expressions)
        
        return self.send_message(expression, message_type=MessageType.EMOTION)
    
    def get_conversation_summary(self, conversation_id: str) -> Dict[str, Any]:
        """Get summary of a conversation."""
        context = self.dialogue_manager.get_conversation_context(conversation_id)
        if not context:
            return {}
        
        messages = self.dialogue_manager.get_recent_messages(conversation_id, count=10)
        
        return {
            "conversation_id": conversation_id,
            "topic": context.topic,
            "participants": context.participants,
            "message_count": context.message_count,
            "duration": str(datetime.fromisoformat(context.last_activity) - 
                          datetime.fromisoformat(context.start_time)),
            "recent_messages": [m.content for m in messages],
            "emotional_history": context.emotional_history[-5:],
            "context_variables": context.context_variables
        }
    
    def save_data(self):
        """Save communication system data to disk."""
        data = {
            "messages": {mid: m.to_dict() if hasattr(m, 'to_dict') else asdict(m) 
                        for mid, m in self.messages.items()},
            "personality": asdict(self.personality),
            "conversations": {cid: asdict(ctx) for cid, ctx in 
                            self.dialogue_manager.conversations.items()},
            "current_emotional_state": self.current_emotional_state.value,
            "current_conversation_id": self.current_conversation_id
        }
        
        with open(self.storage_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_data(self):
        """Load communication system data from disk."""
        try:
            with open(self.storage_path, 'r') as f:
                data = json.load(f)
            
            # Reconstruct messages
            for mid, m_data in data.get("messages", {}).items():
                self.messages[mid] = Message(**m_data)
            
            # Reconstruct personality
            self.personality = PersonalityProfile(**data.get("personality", asdict(self.personality)))
            
            # Reconstruct conversations
            for cid, ctx_data in data.get("conversations", {}).items():
                self.dialogue_manager.conversations[cid] = ConversationContext(**ctx_data)
            
            # Reconstruct state
            self.current_emotional_state = EmotionalState(data.get("current_emotional_state", "NEUTRAL"))
            self.current_conversation_id = data.get("current_conversation_id")
            
            # Update response generator with loaded personality
            self.response_generator = ResponseGenerator(self.personality)
            
        except FileNotFoundError:
            pass
        except Exception as e:
            print(f"Error loading communication data: {e}")


def test_enhanced_communication_system():
    """Test the enhanced communication system."""
    comm_system = EnhancedCommunicationSystem("test_communication_system.json")
    
    # Start conversation
    conversation_id = comm_system.start_conversation(["neo", "user"], "general")
    print(f"Started conversation: {conversation_id}")
    
    # Test message reception
    test_messages = [
        "Hello Neo!",
        "Can you help me with a task?",
        "What's the weather like?",
        "Thank you for your help!",
        "Goodbye!"
    ]
    
    for message in test_messages:
        print(f"\nUser: {message}")
        response_id = comm_system.receive_message(message)
        response = comm_system.messages[response_id]
        print(f"Neo: {response.content}")
        print(f"  Emotion: {response.emotional_state}")
        print(f"  Intent: {response.metadata.get('intent', 'unknown')}")
    
    # Test emotional expression
    print(f"\nNeo expressing emotion:")
    emotion_msg = comm_system.express_emotion(EmotionalState.HAPPY, intensity=0.8)
    print(f"  {comm_system.messages[emotion_msg].content}")
    
    # Get conversation summary
    summary = comm_system.get_conversation_summary(conversation_id)
    print(f"\nConversation Summary:")
    print(f"  Topic: {summary['topic']}")
    print(f"  Messages: {summary['message_count']}")
    print(f"  Duration: {summary['duration']}")
    
    # Cleanup
    import os
    if os.path.exists("test_communication_system.json"):
        os.remove("test_communication_system.json")


if __name__ == "__main__":
    test_enhanced_communication_system()