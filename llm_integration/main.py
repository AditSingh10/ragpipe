"""
Main application for LLM integration with RAG pipeline
"""

from typing import Optional
from .services.rag_orchestrator import RAGOrchestrator
from .models.user_session import UserSession

class AcademicLLMApp:
    """Main application class for handling user queries with LLM and RAG"""
    
    def __init__(self):
        try:
            from ragpipe.services.rag_service import RAGService
            from .services.llm_service import LLMService
            
            print("🔄 Initializing services...")
            
            self.rag_service = RAGService()
            print("   ✅ RAG Service initialized")
            
            self.llm_service = LLMService()
            print("   ✅ LLM Service initialized")
            
            self.rag_orchestrator = RAGOrchestrator(self.rag_service, self.llm_service)
            print("   ✅ RAG Orchestrator initialized")
            
            print("🚀 All services initialized successfully!")
            
        except Exception as e:
            print(f"❌ Error initializing services: {e}")
            raise
    
    def handle_user_query(self, user_id: str, query: str, use_rag: bool = False) -> str:
        """
        Handle a user query with optional RAG augmentation
        
        Args:
            user_id: Unique identifier for the user
            query: User's question
            use_rag: Whether to use RAG for augmentation
            
        Returns:
            LLM response
        """
        try:
            print(f"\n🔍 Processing query: '{query}'")
            print(f"   User: {user_id}")
            print(f"   RAG enabled: {use_rag}")
            
            if use_rag:
                print("   🚀 Using RAG pipeline...")
                # Use RAG orchestrator to get relevant chunks and generate response
                response = self.rag_orchestrator.process_user_query(user_id, query, use_rag=True)
                print("   ✅ RAG response generated")
            else:
                print("   💬 Using direct LLM response...")
                # Use LLM service directly without RAG
                response = self.llm_service.generate_response(query)
                print("   ✅ Direct LLM response generated")
            
            return response
            
        except Exception as e:
            error_msg = f"Error processing query: {e}"
            print(f"❌ {error_msg}")
            return f"I'm sorry, I encountered an error: {error_msg}"
    
    def get_user_session(self, user_id: str) -> Optional[UserSession]:
        """Get or create a user session"""
        # TODO: Implement session management
        pass

def main():
    """Main entry point for the application"""
    print("=== Academic LLM App with RAG Integration ===\n")
    
    try:
        # Initialize the application
        app = AcademicLLMApp()
        
        # Test queries
        test_queries = [
            "How does attention work in transformers?",
            "What is the model architecture?",
            "How does multi-head attention work?"
        ]
        
        print("\n🧪 Testing the integrated system...")
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n--- Test {i} ---")
            print(f"Query: {query}")
            
            # Test with RAG enabled
            print("\n🚀 Testing with RAG (chunked papers):")
            rag_response = app.handle_user_query("test_user", query, use_rag=True)
            print(f"RAG Response: {rag_response[:200]}...")
            
            # Test without RAG (direct LLM)
            print("\n💬 Testing without RAG (direct LLM):")
            direct_response = app.handle_user_query("test_user", query, use_rag=False)
            print(f"Direct Response: {direct_response[:200]}...")
            
            print("-" * 50)
        
        print("\n✅ All tests completed!")
        
        # Interactive mode
        print("\n🎯 Interactive Mode - Ask your own questions!")
        print("Type 'quit' to exit, 'rag' to enable RAG, 'direct' to disable RAG")
        
        use_rag = True  # Default to RAG enabled
        while True:
            try:
                user_input = input(f"\n{'RAG' if use_rag else 'Direct'}> ").strip()
                
                if user_input.lower() == 'quit':
                    print("👋 Goodbye!")
                    break
                elif user_input.lower() == 'rag':
                    use_rag = True
                    print("🚀 RAG enabled")
                    continue
                elif user_input.lower() == 'direct':
                    use_rag = False
                    print("💬 Direct LLM mode")
                    continue
                elif not user_input:
                    continue
                
                # Process the query
                response = app.handle_user_query("interactive_user", user_input, use_rag=use_rag)
                print(f"\n🤖 Response: {response}")
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
        
    except Exception as e:
        print(f"❌ Error in main: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 