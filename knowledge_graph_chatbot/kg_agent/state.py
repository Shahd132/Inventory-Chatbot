from typing import TypedDict, Optional, List

class KGAgentState(TypedDict):
    user_input:       str               
    intent:           Optional[str]     
    entities:         Optional[dict]    
    cypher_query:     Optional[str]      
    db_result:        Optional[list]    
    error:            Optional[str]     
    final_response:   Optional[str]      
    history:          List[dict]        