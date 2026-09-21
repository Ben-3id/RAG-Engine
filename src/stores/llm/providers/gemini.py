from google import genai
from ..generator_interface import GenerateModel 

class Gemini(GenerateModel):

    def __init__(self , api:str , model_id:str , system_instruction:str , streaming:bool = False):
        self.api = api
        self.model = model_id
        self.stream = streaming
        self.system_instruction = system_instruction
        self.client = genai.Client(api_key=self.api)

    def generate_text(self, prompt:str , previous_interaction_id:str = None):
        
        stream = self.client.interactions.create(
            input= prompt , 
            model= self.model,
            system_instruction= self.system_instruction ,
            stream= self.stream ,
            previous_interaction_id = previous_interaction_id  )
        
        if self.stream:
            return self.streaming(stream)
        else:   return stream

    def streaming(self , stream):
        for even in stream:
            if even.event_type == "step.delta":
                if not even.delta.type == "thought_signature":
                    yield even.delta.text 