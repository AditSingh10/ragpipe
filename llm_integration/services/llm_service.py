"""
Interface for language model interactions
"""

from typing import List, Optional
import requests
import sys
import os

try:
    from ..models.conversation import Message
    from ..config.llm_settings import LLMSettings
except ImportError:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    from llm_integration.models.conversation import Message
    from llm_integration.config.llm_settings import LLMSettings

class LLMService:
    """Service for interacting with language models"""
    
    def __init__(self):
        self.model = LLMSettings.LLM_MODEL
        self.provider = LLMSettings.LLM_PROVIDER
        self.base_url = LLMSettings.OLLAMA_BASE_URL
        self.timeout = LLMSettings.OLLAMA_TIMEOUT

        if self.provider.lower() != 'ollama':
            raise ValueError(f"Only Ollama provider is supported. Got: {self.provider}")
        
        self.client = 'ollama'
        self.conversation_history: List[Message] = []
    
    def generate_response(self, prompt: str, context: str = "") -> str:
        """Generate a response from the LLM"""
        simple_greetings = ['hey', 'hi', 'hello', 'thanks', 'thank you', 'ok', 'okay']
        if prompt.lower().strip() in simple_greetings:
            augmented_prompt = prompt
        elif context:
            augmented_prompt = f"{context}\n\n{prompt}\n\nPlease provide a detailed and comprehensive answer based on the context above."
        else:
            augmented_prompt = prompt

        return self._generate_ollama_response(augmented_prompt)
    
    def _generate_ollama_response(self, prompt: str) -> str:
        """Generate response using Ollama API"""
        try:
            url = f"{self.base_url}/api/generate"
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "stop": ["\n\n", "Question:", "Q:", "A:", "Answer:"],
                "options": {
                    "temperature": 0.7,
                    "num_predict": 2048,
                    "top_k": 40,
                    "top_p": 0.9,
                    "repeat_penalty": 1.1,
                }
            }
            
            response = requests.post(url, json=payload, timeout=self.timeout)
            response.raise_for_status()
            
            result = response.json()
            return result.get('response', '')
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Ollama API error: {e}")
    

    
    def add_to_conversation(self, message: Message):
        """Add a message to the conversation history"""
        pass
    
    def get_conversation_history(self) -> List[Message]:
        """Get the conversation history"""
        pass
    
    def clear_conversation(self):
        """Clear the conversation history"""
        pass 

def main():
    """Test function for LLM service"""
    try:
        print(f"Testing LLM Service with provider: {LLMSettings.LLM_PROVIDER}")
        print(f"Model: {LLMSettings.LLM_MODEL}")
        
        llm_service = LLMService()
        response = llm_service.generate_response("What are some of the limitations of NAT?", """Neural architectures designed by Neural Architecture
            Search (NAS) algorithms achieved state-of-the-art perfor-
            mances on many benchmark datasets. Despite the great
            performance, NAS methods are hard to use because of their
            prohibitively high computational costs. Therefore, many re-
            cent works focused on reducing the computational costs of
            NAS while maintaining the advantage of NAS approaches.
            Neural Architecture Transformer (NAT) [2] is the one
            of such kind of works. The authors introduced the archi-
            tecture transformation concept that requires less computa-
            tional costs than traditional NAS methods. Neural architec-
            ture transformation means that optimizing the performance
            of the network by modifying the operations while maintain-
            ing or reducing the computational costs. In this work, the
            authors transform the original operation of a given neural
            architecture into only identity operation or none operation
            to achieve better performance or less computational costs.
            Although they showed the possibility of the NAT to be
            used for network performance improvement, NAT has sev-
            eral limitations. First, the reproducibility of the algorithm
            is not verified since the authors reported only one result for
            each model. Second, the architecture transformation stage
            and network train stage is totally separated. It requires
            not only a lot of computational resources but also an ad-
            ditional human effort to get a transformed architecture and
            train a neural network. Third, it can only transform the neu-
            ral networks with identical cell architectures. Recent NAS
            works focus on searching macroblock based architectures
            that have various cell architectures. However, those archi-
            tectures cannot be transformed by NAT.
            In this paper, we propose differentiable neural architec-
            ture transformation method that overcomes those limita-
            tions. We claim the following contributions:
            • We carried out extensive reproducibility experiments,
            and the results demonstrate the high reproducibility of
            the proposed method.
            • We propose consecutive architecture transformation
            and network learning. The proposed method automat-
            ically transforms the architecture, trains the network,
            and outputs the trained networks.
            • The proposed method can transform not only identi-
            cal cell architectures but also full network architectures
            with various cell architectures like ProxylessNAS [1].
            ∗Equal contribution
            †Corresponding authors
            2. Related Work
            Since the NAS is introduced by [8], many methods have
            been proposed to search effective neural architecture for
            a given dataset. ENAS [6] presented shared weights that
            dramatically reduced the computational complexity of the
            NAS. DARTS [4] and NAO [5] introduced gradient-based
            NAS schemes that search neural architecture by the gradient
            of architectural parameters and does not need the additional
            controller.


            Figure 1. An example of the network architecture reforging by the proposed method. Until the training of the architecture parameters θis
            finished, both ωand θare trained. After the architecture train step, θis fixed and only ωis trained until we get the final trained network.
            Recently, NAT [2] proposed the architecture transforma-
            tion concept that optimizes given neural architecture. Un-
            like traditional NAS methods that search network architec-
            ture by selecting various operations, NAT only transforms
            the original operations into none or identity operations. Al-
            though the authors showed impressive results in the paper,
            there are several drawbacks of the NAT we claimed in the
            Section 1.""")
        print("✅ Test successful!")
        print(f"Response: {response}")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure Ollama is running: ollama serve")
        print("And the model is available: ollama pull llama2:7b")

if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    main()