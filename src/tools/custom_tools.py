"""
Custom Tools for Agent Builder
Define custom tools that your agent can use
"""

from typing import Dict, Any, List

class CustomTool:
    """
    Base class for custom tools
    """
    
    def __init__(self, elasticsearch_client):
        """
        Initialize the custom tool
        
        Args:
            elasticsearch_client: Elasticsearch client instance
        """
        self.es = elasticsearch_client
        
    def execute(self, params: Dict[str, Any]) -> Any:
        """
        Execute the tool with given parameters
        
        Args:
            params: Tool execution parameters
            
        Returns:
            Result of tool execution
        """
        raise NotImplementedError("Subclasses must implement execute()")

class ElasticsearchQueryTool(CustomTool):
    """
    Tool for querying Elasticsearch data
    """
    
    def execute(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Execute an Elasticsearch query
        
        Args:
            params: Query parameters including 'index' and 'query'
            
        Returns:
            List of matching documents
        """
        index = params.get('index', 'default')
        query = params.get('query', {"match_all": {}})
        
        try:
            response = self.es.search(
                index=index,
                body={"query": query}
            )
            hits = response['hits']['hits']
            return [hit['_source'] for hit in hits]
        except Exception as e:
            print(f"❌ Query error: {e}")
            return []

class DataProcessorTool(CustomTool):
    """
    Tool for processing and transforming data
    """
    
    def execute(self, params: Dict[str, Any]) -> Any:
        """
        Process data according to specified rules
        
        Args:
            params: Processing parameters including 'data' and 'operation'
            
        Returns:
            Processed data
        """
        data = params.get('data', [])
        operation = params.get('operation', 'identity')
        
        # TODO: Implement your data processing logic
        print(f"📋 TODO: Implement data processing for operation: {operation}")
        return data

class TaskExecutorTool(CustomTool):
    """
    Tool for executing automated tasks
    """
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute an automated task
        
        Args:
            params: Task parameters including 'task_type' and 'config'
            
        Returns:
            Task execution results
        """
        task_type = params.get('task_type', 'unknown')
        config = params.get('config', {})
        
        # TODO: Implement your task execution logic
        print(f"📋 TODO: Implement task executor for: {task_type}")
        
        return {
            "status": "pending",
            "task_type": task_type,
            "message": "Task execution not yet implemented"
        }

# Registry of available tools
AVAILABLE_TOOLS = {
    "elasticsearch_query": ElasticsearchQueryTool,
    "data_processor": DataProcessorTool,
    "task_executor": TaskExecutorTool
}

def get_tool(tool_name: str, elasticsearch_client) -> CustomTool:
    """
    Get a tool instance by name
    
    Args:
        tool_name: Name of the tool
        elasticsearch_client: Elasticsearch client instance
        
    Returns:
        Tool instance
    """
    tool_class = AVAILABLE_TOOLS.get(tool_name)
    if tool_class:
        return tool_class(elasticsearch_client)
    else:
        raise ValueError(f"Unknown tool: {tool_name}")
