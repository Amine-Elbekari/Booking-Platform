import json
import os
import requests
from sqlalchemy.ext.asyncio import AsyncSession
from models.user import User
from schemas.rag import ChatRequest, ChatResponse, Source
from agent.schemas import AgentDecision
from agent.prompts import ROUTER_PROMPT, GENERATION_PROMPT
from agent.tools import tool_search_documents, tool_get_user_bookings, tool_get_booking, tool_get_property
from fastapi import HTTPException
import asyncio

async def run_agent_loop(request: ChatRequest, current_user: User, db: AsyncSession) -> ChatResponse:
    ollama_base_url = os.getenv("OLLAMA_BASE_URL")
    ollama_model = os.getenv("OLLAMA_MODEL")
    
    if not ollama_base_url or not ollama_model:
        raise HTTPException(status_code=500, detail="Ollama configuration is missing.")

    history_text = ""
    if request.history:
        history_text = "Recent conversation history:\n"
        for msg in request.history:
            history_text += f"{msg.role.capitalize()}: {msg.content}\n"

    # Deterministic query reformulation for conversational follow-ups
    reformulated_question = request.question
    is_doc_follow_up = False
    if request.history and len(request.history) >= 2:
        last_user_msg = next((m.content for m in reversed(request.history) if m.role == "user"), "")
        last_asst_msg = next((m.content for m in reversed(request.history) if m.role == "assistant"), "")
        
        if last_user_msg and "unrelated" not in last_asst_msg.lower():
            follow_up_words = {"it", "this", "that", "they", "them", "about", "if", "he", "she"}
            words = set(request.question.lower().split())
            is_follow_up = len(words) <= 10 or bool(words.intersection(follow_up_words))
            
            if is_follow_up:
                reformulated_question = f"{last_user_msg} {request.question}"
                print(f"AGENT Context Injection: Reformulated question -> '{reformulated_question}'")
                
                # Deterministic override for qwen2.5:3b routing failures
                doc_keywords = ["cancel", "policy", "rules", "guests", "check-in", "checkin", "late", "document", "pdf"]
                if any(kw in reformulated_question.lower() for kw in doc_keywords):
                    is_doc_follow_up = True
    # 1. Phase 1: Determine Intent and Tool Selection
    
    def call_ollama(prompt, format="json"):
        response = requests.post(
            f"{ollama_base_url}/api/generate",
            json={
                "model": ollama_model,
                "prompt": prompt,
                "stream": False,
                "format": format
            },
            timeout=30
        )
        response.raise_for_status()
        return response.json()

    try:
        if is_doc_follow_up:
            print("AGENT: Deterministic routing override for document follow-up.")
            decision = AgentDecision(
                intent="DOCUMENTS",
                tool="search_documents",
                arguments={"query": reformulated_question}
            )
        else:
            router_prompt_text = ROUTER_PROMPT.format(
                history_text=history_text,
                question=reformulated_question
            )
        
            res_json = await asyncio.to_thread(call_ollama, router_prompt_text)
            raw_text = res_json.get("response", "").strip()
            
            print(f"DEBUG AGENT ROUTER RAW: {raw_text}")
            if raw_text.startswith("```json"):
                raw_text = raw_text[7:]
            if raw_text.endswith("```"):
                raw_text = raw_text[:-3]
                
            decision_data = json.loads(raw_text.strip())
            decision = AgentDecision(**decision_data)
            
        print(f"AGENT Intent: {decision.intent} | Tool: {decision.tool} | Args: {decision.arguments}")
    except Exception as e:
        print(f"Agent Router error: {e}")
        # Graceful fallback if JSON parsing or Ollama fails
        decision = AgentDecision(intent="GENERAL_VILLASTAY", tool=None, arguments={})

    # 2. Phase 2: Intercepts & Execution
    if decision.intent == "UNRELATED":
        return ChatResponse(
            answer="I'm here to help with VillaStay — bookings, properties, reservations, rental policies, and rental documents. I can't help with unrelated topics.",
            sources=[]
        )
        
    tool_context = ""
    tool_sources = []
    
    # Tool Execution
    if decision.tool == "search_documents":
        query = decision.arguments.get("query", reformulated_question)
        # Use reformulated question if LLM returned the original raw question
        if query == request.question:
            query = reformulated_question
            
        result = await tool_search_documents(query, str(current_user.id), db)
        tool_context = f"--- UPLOADED DOCUMENTS ---\n{result.get('message', '')}\n{result.get('context', '')}".strip()
        tool_sources = result.get("sources", [])
        print(f"AGENT Tool result: Retrieved {len(tool_sources)} chunks")
        
    elif decision.tool == "get_user_bookings":
        result = await tool_get_user_bookings(str(current_user.id), db)
        tool_context = result.get('message', '') or result.get('context', '')
        print(f"AGENT Tool result: {result['status']}")
        
    elif decision.tool == "get_booking":
        booking_id = decision.arguments.get("booking_id", "")
        result = await tool_get_booking(booking_id, str(current_user.id), db)
        tool_context = result.get('message', '') or result.get('context', '')
        print(f"AGENT Tool result: {result['status']}")
        
    elif decision.tool == "get_property":
        search_term = decision.arguments.get("search_term", "")
        result = await tool_get_property(search_term, db)
        tool_context = result.get('message', '') or result.get('context', '')
        print(f"AGENT Tool result: {result['status']}")
        
    else:
        tool_context = "No tools were executed. Answer generally using Base Knowledge."

    # 3. Phase 3: Final Generation
    final_prompt_text = GENERATION_PROMPT.format(
        tool_context=tool_context,
        question=request.question
    )

    try:
        res_json = await asyncio.to_thread(call_ollama, final_prompt_text)
        raw_text = res_json.get("response", "").strip()
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:]
        if raw_text.endswith("```"):
            raw_text = raw_text[:-3]
            
        data = json.loads(raw_text.strip())
        print(f"DEBUG AGENT GENERATION RAW: {data}")
        answer = data.get("answer", "I'm sorry, I couldn't process that.")
        used_ids = data.get("used_source_ids", [])
        
        # Source Mapping
        sources = []
        seen_sources = set()
        
        for uid in used_ids:
            # Map LLM source ID back to our tool_sources objects
            matched_source = next((s for s in tool_sources if uid in s['chunk_id']), None)
            if matched_source:
                source_key = (matched_source['document_id'], matched_source['page'], matched_source['row'])
                if source_key not in seen_sources:
                    sources.append(Source(**matched_source))
                    seen_sources.add(source_key)
                    
        print(f"AGENT LLM response generated. Sources mapped: {len(sources)}")
                    
    except requests.exceptions.RequestException as e:
        print(f"Ollama connection error: {e}")
        raise HTTPException(status_code=500, detail="The local AI assistant is currently unreachable. Please try again later.")
    except Exception as e:
        print(f"Ollama generation/parsing error: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate answer from the local LLM.")

    return ChatResponse(answer=answer, sources=sources)
