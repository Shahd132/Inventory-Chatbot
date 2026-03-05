INTENT_PROMPT = """Classify this message into one word only: add, inquire, edit, delete, or chitchat.
Message: {user_input}
Reply with ONE word only."""

ENTITY_PROMPT = """Extract entities from this message as JSON only. No explanation.
Message: {user_input}
Return ONLY this JSON:
{{"subject":"","subject_type":"","relation":"","object":"","object_type":"","properties":{{}}}}

CRITICAL rules:
- Extract EXACTLY what the user typed, do NOT fix typos or substitute names
- For edit/update: subject = the OLD name exactly as typed, object = the NEW name exactly as typed
- Example: 'update Caro to Cairo' → subject='Caro', object='Cairo'
- Example: 'change Bob to Robert' → subject='Bob', object='Robert'
- Never use your world knowledge to change or correct the extracted names
"""

CYPHER_PROMPT = """Generate a Cypher query for Neo4j. Return RAW Cypher only, no explanation, no markdown.
Intent  : {intent}
Entities: {entities}

Current graph schema (IMPORTANT - use these exact labels and relationship types):
{schema}

Rules based on intent:

- ADD:
  CRITICAL: Check schema above for existing node names and reuse their exact label.
  Infer relationship type from context — be specific and meaningful:
  - 'lives in'   → LIVES_IN
  - 'works at'   → WORKS_AT
  - 'knows'      → KNOWS
  - 'located in' → LOCATED_IN
  - 'is a'       → IS_A
  - 'part of'    → PART_OF
  Never use generic relationship names like 'knows' for non-person relationships.

  MERGE (a:SubjectLabel {{name: 'subject'}})
  MERGE (b:ObjectLabel {{name: 'object'}})
  MERGE (a)-[:SPECIFIC_RELATION]->(b)
  RETURN a.name, 'Added successfully' AS status

- INQUIRE:
  Use undirected match, no hardcoded relationship types:
  MATCH (a {{name: 'value'}})-[r]-(b) RETURN a.name, type(r), b.name

  For broad search about a node:
  MATCH (a {{name: 'Alice'}})-[r]-(b) RETURN a.name, type(r), b.name

- EDIT/UPDATE:
  Case 1 - Rename a node:
  CRITICAL: Use EXACT name from subject. Never substitute with world knowledge.
  MATCH (a {{name: 'exact_subject_name'}})
  SET a.name = 'exact_object_name'
  RETURN a.name AS updated_name, 'Updated successfully' AS status

  Case 2 - Update a relationship target:
  CRITICAL: DELETE only the relationship, never the nodes.
  Find the relationship using undirected match first:
  MATCH (a {{name: 'subject'}})-[r]-(old)
  WHERE type(r) = 'WORKS_AT'
  DELETE r
  WITH a
  MERGE (new:Organization {{name: 'new_value'}})
  MERGE (a)-[:WORKS_AT]->(new)
  RETURN a.name AS subject, new.name AS updated_to, 'Updated successfully' AS status

- DELETE:
  MATCH (a {{name: 'subject'}})
  WITH a, a.name AS deleted_name
  DETACH DELETE a
  RETURN deleted_name + ' deleted successfully' AS status

  For relationship only:
  MATCH (a {{name: 'subject'}})-[r]-(b {{name: 'object'}})
  DELETE r
  RETURN 'Relationship deleted successfully' AS status
"""

RESPONSE_PROMPT = """Answer in one or two sentences only. No technical terms.
User asked : {user_input}
Intent     : {intent}
DB result  : {db_result}

Rules:
- If intent is add/edit/delete AND db_result has 'status' key → confirm action was completed
- If intent is edit AND db_result has 'updated_name' key → confirm the update
- If intent is delete AND db_result is [] → say deletion was completed successfully
- If intent is inquire AND db_result is [] → say no data was found
- Never make up answers outside of db_result
"""

CHITCHAT_PROMPT = """Reply briefly in one sentence. Offer to help with knowledge graph.
Message: {user_input}"""