import os
import vertexai
from vertexai.types import (
    MemoryBankCustomizationConfig as CustomizationConfig,
    MemoryBankCustomizationConfigMemoryTopic as MemoryTopic,
    MemoryBankCustomizationConfigMemoryTopicCustomMemoryTopic as CustomTopic,
    ReasoningEngineContextSpecMemoryBankConfig as MemoryBankConfig,
)
from dotenv import load_dotenv

load_dotenv()

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
LOCATION = "us-central1"

if not PROJECT_ID:
    print("Error: GOOGLE_CLOUD_PROJECT not found in .env")
    exit(1)

def deploy_agent_engine():
    """
    Deploys a Vertex AI Agent Engine with persistent Memory Bank.
    """
    vertexai.init(project=PROJECT_ID, location=LOCATION)
    
    # Initialize the Vertex AI Client
    client = vertexai.Client(project=PROJECT_ID, location=LOCATION)

    # 1. Define the Custom Memory Topic
    custom_topic = CustomTopic(
        label="card_preferences",
        description="User preferences for their developer card, including theme (hacker, builder, etc.), favorite languages, and color mode (dark or light)."
    )

    memory_topic = MemoryTopic(custom_memory_topic=custom_topic)

    # 2. Configure the Memory Bank
    customization_config = CustomizationConfig(
        memory_topics=[memory_topic]
    )

    memory_bank_config = MemoryBankConfig(
        customization_config=customization_config
    )

    # 3. Create the Agent Engine
    print(f"Creating Agent Engine in project {PROJECT_ID}...")
    
    agent_engine = client.agent_engines.create(
        config={
            "context_spec": {
                "memory_bank_config": memory_bank_config
            }
        }
    )

    # The ID is the last part of the resource name
    agent_engine_id = agent_engine.api_resource.name.split('/')[-1]
    
    print("\n" + "="*40)
    print("SUCCESS: Agent Engine Deployed")
    print(f"AGENT_ENGINE_ID={agent_engine_id}")
    print("="*40)
    print("\nAdd the AGENT_ENGINE_ID to your .env file.")

if __name__ == "__main__":
    deploy_agent_engine()
