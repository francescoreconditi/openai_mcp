import streamlit as st
import httpx
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BACKEND_URL = "http://localhost:8000"


class ChatbotUI:
    def __init__(self):
        self.backend_url = BACKEND_URL
        
    def initialize_session_state(self):
        if "messages" not in st.session_state:
            st.session_state.messages = []
        if "conversation_id" not in st.session_state:
            st.session_state.conversation_id = None
        if "use_tools" not in st.session_state:
            st.session_state.use_tools = True
    
    async def send_message(self, message: str, use_tools: bool) -> Dict[str, Any]:
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.post(
                    f"{self.backend_url}/chat",
                    json={
                        "message": message,
                        "conversation_id": st.session_state.conversation_id,
                        "use_tools": use_tools
                    }
                )
                response.raise_for_status()
                return response.json()
            except Exception as e:
                logger.error(f"Error sending message: {str(e)}")
                return {"error": str(e)}
    
    def display_message(self, role: str, content: str, timestamp: Optional[str] = None, tools_used: Optional[list] = None):
        if role == "user":
            with st.chat_message("user"):
                st.write(content)
                if timestamp:
                    st.caption(f"Sent at {timestamp}")
        else:
            with st.chat_message("assistant"):
                st.write(content)
                if tools_used:
                    with st.expander("Tools used"):
                        for tool in tools_used:
                            st.write(f"- {tool}")
                if timestamp:
                    st.caption(f"Received at {timestamp}")
    
    def run(self):
        st.set_page_config(
            page_title="Chatbot OpenAI + MCP",
            page_icon="💬",
            layout="wide"
        )
        
        self.initialize_session_state()
        
        st.title("Chat with OpenAI powered by MCP tools 💬🔧")
        
        with st.sidebar:
            st.header("Settings")
            
            use_tools = st.checkbox(
                "Use MCP Tools",
                value=st.session_state.use_tools,
                help="Enable/disable MCP tool usage in responses"
            )
            st.session_state.use_tools = use_tools
            
            st.divider()
            
            if st.button("Clear Conversation", type="secondary"):
                st.session_state.messages = []
                st.session_state.conversation_id = None
                st.rerun()
            
            st.divider()
            
            st.caption("Backend Status")
            try:
                response = httpx.get(f"{self.backend_url}/health", timeout=2.0)
                if response.status_code == 200:
                    st.success("Backend: Online ✅")
                else:
                    st.error("Backend: Error ❌")
            except:
                st.error("Backend: Offline ❌")
            
            try:
                response = httpx.get("http://localhost:8001/health", timeout=2.0)
                if response.status_code == 200:
                    st.success("MCP Server: Online ✅")
                else:
                    st.error("MCP Server: Error ❌")
            except:
                st.error("MCP Server: Offline ❌")
        
        chat_container = st.container()
        
        with chat_container:
            for message in st.session_state.messages:
                self.display_message(
                    message["role"],
                    message["content"],
                    message.get("timestamp"),
                    message.get("tools_used")
                )
        
        if prompt := st.chat_input("Ask me a question about Streamlit's open-source Python library!"):
            timestamp = datetime.now().strftime("%H:%M:%S")
            
            st.session_state.messages.append({
                "role": "user",
                "content": prompt,
                "timestamp": timestamp
            })
            
            with chat_container:
                self.display_message("user", prompt, timestamp)
            
            with st.spinner("Thinking..."):
                response = asyncio.run(self.send_message(prompt, st.session_state.use_tools))
            
            if "error" in response:
                st.error(f"Error: {response['error']}")
            else:
                assistant_message = response.get("response", "")
                conversation_id = response.get("conversation_id")
                tools_used = response.get("tools_used")
                response_timestamp = datetime.now().strftime("%H:%M:%S")
                
                st.session_state.conversation_id = conversation_id
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": assistant_message,
                    "timestamp": response_timestamp,
                    "tools_used": tools_used
                })
                
                with chat_container:
                    self.display_message("assistant", assistant_message, response_timestamp, tools_used)
                
                st.rerun()


def main():
    app = ChatbotUI()
    app.run()


if __name__ == "__main__":
    main()