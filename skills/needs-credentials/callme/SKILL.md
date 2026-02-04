---
name: callme
description: Message the user on Telegram when you need input, want to report progress, or need real-time discussion. Use for completed tasks, blocking questions, or milestone celebrations.
allowed-tools:
  - mcp__callme__initiate_call
  - mcp__callme__continue_call
  - mcp__callme__speak_to_user
  - mcp__callme__end_call
---

# Telegram Message Input Skill

## Description

Message the user on Telegram for real-time text conversations. Use this when you need input, want to report on completed work, or need to discuss next steps.

## When to Use This Skill

**Use when:**
- You've **completed a significant task** and want to report status and ask what's next
- You need **real-time user input** for complex decisions
- A question requires **back-and-forth discussion** to fully understand
- You're **blocked** and need urgent clarification to proceed
- You want to **celebrate a milestone** or walk the user through completed work
- A task will take a long time and the user should be notified when it's done

**Do NOT use for:**
- Information the user has already provided
- Every minor step — batch updates for significant milestones

## Tools

### `initiate_call`
Start a Telegram conversation with the user.

**Parameters:**
- `message` (string): What you want to say. Be natural and conversational.

**Returns:**
- Conversation ID and the user's text response

### `continue_call`
Continue an active conversation with a follow-up message.

**Parameters:**
- `call_id` (string): The conversation ID from `initiate_call`
- `message` (string): Your follow-up message

**Returns:**
- The user's response

### `speak_to_user`
Send a message without waiting for a response. Use this to acknowledge requests or provide status updates before starting time-consuming operations.

**Parameters:**
- `call_id` (string): The conversation ID from `initiate_call`
- `message` (string): What to send to the user

**Returns:**
- Confirmation that the message was sent

**When to use:**
- Acknowledge a request before starting a long operation (e.g., "Let me search for that...")
- Provide status updates during multi-step tasks
- Keep the conversation flowing naturally so the user knows you're working

### `end_call`
End an active conversation with a closing message.

**Parameters:**
- `call_id` (string): The conversation ID from `initiate_call`
- `message` (string): Your closing message (say goodbye!)

**Returns:**
- Conversation duration in seconds

## Example Usage

**Simple conversation:**
```
1. initiate_call: "Hey! I finished the auth system. Should I move on to the API endpoints?"
2. User responds: "Yes, go ahead"
3. end_call: "Perfect! I'll start on the API endpoints. Talk soon!"
```

**Multi-turn conversation:**
```
1. initiate_call: "I'm working on payments. Should I use Stripe or PayPal?"
2. User: "Use Stripe"
3. continue_call: "Got it. Do you want the full checkout flow or just a simple button?"
4. User: "Full checkout flow"
5. end_call: "Awesome, I'll build the full Stripe checkout. I'll let you know when it's ready!"
```

**Using speak_to_user for long operations:**
```
1. initiate_call: "Hey! I finished the database migration. What should I work on next?"
2. User: "Can you look up the latest API documentation for Stripe?"
3. speak_to_user: "Sure! Let me search for that. Give me a moment..."
4. [Perform web search and gather information]
5. continue_call: "I found the latest Stripe API docs. They released v2024.1 with new payment methods..."
6. User: "Great, implement that"
7. end_call: "Perfect! I'll implement the new payment methods. Talk soon!"
```

## Best Practices

1. **Be conversational** — Talk naturally, like a real conversation
2. **Provide context** — Explain what you've done before asking questions
3. **Offer clear options** — Make decisions easy with specific choices
4. **Use speak_to_user for acknowledgments** — Before time-consuming operations (searches, file reads, etc.), use `speak_to_user` to acknowledge the request so the user isn't left wondering what's happening
5. **Always end gracefully** — Say goodbye and state what you'll do next
