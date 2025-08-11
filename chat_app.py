#!/usr/bin/env python3
"""
Chat interface for the academic LLM with RAG capabilities
"""

import os
import sys
sys.path.append('.')

from flask import Flask, render_template, request, jsonify, session
from datetime import datetime
import uuid

from llm_integration.services.llm_service import LLMService
from llm_integration.services.rag_orchestrator import RAGOrchestrator
from ragpipe.services.rag_service import RAGService

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this in production

llm_service = LLMService()
rag_service = RAGService()
rag_orchestrator = RAGOrchestrator(rag_service, llm_service)

chat_sessions = {}  # In production, use a database

@app.route('/')
def index():
    """Main chat interface"""
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
        chat_sessions[session['session_id']] = []
    
    return render_template('chat.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        use_rag = data.get('use_rag', False)
        
        if not user_message:
            return jsonify({'error': 'Message cannot be empty'}), 400
        
        session_id = session.get('session_id')
        if not session_id:
            return jsonify({'error': 'Session not found'}), 400
        
        # Get or create chat session
        if session_id not in chat_sessions:
            chat_sessions[session_id] = []
        
        # Add user message to chat history
        user_msg = {
            'id': str(uuid.uuid4()),
            'type': 'user',
            'content': user_message,
            'timestamp': datetime.now().isoformat(),
            'avatar': '👤'
        }
        chat_sessions[session_id].append(user_msg)
        
        # Generate LLM response
        try:
            if use_rag:
                # Use RAG-enhanced response
                llm_response = rag_orchestrator.process_user_query(session_id, user_message, use_rag=True)
            else:
                # Use direct LLM response
                llm_response = llm_service.generate_response(user_message)
            
            # Add LLM response to chat history
            llm_msg = {
                'id': str(uuid.uuid4()),
                'type': 'assistant',
                'content': llm_response,
                'timestamp': datetime.now().isoformat(),
                'avatar': '🤖'
            }
            chat_sessions[session_id].append(llm_msg)
            
            return jsonify({
                'user_message': user_msg,
                'assistant_message': llm_msg
            })
            
        except Exception as e:
            error_msg = {
                'id': str(uuid.uuid4()),
                'type': 'assistant',
                'content': f"I'm sorry, I encountered an error: {str(e)}",
                'timestamp': datetime.now().isoformat(),
                'avatar': '⚠️'
            }
            chat_sessions[session_id].append(error_msg)
            
            return jsonify({
                'user_message': user_msg,
                'assistant_message': error_msg
            })
    
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/chat/history')
def get_chat_history():
    """Get chat history for current session"""
    session_id = session.get('session_id')
    if session_id and session_id in chat_sessions:
        return jsonify(chat_sessions[session_id])
    return jsonify([])

@app.route('/api/chat/clear', methods=['POST'])
def clear_chat():
    """Clear chat history"""
    session_id = session.get('session_id')
    if session_id and session_id in chat_sessions:
        chat_sessions[session_id] = []
    return jsonify({'success': True})

if __name__ == '__main__':
    print("🚀 Starting Modern Chat UI...")
    print("   Open your browser to: http://localhost:5001")
    print("   Press Ctrl+C to stop the server")
    app.run(debug=True, host='0.0.0.0', port=5001)

