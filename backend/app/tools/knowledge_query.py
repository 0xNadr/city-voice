from app.services.knowledge_base import KnowledgeBaseService


def query_knowledge_base(query: str) -> str:
    """
    Search the knowledge base for city service information.

    Args:
        query: The user's question about city services

    Returns:
        Formatted string with relevant information
    """
    if not query or not query.strip():
        return "Bitte stellen Sie eine konkrete Frage zu den städtischen Dienstleistungen."

    kb = KnowledgeBaseService()
    results = kb.query(query=query, n_results=3)

    if not results:
        return "Zu dieser Frage konnte ich leider keine Informationen finden. Bitte versuchen Sie es mit einer anderen Formulierung."

    # Format results for the LLM
    formatted_results = []
    for i, result in enumerate(results, 1):
        content = result["content"]
        metadata = result.get("metadata", {})
        category = metadata.get("category", "Allgemein")

        # Truncate very long content
        if len(content) > 500:
            content = content[:500] + "..."

        formatted_results.append(f"[{category}]: {content}")

    return "\n\n".join(formatted_results)
