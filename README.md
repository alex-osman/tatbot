# Inbox AI Agent

This project creates an AI-powered Gmail agent using LangChain to help manage your inbox.

## Agent Flow

Below is the optimal flow for the agent.

```mermaid
stateDiagram
    direction lr
    [*] --> should_respond
    should_respond --> extract_info : Yes
    should_respond --> [*] : No
    extract_info --> get_gcal_appointments : FIND_DATE
    extract_info --> book_session : BOOK_DATE
    get_gcal_appointments --> draft_response
    book_session --> draft_response
    draft_response --> verify_response
    verify_response --> draft_response: retry
    verify_response --> send_email
    send_email --> [*] : Approve
```

## Additional Work

- [ ] Add a tool to create a draft response
- [ ] Fine train the model to learn from my own email responses
- [ ] Prompts are not optimal and only used for MVP
